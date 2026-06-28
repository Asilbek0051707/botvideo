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
    waiting_for_viral_topic = State()


_ITEMS: list[tuple[str, str]] = [
    ("🔥 Trending Characters", "ta:trending_chars"),
    ("🎵 Trending Music",      "ta:trending_music"),
    ("🎮 Trending Gameplay",   "ta:trending_gameplay"),
    ("😂 Trending Memes",      "ta:trending_memes"),
    ("📈 Trending Shorts",     "ta:trending_shorts"),
    ("🌍 Country Trends",      "ta:country_trends"),
    ("📊 Viral Score",         "ta:viral_score"),
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
}

_SUB_PARENT: dict[str, str] = {
    "chars":    "ta:trending_chars",
    "music":    "ta:trending_music",
    "gameplay": "ta:trending_gameplay",
    "memes":    "ta:trending_memes",
    "shorts":   "ta:trending_shorts",
}


# ── keyboards ─────────────────────────────────────────────────────

def _ta_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
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

    results = await search_youtube(query, limit=4)
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

    results = await scrape_country_trending(code, limit=4)
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
    topic = (message.text or "").strip()
    await state.clear()

    if not topic:
        await message.answer("❌ Bo'sh mavzu. Qayta urinib ko'ring.")
        return

    score, verdict, reasons = _calc_viral_score(topic)
    bar_filled = round(score / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    reasons_text = "\n".join(f"  • {r}" for r in reasons) or "  • Asosiy tahlil"

    await message.answer(
        f"📊 <b>Viral Score: {topic}</b>\n\n"
        f"<code>[{bar}]</code> <b>{score}/100</b>\n"
        f"Natija: {verdict}\n\n"
        f"<b>Ball tahlili:</b>\n{reasons_text}",
        reply_markup=get_nav_keyboard(current="ta:viral_score", parent="menu:trend_analyzer"),
    )
