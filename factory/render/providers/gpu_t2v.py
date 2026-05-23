"""Local/remote CUDA text-to-video via diffusers (RunPod / Vast.ai GPU worker).

Heavy deps (torch, diffusers) are installed only in `worker/Dockerfile.gpu`, so
imports are local to the methods. The pipeline is loaded once per worker process.
Defaults target Lightricks LTX-Video; adjust for other diffusers video pipelines.
"""

from __future__ import annotations

from pathlib import Path

from factory.agents.schema import Scene
from factory.core.config import settings
from factory.core.logging import get_logger
from factory.render.providers.base import T2VProvider

log = get_logger(__name__)

_PIPE = None  # process-wide singleton


def _round_to(value: int, multiple: int) -> int:
    return max(multiple, (value // multiple) * multiple)


class GpuT2V(T2VProvider):
    name = "gpu"

    def _pipeline(self):
        global _PIPE
        if _PIPE is not None:
            return _PIPE
        import torch
        from diffusers import LTXPipeline

        log.info("gpu_t2v.loading_model", model=settings.gpu_t2v_model)
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        pipe = LTXPipeline.from_pretrained(
            settings.gpu_t2v_model, torch_dtype=dtype, token=settings.hf_token
        )
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        pipe.enable_attention_slicing()
        _PIPE = pipe
        return _PIPE

    def generate_clip(self, scene: Scene, out_path: Path, *, width: int, height: int, fps: int) -> Path:
        from diffusers.utils import export_to_video

        pipe = self._pipeline()
        w, h = _round_to(width, 32), _round_to(height, 32)
        # LTX expects num_frames == 8*k + 1
        raw = int(scene.duration_sec * fps)
        num_frames = max(9, (raw // 8) * 8 + 1)

        result = pipe(
            prompt=scene.visual_prompt,
            negative_prompt="blurry, low quality, watermark, distorted, deformed",
            width=w,
            height=h,
            num_frames=num_frames,
            num_inference_steps=40,
        )
        frames = result.frames[0]
        export_to_video(frames, str(out_path), fps=fps)
        return out_path
