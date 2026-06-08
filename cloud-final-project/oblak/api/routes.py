import json

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from oblak.db.session import get_db
from oblak.models.entities import AuditEvent, User
from oblak.schemas.dto import AuditEventResponse, FunctionResponse, InvokeRequest, InvokeResponse
from oblak.security.auth import require_user
from oblak.services.function_service import FunctionService

router = APIRouter()


def function_response(request: Request, function) -> FunctionResponse:
    return FunctionResponse(
        id=function.id,
        name=function.name,
        status=function.status.value,
        invoke_url=str(request.url_for("invoke_function", token=function.invoke_token)),
        verification_report=json.loads(function.verification_report or "{}"),
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/functions", response_model=FunctionResponse)
async def upload_function(
    request: Request,
    name: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    function = await FunctionService(db).upload(user, name, file)
    return function_response(request, function)


@router.get("/functions", response_model=list[FunctionResponse])
def list_functions(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    return [function_response(request, item) for item in FunctionService(db).list_functions(user)]


@router.post("/invoke/{token}", response_model=InvokeResponse, name="invoke_function")
def invoke_function(token: str, body: InvokeRequest, db: Session = Depends(get_db)):
    invocation = FunctionService(db).invoke(token, body.payload)
    return InvokeResponse(
        invocation_id=invocation.id,
        status=invocation.status,
        duration_ms=invocation.duration_ms,
        result=json.loads(invocation.result_json).get("result"),
        stdout=invocation.stdout,
        stderr=invocation.stderr,
    )


@router.get("/audit", response_model=list[AuditEventResponse])
def audit_events(user: User = Depends(require_user), db: Session = Depends(get_db)):
    rows = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()
    return [
        AuditEventResponse(
            action=row.action,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            details=json.loads(row.details_json or "{}"),
        )
        for row in rows
    ]
