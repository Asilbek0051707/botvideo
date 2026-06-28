"""Content Recommendation Engine — template-based, ready for AI integration.

Add new category rules to _CATEGORY_RULES to expand recommendations.
Replace get_recommendations() implementation with an AI call when ready.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Recommendation:
    label: str
    value: str
    reason: str


# ── Rule table per content category ──────────────────────────────

_CATEGORY_RULES: dict[str, dict] = {
    "cartoon": {
        "video_types":  ["Character vs Character", "Funny Story", "Baby Version", "Evolution"],
        "char_combos":  ["Spider-Man + Batman", "Goku + Naruto", "Sonic + Mario"],
        "thumbnail":    "Yuz yaqin ko'rinish + katta sarlavha + yorqin rang (sariq/qizil)",
        "music":        "Quvnoq adventure instrumental",
        "length":       "45–60 soniya (YouTube Shorts)",
        "upload_time":  "Shanba/Yakshanba ertalab 08:00–11:00 UTC",
        "audience":     "2–8 yosh bolalar va ularning ota-onalari",
        "story":        "Qutqarish / jang / sarguzasht hikoyasi",
        "editing":      "Tez montaj, yorqin ranglar, katta sarlavhalar",
    },
    "gaming": {
        "video_types":  ["Gameplay Montage", "Impossible Challenge", "Top 10 Moments"],
        "char_combos":  ["Steve + Creeper", "Sonic + Knuckles", "Mario + Luigi"],
        "thumbnail":    "O'yin screenshoti + hayratlanarli ifoda + CAPS LOCK sarlavha",
        "music":        "Epic/dubstep gaming musiqa",
        "length":       "50–60 soniya",
        "upload_time":  "Juma/Shanba kechqurun 16:00–20:00 UTC",
        "audience":     "8–18 yosh o'spirin o'yinchilar",
        "story":        "O'yin bosqichi, challenge, yutish yoki yutqazish",
        "editing":      "Tez kesish, sound effects, zoom-in effektlar",
    },
    "anime": {
        "video_types":  ["Power Comparison", "Evolution", "Battle", "Transformation"],
        "char_combos":  ["Goku + Naruto", "Luffy + Zoro", "Saitama + Goku"],
        "thumbnail":    "Anime karakter katta ko'z + neon rang + sovuq sarlavha",
        "music":        "AMV / epic anime OST",
        "length":       "55–60 soniya",
        "upload_time":  "Chorshanba/Payshanba 14:00–18:00 UTC",
        "audience":     "10–20 yosh anime muxlislari",
        "story":        "Kuch taqqoslash, jang, hikoya arc",
        "editing":      "Cinematic cuts, slow motion, drama effektlar",
    },
    "meme": {
        "video_types":  ["Meme Compilation", "Reaction", "Funny Story", "Random Generator"],
        "char_combos":  ["Skibidi + NPC", "Sigma + Brainrot", "Ohio + Rizz"],
        "thumbnail":    "Kulgili ifoda + kapcha matn + vintage style",
        "music":        "Viral meme musiqa / trending beat",
        "length":       "15–30 soniya",
        "upload_time":  "Har kuni 10:00–22:00 UTC (meme istalgan vaqt!)",
        "audience":     "13–25 yosh Z-avlod",
        "story":        "Tez tempo, loop, unexpected ending",
        "editing":      "Jump cuts, meme sounds, overlays",
    },
    "kids": {
        "video_types":  ["Color Challenge", "Baby Version", "Rescue Story", "School Day"],
        "char_combos":  ["Bluey + Bingo", "Chase + Skye", "Peppa + George"],
        "thumbnail":    "Ikkita karakter yuz bilan + pasteldagi rang + tabassum",
        "music":        "Mayin, quvnoq bolalar musiqasi",
        "length":       "30–45 soniya",
        "upload_time":  "Dushanba-Juma ertalab 07:00–09:00 UTC",
        "audience":     "0–6 yosh bolalar (tomosha ota-ona bilan)",
        "story":        "Oddiy muammo → yechim → baxt",
        "editing":      "Sekin temp, katta sarlavhalar, animatsion o'tishlar",
    },
    "general": {
        "video_types":  ["Top 10", "Comparison", "Challenge", "Funny Story"],
        "char_combos":  ["Eng mashhur 2 karakter birga"],
        "thumbnail":    "Yorqin rang + yuz ifodasi + qisqa matn (≤4 so'z)",
        "music":        "Mavzuga mos musiqa",
        "length":       "45–60 soniya",
        "upload_time":  "Dushanba–Juma 12:00–18:00 UTC",
        "audience":     "Umumiy tomoshabinlar",
        "story":        "Muammo → kutilmagan burilish → yechim",
        "editing":      "Dinamik montaj, subtitle, CTA oxirida",
    },
}

_CHAR_CATEGORY_MAP: dict[str, str] = {
    "minecraft": "gaming", "roblox": "gaming", "sonic": "gaming",
    "mario": "gaming", "luigi": "gaming", "kirby": "gaming",
    "goku": "anime", "naruto": "anime", "pikachu": "anime",
    "luffy": "anime", "sasuke": "anime", "ichigo": "anime",
    "skibidi": "meme", "npc": "meme", "sigma": "meme",
    "ohio": "meme", "brainrot": "meme", "gigachad": "meme",
    "spider": "cartoon", "batman": "cartoon", "bluey": "cartoon",
    "paw": "cartoon", "patrol": "cartoon", "disney": "cartoon",
    "frozen": "cartoon", "moana": "cartoon", "peppa": "kids",
    "bluey": "kids", "bingo": "kids", "chase": "kids",
}


def _guess_category(character: str) -> str:
    cl = character.lower()
    for keyword, cat in _CHAR_CATEGORY_MAP.items():
        if keyword in cl:
            return cat
    return "general"


def get_recommendations(
    category: str = "general",
    character: str = "",
) -> list[Recommendation]:
    """Return a structured list of recommendations for the given category."""
    rules = _CATEGORY_RULES.get(category, _CATEGORY_RULES["general"])
    char_hint = f" ({character})" if character else ""

    return [
        Recommendation(
            label="🎬 Eng yaxshi video tur",
            value=", ".join(rules["video_types"][:3]),
            reason=f"Bu {category}{char_hint} uchun eng ko'p ko'rilgan formatlar",
        ),
        Recommendation(
            label="🤝 Eng yaxshi karakter kombinatsiya",
            value=rules["char_combos"][0],
            reason="Ikkita mashhur karakter birgalikda 2–3x ko'proq view oladi",
        ),
        Recommendation(
            label="🖼 Thumbnail uslubi",
            value=rules["thumbnail"],
            reason="Click-through rate'ni 2–3x oshiradi",
        ),
        Recommendation(
            label="🎵 Musiqa uslubi",
            value=rules["music"],
            reason="Tomoshabinni ushlab turadi, retention +40%",
        ),
        Recommendation(
            label="⏱ Video uzunligi",
            value=rules["length"],
            reason="YouTube Shorts algoritmi bu uzunlikni afzal ko'radi",
        ),
        Recommendation(
            label="📅 Yuklash vaqti",
            value=rules["upload_time"],
            reason="Eng ko'p tomoshabin shu vaqtda online",
        ),
        Recommendation(
            label="👥 Maqsad auditoriya",
            value=rules["audience"],
            reason="Kanalning tavsiya algoritmiga ta'sir qiladi",
        ),
        Recommendation(
            label="📖 Hikoya turi",
            value=rules["story"],
            reason="Eng yaxshi retention natijasini beradi",
        ),
        Recommendation(
            label="✂️ Montaj uslubi",
            value=rules["editing"],
            reason="Bu kategoriya uchun optimal ko'rish tajribasi",
        ),
    ]


def get_char_recommendations(character: str) -> list[Recommendation]:
    """Auto-detect category from character name and return recommendations."""
    cat = _guess_category(character)
    return get_recommendations(cat, character)


def get_category_list() -> list[tuple[str, str]]:
    """Return all available categories as (id, label) pairs."""
    return [
        ("cartoon",  "🎭 Cartoon / Multfilm"),
        ("gaming",   "🎮 Gaming / O'yin"),
        ("anime",    "🎌 Anime"),
        ("meme",     "😂 Meme"),
        ("kids",     "🧸 Bolalar"),
        ("general",  "🌐 Umumiy"),
    ]
