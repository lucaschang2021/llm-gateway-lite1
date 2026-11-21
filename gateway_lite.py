"""LLM Gateway Lite — one file, zero dependencies (Python standard library only).

What it does:
  * One doorway in front of any OpenAI-compatible API
  * A gateway key check, so your provider key is never shared or embedded in apps
  * A CSV cost log: every request, estimated tokens and cost

Run it:
  UPSTREAM_API_KEY=sk-... python3 gateway_lite.py          # port 8080
Try the demo (no API key needed, uses the bundled mock upstream):
  python3 demo.py

This is the free Lite edition. The full Starter Kit adds per-client keys with
individual daily budget caps, rate limiting, retries, a cost-report script,
Docker deployment and a production checklist — see README.md.
"""
import csv, json, os, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

UPSTREAM = os.environ.get("UPSTREAM_BASE_URL", "https://api.openai.com/v1")
UPSTREAM_KEY = os.environ.get("UPSTREAM_API_KEY", "")
GATEWAY_KEY = os.environ.get("GATEWAY_KEY", "demo-key")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")
LOG_PATH = Path(os.environ.get("REQUEST_LOG", "requests.csv"))
PORT = int(os.environ.get("PORT", "8080"))

PRICES = {  # USD per 1M tokens (input, output) — edit freely
    "gpt-4o": (2.50, 10.00), "gpt-4o-mini": (0.15, 0.60),
    "claude-sonnet": (3.00, 15.00), "default": (1.00, 4.00),
}

def estimate_tokens(text): return 0 if not text else max(1, round(len(text) / 4))

def estimate_cost(model, in_t, out_t):
    ip, op = PRICES.get(model, PRICES["default"])
    return (in_t * ip + out_t * op) / 1_000_000

def log_row(row):
    exists = LOG_PATH.exists()
    with LOG_PATH.open("a", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists: wr.writeheader()
        wr.writerow(row)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"ok": True, "upstream": UPSTREAM})
        return self._json(404, {"error": "not_found"})
    def do_POST(self):
        if self.path != "/v1/chat":
            return self._json(404, {"error": "not_found"})
        if self.headers.get("X-API-Key") != GATEWAY_KEY:
            return self._json(401, {"error": "invalid gateway key"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"error": "invalid json"})
        messages = body.get("messages", [])
        model = body.get("model", DEFAULT_MODEL)
        prompt = " ".join(m.get("content", "") for m in messages)
        payload = {"model": model, "messages": messages}
        if "max_tokens" in body: payload["max_tokens"] = body["max_tokens"]
        req = urllib.request.Request(
            f"{UPSTREAM}/chat/completions",
            data=json.dumps(payload).encode(), method="POST",
            headers={"Authorization": f"Bearer {UPSTREAM_KEY}",
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read()); status = r.status
        except urllib.error.HTTPError as e:
            data = json.loads(e.read() or b"{}"); status = e.code
        except Exception as e:
            return self._json(502, {"error": f"upstream_failed: {e}"})
        usage = data.get("usage", {})
        out_text = ""
        try: out_text = data["choices"][0]["message"]["content"]
        except Exception: pass
        in_t = int(usage.get("prompt_tokens", estimate_tokens(prompt)))
        out_t = int(usage.get("completion_tokens", estimate_tokens(out_text)))
        cost = estimate_cost(model, in_t, out_t)
        log_row({"ts": int(time.time()), "model": model, "input_tokens": in_t,
                 "output_tokens": out_t, "cost_usd": round(cost, 6), "status": status})
        return self._json(status, data)

if __name__ == "__main__":
    print(f"LLM Gateway Lite on http://localhost:{PORT}  (upstream: {UPSTREAM})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
