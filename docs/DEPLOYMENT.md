# Deployment

Pick the topology that matches your scale. All paths converge on the same
runtime (one Docker image per service, shared Redis + Postgres + Storage).

| Stage           | API + workers          | GPU rendering        | DB + Storage         |
| --------------- | ---------------------- | -------------------- | -------------------- |
| Single-host MVP | VPS (Docker Compose)   | same box (if GPU)    | local Postgres+MinIO |
| Hosted PaaS     | Railway *or* Render    | RunPod / Vast        | Supabase             |
| Scale           | Render workers ×N      | RunPod multi-Pod     | Supabase + Cloudflare R2 |

The CPU stack (API, queue, telegram, beat) and the GPU stack (text-to-video)
are **decoupled by the broker**. You can move either independently.

---

## A — Single-host VPS with Nginx + Let's Encrypt

Best for getting to production fast on Hetzner / DigitalOcean / Linode.

1. `git clone` + `cp .env.example .env`; fill in real keys + `STORAGE_BACKEND=supabase`.
2. Point your DNS A record at the box.
3. Edit `deploy/nginx/conf.d/factory.conf` — replace `your-domain.example` (3x).
4. Start without TLS first so certbot can verify the domain:
   ```bash
   docker compose --profile prod up -d
   ```
5. Issue the cert:
   ```bash
   DOMAIN=your-domain.com EMAIL=you@your-domain.com \
     bash deploy/certbot/init-letsencrypt.sh
   ```
6. Schedule renewal + nightly backup:
   ```cron
   0 3 * * *  cd /opt/factory && bash deploy/certbot/renew.sh
   30 3 * * * cd /opt/factory && bash deploy/scripts/backup.sh >> /var/log/factory-backup.log 2>&1
   ```
7. (Optional) install the systemd unit so the stack survives reboots:
   ```bash
   sudo cp deploy/systemd/ai-youtube-factory.service /etc/systemd/system/
   sudo systemctl enable --now ai-youtube-factory
   ```

## B — Render.com (one-click blueprint)

`render.yaml` at the repo root provisions web + worker + beat + telegram +
Redis + Postgres. Push to GitHub → New Blueprint → select repo. Fill the
`sync: false` secrets in the UI (LLM, TTS, Storage, Telegram).

GPU rendering runs on RunPod / Vast (see below); the Render workers consume
the `render` queue, not `gpu`.

## C — Railway

See [`deploy/railway/README.md`](../deploy/railway/README.md). Provision Postgres
and Redis as Railway services, then add one container service per Dockerfile
(API, Worker, Beat, Telegram). The JSON snippets in `deploy/railway/` show the
env wiring (`${{ Postgres.DATABASE_URL }}`, etc.).

## D — GPU rendering on RunPod / Vast.ai

See [`deploy/runpod/README.md`](../deploy/runpod/README.md) and
[`deploy/vast/README.md`](../deploy/vast/README.md).

Workflow:
1. Build & push `worker/Dockerfile.gpu` to your registry.
2. Spin up a Pod / Vast instance with that image, GPU attached, and a persistent
   volume mounted at `/root/.cache/huggingface` for the model weights.
3. Set env vars so the worker connects to your already-deployed broker /
   Postgres / Storage (URLs from Render or Supabase project settings).
4. Set `T2V_PROVIDER=gpu` on the API side. New jobs route to the `gpu` queue.

## Env var checklist (production)

Required for any non-mock provider you enable:

- `ENV=production`, `SECRET_KEY`, `WEBHOOK_SIGNING_SECRET`, `API_KEYS` (strong, comma-separated)
- `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- `STORAGE_BACKEND=supabase` + `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` + `SUPABASE_STORAGE_BUCKET`
  *(or `s3` with full S3 creds)*
- `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` *(or openai + key)*
- `TTS_PROVIDER=elevenlabs` + `ELEVENLABS_API_KEY`
- `T2V_PROVIDER=replicate` + `REPLICATE_API_TOKEN` *(or `=gpu` if running RunPod/Vast)*
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_ADMIN_IDS` if the bot is in use
- `PUBLIC_BASE_URL` so webhooks resolve correctly

## Backups

- DB: nightly `pg_dump` via `deploy/scripts/backup.sh` (retains 14 days locally,
  optionally pushes to S3 when `BACKUP_S3_BUCKET` is set).
- Storage: Supabase has built-in daily snapshots; for S3/MinIO replicate the
  bucket to a second region using lifecycle rules or `mc mirror`.
- Restore tested with `deploy/scripts/restore.sh <dump>` — don't trust a backup
  you haven't restored.

## Scaling

- **Queue depth** (Flower) is the leading signal. Add CPU render replicas when
  `render` queue lags; add GPU pods when `gpu` lags.
- **Postgres connections**: each worker concurrency × replicas needs a
  connection from a pool of size 10 (configured in `factory/db/session.py`).
  Use Supabase pooler (PgBouncer) when going past ~5 worker replicas.
- **Storage egress**: serving final videos directly from Supabase/S3 is fine;
  for high-traffic public videos put Cloudflare in front.
