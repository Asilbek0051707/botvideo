"""Visual agent — the art director.

Hardens each scene's text-to-video prompt with a consistent cinematic style and a
shared negative prompt so the generated clips look like one cohesive video.
"""

from __future__ import annotations

from factory.agents.schema import Scene

STYLE_PRESETS = {
    "documentary": "cinematic documentary, natural lighting, film grain, anamorphic, muted palette",
    "energetic": "vibrant high-contrast, dynamic motion, punchy colors, lens flares",
    "calm": "soft diffused light, pastel palette, gentle slow motion, dreamy bokeh",
    "meme": "bold saturated colors, exaggerated, internet aesthetic, snappy",
}

NEGATIVE_PROMPT = (
    "blurry, low quality, watermark, text artifacts, distorted faces, extra limbs, "
    "jpeg artifacts, deformed, oversaturated, flicker"
)


class VisualAgent:
    def direct(self, scenes: list[Scene], *, style: str) -> list[Scene]:
        look = STYLE_PRESETS.get(style, STYLE_PRESETS["documentary"])
        w, h = (1080, 1920)
        for s in scenes:
            s.visual_prompt = (
                f"{s.visual_prompt}, {look}, {s.motion}, vertical 9:16 {w}x{h}, "
                f"sharp focus, cohesive color grade"
            )
        return scenes

    @staticmethod
    def negative_prompt() -> str:
        return NEGATIVE_PROMPT
