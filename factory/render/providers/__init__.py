"""Text-to-video provider factory."""

from __future__ import annotations

from functools import lru_cache

from factory.core.config import settings
from factory.render.providers.base import T2VProvider


@lru_cache
def get_t2v_provider() -> T2VProvider:
    provider = settings.t2v_provider
    if provider == "replicate":
        from factory.render.providers.replicate_t2v import ReplicateT2V

        return ReplicateT2V()
    if provider == "gpu":
        from factory.render.providers.gpu_t2v import GpuT2V

        return GpuT2V()
    from factory.render.providers.mock_t2v import MockT2V

    return MockT2V()


__all__ = ["T2VProvider", "get_t2v_provider"]
