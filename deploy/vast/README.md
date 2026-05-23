# Vast.ai — GPU text-to-video worker

Same model as RunPod: rent a GPU box, run the worker container, point it at
your already-deployed Redis broker and Postgres. The Vast UI's "On-start
script" field is the easiest way to do this without SSH'ing.

## On-start script

Paste this into the instance template (replace placeholders + image tag first):

```bash
#!/usr/bin/env bash
set -euo pipefail

docker login ghcr.io -u <you> -p $GHCR_TOKEN

docker run -d --name factory-gpu --restart unless-stopped --gpus all \
  -v hf:/root/.cache/huggingface \
  -e ENV=production \
  -e T2V_PROVIDER=gpu \
  -e GPU_T2V_MODEL=Lightricks/LTX-Video \
  -e HF_TOKEN="$HF_TOKEN" \
  -e REDIS_URL="$REDIS_URL" \
  -e CELERY_BROKER_URL="$CELERY_BROKER_URL" \
  -e CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
  -e DATABASE_URL="$DATABASE_URL" \
  -e STORAGE_BACKEND=supabase \
  -e SUPABASE_URL="$SUPABASE_URL" \
  -e SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY" \
  ghcr.io/<you>/factory-worker-gpu:latest

docker logs -f factory-gpu
```

The variables `$REDIS_URL`, `$DATABASE_URL`, etc. should be set via Vast's
"Environment" field on the instance.

## Notes
- Use **interruptible** instances only if you've enabled `task_acks_late` (we do)
  — jobs killed mid-render will be redelivered to the next available worker.
- For long-lived workers prefer **on-demand** with a static price.
- For cost control on bursty traffic, run multiple cheap interruptible Pods and
  scale concurrency in Celery instead of paying for an idle 24/7 box.
