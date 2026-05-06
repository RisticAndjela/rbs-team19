from pathlib import Path
import subprocess
import sys

DEFAULT_ARGS = [
    "http://localhost:8000", # port for site 
    "user1", # username
    "Hacked123!" # password for user1
]


def main() -> int:
    base_dir = Path(__file__).resolve().parent 
    
    # Parse arguments
    args = sys.argv[1:]
    attack_type = "login-bypass"  # default
    if args and args[0] in ["login-bypass", "priv-esc"]:
        attack_type = args.pop(0)
    
    if attack_type == "login-bypass":
        script_path = base_dir / "login-bypass" / "blind_sqli_reset.py"
    elif attack_type == "priv-esc":
        script_path = base_dir / "privilege-escalation" / "xss.py"
    else:
        print("Invalid attack type. Use 'login-bypass' or 'priv-esc'", file=sys.stderr)
        return 1

    if not script_path.exists(): # error handling ako skript nije pronadjena
        print(f"Missing script: {script_path}", file=sys.stderr)
        return 1

    # fallback ako nema argumenata - koristi sve default
    if not args:
        args = DEFAULT_ARGS
    elif len(args) == 2:
        args = [DEFAULT_ARGS[0]] + args
    # ako su data 3 argumenta, koristi kako su data

    command = [sys.executable, str(script_path), *args]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())