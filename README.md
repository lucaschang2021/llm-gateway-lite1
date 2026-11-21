# LLM Gateway Lite (free edition)

**One controlled doorway in front of your LLM API — in a single Python file,
with zero dependencies.**

Stop pasting your provider key into every app and script. Run this gateway,
give your apps the *gateway* key, and get a cost log of every request.

**Demo output** (`python3 demo.py`, no API key needed):
```
1) Health check:       {'ok': True, 'upstream': 'http://localhost:9001/v1'}
2) Wrong key rejected: 401 {'error': 'invalid gateway key'}
3) Chat [200]:         Mock reply: I received 59 characters and answered politely.
3) Chat [200]:         Mock reply: I received 36 characters and answered politely.
4) Cost log (requests.csv):
    ts,model,input_tokens,output_tokens,cost_usd,status
    1795231063,gpt-4o-mini,15,15,1.1e-05,200
    1795231063,gpt-4o-mini,9,15,1e-05,200

DEMO PASSED — the gateway proxied, authenticated and logged real requests.
```

## Free tool: what will your workload cost?
Open [`tools/cost-calculator.html`](tools/cost-calculator.html) in a browser —
a single-file interactive calculator comparing 9 models on your real
request volume. (This calculator shows what you *should* spend; the gateway
below logs what you *actually* spend.)

## Try it in 60 seconds (no API key needed)
```bash
python3 demo.py
```
This starts a mock upstream and the gateway, sends real requests through it,
shows a wrong key being rejected, and prints the cost log. Everything runs
locally with nothing but Python 3.10+ — no `pip install`, ever.

## Run it for real
```bash
UPSTREAM_API_KEY=sk-your-provider-key GATEWAY_KEY=pick-a-secret python3 gateway_lite.py
curl localhost:8080/v1/chat -H "X-API-Key: pick-a-secret" -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```
Works with any OpenAI-compatible upstream (`UPSTREAM_BASE_URL`).

## What Lite does / doesn't do
| | Lite (free) | Full Starter Kit |
|---|---|---|
| Single-file, zero-dependency gateway | ✅ | (FastAPI version) |
| Gateway key check, provider key stays server-side | ✅ | ✅ |
| Per-request cost log (CSV) | ✅ | ✅ |
| **Per-client keys, each with its own daily budget cap** | — | ✅ |
| **Rate limiting per client** | — | ✅ |
| **Retries with backoff** | — | ✅ |
| **Cost report script (spend by key / model / day)** | — | ✅ |
| **Docker + deployment guide + production checklist** | — | ✅ |
| Unit tests for the money math | — | ✅ |

Lite is a learning tool and a taste. The moment more than one app or person
shares the gateway, you want per-client keys and budget caps — that's the
[full Starter Kit](https://gumroad.com) ($39), built from this same design.

## Why not just use LiteLLM?
LiteLLM is excellent — and a large platform (proxy server, database, admin
UI, 100+ providers). If you need that, use it, it's free. This kit is for
the opposite preference: **a gateway you can read end-to-end in an evening**
and modify without learning a framework. Small enough to understand is a
feature.

## License
MIT for this Lite edition — use it anywhere. The full Starter Kit has its
own license (use in unlimited own projects, no resale of the kit).
