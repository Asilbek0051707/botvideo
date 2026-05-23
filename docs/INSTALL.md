# Local install

## Prerequisites
- Docker Desktop 24+ (Compose v2 included)
- 8 GB RAM minimum; 16 GB recommended if you'll also run a local GPU worker
- ports free: 8000 (API), 5432 (Postgres), 6379 (Redis), 9000/9001 (MinIO), 5555 (Flower)

## 1. Configure
```bash
cp .env.example .env
# PowerShell: Copy-Item .env.example .env
```
Defaults boot a working stack with **all providers in mock mode** — no API keys
required. The first job will produce a real `.mp4` with synthetic visuals,
silent voice track, and burned captions.

To use real services, fill in the keys you have and flip the corresponding
`*_PROVIDER` switches in `.env`. Mix and match freely.

## 2. Start the stack
```bash
docker compose up --build -d
docker compose ps
```
You should see `postgres`, `redis`, `minio`, `minio-init` (exits after creating
the bucket), `backend`, `worker`, `beat`, `flower`, and `telegram` (idle if no
token).

## 3. Smoke test the end-to-end pipeline
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: devkey-change-me" \
  -d '{"topic":"3 mind-blowing facts about the deep ocean","style":"documentary"}'
```
Watch progress:
```bash
docker compose logs -f worker
```
And poll:
```bash
curl http://localhost:8000/api/v1/jobs/<id> -H "X-API-Key: devkey-change-me"
```
On `status: completed` the response contains a playable `video.url`.

## 4. Useful URLs
- API docs: http://localhost:8000/docs
- Flower (queue + workers): http://localhost:5555 (admin/admin)
- MinIO console: http://localhost:9001 (minioadmin/minioadmin)

## 5. Telegram (optional)
1. Create a bot with @BotFather, copy the token into `.env` as `TELEGRAM_BOT_TOKEN`.
2. Send `/start` to your bot in Telegram, copy your numeric Telegram user ID
   from any message you send → set `TELEGRAM_ADMIN_IDS=<your_id>` for admin perms.
3. `docker compose restart telegram` and message a topic to your bot.

## Troubleshooting

**`backend` keeps restarting**
Likely DB connectivity. Run `docker compose logs backend | tail -50`. Most often
the URL is wrong — verify `DATABASE_URL` matches the `postgres` service.

**Render task fails with "subtitles filter not found"**
The worker image needs FFmpeg with libass. The provided `worker/Dockerfile`
installs `ffmpeg` from Debian which includes it. If you're running a custom
base, install `ffmpeg` (full, not the `ffmpeg-essentials` variant).

**Telegram service idles**
Expected when `TELEGRAM_BOT_TOKEN` is unset — the container stays up so it
doesn't crash-loop. Set the token and `docker compose restart telegram`.

**GPU model errors with "out of memory"**
Lower `VIDEO_WIDTH`/`VIDEO_HEIGHT` (must be multiples of 32; the code rounds
down), or pick a smaller T2V model and update `GPU_T2V_MODEL`.
