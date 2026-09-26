import hashlib, json, os, time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def mint(hwid, exp, secret, tag):
    sig = hashlib.sha256(f"{hwid}::{exp}::{secret}".encode()).hexdigest().upper()[:16]
    g = [sig[i:i + 4] for i in range(0, 16, 4)]
    return f"KEY-{tag}-{exp}-{'-'.join(g)}"


class handler(BaseHTTPRequestHandler):
    def _send(self, o):
        b = json.dumps(o).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        q = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        pw, secret = os.environ.get("ADMIN_PW", ""), os.environ.get("META_SECRET", "")
        if not secret or not pw:
            self._send({"error": "Server not configured: set META_SECRET + ADMIN_PW env vars in Vercel."})
            return
        if q.get("pw", "") != pw:
            self._send({"error": "Wrong pw."})
            return
        hwid = q.get("hwid", "").strip().upper()
        if not hwid.startswith("HWID-") or len(hwid) != 24:
            self._send({"error": "Bad hwid. Get it from the app's activation window."})
            return
        if q.get("life", "") == "1":
            key = mint(hwid, 9999999999, secret, "LIFE")
            self._send({"key": key, "hwid": hwid, "expires": "lifetime"})
        else:
            try:
                days = max(1, int(q.get("days", "30")))
            except ValueError:
                self._send({"error": "days must be a number."})
                return
            exp = int(time.time()) + days * 86400
            self._send({"key": mint(hwid, exp, secret, "STD"), "hwid": hwid,
                        "expires_in_days": days, "exp": exp})
