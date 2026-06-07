"""Typed content-plan structures shared by agents and the render pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Scene(BaseModel):
    index: int
    narration: str = Field(..., description="What the voiceover says during this scene")
    visual_prompt: str = Field(..., description="Text-to-video prompt for this scene")
    on_screen_text: str = Field("", description="Caption / hook text burned on screen")
    duration_sec: float = Field(..., ge=1.0, le=300.0)
    motion: str = Field("slow push-in", description="Camera/motion hint for the T2V model")


class ContentPlan(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    style: str = "documentary"
    language: str = "en"
    full_narration: str = ""
    scenes: list[Scene] = Field(default_factory=list)

    @property
    def total_duration(self) -> float:
        return round(sum(s.duration_sec for s in self.scenes), 2)
