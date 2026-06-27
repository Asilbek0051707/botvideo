"""Material-type aware provider stubs.

Each material type maps to the correct platforms — videos go to video sites,
music goes to music sites, images go to image sites, etc.
"""

from __future__ import annotations

from urllib.parse import quote_plus

from telegram_bot.services.providers.base import BaseProvider, SearchResult

# ─── per-material-type provider definitions ────────────────────────
# Format: (icon, label, url_template)
# {q} is replaced with the encoded search query
# {char} is replaced with just the character name (for sites that don't want modifiers)

_MATERIAL_PROVIDERS: dict[str, list[tuple[str, str, str]]] = {

    # 🖼 PNG / Transparent Images
    "png": [
        ("🎨", "Freepik PNG",    "https://www.freepik.com/search?query={q}+transparent+png&type=psd"),
        ("🖼", "Pixabay PNG",    "https://pixabay.com/images/search/{q}/?image_type=png"),
        ("🔍", "Google Images",  "https://www.google.com/search?q={q}+transparent+PNG&tbm=isch"),
        ("📷", "Pexels",         "https://www.pexels.com/search/{q}/"),
        ("🔎", "Yandex Images",  "https://yandex.com/images/search?text={q}+png+transparent"),
    ],

    # 🟢 Green Screen
    "gs": [
        ("▶️", "YouTube",        "https://www.youtube.com/results?search_query={q}+green+screen+free"),
        ("🖼", "Pixabay Video",  "https://pixabay.com/videos/search/{q}/"),
        ("🎬", "Videvo",         "https://www.videvo.net/search/{q}/"),
        ("🔍", "Google",         "https://www.google.com/search?q={q}+green+screen+free+download"),
        ("📦", "Motion Array",   "https://motionarray.com/search/?q={q}+green+screen"),
    ],

    # 🎬 Animations
    "anim": [
        ("▶️", "YouTube",        "https://www.youtube.com/results?search_query={q}+animation+loop+free"),
        ("🎭", "LottieFiles",    "https://lottiefiles.com/search?q={q}"),
        ("😂", "GIPHY",          "https://giphy.com/search/{char}"),
        ("🖼", "Pixabay GIF",    "https://pixabay.com/gifs/search/{q}/"),
        ("📦", "Motion Array",   "https://motionarray.com/search/?q={q}+animation"),
    ],

    # 🎞 GIF
    "gif": [
        ("😂", "GIPHY",          "https://giphy.com/search/{char}"),
        ("🎭", "Tenor",          "https://tenor.com/search/{char}-gifs"),
        ("🖼", "Pixabay GIF",    "https://pixabay.com/gifs/search/{q}/"),
        ("🔍", "Google GIF",     "https://www.google.com/search?q={q}+GIF&tbm=isch&tbs=itp:animated"),
    ],

    # 🎥 Videos
    "vid": [
        ("▶️", "YouTube",        "https://www.youtube.com/results?search_query={q}+free+stock+video"),
        ("🖼", "Pixabay Video",  "https://pixabay.com/videos/search/{q}/"),
        ("📷", "Pexels Video",   "https://www.pexels.com/search/videos/{q}/"),
        ("🎬", "Videvo",         "https://www.videvo.net/search/{q}/"),
        ("🎪", "Coverr",         "https://coverr.co/videos?query={q}"),
    ],

    # 🌄 Backgrounds
    "bg": [
        ("🎨", "Freepik",        "https://www.freepik.com/search?query={q}+background&type=photo"),
        ("🖼", "Pixabay",        "https://pixabay.com/images/search/{q}+background/"),
        ("📷", "Unsplash",       "https://unsplash.com/s/photos/{char}"),
        ("📷", "Pexels",         "https://www.pexels.com/search/{q}+background/"),
        ("🔍", "Google Images",  "https://www.google.com/search?q={q}+background+4K&tbm=isch"),
    ],

    # 🎵 Music
    "mus": [
        ("🎵", "YouTube Music",  "https://www.youtube.com/results?search_query={q}+music+no+copyright+free"),
        ("☁️", "SoundCloud",     "https://soundcloud.com/search?q={q}"),
        ("🖼", "Pixabay Music",  "https://pixabay.com/music/search/{q}/"),
        ("🎸", "Free Music Ar.", "https://freemusicarchive.org/search?adv=1&quicksearch={q}"),
        ("🎶", "Bensound",       "https://www.bensound.com/royalty-free-music/search/{q}"),
        ("🎼", "Mixkit Music",   "https://mixkit.co/free-stock-music/search/{q}/"),
    ],

    # 🔊 Sound Effects
    "sfx": [
        ("🔊", "Freesound",      "https://freesound.org/search/?q={q}"),
        ("🔉", "Pixabay SFX",    "https://pixabay.com/sound-effects/search/{q}/"),
        ("🎭", "Mixkit SFX",     "https://mixkit.co/free-sound-effects/search/{q}/"),
        ("▶️", "YouTube SFX",    "https://www.youtube.com/results?search_query={q}+sound+effect+free"),
        ("🎵", "Zapsplat",       "https://www.zapsplat.com/?s={q}"),
    ],

    # 🎤 AI Voices
    "voice": [
        ("🤖", "ElevenLabs",     "https://elevenlabs.io/"),
        ("🎤", "Murf AI",        "https://murf.ai/"),
        ("🗣", "Voicemaker",     "https://voicemaker.in/"),
        ("🎙", "Clipchamp TTS",  "https://clipchamp.com/en/text-to-speech/"),
        ("▶️", "YouTube",        "https://www.youtube.com/results?search_query={q}+AI+voice+generator"),
    ],

    # ✨ Visual Effects
    "fx": [
        ("📦", "Motion Array",   "https://motionarray.com/search/?q={q}+vfx"),
        ("🖼", "Pixabay VFX",    "https://pixabay.com/videos/search/{q}+effect/"),
        ("🎬", "Videvo VFX",     "https://www.videvo.net/search/{q}+effect/"),
        ("▶️", "YouTube VFX",    "https://www.youtube.com/results?search_query={q}+visual+effect+free+download"),
        ("🎭", "ActionVFX",      "https://www.actionvfx.com/search?search={q}"),
    ],

    # 🖌 Thumbnail Assets
    "thumb": [
        ("🎨", "Canva",          "https://www.canva.com/create/youtube-thumbnails/"),
        ("🖼", "Freepik",        "https://www.freepik.com/search?query={q}+thumbnail&type=psd"),
        ("✏️", "Adobe Express",  "https://www.adobe.com/express/create/thumbnail/youtube"),
        ("🎭", "Fotor",          "https://www.fotor.com/features/youtube-thumbnail-maker/"),
        ("🔍", "Google",         "https://www.google.com/search?q={q}+youtube+thumbnail+template&tbm=isch"),
    ],

    # 🎨 AI Prompts
    "prompts": [
        ("🤖", "Midjourney",     "https://www.midjourney.com/"),
        ("🎨", "DALL-E 3",       "https://openai.com/dall-e-3"),
        ("🖼", "Leonardo AI",    "https://app.leonardo.ai/"),
        ("✨", "Ideogram",        "https://ideogram.ai/"),
        ("🌟", "Adobe Firefly",  "https://firefly.adobe.com/"),
    ],

    # 📂 Material Packs
    "pack": [
        ("📦", "Motion Array",   "https://motionarray.com/search/?q={q}"),
        ("🎨", "Freepik Pack",   "https://www.freepik.com/search?query={q}+pack"),
        ("🛒", "Envato",         "https://elements.envato.com/search/{q}"),
        ("🖼", "Pixabay",        "https://pixabay.com/images/search/{q}/"),
        ("🎬", "Mixkit Pack",    "https://mixkit.co/search/{q}/"),
    ],

    # 🌐 Internet Search
    "search": [
        ("🔍", "Google",         "https://www.google.com/search?q={q}"),
        ("🔎", "Yandex",         "https://yandex.com/search/?text={q}"),
        ("▶️", "YouTube",        "https://www.youtube.com/results?search_query={q}"),
        ("🖼", "Bing Images",    "https://www.bing.com/images/search?q={q}"),
        ("🐦", "Pinterest",      "https://www.pinterest.com/search/pins/?q={q}"),
    ],
}

# ─── query builders ────────────────────────────────────────────────

_MAT_MODIFIERS: dict[str, str] = {
    "png":     "transparent PNG",
    "gs":      "green screen",
    "anim":    "animation loop",
    "gif":     "animated GIF",
    "vid":     "video clip",
    "bg":      "background",
    "mus":     "background music",
    "sfx":     "sound effect",
    "voice":   "AI voice",
    "fx":      "visual effect",
    "thumb":   "thumbnail",
    "prompts": "fan art",
    "pack":    "asset pack",
    "search":  "",
}


def build_material_links(character: str, material_type: str) -> list[tuple[str, str]]:
    """Return [(label, url)] list for the given material type with correct platforms."""
    providers = _MATERIAL_PROVIDERS.get(material_type, _MATERIAL_PROVIDERS["search"])
    mod = _MAT_MODIFIERS.get(material_type, "")
    full_query = f"{character} {mod}".strip() if mod else character
    q = quote_plus(full_query)
    char = quote_plus(character)

    result = []
    for icon, label, url_tpl in providers:
        url = url_tpl.replace("{q}", q).replace("{char}", char)
        result.append((f"{icon} {label}", url))
    return result


# ─── legacy compat — kept so existing imports don't break ─────────

class BaseProviderStub(BaseProvider):
    name = "Stub"
    icon = "🔗"

    def build_search_url(self, query: str, material_type: str) -> str:
        links = build_material_links(query, material_type)
        return links[0][1] if links else f"https://www.google.com/search?q={quote_plus(query)}"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []


ALL_PROVIDERS: list[BaseProvider] = [BaseProviderStub()]
