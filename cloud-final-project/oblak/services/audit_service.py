import json
from typing import Any

from sqlalchemy.orm import Session

from oblak.models.entities import AuditEvent, User


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        actor: User | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = AuditEvent(
            actor_id=actor.id if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=json.dumps(details or {}, sort_keys=True),
        )
        self.db.add(event)
        self.db.commit()
