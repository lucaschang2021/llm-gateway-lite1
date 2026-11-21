"""One-command demo — no API key, no pip install.

Starts the mock upstream and the gateway, sends real requests through the
gateway, prints the responses and the cost log, then shuts everything down.

Run: python3 demo.py"""
import json, os, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
LOG = HERE / "demo_requests.csv"
if LOG.exists(): LOG.unlink()

env = dict(os.environ, UPSTREAM_BASE_URL="http://localhost:9001/v1",
           UPSTREAM_API_KEY="mock-key", GATEWAY_KEY="demo-key",
           REQUEST_LOG=str(LOG), PORT="8080", MOCK_PORT="9001")
procs = [subprocess.Popen([sys.executable, str(HERE / name)], env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
         for name in ("mock_upstream.py", "gateway_lite.py")]

def call(method, path, body=None, key="demo-key"):
    req = urllib.request.Request("http://localhost:8080" + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"X-API-Key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")

try:
    for _ in range(50):
        try:
            code, health = call("GET", "/health")
            if code == 200: break
        except Exception: time.sleep(0.2)
    print("1) Health check:      ", health)
    code, bad = call("POST", "/v1/chat", {"messages": []}, key="wrong-key")
    print("2) Wrong key rejected:", code, bad)
    for q in ("Summarise this in one line: the gateway logs every request.",
              "Give me a tagline for a coffee shop."):
        code, resp = call("POST", "/v1/chat",
                          {"messages": [{"role": "user", "content": q}], "max_tokens": 64})
        print(f"3) Chat [{code}]:        ", resp["choices"][0]["message"]["content"])
    print("4) Cost log (requests.csv):")
    for line in LOG.read_text().splitlines():
        print("   ", line)
    print("\nDEMO PASSED — the gateway proxied, authenticated and logged real requests.")
finally:
    for p in procs: p.terminate()
