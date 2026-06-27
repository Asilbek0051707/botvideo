"""Trend Analyzer router — 📈 7-item grid with full implementations."""

from __future__ import annotations

import random
from urllib.parse import quote_plus

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
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

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}

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


def _yt_search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def _ta_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:trend_analyzer")
    return builder.as_markup()


def _url_list_keyboard(items: list[tuple[str, str]], current: str, cols: int = 2):
    builder = InlineKeyboardBuilder()
    for label, query in items:
        builder.button(text=label, url=_yt_search_url(query))
    builder.adjust(cols)
    add_nav_row(builder, current=current, parent="menu:trend_analyzer")
    return builder.as_markup()


def _country_keyboard():
    builder = InlineKeyboardBuilder()
    for flag_name, code in _COUNTRIES:
        url = f"https://www.youtube.com/feed/trending?gl={code}"
        builder.button(text=flag_name, url=url)
    builder.adjust(2)
    add_nav_row(builder, current="ta:country_trends", parent="menu:trend_analyzer")
    return builder.as_markup()


def _calc_viral_score(topic: str) -> tuple[int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    topic_lower = topic.lower()

    results = char_service.search(topic_lower, limit=3)
    if results:
        score += 30
        reasons.append("✅ Character found in database (+30)")

    if any(topic_lower in label.lower() or topic_lower in q.lower()
           for label, q in _TRENDING_CHARS):
        score += 25
        reasons.append("🔥 Matches trending character (+25)")

    if len(topic) <= 10:
        score += 10
        reasons.append("📏 Short, memorable name (+10)")
    elif len(topic) <= 20:
        score += 5
        reasons.append("📏 Good name length (+5)")

    for kw in _VIRAL_KEYWORDS:
        if kw in topic_lower:
            score += 8
            reasons.append(f"🎯 Viral keyword '{kw}' (+8)")
            break

    rng = random.randint(-7, 7)
    score += rng
    if rng > 0:
        reasons.append(f"🎲 Lucky timing (+{rng})")
    elif rng < 0:
        reasons.append(f"🎲 Tough competition ({rng})")

    score = max(5, min(95, score))

    if score >= 75:
        verdict = "🔥 HIGH — go for it!"
    elif score >= 50:
        verdict = "📈 MEDIUM — add a trending twist"
    elif score >= 30:
        verdict = "⚠️ LOW — needs viral hooks"
    else:
        verdict = "❌ VERY LOW — try a different topic"

    return score, verdict, reasons


# ── main grid ─────────────────────────────────────────────────────


@router.callback_query(F.data == "menu:trend_analyzer")
async def on_trend_analyzer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Trend Analyzer</b>\n\nChoose an analysis type:",
        reply_markup=_ta_keyboard(),
    )
    await callback.answer()


# ── individual items ──────────────────────────────────────────────


@router.callback_query(F.data == "ta:trending_chars")
async def on_trending_chars(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔥 <b>Trending Characters</b>\n\n"
        "Top characters on YouTube Shorts right now.\n"
        "Tap any button to search on YouTube:",
        reply_markup=_url_list_keyboard(_TRENDING_CHARS, "ta:trending_chars"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_music")
async def on_trending_music(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎵 <b>Trending Music</b>\n\n"
        "Popular music categories for YouTube Shorts:",
        reply_markup=_url_list_keyboard(_MUSIC_GENRES, "ta:trending_music"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_gameplay")
async def on_trending_gameplay(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎮 <b>Trending Gameplay</b>\n\n"
        "Top trending games on YouTube Shorts:",
        reply_markup=_url_list_keyboard(_GAMES, "ta:trending_gameplay"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_memes")
async def on_trending_memes(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "😂 <b>Trending Memes</b>\n\n"
        "Hottest meme trends on YouTube right now:",
        reply_markup=_url_list_keyboard(_MEMES, "ta:trending_memes"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:trending_shorts")
async def on_trending_shorts(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Trending Shorts</b>\n\n"
        "Top YouTube Shorts categories this week:",
        reply_markup=_url_list_keyboard(_SHORTS_CATS, "ta:trending_shorts"),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:country_trends")
async def on_country_trends(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🌍 <b>Country Trends</b>\n\n"
        "Select a country — opens YouTube Trending for that region:",
        reply_markup=_country_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "ta:viral_score")
async def on_viral_score(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TrendStates.waiting_for_viral_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Viral Score Calculator</b>\n\n"
        "Type your video topic, character name, or idea:"
    )
    await callback.answer()


@router.message(TrendStates.waiting_for_viral_topic)
async def on_viral_topic(message: Message, state: FSMContext) -> None:
    topic = (message.text or "").strip()
    await state.clear()

    if not topic:
        await message.answer("❌ Empty topic. Tap Viral Score to try again.")
        return

    score, verdict, reasons = _calc_viral_score(topic)
    bar_filled = round(score / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    reasons_text = "\n".join(f"  • {r}" for r in reasons) or "  • Basic analysis"

    await message.answer(
        f"📊 <b>Viral Score: {topic}</b>\n\n"
        f"<code>[{bar}]</code> <b>{score}/100</b>\n"
        f"Verdict: {verdict}\n\n"
        f"<b>Score breakdown:</b>\n{reasons_text}",
        reply_markup=get_nav_keyboard(current="ta:viral_score", parent="menu:trend_analyzer"),
    )
