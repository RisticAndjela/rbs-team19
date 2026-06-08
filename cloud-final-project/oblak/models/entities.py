import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oblak.db.session import Base


def new_id() -> str:
    return str(uuid.uuid4())


class FunctionStatus(str, enum.Enum):
    uploaded = "uploaded"
    verified = "verified"
    rejected = "rejected"
    prepared = "prepared"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    api_key_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    functions: Mapped[list["Function"]] = relationship(back_populates="owner")


class Function(Base):
    __tablename__ = "functions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[FunctionStatus] = mapped_column(Enum(FunctionStatus), default=FunctionStatus.uploaded)
    verification_report: Mapped[str] = mapped_column(Text, default="{}")
    invoke_token: Mapped[str] = mapped_column(String(80), unique=True, index=True, default=new_id)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner: Mapped[User] = relationship(back_populates="functions")
    invocations: Mapped[list["Invocation"]] = relationship(back_populates="function")


class Invocation(Base):
    __tablename__ = "invocations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    function_id: Mapped[str] = mapped_column(ForeignKey("functions.id"), index=True)
    status: Mapped[str] = mapped_column(String(40))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    stdout: Mapped[str] = mapped_column(Text, default="")
    stderr: Mapped[str] = mapped_column(Text, default="")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    function: Mapped[Function] = relationship(back_populates="invocations")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
