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
    waiting_for_channel        = State()
    waiting_for_video          = State()
    waiting_for_niche          = State()
    waiting_for_stats_ch       = State()
    # New states
    waiting_for_seo_title      = State()
    waiting_for_thumb_url      = State()
    waiting_for_report_channel = State()


_ITEMS: list[tuple[str, str]] = [
    ("🔗 Kanal Tahlili",     "ca:channel"),
    ("🎥 Video Tahlili",     "ca:video"),
    ("🖼 Thumbnail Tahlili", "ca:thumbnail"),
    ("📈 O'sish Maslahat",   "ca:growth"),
    ("🏆 Raqiblar",          "ca:competitors"),
    ("🎯 SEO Tahlil",        "ca:seo"),
    ("📅 Yuklash Strategiya","ca:upload_strategy"),
    ("📊 Hisobot",           "ca:report"),
    ("💡 AI Tavsiyalar",     "ca:ai_recs"),
    ("📂 Saqlangan",         "ca:saved_reports"),
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
    builder.adjust(2, 2, 2, 2, 2)   # 10 items → 5 rows × 2 columns
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


# ── Thumbnail tahlili ─────────────────────────────────────────────

@router.callback_query(F.data == "ca:thumbnail")
async def on_thumbnail(callback: CallbackQuery, state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Video URL kiritish", callback_data="ca:thumb_url")
    builder.button(text="📋 Qoidalarni ko'rish",  callback_data="ca:thumb_rules")
    builder.adjust(1)
    add_nav_row(builder, current="ca:thumbnail", parent="menu:channel_analyzer")
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🖼 <b>Thumbnail Tahlili</b>\n\n"
        "Thumbnail URL kiritib tahlil qilish yoki\n"
        "umumiy qoidalarni ko'ring:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "ca:thumb_rules")
async def on_thumb_rules(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        _THUMBNAIL_RULES,
        reply_markup=get_nav_keyboard("ca:thumbnail", "menu:channel_analyzer"),
    )
    await callback.answer()


@router.callback_query(F.data == "ca:thumb_url")
async def on_thumb_url_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_thumb_url)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🖼 <b>Thumbnail Tahlili</b>\n\n"
        "YouTube video URL yoki thumbnail URL yuboring:\n\n"
        "Misol: <code>https://youtu.be/VIDEO_ID</code>\n"
        "Yoki: <code>https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg</code>"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_thumb_url)
async def on_thumb_url_input(message: Message, state: FSMContext) -> None:
    import re
    import httpx
    raw = (message.text or "").strip()
    await state.clear()

    if not raw:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    wait_msg = await message.answer("🖼 Thumbnail yuklanmoqda...")

    # Extract video ID from YouTube URL
    vid_id = None
    m = re.search(r"youtu\.be/([\w-]{11})", raw)
    if m:
        vid_id = m.group(1)
    else:
        m = re.search(r"(?:v=|/shorts/|/embed/)([\w-]{11})", raw)
        if m:
            vid_id = m.group(1)
        elif re.match(r"^[\w-]{11}$", raw):
            vid_id = raw

    # Determine image URL
    if vid_id:
        thumb_url = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
    elif raw.startswith("http"):
        thumb_url = raw
    else:
        await wait_msg.edit_text(
            "❌ Noto'g'ri URL. YouTube video URL yuboring.",
            reply_markup=get_nav_keyboard("ca:thumbnail", "menu:channel_analyzer"),
        )
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(thumb_url, follow_redirects=True)
        if resp.status_code != 200 or len(resp.content) < 5000:
            # Try lower quality
            if vid_id:
                thumb_url = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(thumb_url)
    except Exception as e:
        await wait_msg.edit_text(
            f"❌ Yuklab bo'lmadi: {e}",
            reply_markup=get_nav_keyboard("ca:thumbnail", "menu:channel_analyzer"),
        )
        return

    if not resp or len(resp.content) < 5000:
        await wait_msg.edit_text(
            "❌ Thumbnail topilmadi.",
            reply_markup=get_nav_keyboard("ca:thumbnail", "menu:channel_analyzer"),
        )
        return

    # Rule-based analysis
    size_kb = len(resp.content) // 1024
    w_hint = "1280×720" if size_kb > 40 else "320×180 (past sifat)"

    lines = [
        "🖼 <b>Thumbnail Tahlili</b>\n",
        f"📦 Hajm: <b>{size_kb} KB</b>",
        f"📐 Taxminiy o'lcham: <b>{w_hint}</b>",
    ]

    # Scoring
    score = 0
    tips = []

    if size_kb >= 50:
        score += 30
        lines.append("✅ Sifat: <b>Yuqori</b> (HD)")
    elif size_kb >= 20:
        score += 15
        lines.append("⚠️ Sifat: <b>O'rta</b>")
        tips.append("Yuqori sifatli thumbnail ishlating")
    else:
        score += 5
        lines.append("❌ Sifat: <b>Past</b> (thumbnail kichik yoki siqilgan)")
        tips.append("1280×720px, 2MB'dan kam thumbnail tayyorlang")

    if vid_id:
        score += 20
        tips_text = "\n".join(f"  • {t}" for t in [
            "1280×720px o'lcham: optimal",
            "Matn 6 so'zdan kam bo'lsin",
            "Yuz ifodasi CTR +38% oshiradi",
            "Qizil/sariq ranglar e'tiborni jalb qiladi",
            "Burchaklarda matn bo'lmasin",
        ])
        lines.append(f"\n<b>Qoidalar tekshiruvi:</b>\n{tips_text}")

    # Estimate score
    score = min(95, score + 30)   # base 30 for having a thumbnail at all
    bar = "█" * round(score / 10) + "░" * (10 - round(score / 10))
    lines.insert(1, f"<code>[{bar}]</code> <b>{score}/100</b>")

    if tips:
        lines.append("\n<b>💡 Tavsiyalar:</b>")
        for t in tips:
            lines.append(f"  • {t}")

    builder = InlineKeyboardBuilder()
    if vid_id:
        builder.button(text="▶️ YouTube'da ko'rish", url=f"https://youtu.be/{vid_id}")
    builder.button(text="📋 Qoidalar", callback_data="ca:thumb_rules")
    builder.button(text="⬅ Orqaga",  callback_data="ca:thumbnail")
    builder.adjust(1, 2)

    photo = BufferedInputFile(resp.content, filename="thumb.jpg")
    await wait_msg.delete()
    await message.answer_photo(
        photo,
        caption="\n".join(lines),
        parse_mode="HTML",
        reply_markup=builder.as_markup(),
    )


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


# ── NEW: SEO Tahlil ───────────────────────────────────────────────

@router.callback_query(F.data == "ca:seo")
async def on_seo(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_seo_title)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎯 <b>SEO Tahlil</b>\n\n"
        "Video sarlavhasini yozing — bot SEO balini hisoblaydi:\n\n"
        "Misol: <code>Spider-Man vs Batman EPIC Battle #shorts</code>\n\n"
        "💡 Sarlavha + tavsif + teglarni bir xatga yozing (ixtiyoriy)"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_seo_title)
async def on_seo_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.seo_service import calculate_seo_score, format_seo_result, save_seo_result

    raw = (message.text or "").strip()
    await state.clear()

    if not raw:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    # Parse: first line = title, remaining = description
    lines = raw.split("\n", 1)
    title = lines[0].strip()
    desc = lines[1].strip() if len(lines) > 1 else ""

    result = calculate_seo_score(title, desc)
    text = format_seo_result(result, title)

    await save_seo_result(title, result, desc)

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Yangi tahlil",   callback_data="ca:seo")
    builder.button(text="📊 Hisobot",         callback_data="ca:report")
    builder.button(text="⬅ Orqaga",           callback_data="menu:channel_analyzer")
    builder.adjust(2, 1)

    await message.answer(text, reply_markup=builder.as_markup())


# ── NEW: Upload Strategy ──────────────────────────────────────────

@router.callback_query(F.data == "ca:upload_strategy")
async def on_upload_strategy(callback: CallbackQuery) -> None:
    from telegram_bot.services.upload_strategy_service import get_category_list

    cats = get_category_list()
    builder = InlineKeyboardBuilder()
    for cat_id, cat_label in cats:
        builder.button(text=cat_label, callback_data=f"ca_strat:{cat_id}")
    builder.adjust(2)
    add_nav_row(builder, current="ca:upload_strategy", parent="menu:channel_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "📅 <b>Yuklash Strategiyasi</b>\n\n"
        "Kontent kategoriyangizni tanlang:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ca_strat:"))
async def on_strat_category(callback: CallbackQuery) -> None:
    from telegram_bot.services.upload_strategy_service import get_upload_strategy

    cat_id = callback.data.split(":", 1)[1]
    strat = get_upload_strategy(cat_id)
    sched = strat["schedule"]
    cal = strat["calendar"]

    lines = [
        f"📅 <b>Yuklash Strategiyasi — {cat_id.title()}</b>\n",
        f"📆 <b>Chastota:</b> {sched['frequency']}",
        f"✅ <b>Eng yaxshi kunlar:</b> {sched['best_days']}",
        f"🕐 <b>Eng yaxshi vaqt:</b> {sched['best_times']}",
        f"❌ <b>Qochish kerak:</b> {sched['avoid']}",
        f"🎬 <b>Kontent mix:</b> {sched['content_mix']}",
        f"🔄 <b>Muntazamlik:</b> {sched['consistency']}",
        f"🪝 <b>Hook:</b> {sched['hook_tip']}",
        f"🖼 <b>Thumbnail:</b> {sched['thumbnail_tip']}",
        f"📣 <b>Engagement:</b> {sched['engagement_tip']}",
        f"🗓 <b>Mavsum:</b> {sched['season_tip']}",
        "\n<b>📅 Haftalik Kontent Takvim:</b>",
    ]
    for day, plan in cal.items():
        lines.append(f"  <b>{day}:</b> {plan}")

    builder = InlineKeyboardBuilder()
    builder.button(text="💡 AI Tavsiyalar", callback_data=f"ca_airec:{cat_id}")
    builder.button(text="⬅ Strategiya",     callback_data="ca:upload_strategy")
    builder.adjust(2)

    await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ── NEW: Performance Report ───────────────────────────────────────

@router.callback_query(F.data == "ca:report")
async def on_report_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChannelStates.waiting_for_report_channel)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📊 <b>Performance Hisobot</b>\n\n"
        "Kanal @username yoki URL kiriting —\n"
        "Bot to'liq hisobot yaratib saqlaydi:\n\n"
        "Misol: <code>@MrBeast</code>\n"
        "Yoki: <code>https://youtube.com/@channel</code>"
    )
    await callback.answer()


@router.message(ChannelStates.waiting_for_report_channel)
async def on_report_channel_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.youtube_service import get_channel
    from telegram_bot.services.report_service import (
        generate_channel_report, format_report, save_report, save_channel_to_history
    )

    raw = (message.text or "").strip()
    await state.clear()

    if not raw:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    wait_msg = await message.answer("📊 Hisobot tayyorlanmoqda...")

    try:
        ch = await get_channel(raw)
    except Exception as e:
        await wait_msg.edit_text(
            f"❌ Xatolik: {e}",
            reply_markup=get_nav_keyboard("ca:report", "menu:channel_analyzer"),
        )
        return

    if not ch:
        await wait_msg.edit_text(
            f"❌ <b>{raw}</b> — kanal topilmadi.",
            reply_markup=get_nav_keyboard("ca:report", "menu:channel_analyzer"),
        )
        return

    await save_channel_to_history(ch)
    rd = generate_channel_report(ch)
    report_id = await save_report(rd)
    text = format_report(rd)

    builder = InlineKeyboardBuilder()
    builder.button(text="📺 YouTube'da ochish", url=ch.channel_url)
    builder.button(text="📂 Saqlangan",         callback_data="ca:saved_reports")
    builder.button(text="🔄 Yangi hisobot",     callback_data="ca:report")
    builder.button(text="⬅ Orqaga",             callback_data="menu:channel_analyzer")
    builder.adjust(2, 2)

    await wait_msg.edit_text(
        text + f"\n\n💾 <i>Saqlandi (#{report_id})</i>",
        reply_markup=builder.as_markup(),
    )


# ── NEW: AI Recommendations ───────────────────────────────────────

@router.callback_query(F.data == "ca:ai_recs")
async def on_ai_recs(callback: CallbackQuery) -> None:
    from telegram_bot.services.upload_strategy_service import get_category_list

    cats = get_category_list()
    builder = InlineKeyboardBuilder()
    for cat_id, cat_label in cats:
        builder.button(text=cat_label, callback_data=f"ca_airec:{cat_id}")
    builder.adjust(2)
    add_nav_row(builder, current="ca:ai_recs", parent="menu:channel_analyzer")

    await callback.message.edit_text(  # type: ignore[union-attr]
        "💡 <b>AI Tavsiyalar</b>\n\n"
        "Kontent kategoriyangizni tanlang —\n"
        "bot optimal strategiya tavsiya qiladi:\n\n"
        "<i>(Hozir shablon asosida, keyinroq AI bilan kuchaytiriladi)</i>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ca_airec:"))
async def on_ai_rec_category(callback: CallbackQuery) -> None:
    from telegram_bot.services.upload_strategy_service import get_ai_recommendations

    cat_id = callback.data.split(":", 1)[1]
    recs = get_ai_recommendations(cat_id)

    lines = [f"💡 <b>AI Tavsiyalar — {cat_id.title()}</b>\n"]
    for rec in recs:
        lines.append(f"{rec['label']}\n<code>{rec['value']}</code>")

    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Yuklash Strategiyasi", callback_data=f"ca_strat:{cat_id}")
    builder.button(text="⬅ Kategoriyalar",         callback_data="ca:ai_recs")
    builder.adjust(2)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n\n".join(lines), reply_markup=builder.as_markup()
    )
    await callback.answer()


# ── NEW: Saved Reports ────────────────────────────────────────────

_RPT_PAGE = 5


@router.callback_query(F.data == "ca:saved_reports")
async def on_saved_reports(callback: CallbackQuery) -> None:
    from telegram_bot.services.report_service import list_reports

    reports = await list_reports(limit=_RPT_PAGE)

    if not reports:
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Hisobot yaratish", callback_data="ca:report")
        builder.button(text="⬅ Orqaga",            callback_data="menu:channel_analyzer")
        builder.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "📂 <b>Saqlangan Hisobotlar</b>\n\nHali hech qanday hisobot saqlanmagan.",
            reply_markup=builder.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"📂 <b>Saqlangan Hisobotlar</b> ({len(reports)} ta so'nggi):\n"]
    for i, rep in enumerate(reports, 1):
        import json
        scores = json.loads(rep.scores or "{}")
        health = scores.get("health", "—")
        lines.append(
            f"{i}. <b>{rep.title[:45]}</b>\n"
            f"   📊 Ball: {health}/100 | 🗓 {rep.created_at.strftime('%d.%m %H:%M')}"
        )

    builder = InlineKeyboardBuilder()
    for i, rep in enumerate(reports, 1):
        builder.button(text=f"🗑 {i}. O'chirish", callback_data=f"ca_del_rep:{rep.id}")
    builder.adjust(2)
    builder.button(text="📊 Yangi hisobot",  callback_data="ca:report")
    builder.button(text="⬅ Orqaga",         callback_data="menu:channel_analyzer")
    builder.adjust(2)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines), reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ca_del_rep:"))
async def on_delete_report(callback: CallbackQuery) -> None:
    from telegram_bot.services.report_service import delete_report

    rep_id = int(callback.data.split(":", 1)[1])
    await delete_report(rep_id)
    await callback.answer("🗑 O'chirildi")
    await on_saved_reports(callback)
