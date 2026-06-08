from typing import Any

from pydantic import BaseModel, Field


class FunctionResponse(BaseModel):
    id: str
    name: str
    status: str
    invoke_url: str
    verification_report: dict[str, Any]


class InvokeRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    invocation_id: str
    status: str
    duration_ms: int
    result: Any
    stdout: str
    stderr: str


class AuditEventResponse(BaseModel):
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any]
