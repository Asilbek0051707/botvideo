# frontend/ (optional dashboard — placeholder)

The backend exposes a complete REST API at `/api/v1/*`; a Next.js dashboard is
explicitly Phase 3 (see [ROADMAP](../docs/ROADMAP.md)). Scaffold it here when you're ready:

```bash
npx create-next-app@latest . --typescript --app --tailwind
```

Recommended starting screens:
- **/jobs** — live queue (poll `/api/v1/jobs?status=...` or subscribe to a
  future `/api/v1/jobs/{id}/events` SSE endpoint)
- **/videos** — render history with the preview player (`videos[].url` is
  directly playable)
- **/analytics** — per-channel job counts + completion rate from `/api/v1/jobs`
- **/billing** — Stripe/LemonSqueezy subscription tied to `subscriptions` table

API client: simple `fetch` with `X-API-Key` header until you swap to JWT.
