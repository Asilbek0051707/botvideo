# Monitoring & observability

Built-in:

- **Flower** at `:5555` (or `/flower/` behind nginx) — queue depth, active tasks,
  per-worker stats, task history. Basic-auth via `FLOWER_BASIC_AUTH`.
- **Structured logs** — every service uses `structlog`; in production it emits
  JSON to stdout. Ship to Loki / Datadog / Logtail by tailing the Docker logs.
- **Healthchecks** — Docker healthchecks on `postgres`, `redis`, `minio`, and
  `backend` (`/api/health`). `backend` also exposes `/api/ready` which probes
  the DB + broker.
- **Sentry** — set `SENTRY_DSN` and add `sentry_sdk.init(...)` in
  `factory/core/logging.py` (1-line drop-in; left out by default to keep deps
  small until you're ready).

A one-shot host healthcheck for cron / Uptime Kuma:

```bash
curl -fsS http://localhost:8000/api/ready | jq -e '.status == "ok"'
```

What to alert on:

| signal                          | likely cause                       |
| ------------------------------- | ---------------------------------- |
| `/api/ready` non-200            | DB or Redis is down                |
| Flower: gpu queue depth > N for | GPU worker offline / model OOM     |
| Job status `failed` rate spike  | upstream provider (LLM/TTS/T2V)    |
| Storage 4xx/5xx in worker logs  | Supabase/S3 creds or quota         |
