import logging
import json
from datetime import datetime, UTC
import uuid

logging.basicConfig(filename='app.log', level=logging.INFO)

def log_event(event_type, user_id, ip, message, security_event=False):
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip": ip,
        "request_id": str(uuid.uuid4()),
        "message": message,
        "security_event": security_event
    }
    logging.info(json.dumps(log_entry))

log_event(
    event_type="USER_LOGIN",
    user_id="123",
    ip="192.168.0.1",
    message="User logged in",
    security_event=True
)