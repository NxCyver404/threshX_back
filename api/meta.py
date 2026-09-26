import json, urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
RAW = "https://raw.githubusercontent.com/NxCyver404/threshX_back/refs/heads/main"
D = "licenses/meta"


def gh(p):
    try:
        r = urllib.request.Request(RAW + "/" + p, headers={"User-Agent": "mz"})
        with urllib.request.urlopen(r, timeout=10) as x:
            return json.loads(x.read().decode())
    except Exception:
        return None


def blocked_list():
    b = gh(D + "/blocked.json")
    return [str(h).strip().upper() for h in b] if isinstance(b, list) else []


class handler(BaseHTTPRequestHandler):
    def _send(self, o):
        b = json.dumps(o).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _params(self):
        q = parse_qs(urlparse(self.path).query)
        p = {k: v[0] for k, v in q.items()}
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 0:
                body = json.loads(self.rfile.read(n) or b"{}")
                if isinstance(body, dict):
                    p.update({k: str(v) for k, v in body.items()})
        except Exception:
            pass
        return p

    def _answer(self):
        p = self._params()
        hwid = str(p.get("hwid", "")).strip().upper()
        if hwid and hwid in blocked_list():
            return {"blocked": True, "message": "Device blocked by admin."}
        return {"blocked": False, "ok": True}

    def do_GET(self):
        if urlparse(self.path).path.rstrip("/").endswith("/meta/check"):
            self._send(self._answer())
        else:
            self._send({"status": "ok", "shim": "meta-license"})

    def do_POST(self):
        self._send(self._answer())
