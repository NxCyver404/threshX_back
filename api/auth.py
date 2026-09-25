import json, re, urllib.request
from datetime import date
from http.server import BaseHTTPRequestHandler
RAW = "https://raw.githubusercontent.com/NxCyver404/threshX_back/refs/heads/main"
D = "licenses/kazi"


def gh(p):
    try:
        r = urllib.request.Request(RAW + "/" + p, headers={"User-Agent": "kz"})
        with urllib.request.urlopen(r, timeout=10) as x:
            return json.loads(x.read().decode())
    except Exception:
        return None


def decide(did):
    if gh(D + "/_maintenance.json") is not None:
        return {"status": "maintenance", "message": "Under maintenance."}
    lic = gh(D + "/" + did + ".json")
    if not lic:
        return {"status": "not_registered", "message": "Device not registered!"}
    try:
        exp = date(*map(int, str(lic.get("expire_date", "")).split("-")))
    except Exception:
        return {"status": "expired", "message": "Bad expiry on file."}
    iso = exp.isoformat() + "T23:59:59+00:00"
    nm = lic.get("user", "Unknown")
    if exp < date.today():
        return {"status": "expired", "user_name": nm, "user": nm,
                "expires_at": iso, "expiry": iso}
    return {"status": "active", "user_name": nm, "user": nm,
            "days_left": (exp - date.today()).days,
            "expires_at": iso, "expiry": iso}


class handler(BaseHTTPRequestHandler):
    def _send(self, o):
        b = json.dumps(o).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            did = str(json.loads(self.rfile.read(n) or b"{}").get("device_id", ""))
        except Exception:
            did = ""
        did = re.sub(r"[^A-Za-z0-9_.\-]", "", did)[:64] or "invalid"
        self._send(decide(did))

    def do_GET(self):
        self._send({"status": "ok", "shim": "kazi-license"})
