import shutil
import zipfile
from pathlib import Path

from oblak.core.config import get_settings


class StorageError(ValueError):
    pass


class LocalFunctionStorage:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = self.settings.storage_root

    def save_zip(self, owner_id: str, function_name: str, data: bytes) -> Path:
        if len(data) > self.settings.max_archive_bytes:
            raise StorageError("Archive is too large")
        target = self.root / owner_id / function_name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        archive_path = target / "source.zip"
        archive_path.write_bytes(data)
        self._safe_extract(archive_path, target / "source")
        return target

    def _safe_extract(self, archive_path: Path, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                member_path = (destination / member.filename).resolve()
                if not str(member_path).startswith(str(destination.resolve())):
                    raise StorageError("Archive contains unsafe path traversal")
                if member.file_size > self.settings.max_archive_bytes:
                    raise StorageError("Archive member is too large")
            archive.extractall(destination)

    def source_dir(self, storage_path: str) -> Path:
        return Path(storage_path) / "source"
