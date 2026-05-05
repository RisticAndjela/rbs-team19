from pathlib import Path
import subprocess
import sys

DEFAULT_ARGS = [
    "http://localhost:8000", # port for site 
    "user1", # who is trying to login used for login bypass
    "Hacked123!" # password for user1, used for login bypass
]


def main() -> int:
    base_dir = Path(__file__).resolve().parent 
    login_bypass = base_dir / "login-bypass" / "blind_sqli_reset.py" 

    if not login_bypass.exists(): # error handling ako skript nije pronadjena
        print(f"Missing script: {login_bypass}", file=sys.stderr)
        return 1

    args = sys.argv[1:] # argumeti

    # fallback ako nema argumenata
    if not args:
        args = DEFAULT_ARGS

    command = [sys.executable, str(login_bypass), *args]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())