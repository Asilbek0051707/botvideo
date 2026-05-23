# configs/

Runtime configuration lives in `.env` (loaded by `factory.core.config`). This
folder is for **extension configs** that ship alongside code:

- `voices.yaml` — per-channel TTS voice presets (mapping to ElevenLabs voice IDs)
- `styles.yaml` — visual style presets beyond the built-ins in
  `factory.agents.visual_agent.STYLE_PRESETS`
- `niches.yaml` — niche-specific prompt overrides

These are placeholders today — the in-code presets are authoritative. Move
presets here when you outgrow editing Python (a non-engineer should be able to
add a new style without touching the codebase).
