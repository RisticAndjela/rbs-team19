import json
import tempfile
from pathlib import Path

import requests
import typer
from rich import print

from oblak.cli.config import load_config, save_config
from oblak.cli.packager import package_directory

app = typer.Typer(help="Oblak CDK CLI")


@app.command()
def configure(server_url: str, api_key: str) -> None:
    save_config(server_url, api_key)
    print("[green]Configuration saved.[/green]")


@app.command()
def deploy(path: Path, name: str) -> None:
    config = load_config()
    with tempfile.TemporaryDirectory() as tmp:
        archive = package_directory(path, Path(tmp) / f"{name}.zip")
        with archive.open("rb") as file_obj:
            response = requests.post(
                f"{config['server_url']}/functions",
                headers={"X-API-Key": config["api_key"]},
                data={"name": name},
                files={"file": (archive.name, file_obj, "application/zip")},
                timeout=30,
            )
    _print_response(response)


@app.command()
def invoke(name: str, payload: str = "{}") -> None:
    config = load_config()
    list_response = requests.get(
        f"{config['server_url']}/functions",
        headers={"X-API-Key": config["api_key"]},
        timeout=30,
    )
    list_response.raise_for_status()
    functions = list_response.json()
    match = next((item for item in functions if item["name"] == name), None)
    if match is None:
        raise typer.BadParameter(f"Function not found: {name}")
    response = requests.post(match["invoke_url"], json={"payload": json.loads(payload)}, timeout=30)
    _print_response(response)


@app.command()
def audit() -> None:
    config = load_config()
    response = requests.get(
        f"{config['server_url']}/audit",
        headers={"X-API-Key": config["api_key"]},
        timeout=30,
    )
    _print_response(response)


def _print_response(response: requests.Response) -> None:
    try:
        body = response.json()
    except ValueError:
        body = response.text
    if response.ok:
        print_json(body)
        return
    print(f"[red]HTTP {response.status_code}[/red]")
    print_json(body)
    response.raise_for_status()


def print_json(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
