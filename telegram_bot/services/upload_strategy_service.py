"""Upload Strategy & AI Recommendations Service.

Template-based recommendations — designed so the implementation can be
swapped for real AI without changing any handler code (same return types).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── Upload schedules per category ────────────────────────────────

_SCHEDULES: dict[str, dict] = {
    "cartoon": {
        "frequency":       "Haftada 4–6 ta Shorts yoki haftada 1 ta Long-form",
        "best_days":       "Shanba, Yakshanba, Seshanba",
        "best_times":      "08:00–11:00 UTC (bolalar maktabdan keyin)",
        "avoid":           "Chorshanba kechasi, Juma ertalab",
        "content_mix":     "70% Shorts + 30% Long (>3 daqiqa)",
        "consistency":     "Bir xil vaqt, bir xil format — algoritm sevadi",
        "engagement_tip":  "Dastlabki 30 daqiqada 3+ izoh javob bering",
        "thumbnail_tip":   "Yorqin ranglar, yuz yaqin, 1280×720px",
        "hook_tip":        "Birinchi 2 soniyada harakat yoki savol",
        "season_tip":      "Yanvar, Sentyabr — maktab boshlanish = pik vaqt",
    },
    "gaming": {
        "frequency":       "Haftada 5–7 ta Shorts yoki 2 ta Long-form",
        "best_days":       "Payshanba, Juma, Shanba",
        "best_times":      "16:00–21:00 UTC (maktabdan keyin)",
        "avoid":           "Dushanba ertalab",
        "content_mix":     "60% Shorts + 40% Long (5–15 daqiqa)",
        "consistency":     "Live stream hafta bir marta — auditoriya qoladi",
        "engagement_tip":  "Komentariyada o'yinchilarni tag qiling",
        "thumbnail_tip":   "CAPS LOCK sarlavha + o'yin screenshoti",
        "hook_tip":        "O'yin boshlanganda darhol aktsiya — intro yo'q",
        "season_tip":      "Yangi o'yin chiqqanda tezda video — hype vaqti",
    },
    "anime": {
        "frequency":       "Haftada 3–5 ta Shorts yoki haftada 1–2 ta Long",
        "best_days":       "Chorshanba, Payshanba, Yakshanba",
        "best_times":      "14:00–18:00 UTC",
        "avoid":           "Shanba ertalab (raqobat yuqori)",
        "content_mix":     "50% Shorts + 50% Long (3–8 daqiqa)",
        "consistency":     "Anime yangi season bilan sinkronlashtiring",
        "engagement_tip":  "Savol bilan tugating: 'Kim kuchliroq?'",
        "thumbnail_tip":   "Neon ranglar + katta ko'z + dramatik ifoda",
        "hook_tip":        "Epik soundtrack bilan boshlang",
        "season_tip":      "Yangi anime season — shu vaqtda ko'proq yuklang",
    },
    "meme": {
        "frequency":       "Kuniga 1–3 ta Shorts (tezlik muhim)",
        "best_days":       "Har kuni — meme har vaqt ishlaydi",
        "best_times":      "10:00–14:00 UTC yoki 19:00–23:00 UTC",
        "avoid":           "Eskirgan trend — vaqtida yetib boring",
        "content_mix":     "95% Shorts + 5% Long",
        "consistency":     "Trend + o'z stilingiz = brend meme kanal",
        "engagement_tip":  "Meme formatida izoh so'rang",
        "thumbnail_tip":   "Vintage/kapcha matn + kulgili ifoda",
        "hook_tip":        "0 soniyada kulgi yoki shok — intro yo'q",
        "season_tip":      "Yangi viral trend + 6 soat ichida — yutadi",
    },
    "kids": {
        "frequency":       "Haftada 3–4 ta Shorts",
        "best_days":       "Dushanba, Chorshanba, Shanba",
        "best_times":      "07:00–09:00 UTC (maktabgacha) yoki 14:00–17:00",
        "avoid":           "Kech kechqurun (bolalar uxlaydi)",
        "content_mix":     "80% Shorts + 20% Long (<5 daqiqa)",
        "consistency":     "Bir xil kalit so'z va mavzu — ota-onalar topadi",
        "engagement_tip":  "Bolalar o'z ismlarini izohda yozishiga undang",
        "thumbnail_tip":   "Pastel ranglar + ikkita yuz + tabassum",
        "hook_tip":        "Qo'shiq yoki quvnoq ovoz bilan boshlang",
        "season_tip":      "Bayramlar: Yangi yil, Eid, Navro'z — maxsus video",
    },
    "general": {
        "frequency":       "Haftada 3–5 ta Shorts yoki haftada 1 ta Long",
        "best_days":       "Seshanba, Chorshanba, Payshanba",
        "best_times":      "12:00–16:00 UTC",
        "avoid":           "Shanba kechasi (raqobat yuqori)",
        "content_mix":     "60% Shorts + 40% Long",
        "consistency":     "Muntazamlik — har hafta bir xil kunda",
        "engagement_tip":  "Birinchi 24 soatda har izohga javob",
        "thumbnail_tip":   "Yorqin rang + yuz ifodasi + qisqa matn",
        "hook_tip":        "Dastlabki 3 soniyada eng qiziq narsani ko'rsating",
        "season_tip":      "Yillik bayram va trend vaqtlarini rejalashtiring",
    },
}

# ── Content calendar ──────────────────────────────────────────────

_WEEKLY_CALENDAR: dict[str, str] = {
    "Dushanba":    "📋 Reja haftasi — mavzu va g'oyalar tanlash",
    "Seshanba":    "🎬 Asosiy video suratga olish",
    "Chorshanba":  "✂️ Montaj + thumbnail tayyorlash",
    "Payshanba":   "🚀 Birinchi video yuklash + SEO optimallashtirish",
    "Juma":        "🎬 Ikkinchi video suratga olish",
    "Shanba":      "🚀 Ikkinchi video yuklash + Community post",
    "Yakshanba":   "📊 Statistika tahlil + keyingi hafta rejasi",
}

# ── AI Recommendation templates ───────────────────────────────────

_AI_RECS: dict[str, list[dict]] = {
    "cartoon": [
        {"label": "⏱ Eng yaxshi video uzunligi",      "value": "45–60 soniya (Shorts)"},
        {"label": "🕐 Eng yaxshi yuklash vaqti",        "value": "Shanba 08:00–10:00 UTC"},
        {"label": "🎭 Tavsiya etilgan karakter",        "value": "Spider-Man, Bluey, PAW Patrol"},
        {"label": "🖼 Tavsiya etilgan thumbnail uslubi", "value": "Yuz yaqin + sariq/qizil fon"},
        {"label": "🎵 Tavsiya etilgan musiqa",          "value": "Adventure/quvnoq instrumental"},
        {"label": "🪝 Eng yaxshi hook turi",            "value": "Aktsiya bilan boshlang (jang/qutqarish)"},
        {"label": "📖 Eng yaxshi hikoya turi",          "value": "Muammo → Qahramonlik → Yechim"},
        {"label": "🎯 Eng yaxshi SEO strategiyasi",     "value": "#Shorts + #[Karakter] + 3 kalit so'z"},
        {"label": "👥 Maqsad auditoriya",              "value": "3–10 yosh bolalar + ota-onalar"},
    ],
    "gaming": [
        {"label": "⏱ Eng yaxshi video uzunligi",      "value": "50–60 soniya (Shorts) / 8–15 daqiqa (Long)"},
        {"label": "🕐 Eng yaxshi yuklash vaqti",        "value": "Juma 17:00–19:00 UTC"},
        {"label": "🎮 Tavsiya etilgan gameplay",        "value": "Minecraft, Roblox, Brawl Stars"},
        {"label": "🖼 Tavsiya etilgan thumbnail uslubi", "value": "CAPS LOCK sarlavha + o'yin screenshot"},
        {"label": "🎵 Tavsiya etilgan musiqa",          "value": "Epic EDM / gaming beat"},
        {"label": "🪝 Eng yaxshi hook turi",            "value": "O'yin aksiyasi 0-soniyadan"},
        {"label": "📖 Eng yaxshi hikoya turi",          "value": "Challenge → Epic Fail → Win"},
        {"label": "🎯 Eng yaxshi SEO strategiyasi",     "value": "O'yin nomi + 'shorts' + trend tag"},
        {"label": "👥 Maqsad auditoriya",              "value": "8–18 yosh o'yinchilar"},
    ],
    "anime": [
        {"label": "⏱ Eng yaxshi video uzunligi",      "value": "55–60 soniya (Shorts) / 3–8 daqiqa (Long)"},
        {"label": "🕐 Eng yaxshi yuklash vaqti",        "value": "Payshanba 15:00–17:00 UTC"},
        {"label": "🎌 Tavsiya etilgan anime",          "value": "Dragon Ball, Naruto, One Piece"},
        {"label": "🖼 Tavsiya etilgan thumbnail uslubi", "value": "Neon + dramatik yuz + katakana matn"},
        {"label": "🎵 Tavsiya etilgan musiqa",          "value": "Epic anime OST / AMV beats"},
        {"label": "🪝 Eng yaxshi hook turi",            "value": "Epik sahna / transformation"},
        {"label": "📖 Eng yaxshi hikoya turi",          "value": "Kuch taqqoslash / jang arc"},
        {"label": "🎯 Eng yaxshi SEO strategiyasi",     "value": "#anime #shorts + karakter ismi"},
        {"label": "👥 Maqsad auditoriya",              "value": "10–22 yosh anime muxlislari"},
    ],
    "meme": [
        {"label": "⏱ Eng yaxshi video uzunligi",      "value": "15–30 soniya"},
        {"label": "🕐 Eng yaxshi yuklash vaqti",        "value": "Kuniga istalgan, trenddan 4–6 soat keyin"},
        {"label": "😂 Tavsiya etilgan format",         "value": "Skibidi, NPC, Sigma, Ohio, Brainrot"},
        {"label": "🖼 Tavsiya etilgan thumbnail uslubi", "value": "Kapcha matn + kulgili ifoda"},
        {"label": "🎵 Tavsiya etilgan musiqa",          "value": "Viral meme beat / trending audio"},
        {"label": "🪝 Eng yaxshi hook turi",            "value": "Darhol kulgi / shok — 0 soniyada"},
        {"label": "📖 Eng yaxshi hikoya turi",          "value": "Loop / unexpected ending / absurd"},
        {"label": "🎯 Eng yaxshi SEO strategiyasi",     "value": "Trending meme nomi + #shorts #viral"},
        {"label": "👥 Maqsad auditoriya",              "value": "13–25 yosh Z-avlod"},
    ],
    "kids": [
        {"label": "⏱ Eng yaxshi video uzunligi",      "value": "30–45 soniya"},
        {"label": "🕐 Eng yaxshi yuklash vaqti",        "value": "Dushanba/Shanba 07:00–09:00 UTC"},
        {"label": "🧸 Tavsiya etilgan karakter",        "value": "Bluey, PAW Patrol, Peppa Pig"},
        {"label": "🖼 Tavsiya etilgan thumbnail uslubi", "value": "Pastel ranglar + tabassum + 2 karakter"},
        {"label": "🎵 Tavsiya etilgan musiqa",          "value": "Mayin quvnoq bolalar musiqasi"},
        {"label": "🪝 Eng yaxshi hook turi",            "value": "Qo'shiq yoki quvnoq tovush"},
        {"label": "📖 Eng yaxshi hikoya turi",          "value": "Oddiy muammo → yordamlashish → baxt"},
        {"label": "🎯 Eng yaxshi SEO strategiyasi",     "value": "#kids #cartoon + karakter ismi"},
        {"label": "👥 Maqsad auditoriya",              "value": "0–6 yosh bolalar + ota-onalar"},
    ],
    "general": [
        {"label": "⏱ Eng yaxshi video uzunligi",      "value": "45–60 soniya (Shorts) / 5–10 daqiqa (Long)"},
        {"label": "🕐 Eng yaxshi yuklash vaqti",        "value": "Seshanba-Payshanba 12:00–16:00 UTC"},
        {"label": "🎯 Tavsiya etilgan format",         "value": "Top 10, Challenge, Comparison, Story"},
        {"label": "🖼 Tavsiya etilgan thumbnail uslubi", "value": "Yorqin rang + yuz + qisqa matn (≤4 so'z)"},
        {"label": "🎵 Tavsiya etilgan musiqa",         "value": "Mavzuga mos instrumental"},
        {"label": "🪝 Eng yaxshi hook turi",           "value": "Savol yoki shok fakti bilan boshlang"},
        {"label": "📖 Eng yaxshi hikoya turi",         "value": "Muammo → kutilmagan burilish → yechim"},
        {"label": "🎯 Eng yaxshi SEO strategiyasi",    "value": "Asosiy kalit so'z sarlavha boshida"},
        {"label": "👥 Maqsad auditoriya",             "value": "Umumiy — niche aniq bo'lganda o'zgartiring"},
    ],
}

_CATEGORY_LIST = [
    ("cartoon",  "🎭 Cartoon"),
    ("gaming",   "🎮 Gaming"),
    ("anime",    "🎌 Anime"),
    ("meme",     "😂 Meme"),
    ("kids",     "🧸 Bolalar"),
    ("general",  "🌐 Umumiy"),
]


def get_upload_strategy(category: str = "general") -> dict:
    """Return upload schedule + strategy for a content category."""
    sched = _SCHEDULES.get(category, _SCHEDULES["general"])
    return {
        "category": category,
        "schedule": sched,
        "calendar": _WEEKLY_CALENDAR,
    }


def get_ai_recommendations(category: str = "general") -> list[dict]:
    """Return template-based AI recommendations for a category."""
    return _AI_RECS.get(category, _AI_RECS["general"])


def get_category_list() -> list[tuple[str, str]]:
    return _CATEGORY_LIST
