import json
import subprocess
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from oblak.core.config import get_settings
from oblak.models.entities import Function, FunctionStatus, Invocation, User
from oblak.orchestrator.subprocess_sandbox import SubprocessSandboxOrchestrator
from oblak.services.audit_service import AuditService
from oblak.storage.local_storage import LocalFunctionStorage, StorageError
from oblak.verifier.code_verifier import CodeVerifier


class FunctionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = LocalFunctionStorage()
        self.verifier = CodeVerifier()
        self.orchestrator = SubprocessSandboxOrchestrator()
        self.audit = AuditService(db)
        self.settings = get_settings()

    async def upload(self, owner: User, name: str, file: UploadFile) -> Function:
        data = await file.read()
        self._validate_zip(data)
        try:
            storage_path = self.storage.save_zip(owner.id, name, data)
        except StorageError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        function = Function(owner_id=owner.id, name=name, storage_path=str(storage_path))
        self.db.add(function)
        self.db.commit()
        self.db.refresh(function)
        self.audit.record("function.uploaded", "function", function.id, owner, {"name": name})

        source_dir = self.storage.source_dir(function.storage_path)
        report = self.verifier.verify(source_dir)
        function.verification_report = json.dumps(report.to_dict())
        function.status = FunctionStatus.verified if report.accepted else FunctionStatus.rejected
        if report.accepted:
            self._prepare(source_dir)
            function.status = FunctionStatus.prepared
        self.db.commit()
        self.db.refresh(function)
        self.audit.record("function.verified", "function", function.id, owner, report.to_dict())
        return function

    def invoke(self, invoke_token: str, payload: dict[str, Any]) -> Invocation:
        function = self.db.query(Function).filter(Function.invoke_token == invoke_token).one_or_none()
        if function is None:
            raise HTTPException(status_code=404, detail="Function not found")
        if function.status != FunctionStatus.prepared:
            raise HTTPException(status_code=409, detail="Function is not prepared for execution")
        source_dir = self.storage.source_dir(function.storage_path)
        result = self.orchestrator.execute(source_dir, payload)
        invocation = Invocation(
            function_id=function.id,
            status=result.status,
            duration_ms=result.duration_ms,
            stdout=result.stdout,
            stderr=result.stderr,
            result_json=json.dumps({"result": result.result}, default=str),
        )
        self.db.add(invocation)
        self.db.commit()
        self.db.refresh(invocation)
        self.audit.record("function.invoked", "function", function.id, function.owner, {"status": result.status})
        return invocation

    def list_functions(self, owner: User) -> list[Function]:
        return self.db.query(Function).filter(Function.owner_id == owner.id).order_by(Function.created_at.desc()).all()

    def _validate_zip(self, data: bytes) -> None:
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                names = archive.namelist()
        except zipfile.BadZipFile as exc:
            raise HTTPException(status_code=400, detail="Upload must be a zip archive") from exc
        if not any(Path(name).name == "handler.py" for name in names):
            raise HTTPException(status_code=400, detail="Archive must include handler.py")

    def _prepare(self, source_dir: Path) -> None:
        """Prepare an uploaded function for execution.

        If `requirements.txt` exists, dependencies are installed into a per-function target
        directory (`.oblak-deps`) instead of the server environment. This is still not a
        substitute for a Firecracker root filesystem, but it makes the academic Lambda flow
        functional and keeps dependencies isolated at the filesystem level.
        """
        requirements = source_dir / "requirements.txt"
        deps_dir = source_dir / ".oblak-deps"
        marker = source_dir / ".oblak-prepared"

        if requirements.exists() and self.settings.enable_dependency_install:
            deps_dir.mkdir(exist_ok=True)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-input",
                    "--target",
                    str(deps_dir),
                    "-r",
                    str(requirements),
                ],
                text=True,
                capture_output=True,
                timeout=self.settings.dependency_install_timeout_seconds,
                check=False,
            )
            if completed.returncode != 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "message": "Dependency installation failed",
                        "stderr": completed.stderr[-4000:],
                    },
                )

        marker.write_text(
            "prepared=true\n"
            f"requirements_present={requirements.exists()}\n"
            f"dependencies_installed={deps_dir.exists()}\n",
            encoding="utf-8",
        )
