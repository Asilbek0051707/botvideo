"""Hosted text-to-video via Replicate (no local GPU needed).

Input keys vary between video models — adjust `_build_input` for your chosen
REPLICATE_T2V_MODEL. Defaults target Lightricks LTX-Video.
"""

from __future__ import annotations

import time
from pathlib import Path

import httpx

from factory.agents.schema import Scene
from factory.core.config import settings
from factory.core.logging import get_logger
from factory.render.providers.base import T2VProvider

log = get_logger(__name__)
API = "https://api.replicate.com/v1"


class ReplicateT2V(T2VProvider):
    name = "replicate"

    def __init__(self) -> None:
        if not settings.replicate_api_token:
            raise RuntimeError("REPLICATE_API_TOKEN is required for T2V_PROVIDER=replicate")
        self.model = settings.replicate_t2v_model
        self.headers = {
            "Authorization": f"Bearer {settings.replicate_api_token}",
            "Content-Type": "application/json",
        }

    def _build_input(self, scene: Scene, width: int, height: int, fps: int) -> dict:
        return {
            "prompt": scene.visual_prompt,
            "negative_prompt": "blurry, low quality, watermark, distorted",
            "width": width,
            "height": height,
            "num_frames": int(scene.duration_sec * fps),
            "fps": fps,
        }

    def generate_clip(self, scene: Scene, out_path: Path, *, width: int, height: int, fps: int) -> Path:
        with httpx.Client(timeout=600) as client:
            resp = client.post(
                f"{API}/models/{self.model}/predictions",
                headers=self.headers,
                json={"input": self._build_input(scene, width, height, fps)},
            )
            resp.raise_for_status()
            pred = resp.json()
            url = self._poll(client, pred)
            self._download(client, url, out_path)
        return out_path

    def _poll(self, client: httpx.Client, pred: dict) -> str:
        get_url = pred["urls"]["get"]
        for _ in range(180):  # up to ~15 min
            if pred["status"] == "succeeded":
                out = pred["output"]
                return out[0] if isinstance(out, list) else out
            if pred["status"] in ("failed", "canceled"):
                raise RuntimeError(f"replicate prediction {pred['status']}: {pred.get('error')}")
            time.sleep(5)
            pred = client.get(get_url, headers=self.headers).json()
        raise TimeoutError("replicate prediction timed out")

    def _download(self, client: httpx.Client, url: str, out_path: Path) -> None:
        with client.stream("GET", url) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
