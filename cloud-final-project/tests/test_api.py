import io
import zipfile

from fastapi.testclient import TestClient

from oblak.api.main import app
from oblak.db.session import SessionLocal
from oblak.models.entities import User
from oblak.security.auth import hash_api_key


def make_zip(source: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("handler.py", source)
    return buffer.getvalue()


def ensure_user():
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "test").one_or_none()
        if not user:
            db.add(User(username="test", api_key_hash=hash_api_key("test-key")))
            db.commit()


def test_upload_and_invoke():
    ensure_user()
    client = TestClient(app)
    archive = make_zip("def handler(event, context):\n    return {'hello': event.get('name')}\n")
    upload = client.post(
        "/functions",
        headers={"X-API-Key": "test-key"},
        data={"name": "test-fn"},
        files={"file": ("fn.zip", archive, "application/zip")},
    )
    assert upload.status_code == 200, upload.text
    body = upload.json()
    assert body["status"] == "prepared"

    invoke = client.post(body["invoke_url"], json={"payload": {"name": "Ada"}})
    assert invoke.status_code == 200, invoke.text
    assert invoke.json()["result"] == {"hello": "Ada"}
