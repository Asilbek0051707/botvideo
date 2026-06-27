"""Channel Analyzer — in-bot analytics via yt-dlp (no API key needed)."""

from __future__ import annotations

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
    ("🔗 Kanal Tahlili",     "ca:channel"),
    ("🎥 Video Tahlili",     "ca:video"),
    ("🖼 Thumbnail Qoidasi", "ca:thumbnail"),
    ("🏆 Raqiblar",          "ca:competitors"),
    ("📈 O'sish Maslahat",   "ca:growth"),
    ("📊 Stats Asboblar",    "ca:statistics"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}

_GROWTH_TIPS = [
    "📅 Haftada 3–5 Shorts yuklang — muntazamlik asosiy",
    "🎯 Bitta mavzuga yopishing — algoritm tezroq taniydi",
    "🔥 Dastlabki 2 soniyada hook bo'lsin — sekin boshlash yo'q",
    "🏷 3–5 hashtag: #Shorts + 2 niche + 1 trending",
    "🖼 CTR 4% dan past bo'lsa thumbnail'ni almashtiring",
    "💬 Dastlabki 24 soatda har bir izohga javob bering",
    "🔄 Uzun video → 5–10 ta Shorts klip qiling",
    "📊 Auditoriyangiz onlayn bo'lgan vaqtda yuklang",
    "🤝 O'zingiz bilan bir niche'dagi kanallar bilan hamkorlik",
    "📈 End screen + pinned comment = +30% ko'rish vaqti",
]


def _ca_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:channel_analyzer")
    return builder.as_markup()


# ── main grid ─────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:channel_analyzer")
async def on_channel_analyzer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Channel Analyzer</b>\n\nNimani tahlil qilmoqchisiz?",
        reply_markup=_ca_keyboard(),
    )
    await callback.answer()


# ── Kanal tahlili ─────────────────────────────────────────────────

@router.callback_query(F.data == "ca:channel")
async def on_channel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_channel)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔗 <b>Kanal Tahlili</b>\n\n"
        "Kanal @username, URL yoki nomini yozing:\n\n"
        "Misol: <code>@MrBeast</code>\n"
        "Yoki: <code>NeonRush</code>"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_channel)
async def on_channel_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.youtube_service import get_channel, format_channel
    raw = (message.text or "").strip()
    await state.clear()

    if not raw:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    wait_msg = await message.answer("🔍 Kanal ma'lumotlari yuklanmoqda...")

    try:
        ch = await get_channel(raw)
    except Exception as e:
        await wait_msg.edit_text(
            f"❌ Xatolik yuz berdi: {e}\n\nQayta urining.",
            reply_markup=get_nav_keyboard("ca:channel", "menu:channel_analyzer"),
        )
        return

    if not ch:
        await wait_msg.edit_text(
            f"❌ <b>{raw}</b> — kanal topilmadi.\n\n"
            "To'g'ri @username yoki URL kiriting.",
            reply_markup=get_nav_keyboard("ca:channel", "menu:channel_analyzer"),
        )
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ YouTube'da ochish", url=ch.channel_url)
    builder.adjust(1)
    add_nav_row(builder, current="ca:channel", parent="menu:channel_analyzer")

    await wait_msg.edit_text(
        format_channel(ch),
        reply_markup=builder.as_markup(),
    )


# ── Video tahlili ─────────────────────────────────────────────────

@router.callback_query(F.data == "ca:video")
async def on_video(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_video)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎥 <b>Video Tahlili</b>\n\n"
        "Video URL yoki ID ni yozing:\n\n"
        "Misol: <code>https://youtu.be/dQw4w9WgXcQ</code>\n"
        "Yoki: <code>dQw4w9WgXcQ</code>"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_video)
async def on_video_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.youtube_service import get_video, format_video
    raw = (message.text or "").strip()
    await state.clear()

    if not raw:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    wait_msg = await message.answer("🔍 Video ma'lumotlari yuklanmoqda...")

    try:
        v = await get_video(raw)
    except Exception as e:
        await wait_msg.edit_text(
            f"❌ Xatolik: {e}\n\nQayta urining.",
            reply_markup=get_nav_keyboard("ca:video", "menu:channel_analyzer"),
        )
        return

    if not v:
        await wait_msg.edit_text(
            "❌ Video topilmadi.\n\nTo'g'ri YouTube URL yuboring.",
            reply_markup=get_nav_keyboard("ca:video", "menu:channel_analyzer"),
        )
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ YouTube'da ko'rish", url=f"https://youtu.be/{v.video_id}")
    builder.adjust(1)
    add_nav_row(builder, current="ca:video", parent="menu:channel_analyzer")

    await wait_msg.edit_text(format_video(v), reply_markup=builder.as_markup())


# ── Thumbnail qoidalari ───────────────────────────────────────────

@router.callback_query(F.data == "ca:thumbnail")
async def on_thumbnail(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    for label, url in [
        ("🎨 Canva",         "https://www.canva.com/create/youtube-thumbnails/"),
        ("✏️ Adobe Express", "https://www.adobe.com/express/create/thumbnail/youtube"),
        ("🎭 Fotor",         "https://www.fotor.com/features/youtube-thumbnail-maker/"),
        ("🖼 Freepik",       "https://www.freepik.com/search?query=youtube+thumbnail&type=psd"),
    ]:
        builder.button(text=label, url=url)
    builder.adjust(1)
    add_nav_row(builder, current="ca:thumbnail", parent="menu:channel_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "🖼 <b>Thumbnail Qoidalari</b>\n\n"
        "✅ O'lcham: <b>1280×720px</b> (16:9)\n"
        "✅ Fayl hajmi: <b>2 MB dan kam</b>\n"
        "✅ Matn: <b>maksimal 6 so'z</b>, katta shrift\n"
        "✅ Yuqori kontrast ranglar\n"
        "✅ Yuz ifodasi (CTR +38% oshiradi)\n"
        "✅ Burchaklarda matn yo'q (mobilda kesiladi)\n\n"
        "Dizayn asboblari:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ── Raqiblar ─────────────────────────────────────────────────────

@router.callback_query(F.data == "ca:competitors")
async def on_competitors(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_niche)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🏆 <b>Raqiblar Tahlili</b>\n\n"
        "Kanal yo'nalishi yoki mavzusini yozing:\n\n"
        "Misol: <code>Minecraft kids animation</code>"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_niche)
async def on_niche_input(message: Message, state: FSMContext) -> None:
    from urllib.parse import quote_plus
    niche = (message.text or "").strip()
    await state.clear()

    if not niche:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    q = quote_plus(niche)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔍 YouTube'da qidirish",
        url=f"https://www.youtube.com/results?search_query={q}&sp=CAM%253D"
    )
    builder.button(
        text="📊 Noxinfluencer",
        url=f"https://www.noxinfluencer.com/youtube/search?keyword={q}"
    )
    builder.adjust(1)
    add_nav_row(builder, current="ca:competitors", parent="menu:channel_analyzer")

    await message.answer(
        f"🏆 <b>Raqiblar: {niche}</b>\n\n"
        "Shu yo'nalishdagi top kanallarni toping:",
        reply_markup=builder.as_markup(),
    )


# ── O'sish maslahatlar ────────────────────────────────────────────

@router.callback_query(F.data == "ca:growth")
async def on_growth(callback: CallbackQuery) -> None:
    tips = "\n".join(f"{i+1}. {t}" for i, t in enumerate(_GROWTH_TIPS))
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 YouTube Creator Academy", url="https://creatoracademy.youtube.com/")
    builder.adjust(1)
    add_nav_row(builder, current="ca:growth", parent="menu:channel_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📈 <b>O'sish Maslahatlar</b>\n\n{tips}",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ── Stats asboblar ────────────────────────────────────────────────

@router.callback_query(F.data == "ca:statistics")
async def on_statistics(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    for label, url in [
        ("📊 SocialBlade",    "https://socialblade.com/youtube/"),
        ("🔍 Noxinfluencer",  "https://www.noxinfluencer.com/youtube/"),
        ("🎯 vidIQ",          "https://vidiq.com/"),
        ("🔧 TubeBuddy",      "https://www.tubebuddy.com/"),
        ("📈 YouTube Studio", "https://studio.youtube.com/"),
        ("📉 Google Trends",  "https://trends.google.com/"),
    ]:
        builder.button(text=label, url=url)
    builder.adjust(1)
    add_nav_row(builder, current="ca:statistics", parent="menu:channel_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Statistika Asboblari</b>\n\n"
        "Kanal statistikasi uchun professional asboblar:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
