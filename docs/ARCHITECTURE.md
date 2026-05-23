# Architecture

```
                            ┌──────────────────────┐
   ┌──────┐    HTTP/JSON    │  FastAPI (backend)   │
   │client│ ───────────────►│  • /api/v1/jobs      │──┐
   └──────┘                 │  • /api/v1/videos    │  │ enqueue
                            │  • /api/v1/webhooks  │  ▼
   ┌──────┐    long poll    │                      │  ┌──────────┐
   │TG bot│ ────────────────┤                      │  │  Redis   │ ◄── beat
   └──────┘   shares core   └──────────────────────┘  │ (broker) │
                                  ▲                   └──────────┘
                                  │ status/results            │
                                  │                           ▼
                                  │            ┌─────────────────────────┐
                                  │            │  Celery worker (render) │
                                  │            │  orchestrator → plan    │
                                  │            │  voice → T2V → assemble │
                                  │            │  upload → notify        │
                                  │            └────────────┬────────────┘
                                  │                         │
                ┌─────────────────┴────────┐                ▼
                │       Postgres           │       ┌────────────────────┐
                │ users / channels / jobs  │       │  Storage           │
                │ videos / assets / events │       │  Supabase / S3 /   │
                │ subscriptions            │       │  MinIO / local     │
                └──────────────────────────┘       └────────────────────┘

  ┌──── GPU overlay (RunPod / Vast / local CUDA) ─────────────────────────┐
  │   Celery worker (gpu queue)  → diffusers T2V (LTX-Video)              │
  │   Same Redis broker, same Postgres, same Storage. No infra changes.   │
  └───────────────────────────────────────────────────────────────────────┘
```

## Layers & boundaries

The `factory/` package is the **single source of truth**. The three deployable
services (`backend`, `worker`, `telegram_bot`) are thin entrypoints that wire
HTTP / queue / Telegram I/O to the core. This is why DB migrations, agents,
storage, and the queue helper all live in `factory/` — they're shared.

| Concern    | Where                                       | Interface |
| ---------- | ------------------------------------------- | --------- |
| Settings   | `factory.core.config.settings`              | typed pydantic-settings; nothing else reads env |
| Logging    | `factory.core.logging`                      | structlog; JSON in prod, dev-formatter locally |
| DB         | `factory.db.models` + `factory.db.session`  | SQLAlchemy 2.0, sync sessions everywhere |
| Schemas    | `factory.schemas`                           | pydantic v2 request/response models |
| Agents     | `factory.agents.*`                          | `Orchestrator.build_plan(topic) -> ContentPlan` |
| Render     | `factory.render`                            | `RenderPipeline().render(plan, audio, dir)` |
| T2V        | `factory.render.providers`                  | `T2VProvider.generate_clip(scene, path, ...)` |
| Storage    | `factory.storage`                           | `Storage.put_file / url_for / exists / delete` |
| Queue      | `factory.services.queue`                    | `enqueue_pipeline(job_id) -> task_id` |
| Jobs      | `factory.services.jobs`                     | the single mutator of job state |
| Notify     | `factory.services.notify`                   | signed webhooks + Telegram delivery |

## Provider selection

Three providers swap by env var, with no code changes upstream:

- `LLM_PROVIDER` — `anthropic` (Claude) | `openai` | `mock`. Mock paths in the
  agents produce deterministic, valid output so the pipeline always completes.
- `TTS_PROVIDER` — `elevenlabs` | `openai` | `mock`. Mock emits a silent WAV of
  the planned duration so timing/sync still works without an API key.
- `T2V_PROVIDER` — `mock` (FFmpeg gradients) | `replicate` (hosted GPU API) |
  `gpu` (local CUDA via diffusers, routed to the dedicated `gpu` worker).

## Queue topology

- `default` — maintenance / housekeeping
- `render`  — the orchestration task (lightweight CPU work + T2V when not GPU)
- `gpu`     — selected only when `T2V_PROVIDER=gpu`; consumed by the GPU worker

Routing happens in `factory.services.queue.pipeline_queue()` so the *same*
pipeline code runs on CPU or GPU — only the worker that receives it changes.

## Data flow for one job

1. `POST /api/v1/jobs` validates input, writes a `jobs` row (`status=queued`),
   enqueues `factory.pipeline.run(job_id)` on the right queue, returns the job.
2. The worker pulls the task, transitions the job through `scripting`,
   `voicing`, `rendering`, `uploading`, emitting `events` and updating
   `progress` so the client can poll or the bot can stream status.
3. The render produces: `final.mp4`, `thumbnail.jpg`, `captions.srt`, and
   `voice.{wav,mp3}`. Each is uploaded and stored as an `Asset`, plus a
   `Video` row aggregates the public URLs.
4. On success the worker fires Telegram delivery (if `chat_id` in params)
   and/or a signed webhook (if `webhook_url` in params), then marks the job
   `completed`. Failures are classified as retryable vs deterministic;
   deterministic failures don't burn GPU time on auto-retry.
