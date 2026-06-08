import zipfile
from pathlib import Path


def package_directory(source: Path, archive_path: Path) -> Path:
    if not (source / "handler.py").exists():
        raise ValueError("Function directory must contain handler.py")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in source.rglob("*"):
            if path.is_file() and not _ignored(path):
                archive.write(path, path.relative_to(source))
    return archive_path


def _ignored(path: Path) -> bool:
    return any(part in {"__pycache__", ".venv", ".git"} for part in path.parts) or path.suffix == ".pyc"
