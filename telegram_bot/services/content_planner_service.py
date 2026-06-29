"""Content Planner Service — daily/weekly/monthly content planning templates.

Template-based, AI-ready: replace function bodies with AI calls.
"""

from __future__ import annotations

from datetime import datetime, timezone

PLANNER_TYPES: list[tuple[str, str]] = [
    ("daily",    "📅 Daily Plan"),
    ("weekly",   "📆 Weekly Plan"),
    ("monthly",  "🗓 Monthly Plan"),
    ("checklist","✅ Publishing Checklist"),
]

_PUBLISHING_CHECKLIST = [
    "✅ Video recorded and exported (1080p or 4K)",
    "✅ Thumbnail created (1280×720px, <2MB)",
    "✅ Title written (50–70 chars, keyword front-loaded)",
    "✅ Description added (300+ chars with hashtags + CTA)",
    "✅ Tags added (10–15 relevant tags + #Shorts if applicable)",
    "✅ End screen / cards added (for long videos)",
    "✅ Chapters added (for videos 10min+)",
    "✅ Subtitles/captions added",
    "✅ Scheduled at optimal upload time",
    "✅ Community post / Story cross-promotion scheduled",
    "✅ Instagram Reel / TikTok version exported",
    "✅ First comment pinned (subscribe CTA)",
]


def generate_daily_plan(topic: str) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%d.%m.%Y")
    return (
        f"📅 <b>Kunlik Kontent Rejasi — {date_str}</b>\n"
        f"🎯 <b>Mavzu:</b> {topic}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🌅 <b>ERTALAB (08:00–11:00)</b>\n"
        f"  📋 Bugungi video g'oyasini yakunlash: <i>{topic}</i>\n"
        "  🔍 Trending kalit so'zlarni tekshirish\n"
        "  ✏️ Script yozish (5–10 daqiqa)\n\n"
        "☀️ <b>KUNDUZ (11:00–15:00)</b>\n"
        "  🎬 Video suratga olish / animatsiya tayyor\n"
        "  🖼 Thumbnail yaratish (1280×720px)\n"
        "  ✂️ Montaj: kirish 3 soniya, asosiy qism, CTA\n\n"
        "🌆 <b>KECHQURUN (15:00–19:00)</b>\n"
        "  📝 Sarlavha, tavsif, teglar yozish\n"
        "  📤 Optimal vaqtda yuklash (17:00–19:00 UTC)\n"
        "  💬 Birinchi 30 daqiqada izohlarga javob\n\n"
        "🌙 <b>KECH (19:00–22:00)</b>\n"
        "  📊 Statistika tekshirish (ko'rishlar, CTR)\n"
        "  📱 Instagram/TikTok versiyasini repost\n"
        "  💡 Ertangi mavzuni belgilash\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Bugungi maqsad:</b> {topic} videosi yuklangan bo'lsin!\n"
        "📈 <b>KPI:</b> 500+ ko'rish birinchi 24 soatda"
    )


def generate_weekly_plan(topic: str) -> str:
    return (
        f"📆 <b>Haftalik Kontent Rejasi</b>\n"
        f"🎯 <b>Hafta mavzusi:</b> {topic}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🟢 <b>DUSHANBA</b>\n"
        f"  📋 Hafta rejasi: 5 ta {topic} video g'oyasi\n"
        "  🔍 Raqiblar tahlili + trending tekshirish\n"
        "  ✏️ 2 ta script yozish\n\n"
        "🟡 <b>SESHANBA</b>\n"
        "  🎬 Video 1 suratga olish\n"
        "  ✂️ Montaj + thumbnail\n"
        f"  📤 Video 1 yuklash: <i>{topic} — birinchi epizod</i>\n\n"
        "🔵 <b>CHORSHANBA</b>\n"
        "  📊 Video 1 statistikasini tahlil\n"
        "  🎬 Video 2 tayyorlash\n"
        "  💬 Izohlarga javob + community post\n\n"
        "🟠 <b>PAYSHANBA</b>\n"
        "  ✂️ Video 2 montaj + thumbnail\n"
        f"  📤 Video 2 yuklash: <i>{topic} — ikkinchi epizod</i>\n"
        "  🔍 SEO optimallashtirish\n\n"
        "🔴 <b>JUMA</b>\n"
        "  🎬 Video 3 suratga olish\n"
        "  📱 TikTok/Instagram repost\n"
        "  💡 Keyingi hafta g'oyalari\n\n"
        "🟣 <b>SHANBA</b>\n"
        "  ✂️ Video 3 montaj\n"
        f"  📤 Video 3 yuklash: <i>{topic} — hafta yakuni</i>\n"
        "  📊 Haftalik statistika hisoboti\n\n"
        "⚪ <b>YAKSHANBA</b>\n"
        "  🧘 Dam olish / Yaratuvchilik vaqti\n"
        "  📋 Keyingi hafta rejasi tuzish\n"
        "  🎯 Maqsadlar ko'rib chiqish\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>Haftalik maqsad:</b> 3 video, 2000+ obunachi qo'shish\n"
        f"🎯 <b>Fokus:</b> {topic} auditoriyasini kengaytirish"
    )


def generate_monthly_plan(topic: str) -> str:
    now = datetime.now(timezone.utc)
    month_names = {
        1:"Yanvar",2:"Fevral",3:"Mart",4:"Aprel",5:"May",6:"Iyun",
        7:"Iyul",8:"Avgust",9:"Sentyabr",10:"Oktabr",11:"Noyabr",12:"Dekabr",
    }
    month = month_names.get(now.month, str(now.month))
    return (
        f"🗓 <b>{month} Oylik Kontent Rejasi</b>\n"
        f"🎯 <b>Oy mavzusi:</b> {topic}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📅 <b>1-HAFTA: Asos</b>\n"
        f"  Mavzu: {topic} — kirish, tanishish\n"
        "  Maqsad: Auditoriyani jalb qilish\n"
        "  Videolar: 3–5 ta Shorts\n"
        "  KPI: 10,000 ko'rish\n\n"
        "📅 <b>2-HAFTA: Chuqurlashtirish</b>\n"
        f"  Mavzu: {topic} — kuchli tomonlar, qobiliyatlar\n"
        "  Maqsad: Engagement oshirish\n"
        "  Videolar: 3 ta Shorts + 1 ta Long-form\n"
        "  KPI: 25,000 ko'rish, 500 obunachi\n\n"
        "📅 <b>3-HAFTA: Viral Attempt</b>\n"
        f"  Mavzu: {topic} vs [RAQIB] — battle format\n"
        "  Maqsad: Viral bo'lish\n"
        "  Videolar: 5 ta Shorts (battle seriyasi)\n"
        "  KPI: 50,000 ko'rish, 1000 obunachi\n\n"
        "📅 <b>4-HAFTA: Sayqa</b>\n"
        f"  Mavzu: {topic} — o'sish hikoyasi, xulosa\n"
        "  Maqsad: Sodiq auditoriya\n"
        "  Videolar: 3 ta Shorts + 1 ta Special\n"
        "  KPI: 100,000 ko'rish, 2000 obunachi\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Oylik maqsad:</b> 185,000+ ko'rish\n"
        f"👥 <b>Obunachi maqsadi:</b> +3,500 obunachi\n"
        f"🎯 <b>Asosiy mavzu:</b> {topic}\n"
        "💰 <b>Monitorizatsiya:</b> Har dushanba statistika tahlili"
    )


def get_publishing_checklist() -> str:
    lines = ["✅ <b>Video Yuklash Chek-listi</b>\n"]
    lines += [f"  {item}" for item in _PUBLISHING_CHECKLIST]
    lines.append("\n💡 <b>Pro tip:</b> Har bir video uchun shu listni o'qing!")
    return "\n".join(lines)
