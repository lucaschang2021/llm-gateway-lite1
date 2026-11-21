"""A fake OpenAI-compatible upstream for demos and tests. Stdlib only.
Run: python3 mock_upstream.py   (port 9001, or $MOCK_PORT)"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        prompt = " ".join(m.get("content", "") for m in body.get("messages", []))
        reply = f"Mock reply: I received {len(prompt)} characters and answered politely."
        out = {"id": "chatcmpl-mock", "object": "chat.completion",
               "model": body.get("model", "mock-model"),
               "choices": [{"index": 0, "message": {"role": "assistant", "content": reply},
                            "finish_reason": "stop"}],
               "usage": {"prompt_tokens": max(1, round(len(prompt) / 4)),
                         "completion_tokens": max(1, round(len(reply) / 4)),
                         "total_tokens": 42}}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

if __name__ == "__main__":
    port = int(os.environ.get("MOCK_PORT", "9001"))
    print(f"Mock upstream on http://localhost:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
