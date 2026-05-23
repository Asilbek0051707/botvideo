# RunPod — GPU text-to-video worker

The CPU stack (API, queue, telegram) can live anywhere — Railway, Render, a VPS —
while the GPU worker lives on a RunPod Pod that pulls jobs off the same Redis
broker. The worker connects out; nothing needs to expose ports inward.

## 1. Build & push the GPU image

From the repo root:

```bash
docker build -f worker/Dockerfile.gpu -t ghcr.io/<you>/factory-worker-gpu:latest .
docker push ghcr.io/<you>/factory-worker-gpu:latest
```

## 2. Create a Pod

- Template type: **Custom**
- GPU: any 16GB+ (e.g. RTX 4090, L4, A10). LTX-Video runs in ~12–14GB at 768×1280.
- Container image: `ghcr.io/<you>/factory-worker-gpu:latest`
- Container disk: 30 GB
- Volume mount: `/root/.cache/huggingface` → 50 GB (persists model weights)
- Docker command: leave blank (the image's CMD already runs the GPU worker)

## 3. Environment variables

Paste from `deploy/runpod/env.example` (below). The Redis/Postgres URLs must
point at your already-deployed broker and DB — Pods are *workers*, not infra.

## 4. Verify

After the Pod boots, in your broker (e.g. Render Redis + flower), you should
see a worker named `celery@<pod-host>` consuming the `gpu` queue. Submit a job
with `T2V_PROVIDER=gpu` on the API side and watch it process.
