"""Trend Analyzer — all results shown inside the bot via yt-dlp + thumbnails."""

from __future__ import annotations

import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile, CallbackQuery, InlineKeyboardButton, InputMediaPhoto, Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.services.character_service import char_service

router = Router(name="trend_analyzer")


class TrendStates(StatesGroup):
    waiting_for_viral_topic  = State()
    waiting_for_opps_topic   = State()


_ITEMS: list[tuple[str, str]] = [
    # Row 1 — Characters & Music
    ("🔥 Trending Characters",  "ta:trending_chars"),
    ("🎵 Trending Music",        "ta:trending_music"),
    # Row 2 — Games & Movies
    ("🎮 Trending Games",        "ta:trending_gameplay"),
    ("🎬 Trending Movies",       "ta:trending_movies"),
    # Row 3 — Cartoons & Memes
    ("📺 Trending Cartoons",     "ta:trending_cartoons"),
    ("😂 Trending Memes",        "ta:trending_memes"),
    # Row 4 — Shorts & Country
    ("📱 Trending Shorts",       "ta:trending_shorts"),
    ("🌍 Country Trends",        "ta:country_trends"),
    # Row 5 — Rising & Viral
    ("📈 Rising Trends",         "ta:rising_trends"),
    ("⭐ Viral Opportunities",   "ta:viral_opps"),
    # Row 6 — Keywords & Content
    ("🏷 Trending Keywords",     "ta:trend_keywords"),
    ("🎯 Content Opportunities", "ta:content_opps"),
    # Row 7 — Time-based
    ("📅 Daily Trends",          "ta:daily_trends"),
    ("📆 Weekly Trends",         "ta:weekly_trends"),
    ("🗓 Monthly Trends",        "ta:monthly_trends"),
]

_TRENDING_CHARS: list[tuple[str, str]] = [
    ("🕷 Spider-Man",    "Spider-Man shorts 2024"),
    ("🦇 Batman",        "Batman cartoon shorts"),
    ("🦸 Goku",          "Goku Dragon Ball shorts"),
    ("🐢 TMNT",          "Ninja Turtles shorts 2024"),
    ("🎮 Steve",         "Minecraft Steve character"),
    ("🦊 Sonic",         "Sonic the Hedgehog shorts"),
    ("🐾 Chase",         "PAW Patrol Chase shorts"),
    ("🐟 Bluey",         "Bluey cartoon shorts"),
    ("👾 Skibidi",       "Skibidi Toilet shorts"),
    ("🎪 Huggy",         "Huggy Wuggy Poppy Playtime"),
    ("⚡ Pikachu",       "Pikachu Pokemon shorts 2024"),
    ("🤖 Optimus",       "Optimus Prime Transformers shorts"),
]

_MUSIC_GENRES: list[tuple[str, str]] = [
    ("🎵 Kids Songs",    "kids songs trending YouTube 2024"),
    ("🎮 Gaming Music",  "gaming background music trending"),
    ("🎪 Cartoon OST",   "cartoon theme songs trending"),
    ("🔥 Viral Beats",   "viral music shorts 2024"),
    ("🎸 Rock Kids",     "kids rock songs trending YouTube"),
    ("🎹 Lo-Fi Kids",    "lofi music kids videos trending"),
]

_GAMES: list[tuple[str, str]] = [
    ("🎮 Minecraft",     "Minecraft gameplay trending shorts"),
    ("🔫 Roblox",        "Roblox gameplay trending 2024"),
    ("🃏 Among Us",      "Among Us animation shorts"),
    ("🏎 Fall Guys",     "Fall Guys funny moments shorts"),
    ("⚔ Fortnite",      "Fortnite shorts trending 2024"),
    ("🐉 Brawl Stars",   "Brawl Stars gameplay shorts"),
    ("🌍 GTA",           "GTA funny moments shorts"),
    ("🎯 Stumble Guys",  "Stumble Guys trending shorts"),
]

_MEMES: list[tuple[str, str]] = [
    ("😂 Skibidi",       "Skibidi meme shorts 2024"),
    ("🤡 NPC Trend",     "NPC trend YouTube shorts"),
    ("👀 Sigma Rule",    "Sigma rule meme shorts"),
    ("🧃 Ohio",          "Only in Ohio meme compilation"),
    ("🫵 Brain Rot",     "brain rot meme compilation 2024"),
    ("🐸 GigaChad",      "GigaChad meme music shorts"),
    ("💀 Coffin Dance",  "coffin dance meme 2024"),
    ("🔥 Rizz Trend",    "rizz meme shorts 2024"),
]

_SHORTS_CATS: list[tuple[str, str]] = [
    ("🎨 Art Shorts",    "art animation shorts trending"),
    ("🤸 Challenge",     "challenge trending YouTube shorts"),
    ("🎭 Skit Comedy",   "funny skit shorts trending"),
    ("🐾 Animals",       "funny animals shorts viral"),
    ("🏋 Fitness",       "fitness motivation shorts 2024"),
    ("🍕 Food Hacks",    "food hacks shorts trending"),
    ("🧪 Science",       "science experiment shorts kids"),
    ("😎 Life Hacks",    "life hacks trending shorts 2024"),
]

_MOVIES: list[tuple[str, str]] = [
    ("🦁 The Wild Robot",      "The Wild Robot movie animation shorts 2024"),
    ("🐠 Moana 2",             "Moana 2 movie animation shorts"),
    ("🤠 Despicable Me 4",     "Despicable Me 4 Minions animation shorts"),
    ("🐼 Kung Fu Panda 4",     "Kung Fu Panda 4 animation shorts 2024"),
    ("🐈 Puss in Boots 2",     "Puss in Boots Last Wish animation"),
    ("❄ Frozen 3",             "Frozen 3 Elsa Anna movie shorts"),
    ("🫧 Inside Out 2",        "Inside Out 2 Pixar animation shorts"),
    ("🧠 Migration",           "Migration movie ducks animation 2024"),
    ("🧜 The Little Mermaid",  "Little Mermaid live action movie"),
    ("🤖 Elemental",           "Elemental Pixar fire water animation"),
    ("⭐ Wish",                "Wish Disney animation movie shorts"),
    ("🎪 Trolls 3",            "Trolls Band Together movie shorts"),
]

_CARTOONS: list[tuple[str, str]] = [
    ("🐶 PAW Patrol",         "PAW Patrol cartoon shorts trending"),
    ("🔵 Bluey",              "Bluey cartoon shorts trending 2024"),
    ("🕷 Spider-Man",         "Spider-Man animated series shorts"),
    ("🦸 Avengers Assemble",  "Avengers cartoon animated shorts"),
    ("🐢 TMNT",               "Teenage Mutant Ninja Turtles shorts"),
    ("🌈 Rainbow Friends",    "Rainbow Friends Roblox cartoon shorts"),
    ("🎪 Amazing Circus",     "Amazing Digital Circus animation shorts"),
    ("🐻 Grizzy Bears",       "Grizzy and the Lemmings cartoon"),
    ("🐣 Peppa Pig",          "Peppa Pig cartoon shorts kids"),
    ("🦋 Miraculous",         "Miraculous Ladybug cartoon shorts"),
    ("🤖 Transformers",       "Transformers animated shorts 2024"),
    ("⚡ Teen Titans",        "Teen Titans Go cartoon shorts"),
]

_RISING: list[tuple[str, str]] = [
    ("🚀 Rising This Week",   "rising viral trend this week youtube shorts 2024"),
    ("🆕 New Viral Chars",    "new character trending viral shorts 2024"),
    ("📈 Fast Growing",       "fast growing viral youtube channel shorts"),
    ("💥 Breakout Content",   "breakout viral content youtube shorts 2024"),
    ("🌟 Underrated Gems",    "underrated viral youtube shorts trending"),
    ("🎯 Niche Trending",     "niche trending youtube shorts 2024"),
]

_COUNTRIES: list[tuple[str, str]] = [
    ("🇺🇸 USA",           "US"),
    ("🇬🇧 UK",            "GB"),
    ("🇩🇪 Germany",       "DE"),
    ("🇯🇵 Japan",         "JP"),
    ("🇰🇷 Korea",         "KR"),
    ("🇮🇳 India",         "IN"),
    ("🇧🇷 Brazil",        "BR"),
    ("🇷🇺 Russia",        "RU"),
    ("🇺🇿 O'zbekiston",   "UZ"),
    ("🇹🇷 Türkiye",       "TR"),
    ("🇸🇦 Saudi Arabia",  "SA"),
    ("🇫🇷 France",        "FR"),
    ("🇪🇸 Spain",         "ES"),
    ("🇲🇽 Mexico",        "MX"),
    ("🇵🇭 Philippines",   "PH"),
    ("🇵🇰 Pakistan",      "PK"),
]

_VIRAL_KEYWORDS = [
    "vs", "evolution", "all characters", "funny", "challenge",
    "transformation", "baby", "minecraft", "roblox", "shorts",
    "animation", "compilation", "trending", "viral", "epic",
]

_SUB_MAP: dict[str, list[tuple[str, str]]] = {
    "chars":    _TRENDING_CHARS,
    "music":    _MUSIC_GENRES,
    "gameplay": _GAMES,
    "memes":    _MEMES,
    "shorts":   _SHORTS_CATS,
    "movies":   _MOVIES,
    "cartoons": _CARTOONS,
    "rising":   _RISING,
}

_SUB_PARENT: dict[str, str] = {
    "chars":    "ta:trending_chars",
    "music":    "ta:trending_music",
    "gameplay": "ta:trending_gameplay",
    "memes":    "ta:trending_memes",
    "shorts":   "ta:trending_shorts",
    "movies":   "ta:trending_movies",
    "cartoons": "ta:trending_cartoons",
    "rising":   "ta:rising_trends",
}


# ── keyboards ─────────────────────────────────────────────────────

def _ta_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    # 15 items → 2 per row (last row has 1)
    builder.adjust(2, 2, 2, 2, 2, 2, 2, 1)
    add_nav_row(builder, current="menu:trend_analyzer")
    return builder.as_markup()


def _sub_keyboard(items: list[tuple[str, str]], sub_key: str, current: str):
    """Category sub-buttons — callback triggers in-bot search."""
    builder = InlineKeyboardBuilder()
    for i, (label, _) in enumerate(items):
        builder.button(text=label, callback_data=f"ta_sub:{sub_key}:{i}")
    builder.adjust(2)
    add_nav_row(builder, current=current, parent="menu:trend_analyzer")
    return builder.as_markup()


def _country_keyboard():
    builder = InlineKeyboardBuilder()
    for flag_name, code in _COUNTRIES:
        builder.button(text=flag_name, callback_data=f"ta_country:{code}")
    builder.adjust(2)
    add_nav_row(builder, current="ta:country_trends", parent="menu:trend_analyzer")
    return builder.as_markup()


def _calc_viral_score(topic: str) -> tuple[int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    topic_lower = topic.lower()

    if char_service.search(topic_lower, limit=1):
        score += 30
        reasons.append("✅ Bazada mavjud karakter (+30)")

    if any(
        topic_lower in label.lower() or topic_lower in q.lower()
        for label, q in _TRENDING_CHARS
    ):
        score += 25
        reasons.append("🔥 Trending karakter mos keldi (+25)")

    if len(topic) <= 10:
        score += 10
        reasons.append("📏 Qisqa, yodda qoladigan nom (+10)")
    elif len(topic) <= 20:
        score += 5
        reasons.append("📏 Yaxshi nom uzunligi (+5)")

    for kw in _VIRAL_KEYWORDS:
        if kw in topic_lower:
            score += 8
            reasons.append(f"🎯 Viral kalit so'z '{kw}' (+8)")
            break

    rng = random.randint(-7, 7)
    score += rng
    if rng > 0:
        reasons.append(f"🎲 Omadli vaqt (+{rng})")
    elif rng < 0:
        reasons.append(f"🎲 Raqobat qattiq ({rng})")

    score = max(5, min(95, score))
    if score >= 75:
        verdict = "🔥 YUQORI — olg'a!"
    elif score >= 50:
        verdict = "📈 O'RTA — trending hook qo'shing"
    elif score >= 30:
        verdict = "⚠️ PAST — viral element kerak"
    else:
        verdict = "❌ JUDA PAST — mavzuni o'zgartiring"

    return score, verdict, reasons


# ── shared helper — send yt thumbnails as album ───────────────────

async def _send_yt_results(
    callback: CallbackQuery,
    results: list,
    title: str,
    back_cb: str,
) -> None:
    from telegram_bot.services.real_search import download_yt_thumbnails

    if not results:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{title}\n\n❌ Natija topilmadi. Keyinroq urinib ko'ring.",
            reply_markup=get_nav_keyboard(back_cb, "menu:trend_analyzer"),
        )
        return

    photos = await download_yt_thumbnails(results, limit=4)
    if not photos:
        # Fall back to text list
        lines = [f"{title}\n"]
        for i, r in enumerate(results[:4], 1):
            lines.append(f"{i}. <b>{r.title}</b> {r.extra}")
        builder = InlineKeyboardBuilder()
        for i, r in enumerate(results[:4], 1):
            builder.button(text=f"▶️ {i}. Ko'rish", url=r.url)
        builder.adjust(2)
        builder.row(InlineKeyboardButton(text="⬅ Orqaga", callback_data=back_cb))
        await callback.message.edit_text(  # type: ignore[union-attr]
            "\n".join(lines), reply_markup=builder.as_markup()
        )
        return

    media = []
    for i, (data, r) in enumerate(photos):
        cap = f"<b>{r.title}</b>\n{r.extra}" if i == 0 else f"<b>{r.title}</b>"
        media.append(InputMediaPhoto(
            media=BufferedInputFile(data, filename=f"thumb_{i}.jpg"),
            caption=cap,
            parse_mode="HTML",
        ))
    await callback.message.answer_media_group(media)  # type: ignore[union-attr]

    builder = InlineKeyboardBuilder()
    for i, (_, r) in enumerate(photos, 1):
        builder.button(text=f"▶️ {i}. Ko'rish", url=r.url)
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅ Orqaga", callback_data=back_cb))

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{title} — <b>{len(photos)}</b> ta top video:",
        reply_markup=builder.as_markup(),
    )


# ── main grid ─────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:trend_analyzer")
async def on_trend_analyzer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Trend Analyzer</b>\n\nTahlil turini tanlang:",
        reply_markup=_ta_keyboard(),
    )
    await callback.answer()


# ── category grids (sub-item buttons → in-bot search) ────────────

@router.callback_query(F.data == "ta:trending_chars")
async def on_trending_chars(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔥 <b>Trending Characters</b>\n\nKarakter tanlang — bot YouTube'dan topib beradi:",
        reply_markup=_sub_keyboard(_TRENDING_CHARS, "chars", "ta:trending_chars"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_music")
async def on_trending_music(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎵 <b>Trending Music</b>\n\nMusiqa janrini tanlang:",
        reply_markup=_sub_keyboard(_MUSIC_GENRES, "music", "ta:trending_music"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_gameplay")
async def on_trending_gameplay(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎮 <b>Trending Gameplay</b>\n\nO'yinni tanlang:",
        reply_markup=_sub_keyboard(_GAMES, "gameplay", "ta:trending_gameplay"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_memes")
async def on_trending_memes(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "😂 <b>Trending Memes</b>\n\nMeme turini tanlang:",
        reply_markup=_sub_keyboard(_MEMES, "memes", "ta:trending_memes"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_shorts")
async def on_trending_shorts(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Trending Shorts</b>\n\nKategoriya tanlang:",
        reply_markup=_sub_keyboard(_SHORTS_CATS, "shorts", "ta:trending_shorts"),
    )
    await callback.answer()


# ── sub-item selected → search YouTube → show thumbnails ──────────

@router.callback_query(F.data.startswith("ta_sub:"))
async def on_trend_sub(callback: CallbackQuery) -> None:
    from telegram_bot.services.real_search import search_youtube

    parts = callback.data.split(":", 2)  # ta_sub:chars:0
    if len(parts) < 3:
        await callback.answer()
        return

    sub_key = parts[1]
    try:
        idx = int(parts[2])
    except ValueError:
        await callback.answer()
        return

    items = _SUB_MAP.get(sub_key, [])
    if idx >= len(items):
        await callback.answer("Topilmadi")
        return

    label, query = items[idx]
    back_cb = _SUB_PARENT.get(sub_key, "menu:trend_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n🔍 YouTube'dan qidirilmoqda..."
    )
    await callback.answer()

    uid = callback.from_user.id if callback.from_user else 0
    results = await search_youtube(query, limit=4, user_id=uid)
    await _send_yt_results(callback, results, label, back_cb)


# ── country trends ────────────────────────────────────────────────

@router.callback_query(F.data == "ta:country_trends")
async def on_country_trends(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🌍 <b>Country Trends</b>\n\nMamlakatni tanlang — bot YouTube trending'ni yuklab beradi:",
        reply_markup=_country_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ta_country:"))
async def on_country_select(callback: CallbackQuery) -> None:
    from telegram_bot.services.real_search import scrape_country_trending

    code = callback.data.split(":", 1)[1]
    flag_name = next((f for f, c in _COUNTRIES if c == code), code)

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🌍 {flag_name}\n\n📥 YouTube trending yuklanmoqda..."
    )
    await callback.answer()

    from telegram_bot.services.real_search import _user_pick
    uid = callback.from_user.id if callback.from_user else 0
    results = await scrape_country_trending(code, limit=4)
    results = _user_pick(results, uid, 4)
    await _send_yt_results(callback, results, f"🌍 {flag_name} Trending", "ta:country_trends")


# ── viral score ───────────────────────────────────────────────────

@router.callback_query(F.data == "ta:viral_score")
async def on_viral_score(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TrendStates.waiting_for_viral_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Viral Score Calculator</b>\n\n"
        "Video mavzusi, karakter nomi yoki g'oyangizni yozing:"
    )
    await callback.answer()


@router.message(TrendStates.waiting_for_viral_topic)
async def on_viral_topic(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.viral_score import calculate as vs_calc

    topic = (message.text or "").strip()
    await state.clear()

    if not topic:
        await message.answer("❌ Bo'sh mavzu. Qayta urinib ko'ring.")
        return

    score, verdict, reasons = vs_calc(topic)
    bar_filled = round(score / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    reasons_text = "\n".join(f"  • {r}" for r in reasons) or "  • Asosiy tahlil"

    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 G'oyalar yaratish", callback_data="ta:video_ideas")
    builder.button(text="⬅ Orqaga",             callback_data="menu:trend_analyzer")
    builder.adjust(2)

    await message.answer(
        f"📊 <b>Viral Score: {topic}</b>\n\n"
        f"<code>[{bar}]</code> <b>{score}/100</b>\n"
        f"Natija: {verdict}\n\n"
        f"<b>Ball tahlili:</b>\n{reasons_text}",
        reply_markup=builder.as_markup(),
    )


# ── NEW: Trending Movies ───────────────────────────────────────────

@router.callback_query(F.data == "ta:trending_movies")
async def on_trending_movies(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Trending Movies</b>\n\nFilm tanlang — bot YouTube'dan toping:",
        reply_markup=_sub_keyboard(_MOVIES, "movies", "ta:trending_movies"),
    )
    await callback.answer()


# ── NEW: Trending Cartoons ────────────────────────────────────────

@router.callback_query(F.data == "ta:trending_cartoons")
async def on_trending_cartoons(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📺 <b>Trending Cartoons</b>\n\nMultfilm tanlang:",
        reply_markup=_sub_keyboard(_CARTOONS, "cartoons", "ta:trending_cartoons"),
    )
    await callback.answer()


# ── NEW: Rising Trends ────────────────────────────────────────────

@router.callback_query(F.data == "ta:rising_trends")
async def on_rising_trends(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Rising Trends</b>\n\nO'sib kelayotgan trendni tanlang:",
        reply_markup=_sub_keyboard(_RISING, "rising", "ta:rising_trends"),
    )
    await callback.answer()


# ── NEW: Viral Opportunities ──────────────────────────────────────

@router.callback_query(F.data == "ta:viral_opps")
async def on_viral_opps(callback: CallbackQuery, state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Viral Score hisoblash",   callback_data="ta:viral_score")
    builder.button(text="🎯 Video g'oyalar yaratish",  callback_data="ta:video_ideas")
    builder.button(text="🔥 Trending Characters",       callback_data="ta:trending_chars")
    builder.button(text="🎬 Trending Movies",           callback_data="ta:trending_movies")
    builder.button(text="📅 Bugungi Trendlar",          callback_data="ta:daily_trends")
    builder.adjust(1, 2, 2)
    add_nav_row(builder, current="ta:viral_opps", parent="menu:trend_analyzer")

    # Quick opportunity list
    opportunities = [
        "🔥 <b>Spider-Man + Minecraft</b> — ayni paytda viral (Score: ~85)",
        "📈 <b>Baby + [Karakter]</b> — bolalar auditoriyasi uchun yuqori CTR",
        "🎬 <b>Inside Out 2 + Emojis</b> — film trend bo'lmoqda",
        "😂 <b>Skibidi Toilet Evolution</b> — meme format hali kuchli",
        "🌟 <b>[Karakter] vs [Karakter]</b> — doim ishlaydi, qisqa format",
    ]
    text = (
        "⭐ <b>Viral Opportunities</b>\n\n"
        "Hozir eng yuqori potentsial g'oyalar:\n\n"
        + "\n".join(opportunities)
        + "\n\n💡 <i>Viral Score hisoblash uchun mavzuingizni kiriting</i>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── NEW: Content Opportunities ────────────────────────────────────

@router.callback_query(F.data == "ta:content_opps")
async def on_content_opps(callback: CallbackQuery) -> None:
    from telegram_bot.services.recommendation_service import get_category_list

    cats = get_category_list()
    builder = InlineKeyboardBuilder()
    for cat_id, cat_label in cats:
        builder.button(text=cat_label, callback_data=f"ta_rec:{cat_id}")
    builder.adjust(2)
    add_nav_row(builder, current="ta:content_opps", parent="menu:trend_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎯 <b>Content Opportunities</b>\n\n"
        "Kontent kategoriyasini tanlang —\n"
        "bot eng yaxshi strategiyani tavsiya qiladi:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ta_rec:"))
async def on_rec_category(callback: CallbackQuery) -> None:
    from telegram_bot.services.recommendation_service import get_recommendations

    cat_id = callback.data.split(":", 1)[1]
    recs = get_recommendations(cat_id)

    lines = [f"🎯 <b>Content Strategy — {cat_id.title()}</b>\n"]
    for rec in recs:
        lines.append(f"{rec.label}\n<code>{rec.value}</code>\n💡 {rec.reason}")

    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 G'oyalar yaratish", callback_data="ta:video_ideas")
    builder.button(text="⬅ Kategoriyalar",      callback_data="ta:content_opps")
    builder.adjust(2)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n\n".join(lines), reply_markup=builder.as_markup()
    )
    await callback.answer()


# ── NEW: Daily Trends ─────────────────────────────────────────────

@router.callback_query(F.data == "ta:daily_trends")
async def on_daily_trends(callback: CallbackQuery) -> None:
    from telegram_bot.services.real_search import search_youtube

    await callback.message.edit_text(  # type: ignore[union-attr]
        "📅 <b>Daily Trends</b>\n\n🔍 Bugungi YouTube trendlar yuklanmoqda..."
    )
    await callback.answer()

    uid = callback.from_user.id if callback.from_user else 0
    results = await search_youtube("trending today viral shorts 2024", limit=4, user_id=uid)
    await _send_yt_results(callback, results, "📅 Daily Trends — Bugun", "ta:daily_trends")


# ── NEW: Weekly Trends ────────────────────────────────────────────

@router.callback_query(F.data == "ta:weekly_trends")
async def on_weekly_trends(callback: CallbackQuery) -> None:
    from telegram_bot.services.real_search import search_youtube

    await callback.message.edit_text(  # type: ignore[union-attr]
        "📆 <b>Weekly Trends</b>\n\n🔍 Bu haftaning YouTube trendlari yuklanmoqda..."
    )
    await callback.answer()

    uid = callback.from_user.id if callback.from_user else 0
    results = await search_youtube("viral this week trending youtube shorts 2024", limit=4, user_id=uid)
    await _send_yt_results(callback, results, "📆 Weekly Trends — Bu Hafta", "ta:weekly_trends")


# ── NEW: Monthly Trends ───────────────────────────────────────────

@router.callback_query(F.data == "ta:monthly_trends")
async def on_monthly_trends(callback: CallbackQuery) -> None:
    from telegram_bot.services.real_search import search_youtube

    await callback.message.edit_text(  # type: ignore[union-attr]
        "🗓 <b>Monthly Trends</b>\n\n🔍 Bu oyning YouTube trendlari yuklanmoqda..."
    )
    await callback.answer()

    uid = callback.from_user.id if callback.from_user else 0
    results = await search_youtube("best viral videos this month 2024 youtube shorts", limit=4, user_id=uid)
    await _send_yt_results(callback, results, "🗓 Monthly Trends — Bu Oy", "ta:monthly_trends")


