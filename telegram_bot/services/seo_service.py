"""SEO Analyzer — rule-based title/description/tag analysis.

No external API needed. Ready for future AI enhancement (replace
calculate_seo_score() with an AI call that returns the same interface).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

# ── Word lists ────────────────────────────────────────────────────

_POWER_WORDS = {
    "amazing", "shocking", "secret", "viral", "trending", "epic",
    "ultimate", "hidden", "revealed", "challenge", "impossible",
    "funny", "scary", "mystery", "top 10", "vs", "evolution",
    "transformation", "compilation", "best", "worst", "new",
    "leaked", "exclusive", "never seen", "unbelievable", "insane",
}

_VIRAL_PATTERNS = [
    r"\d+\s*(tips|things|ways|secrets|facts|hacks|tricks)",  # numbers + noun
    r"(how to|why|what if|when|what happens)",                # question starters
    r"(vs\.?|versus)",                                         # comparison
    r"(caught|found|discovered|spotted)",                      # discovery words
    r"(glow ?up|before.{0,10}after)",                         # transformation
]

_NEGATIVE_PATTERNS = [
    r"click here",
    r"must watch",
    r"you won'?t believe",                                    # overused clickbait
]

_HASHTAG_RE = re.compile(r"#\w+")
_EMOJI_RE   = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)


@dataclass
class SEOResult:
    score: int                            # 0–100
    verdict: str
    title_analysis: dict = field(default_factory=dict)
    desc_analysis:  dict = field(default_factory=dict)
    tag_analysis:   dict = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)
    keywords_found: list[str] = field(default_factory=list)


# ── Title analysis ────────────────────────────────────────────────

def _analyze_title(title: str) -> tuple[int, dict, list[str]]:
    score = 0
    info  = {}
    tips  = []
    tl    = title.lower()

    # Length
    ln = len(title)
    info["length"] = ln
    if 40 <= ln <= 70:
        score += 20
        info["length_status"] = "ideal"
    elif 25 <= ln < 40 or 70 < ln <= 85:
        score += 10
        info["length_status"] = "ok"
        if ln < 40:
            tips.append(f"📝 Sarlavha qisqa ({ln} belgi) — 40–70 gacha uzaytiring")
        else:
            tips.append(f"📝 Sarlavha uzun ({ln} belgi) — 70 belgidan qisqartiring")
    else:
        info["length_status"] = "poor"
        if ln < 25:
            tips.append(f"📝 Sarlavha juda qisqa ({ln} belgi) — kamida 40 belgi bo'lsin")
        else:
            tips.append(f"📝 Sarlavha juda uzun ({ln} belgi) — 70 belgidan qisqartiring")

    # Power words
    matched_pw = [pw for pw in _POWER_WORDS if pw in tl]
    info["power_words"] = matched_pw
    if matched_pw:
        score += min(20, len(matched_pw) * 7)
    else:
        tips.append("💥 Sarlavhaga viral so'z qo'shing: 'epic', 'secret', 'challenge', 'vs'")

    # Viral patterns
    matched_vp = []
    for pattern in _VIRAL_PATTERNS:
        if re.search(pattern, tl):
            matched_vp.append(pattern)
    info["viral_patterns"] = len(matched_vp)
    if matched_vp:
        score += min(15, len(matched_vp) * 8)
    else:
        tips.append("🔥 Sarlavhaga viral format qo'shing: raqam, savol yoki 'vs'")

    # Numbers
    has_number = bool(re.search(r"\d", title))
    info["has_number"] = has_number
    if has_number:
        score += 10
    else:
        tips.append("🔢 Sarlavhaga raqam qo'shing (Top 5, 10 ta, 2024 kabi)")

    # Emoji (moderate use)
    emojis = _EMOJI_RE.findall(title)
    info["emoji_count"] = len(emojis)
    if 1 <= len(emojis) <= 3:
        score += 8
    elif len(emojis) == 0:
        tips.append("✨ 1–2 ta emoji qo'shing — e'tiborni jalb qiladi")
    else:
        tips.append("⚠️ Juda ko'p emoji — 1–3 ta qolsin")

    # Negative patterns (penalize)
    for pat in _NEGATIVE_PATTERNS:
        if re.search(pat, tl):
            score -= 5
            tips.append(f"❌ '{pat}' – overused clickbait, boshqasini tanlang")

    # Keyword front-loading (first 2 words)
    words = title.split()
    info["word_count"] = len(words)
    if words and any(pw in " ".join(words[:3]).lower() for pw in _POWER_WORDS):
        score += 5
        info["front_loaded"] = True
    else:
        info["front_loaded"] = False

    return max(0, score), info, tips


# ── Description analysis ──────────────────────────────────────────

def _analyze_description(desc: str) -> tuple[int, dict, list[str]]:
    score = 0
    info  = {}
    tips  = []

    if not desc:
        return 0, {"status": "missing"}, ["📝 Tavsif qo'shing — SEO uchun muhim"]

    ln = len(desc)
    info["length"] = ln
    if ln >= 300:
        score += 20
    elif ln >= 150:
        score += 12
        tips.append("📝 Tavsifni 300+ belgiga uzaytiring")
    else:
        score += 5
        tips.append("📝 Tavsif juda qisqa — kamida 150 belgi kiriting")

    # Hashtags in description
    hashtags = _HASHTAG_RE.findall(desc)
    info["hashtags"] = hashtags
    if 3 <= len(hashtags) <= 8:
        score += 15
    elif len(hashtags) == 0:
        tips.append("🏷 Tavsifga 3–5 hashtag qo'shing: #Shorts #Trending")
    elif len(hashtags) > 8:
        tips.append("🏷 Juda ko'p hashtag ({}), 3–8 ta optimal".format(len(hashtags)))

    # Links (channel, social)
    has_links = bool(re.search(r"https?://", desc))
    info["has_links"] = has_links
    if has_links:
        score += 5
    else:
        tips.append("🔗 Tavsifga kanal yoki ijtimoiy tarmoq havolasi qo'shing")

    # Call to action
    cta_words = ["subscribe", "like", "comment", "obuna", "like bos", "izoh"]
    has_cta = any(c in desc.lower() for c in cta_words)
    info["has_cta"] = has_cta
    if has_cta:
        score += 10
    else:
        tips.append("📢 CTA qo'shing: 'Obuna bo'ling', 'Like bosing'")

    return min(50, score), info, tips


# ── Tag analysis ──────────────────────────────────────────────────

def _analyze_tags(tags: list[str]) -> tuple[int, dict, list[str]]:
    score = 0
    info  = {}
    tips  = []

    count = len(tags)
    info["count"] = count

    if 5 <= count <= 15:
        score += 20
    elif 1 <= count < 5:
        score += 8
        tips.append(f"🏷 {count} ta tag kam — 5–15 ta optimal")
    elif count > 15:
        score += 12
        tips.append(f"🏷 {count} ta tag ko'p — 10–15 ta eng yaxshi")
    else:
        tips.append("🏷 Tag qo'shing — YouTube qidiruvida yuqori chiqish uchun")

    # Check for Shorts tag
    tags_lower = [t.lower() for t in tags]
    if "shorts" in tags_lower or "#shorts" in tags_lower:
        score += 5
    else:
        if count > 0:
            tips.append("🏷 '#Shorts' tegini qo'shing")

    # Variety check (not all tags same length)
    if count >= 3:
        lengths = [len(t) for t in tags]
        variety = max(lengths) - min(lengths)
        if variety >= 5:
            score += 5
            info["variety"] = "good"
        else:
            info["variety"] = "low"

    return min(30, score), info, tips


# ── Main calculator ───────────────────────────────────────────────

def calculate_seo_score(
    title: str,
    description: str = "",
    tags: list[str] | None = None,
) -> SEOResult:
    """
    Full SEO analysis. Returns SEOResult with score 0–100, verdict, suggestions.

    Architecture is ready for AI: replace this function body with an AI call
    and return the same SEOResult shape.
    """
    tags = tags or []

    t_score, t_info, t_tips = _analyze_title(title)
    d_score, d_info, d_tips = _analyze_description(description)
    tg_score, tg_info, tg_tips = _analyze_tags(tags)

    total = min(100, t_score + d_score + tg_score)
    all_tips = t_tips + d_tips + tg_tips

    if total >= 75:
        verdict = "🔥 AJOYIB — SEO juda yaxshi optimallashtirilgan!"
    elif total >= 55:
        verdict = "📈 YAXSHI — bir necha tuzatish bilan mukammal"
    elif total >= 35:
        verdict = "📊 O'RTA — muhim elementlar yetishmayapti"
    elif total >= 20:
        verdict = "⚠️ PAST — asosiy SEO elementlari yo'q"
    else:
        verdict = "❌ JUDA PAST — katta o'zgarishlar kerak"

    # Extract keywords found in title
    tl = title.lower()
    kws_found = [pw for pw in _POWER_WORDS if pw in tl]

    return SEOResult(
        score=total,
        verdict=verdict,
        title_analysis=t_info,
        desc_analysis=d_info,
        tag_analysis=tg_info,
        suggestions=all_tips[:8],          # top 8 suggestions
        keywords_found=kws_found[:6],
    )


def format_seo_result(result: SEOResult, title: str) -> str:
    bar_filled = round(result.score / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)

    lines = [
        f"🎯 <b>SEO Tahlil: {title[:50]}</b>\n",
        f"<code>[{bar}]</code> <b>{result.score}/100</b>",
        f"Natija: {result.verdict}\n",
    ]

    # Title details
    ti = result.title_analysis
    lines.append(f"📏 Sarlavha uzunligi: <b>{ti.get('length', 0)} belgi</b> "
                 f"({ti.get('length_status', '?')})")
    if ti.get("power_words"):
        lines.append(f"💥 Viral so'zlar: <code>{', '.join(ti['power_words'][:4])}</code>")
    if ti.get("has_number"):
        lines.append("🔢 Raqam: ✅")
    if ti.get("emoji_count"):
        lines.append(f"✨ Emoji: {ti['emoji_count']} ta")

    # Tag details
    tg = result.tag_analysis
    if tg.get("count"):
        lines.append(f"🏷 Teglar: <b>{tg['count']} ta</b>")

    # Hashtags in desc
    di = result.desc_analysis
    if di.get("hashtags"):
        ht = di["hashtags"][:4]
        lines.append(f"# Hashtag: <code>{' '.join(ht)}</code>")

    # Suggestions
    if result.suggestions:
        lines.append("\n<b>💡 Tavsiyalar:</b>")
        for tip in result.suggestions[:5]:
            lines.append(f"  • {tip}")

    return "\n".join(lines)


# ── DB persistence ────────────────────────────────────────────────

import asyncio


def _save_seo_sync(title: str, result: SEOResult, description: str, tags: list[str]) -> int:
    from telegram_bot.db.channel_models import SEORecord
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rec = SEORecord(
            title=title,
            description=description[:1000],
            tags=json.dumps(tags[:20]),
            hashtags=json.dumps(result.desc_analysis.get("hashtags", [])[:20]),
            keywords=json.dumps(result.keywords_found),
            seo_score=result.score,
            suggestions=json.dumps(result.suggestions),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec.id


async def save_seo_result(title: str, result: SEOResult, description: str = "", tags: list[str] | None = None) -> int:
    return await asyncio.to_thread(_save_seo_sync, title, result, description, tags or [])
