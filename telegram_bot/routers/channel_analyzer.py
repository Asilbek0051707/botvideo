"""Channel Analyzer router — 📊 6-item grid with useful tools."""

from __future__ import annotations

from urllib.parse import quote_plus

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="channel_analyzer")


class ChannelStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_video = State()
    waiting_for_niche = State()


_ITEMS: list[tuple[str, str]] = [
    ("🔗 Analyze Channel",   "ca:channel"),
    ("🎥 Analyze Video",     "ca:video"),
    ("🖼 Analyze Thumbnail", "ca:thumbnail"),
    ("🏆 Competitors",       "ca:competitors"),
    ("📈 Growth Prediction", "ca:growth"),
    ("📊 Statistics",        "ca:statistics"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}

_STATS_TOOLS: list[tuple[str, str]] = [
    ("📊 SocialBlade",       "https://socialblade.com/youtube/"),
    ("🔍 Noxinfluencer",     "https://www.noxinfluencer.com/youtube/"),
    ("🎯 vidIQ Extension",   "https://vidiq.com/"),
    ("🔧 TubeBuddy",         "https://www.tubebuddy.com/"),
    ("📈 YouTube Studio",    "https://studio.youtube.com/"),
    ("📉 Google Trends",     "https://trends.google.com/trends/?geo=US&q=youtube"),
]

_THUMBNAIL_TOOLS: list[tuple[str, str]] = [
    ("🎨 Canva Thumbnail",   "https://www.canva.com/create/youtube-thumbnails/"),
    ("🖼 Adobe Express",     "https://www.adobe.com/express/create/thumbnail/youtube"),
    ("🔍 Thumbnail Test",    "https://www.thumbnailtest.com/"),
    ("🤖 Midjourney",        "https://www.midjourney.com/"),
    ("🎭 Fotor",             "https://www.fotor.com/features/youtube-thumbnail-maker/"),
]

_GROWTH_TIPS = [
    "📅 Upload consistently — 3–5 Shorts per week minimum",
    "🎯 Niche down — 1 topic = faster algorithm pick-up",
    "🔥 Hook in first 2 seconds — no slow intros",
    "🏷 Use 3–5 hashtags: #Shorts + 2 niche + 1 trending",
    "🖼 A/B test thumbnails — change thumbnail if CTR < 4%",
    "💬 Reply to every comment in first 24h — boosts algo",
    "🔄 Repurpose: long video → 5–10 Shorts clips",
    "📊 Post when your audience is online (check YouTube Analytics)",
    "🤝 Collaborate with channels in same niche",
    "📈 End screen + pinned comment = +30% watch time",
]


def _ca_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:channel_analyzer")
    return builder.as_markup()


def _url_buttons_keyboard(items: list[tuple[str, str]], current: str):
    builder = InlineKeyboardBuilder()
    for label, url in items:
        builder.button(text=label, url=url)
    builder.adjust(1)
    add_nav_row(builder, current=current, parent="menu:channel_analyzer")
    return builder.as_markup()


@router.callback_query(F.data == "menu:channel_analyzer")
async def on_channel_analyzer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Channel Analyzer</b>\n\nChoose an analysis:",
        reply_markup=_ca_keyboard(),
    )
    await callback.answer()


# ── Analyze Channel ───────────────────────────────────────────────


@router.callback_query(F.data == "ca:channel")
async def on_channel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_channel)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔗 <b>Analyze Channel</b>\n\n"
        "Enter the YouTube channel @username or URL:"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_channel)
async def on_channel_input(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip().lstrip("@")
    await state.clear()

    if not raw:
        await message.answer("❌ Empty input. Tap Analyze Channel to try again.")
        return

    encoded = quote_plus(raw)
    yt_channel_url = (
        raw if raw.startswith("http")
        else f"https://www.youtube.com/@{raw}"
    )
    sb_url = f"https://socialblade.com/youtube/user/{encoded}"
    nox_url = f"https://www.noxinfluencer.com/youtube/channel/{encoded}"

    builder = InlineKeyboardBuilder()
    builder.button(text="📺 Open Channel",     url=yt_channel_url)
    builder.button(text="📊 SocialBlade",      url=sb_url)
    builder.button(text="🔍 Noxinfluencer",    url=nox_url)
    builder.button(text="🎯 vidIQ",            url="https://vidiq.com/")
    builder.adjust(1)
    add_nav_row(builder, current="ca:channel", parent="menu:channel_analyzer")

    await message.answer(
        f"🔗 <b>Channel: {raw}</b>\n\n"
        "Open these tools to see full analytics:",
        reply_markup=builder.as_markup(),
    )


# ── Analyze Video ─────────────────────────────────────────────────


@router.callback_query(F.data == "ca:video")
async def on_video(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_video)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎥 <b>Analyze Video</b>\n\n"
        "Paste the YouTube video URL:"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_video)
async def on_video_input(message: Message, state: FSMContext) -> None:
    url = (message.text or "").strip()
    await state.clear()

    if not url:
        await message.answer("❌ Empty URL. Tap Analyze Video to try again.")
        return

    # Extract video ID for tool links
    vid_id = ""
    if "v=" in url:
        vid_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        vid_id = url.split("youtu.be/")[1].split("?")[0]

    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Open Video",         url=url if url.startswith("http") else f"https://youtu.be/{url}")
    if vid_id:
        builder.button(text="🔍 vidIQ Analysis", url=f"https://vidiq.com/youtube-tools/video-scorecard/?v={vid_id}")
    builder.button(text="🔧 TubeBuddy",          url="https://www.tubebuddy.com/")
    builder.button(text="📈 YouTube Studio",      url="https://studio.youtube.com/")
    builder.adjust(1)
    add_nav_row(builder, current="ca:video", parent="menu:channel_analyzer")

    await message.answer(
        "🎥 <b>Video Analysis Tools</b>\n\n"
        "Open these tools to analyze the video:",
        reply_markup=builder.as_markup(),
    )


# ── Thumbnail Analyzer ────────────────────────────────────────────


@router.callback_query(F.data == "ca:thumbnail")
async def on_thumbnail(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🖼 <b>Thumbnail Analyzer</b>\n\n"
        "<b>Best practices:</b>\n"
        "• 1280×720px (16:9 ratio)\n"
        "• Max 2 MB file size\n"
        "• Big bold text (max 6 words)\n"
        "• High contrast colors\n"
        "• Face with expression (CTR +38%)\n"
        "• No text in corners (cropped on mobile)\n\n"
        "Design tools:",
        reply_markup=_url_buttons_keyboard(_THUMBNAIL_TOOLS, "ca:thumbnail"),
    )
    await callback.answer()


# ── Competitors ───────────────────────────────────────────────────


@router.callback_query(F.data == "ca:competitors")
async def on_competitors(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_niche)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🏆 <b>Competitor Research</b>\n\n"
        "Enter your channel niche or topic\n"
        "(e.g. <i>Minecraft kids, Spider-Man animation</i>):"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_niche)
async def on_niche_input(message: Message, state: FSMContext) -> None:
    niche = (message.text or "").strip()
    await state.clear()

    if not niche:
        await message.answer("❌ Empty input. Tap Competitors to try again.")
        return

    encoded = quote_plus(niche)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔍 YouTube Search",
        url=f"https://www.youtube.com/results?search_query={encoded}&sp=CAM%253D"
    )
    builder.button(
        text="📊 Top Channels",
        url=f"https://www.youtube.com/results?search_query={encoded}+channel&sp=CAM%253D"
    )
    builder.button(
        text="🌐 Noxinfluencer Search",
        url=f"https://www.noxinfluencer.com/youtube/search?keyword={encoded}"
    )
    builder.adjust(1)
    add_nav_row(builder, current="ca:competitors", parent="menu:channel_analyzer")

    await message.answer(
        f"🏆 <b>Competitors: {niche}</b>\n\n"
        "Find top channels in your niche:",
        reply_markup=builder.as_markup(),
    )


# ── Growth Prediction ─────────────────────────────────────────────


@router.callback_query(F.data == "ca:growth")
async def on_growth(callback: CallbackQuery) -> None:
    tips_text = "\n".join(f"{i+1}. {tip}" for i, tip in enumerate(_GROWTH_TIPS))
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📈 YouTube Creator Academy",
        url="https://creatoracademy.youtube.com/"
    )
    builder.button(
        text="📊 Think with Google",
        url="https://www.thinkwithgoogle.com/marketing-strategies/video/youtube-shorts/"
    )
    builder.adjust(1)
    add_nav_row(builder, current="ca:growth", parent="menu:channel_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>Growth Prediction Tips</b>\n\n"
        f"{tips_text}",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ── Statistics ────────────────────────────────────────────────────


@router.callback_query(F.data == "ca:statistics")
async def on_statistics(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Channel Statistics Tools</b>\n\n"
        "Professional tools to track your YouTube stats:",
        reply_markup=_url_buttons_keyboard(_STATS_TOOLS, "ca:statistics"),
    )
    await callback.answer()
