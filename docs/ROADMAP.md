# Roadmap

This is the honest "foundation → production" plan. The repo today is a
runnable, end-to-end skeleton with real infrastructure and real provider
adapters. The work below is what turns it into a content business.

## What's real today

- ✅ End-to-end pipeline from topic to playable `.mp4` (works with zero API keys via mocks)
- ✅ FastAPI + Celery + Redis + Postgres + Supabase/S3/MinIO storage + Telegram
- ✅ AI agents: script, scene, visual, voice, SEO, orchestrator (Claude-ready)
- ✅ T2V providers: mock (FFmpeg), Replicate (hosted), GPU diffusers (RunPod/Vast)
- ✅ Captions burned into video + sidecar SRT
- ✅ Queue topology that routes GPU work to the GPU worker
- ✅ Docker for every service incl. CUDA worker; nginx + TLS; Render Blueprint;
     Railway + RunPod + Vast templates; backups + systemd

## What's a placeholder you'll outgrow

- ⚠️ **Mock T2V** is animated gradients — perfect for tests, useless for a YouTube
  channel. Flip to `replicate` or `gpu` for real video.
- ⚠️ **Mock TTS** is silent. Set `TTS_PROVIDER=elevenlabs` or `openai`.
- ⚠️ **Scene timing** comes from the LLM's plan; real TTS audio length will drift.
  See "forced alignment" below.

## Next: production-quality content (Phase 2)

1. **Forced alignment between audio and captions.** Use `whisper-timestamped`
   or `WhisperX` to get word-level timestamps from the actual narration audio,
   then rebuild the ASS so captions are word-synced (TikTok-style). Adjust
   scene clip durations to match real audio segments.
2. **Music bed + ducking.** Add a music asset library, mix at -18 LUFS under
   narration with `sidechaincompress` in FFmpeg.
3. **B-roll search.** Add a Pexels/Pixabay agent that fetches matching footage
   when the topic is concrete enough (history, news), used as a `T2VProvider`
   variant. Routes by scene rather than globally.
4. **Thumbnail composer.** Generate 3 thumbnail variants (frame extract + text
   overlay + face-zoom) and store all three; YouTube A/B picks the winner.
5. **Hook A/B testing.** Generate 2–3 hook variants per script. Render only the
   first 3s of each, attach to the same body, store as separate `Video` rows.

## Next: scale & ops (Phase 3)

1. **Frontend.** Next.js dashboard scaffolded in `frontend/` — render history,
   live job progress (SSE off `/api/v1/jobs/{id}/events`), credit balance, retries.
2. **Auth.** JWT or Supabase Auth in front of `X-API-Key`; per-user quotas in
   `subscriptions`. Stripe/LemonSqueezy webhook handler is already a stub.
3. **Multi-channel publishing.** Add YouTube Data API + TikTok upload (when
   API access opens). One `Channel` row → one connected account.
4. **Cost telemetry.** Per-job cost rollup (LLM tokens, TTS seconds, GPU
   minutes, storage) → emit on `events`, surface in dashboard.

## Next: AI quality (Phase 4)

1. **Style learning per channel.** Fine-tune a system prompt from a channel's
   top-performing videos (titles, hooks, scripts) stored in Postgres.
2. **Retention loop.** Pull YouTube analytics for shipped videos, feed audience
   retention curves back as reinforcement on the SEO/script agents.
3. **Multi-LLM ensemble.** Run script generation 3x with different temperatures
   and let a critic agent pick the best one before rendering.
4. **Voice cloning.** Per-channel voice via ElevenLabs voice IDs (already
   surfaced as `channels.voice`) — UI to upload reference audio.

## Risks / things to plan for

- **YouTube TOS.** Automated content at scale needs human review on the
  publishing path or you risk channel termination. Surface a "review" step in
  the dashboard before any YouTube upload.
- **Generative video cost.** Hosted T2V on Replicate is the cheapest *easy*
  option. Self-hosted GPU is cheaper at high volume but operationally heavier.
  Build a per-job cost cap.
- **Model availability.** LTX-Video and similar models change rapidly; pin the
  diffusers + model version and treat the upgrade as a discrete project.
