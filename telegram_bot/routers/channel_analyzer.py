"""Channel Analyzer — all analytics shown inside the bot via yt-dlp."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile, CallbackQuery, InlineKeyboardButton, InputMediaPhoto, Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="channel_analyzer")


class ChannelStates(StatesGroup):
    waiting_for_channel    = State()
    waiting_for_video      = State()
    waiting_for_niche      = State()
    waiting_for_stats_ch   = State()


_ITEMS: list[tuple[str, str]] = [
    ("🔗 Kanal Tahlili",     "ca:channel"),
    ("🎥 Video Tahlili",     "ca:video"),
    ("🖼 Thumbnail Qoidasi", "ca:thumbnail"),
    ("🏆 Raqiblar",          "ca:competitors"),
    ("📈 O'sish Maslahat",   "ca:growth"),
    ("📊 Stats Asboblar",    "ca:statistics"),
]

_GROWTH_TIPS = [
    "📅 Haftada 3–5 Shorts yuklang — muntazamlik asosiy",
    "🎯 Bitta mavzuga yopishing — algoritm tezroq taniydi",
    "🔥 Dastlabki 2 soniyada hook bo'lsin — sekin boshlash yo'q",
    "🏷 3–5 hashtag: #Shorts + 2 niche + 1 trending",
    "🖼 CTR 4% dan past bo'lsa thumbnail'ni almashtiring",
    "💬 Dastlabki 24 soatda har bir izohga javob bering",
    "🔄 Uzun video → 5–10 ta Shorts klip qiling",
    "📊 Auditoriyangiz onlayn bo'lgan vaqtda yuklang",
    "🤝 O'z nichengizda kanallar bilan hamkorlik qiling",
    "📈 End screen + pinned comment = +30% ko'rish vaqti",
    "🎙 Ovozli tavsif + subtitle = SEO +40%",
    "🔁 Eng yaxshi videolaringizni yangi trending bilan qayta qiling",
    "📌 Kanal tavsifida asosiy kalit so'zlarni ishlating",
    "⏰ Yuklash vaqti: Seshanba–Payshanba 12:00–15:00 eng yaxshi",
    "📢 Community post → videogacha hype yarating",
]

_THUMBNAIL_RULES = """🖼 <b>Thumbnail Qoidalari</b>

<b>📐 Texnik talablar:</b>
• O'lcham: <b>1280×720px</b> (16:9)
• Fayl formati: JPG, PNG, GIF, BMP
• Hajm: <b>2 MB dan kam</b>

<b>🎨 Dizayn qoidalari:</b>
• Matn: <b>6 so'zdan kam</b>, katta shrift (min 60pt)
• Rang kontrasti yuqori bo'lsin (oq/qora, sariq/qora)
• Yuz ifodasi: CTR ni <b>+38%</b> oshiradi
• Burchaklarda matn bo'lmasin (mobilda kesiladi)
• Asosiy element markazda yoki 1/3 qoidasida

<b>🔥 CTR oshirish sirlari:</b>
• Qizil/sariq ranglar e'tiborni jalb qiladi
• Raqamlar ishlatish (<b>5 ta sir</b>, <b>1 million</b>)
• Savol yoki shok ifodasi qo'shing
• A/B test qiling (YouTube Studio → Analytics)
• Birinchi 48 soat CTR ni kuzating

<b>❌ Qilmang:</b>
• Kichik matn (mobilda o'qilmaydi)
• Juda ko'p element (tartibsiz ko'rinadi)
• Clickbait (uzoq muddatda zararli)
• Thumbnail va title bir xil bo'lmasin"""


def _ca_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    add_nav_row(builder, current="menu:channel_analyzer")
    return builder.as_markup()


def _fmt_subs(n: int | None) -> str:
    if n is None:
        return "Yashirin"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


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
            f"❌ Xatolik: {e}\n\nQayta urining.",
            reply_markup=get_nav_keyboard("ca:channel", "menu:channel_analyzer"),
        )
        return

    if not ch:
        await wait_msg.edit_text(
            f"❌ <b>{raw}</b> — kanal topilmadi.\n\nTo'g'ri @username yoki URL kiriting.",
            reply_markup=get_nav_keyboard("ca:channel", "menu:channel_analyzer"),
        )
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ YouTube'da ochish", url=ch.channel_url)
    builder.adjust(1)
    add_nav_row(builder, current="ca:channel", parent="menu:channel_analyzer")

    await wait_msg.edit_text(format_channel(ch), reply_markup=builder.as_markup())


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

    # Download video thumbnail and send as photo
    import httpx
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"https://img.youtube.com/vi/{v.video_id}/hqdefault.jpg"
            )
        if resp.status_code == 200 and len(resp.content) > 5000:
            builder = InlineKeyboardBuilder()
            builder.button(text="▶️ YouTube'da ko'rish", url=f"https://youtu.be/{v.video_id}")
            builder.adjust(1)
            add_nav_row(builder, current="ca:video", parent="menu:channel_analyzer")
            photo = BufferedInputFile(resp.content, filename="thumb.jpg")
            await message.answer_photo(photo, caption=format_video(v), parse_mode="HTML",
                                       reply_markup=builder.as_markup())
            await wait_msg.delete()
            return
    except Exception:
        pass

    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ YouTube'da ko'rish", url=f"https://youtu.be/{v.video_id}")
    builder.adjust(1)
    add_nav_row(builder, current="ca:video", parent="menu:channel_analyzer")
    await wait_msg.edit_text(format_video(v), reply_markup=builder.as_markup())


# ── Thumbnail qoidalari ───────────────────────────────────────────

@router.callback_query(F.data == "ca:thumbnail")
async def on_thumbnail(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        _THUMBNAIL_RULES,
        reply_markup=get_nav_keyboard("ca:thumbnail", "menu:channel_analyzer"),
    )
    await callback.answer()


# ── Raqiblar ─────────────────────────────────────────────────────

@router.callback_query(F.data == "ca:competitors")
async def on_competitors(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_niche)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🏆 <b>Raqiblar Tahlili</b>\n\n"
        "Kanal yo'nalishi yoki mavzusini yozing:\n\n"
        "Misol: <code>Minecraft kids animation</code>\n"
        "Yoki: <code>Spider-Man shorts Uzbek</code>"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_niche)
async def on_niche_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.real_search import search_competitors, download_yt_thumbnails, search_youtube

    niche = (message.text or "").strip()
    await state.clear()

    if not niche:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    wait_msg = await message.answer(f"🏆 <b>{niche}</b> yo'nalishidagi raqiblar qidirilmoqda...")

    channels = await search_competitors(niche, limit=4)

    if not channels:
        await wait_msg.edit_text(
            f"❌ <b>{niche}</b> bo'yicha kanal topilmadi.\n\nBoshqa kalit so'z sinab ko'ring.",
            reply_markup=get_nav_keyboard("ca:competitors", "menu:channel_analyzer"),
        )
        return

    # Get thumbnails from one video per channel
    from telegram_bot.services.real_search import RealResult
    pseudo_results = []
    for ch in channels:
        if ch.get("video_id"):
            pseudo_results.append(RealResult(
                title=ch["name"],
                url=f"https://youtu.be/{ch['video_id']}",
                source="youtube.com",
                extra=_fmt_subs(ch.get("subs")),
            ))

    photos = await download_yt_thumbnails(pseudo_results, limit=4)

    # Build text
    lines = [f"🏆 <b>Raqiblar: {niche}</b>\n"]
    for i, ch in enumerate(channels, 1):
        subs = _fmt_subs(ch.get("subs"))
        lines.append(f"{i}. <b>{ch['name']}</b> — {subs} obunachi")

    text = "\n".join(lines)

    if photos:
        media = []
        for i, (data, r) in enumerate(photos):
            cap = text if i == 0 else f"<b>{r.title}</b>"
            media.append(InputMediaPhoto(
                media=BufferedInputFile(data, f"ch_{i}.jpg"),
                caption=cap,
                parse_mode="HTML",
            ))
        await message.answer_media_group(media)
        await wait_msg.delete()
    else:
        await wait_msg.edit_text(text, parse_mode="HTML")

    builder = InlineKeyboardBuilder()
    for ch in channels[:4]:
        name = ch["name"][:28]
        builder.button(text=f"📺 {name}", url=ch["url"])
    builder.adjust(1)
    add_nav_row(builder, current="ca:competitors", parent="menu:channel_analyzer")
    await message.answer("Kanallarga o'tish:", reply_markup=builder.as_markup())


# ── O'sish maslahatlar ────────────────────────────────────────────

@router.callback_query(F.data == "ca:growth")
async def on_growth(callback: CallbackQuery) -> None:
    tips = "\n".join(f"{i+1}. {t}" for i, t in enumerate(_GROWTH_TIPS))
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📈 <b>O'sish Maslahatlar</b>\n\n{tips}",
        reply_markup=get_nav_keyboard("ca:growth", "menu:channel_analyzer"),
    )
    await callback.answer()


# ── Stats asboblar ────────────────────────────────────────────────

@router.callback_query(F.data == "ca:statistics")
async def on_statistics(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_stats_ch)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Stats Asboblar</b>\n\n"
        "Tahlil qilmoqchi bo'lgan kanal @username yoki URL ini yozing:\n\n"
        "Misol: <code>@MrBeast</code>\n\n"
        "Bot barcha statistikani hozir ko'rsatadi:"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_stats_ch)
async def on_stats_channel(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.youtube_service import get_channel, format_channel
    raw = (message.text or "").strip()
    await state.clear()

    if not raw:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    wait_msg = await message.answer("📊 Statistika yuklanmoqda...")
    try:
        ch = await get_channel(raw)
    except Exception as e:
        await wait_msg.edit_text(
            f"❌ Xatolik: {e}",
            reply_markup=get_nav_keyboard("ca:statistics", "menu:channel_analyzer"),
        )
        return

    if not ch:
        await wait_msg.edit_text(
            f"❌ <b>{raw}</b> — topilmadi.",
            reply_markup=get_nav_keyboard("ca:statistics", "menu:channel_analyzer"),
        )
        return

    # Enhanced stats view
    views_per_vid = (ch.view_count // ch.video_count) if ch.video_count else 0
    lines = [
        f"📊 <b>{ch.title}</b> — To'liq Statistika\n",
        f"👥 Obunachílar: <b>{_fmt_subs(ch.subscriber_count)}</b>",
        f"👁 Jami ko'rishlar: <b>{_fmt_subs(ch.view_count)}</b>",
        f"🎥 Videolar soni: <b>{ch.video_count}</b>",
        f"📊 O'rtacha ko'rish/video: <b>{_fmt_subs(views_per_vid)}</b>",
    ]
    if ch.country and ch.country != "—":
        lines.append(f"🌍 Mamlakat: <b>{ch.country}</b>")

    if ch.recent_videos:
        lines += ["", "🕐 <b>So'nggi videolar:</b>"]
        for i, v in enumerate(ch.recent_videos, 1):
            t = v["title"] + ("…" if len(v["title"]) >= 50 else "")
            extra = ""
            if v.get("view_count"):
                extra += f" · 👁 {v['view_count']}"
            if v.get("duration") and v["duration"] != "0:00":
                extra += f" · ⏱ {v['duration']}"
            lines.append(f"  {i}. {t}{extra}")

    builder = InlineKeyboardBuilder()
    builder.button(text="📺 YouTube'da ochish", url=ch.channel_url)
    builder.adjust(1)
    add_nav_row(builder, current="ca:statistics", parent="menu:channel_analyzer")

    await wait_msg.edit_text("\n".join(lines), reply_markup=builder.as_markup())
