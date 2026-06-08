import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".oblak" / "config.json"


def save_config(server_url: str, api_key: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({"server_url": server_url.rstrip("/"), "api_key": api_key}, indent=2), encoding="utf-8")


def load_config() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        raise RuntimeError("Run: oblak-cdk configure --server-url URL --api-key KEY")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
