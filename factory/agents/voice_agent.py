"""Voice agent — narration text -> audio bytes.

Providers: ElevenLabs, OpenAI TTS, or a stdlib silent-WAV mock so the pipeline
produces a correctly-timed track with no API key.
"""

from __future__ import annotations

import io
import wave

import httpx

from factory.core.config import settings
from factory.core.logging import get_logger

log = get_logger(__name__)


class VoiceAgent:
    def synthesize(self, text: str, *, voice: str | None = None, fallback_seconds: float = 30.0) -> tuple[bytes, str]:
        """Return (audio_bytes, extension)."""
        provider = settings.tts_provider
        try:
            if provider == "elevenlabs" and settings.elevenlabs_api_key:
                return self._elevenlabs(text, voice), "mp3"
            if provider == "openai" and settings.openai_api_key:
                return self._openai(text, voice), "mp3"
        except Exception as exc:
            log.warning("voice_agent.tts_failed_fallback", provider=provider, error=str(exc))
        return self._silent_wav(fallback_seconds), "wav"

    def _elevenlabs(self, text: str, voice: str | None) -> bytes:
        voice_id = voice or settings.elevenlabs_voice_id
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        resp = httpx.post(
            url,
            headers={"xi-api-key": settings.elevenlabs_api_key, "accept": "audio/mpeg"},
            json={"text": text, "model_id": "eleven_multilingual_v2"},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.content

    def _openai(self, text: str, voice: str | None) -> bytes:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.audio.speech.create(
            model="tts-1", voice=voice or settings.openai_tts_voice, input=text
        )
        return resp.read()

    def _silent_wav(self, seconds: float, sample_rate: int = 44100) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            w.writeframes(b"\x00\x00" * int(max(1.0, seconds) * sample_rate))
        return buf.getvalue()
