"""Video Kit — complete material pack delivered as actual files inside the bot.

PNG + Background + GIF → photo albums
Green Screen          → downloaded video file
Music                 → downloaded mp3 audio files
Sound Effects         → downloaded mp3 audio files
"""

from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile, CallbackQuery, InputMediaPhoto, Message,
)
# BufferedInputFile is still used for audio/video downloads below
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import get_nav_keyboard

router = Router(name="video_kit")


class VideoKitStates(StatesGroup):
    waiting_for_topic = State()


# ── image albums ───────────────────────────────────────────────────

async def _send_image_album(message: Message, results: list, label: str, ext: str = "png") -> int:
    """Send images by URL — Telegram fetches them directly, no download needed."""
    if not results:
        return 0
    media = [
        InputMediaPhoto(
            media=r.url,
            caption=label if i == 0 else None,
            parse_mode="HTML",
        )
        for i, r in enumerate(results[:4])
    ]
    if not media:
        return 0
    try:
        await message.answer_media_group(media)
        return len(media)
    except Exception:
        # If Telegram can't fetch the URL, send links as text fallback
        lines = [label]
        for r in results[:4]:
            lines.append(f"• <a href='{r.url}'>{r.title[:60]}</a>")
        try:
            await message.answer("\n".join(lines))
        except Exception:
            pass
        return 0


# ── audio download & send ──────────────────────────────────────────

_AUDIO_TIMEOUT = 60   # yt-dlp audio download max seconds
_VIDEO_TIMEOUT = 90   # yt-dlp video download max seconds


async def _download_and_send_audio(
    message: Message,
    url: str,
    title: str,
    performer: str = "",
) -> bool:
    from telegram_bot.services.real_search import download_yt_audio
    try:
        result = await asyncio.wait_for(download_yt_audio(url), timeout=_AUDIO_TIMEOUT)
    except asyncio.TimeoutError:
        return False
    except Exception:
        return False
    if not result:
        return False
    data, actual_title = result
    short_title = (actual_title or title)[:60]
    ext = "mp3" if data[:3] == b"ID3" or data[:4] in (b"\xff\xfb", b"\xff\xf3") else "m4a"
    try:
        await message.answer_audio(
            audio=BufferedInputFile(data, filename=f"{short_title[:40]}.{ext}"),
            title=short_title,
            performer=performer or "YouTube",
            caption=f"🎵 {short_title}",
        )
        return True
    except Exception:
        return False


# ── video download & send ──────────────────────────────────────────

async def _download_and_send_video(
    message: Message,
    url: str,
    title: str,
) -> bool:
    from telegram_bot.services.real_search import download_yt_video
    try:
        result = await asyncio.wait_for(download_yt_video(url, max_mb=45), timeout=_VIDEO_TIMEOUT)
    except asyncio.TimeoutError:
        return False
    except Exception:
        return False
    if not result:
        return False
    data, actual_title = result
    short = (actual_title or title)[:50]
    try:
        await message.answer_video(
            video=BufferedInputFile(data, filename=f"{short[:40]}.mp4"),
            caption=f"🟢 {short}",
            supports_streaming=True,
        )
        return True
    except Exception:
        return False


# ── main kit delivery ──────────────────────────────────────────────

async def _deliver_kit(message: Message, query: str, back_cb: str, user_id: int = 0) -> None:
    from telegram_bot.services.real_search import search_for_material, search_youtube

    status = await message.answer(
        f"📦 <b>{query}</b> uchun materiallar yuklanmoqda...\n\n"
        "⏳ Bu 30–60 soniya davom etadi. Iltimos kuting...\n\n"
        "🔍 Qidirilmoqda..."
    )

    # ── parallel search for all types (personalised by user_id) ──
    (png_r, bg_r, gif_r, gs_r, mus_r, sfx_r) = await asyncio.gather(
        search_for_material(query, "png",  limit=3, user_id=user_id),
        search_for_material(query, "bg",   limit=3, user_id=user_id),
        search_for_material(query, "gif",  limit=3, user_id=user_id),
        search_youtube(f"{query} green screen free download", limit=2, user_id=user_id),
        search_youtube(f"{query} background music no copyright free", limit=3, user_id=user_id),
        search_youtube(f"{query} sound effect free", limit=3, user_id=user_id),
    )

    await status.edit_text(
        f"📦 <b>{query}</b>\n\n"
        "✅ Qidiruv tugadi.\n"
        "🖼 Rasmlar jo'natilmoqda..."
    )

    counts = {
        "png": 0, "bg": 0, "gif": 0,
        "gs": 0, "mus": 0, "sfx": 0,
    }

    # ── 1-3. Images — all three albums sent in parallel (URLs, no download) ──
    results_img = await asyncio.gather(
        _send_image_album(message, png_r, "🖼 <b>PNG Rasmlar</b>", "png"),
        _send_image_album(message, bg_r,  "🌄 <b>Backgroundlar</b>", "jpg"),
        _send_image_album(message, gif_r, "🎞 <b>GIF / Animatsiyalar</b>", "gif"),
        return_exceptions=True,
    )
    counts["png"] = results_img[0] if isinstance(results_img[0], int) else 0
    counts["bg"]  = results_img[1] if isinstance(results_img[1], int) else 0
    counts["gif"] = results_img[2] if isinstance(results_img[2], int) else 0

    await status.edit_text(
        f"📦 <b>{query}</b>\n\n"
        f"✅ PNG: {counts['png']}  ✅ BG: {counts['bg']}  ✅ GIF: {counts['gif']}\n"
        "⬇️ Green Screen video yuklanmoqda..."
    )

    # ── 4. Green Screen — download actual video ──
    for r in gs_r[:2]:
        ok = await _download_and_send_video(message, r.url, r.title)
        if ok:
            counts["gs"] += 1

    await status.edit_text(
        f"📦 <b>{query}</b>\n\n"
        f"✅ PNG:{counts['png']} BG:{counts['bg']} GIF:{counts['gif']} GS:{counts['gs']}\n"
        "⬇️ Musiqa fayllar yuklanmoqda..."
    )

    # ── 5. Music — download audio files ──
    for r in mus_r[:3]:
        ok = await _download_and_send_audio(message, r.url, r.title, performer="Music")
        if ok:
            counts["mus"] += 1

    await status.edit_text(
        f"📦 <b>{query}</b>\n\n"
        f"✅ PNG:{counts['png']} BG:{counts['bg']} GIF:{counts['gif']} "
        f"GS:{counts['gs']} 🎵:{counts['mus']}\n"
        "⬇️ Sound Effects yuklanmoqda..."
    )

    # ── 6. SFX — download audio files ──
    for r in sfx_r[:3]:
        ok = await _download_and_send_audio(message, r.url, r.title, performer="SFX")
        if ok:
            counts["sfx"] += 1

    # ── final summary ──
    total = sum(counts.values())

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Yangilash",  callback_data=back_cb)
    builder.button(text="🏠 Bosh menyu", callback_data="menu:main")
    builder.adjust(2)

    await status.edit_text(
        f"✅ <b>{query}</b> — Video Kit tayyor!\n\n"
        f"🖼 PNG rasmlar: {counts['png']} ta\n"
        f"🌄 Backgroundlar: {counts['bg']} ta\n"
        f"🎞 GIF/Animatsiya: {counts['gif']} ta\n"
        f"🟢 Green Screen (video): {counts['gs']} ta\n"
        f"🎵 Musiqa (mp3): {counts['mus']} ta\n"
        f"🔊 Sound Effects (mp3): {counts['sfx']} ta\n\n"
        f"📦 Jami: <b>{total}</b> ta fayl yuborildi",
        reply_markup=builder.as_markup(),
    )


# ── entry: materials menu ─────────────────────────────────────────

@router.callback_query(F.data == "menu:video_kit")
async def on_video_kit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VideoKitStates.waiting_for_topic)
    await state.update_data(back_cb="menu:video_kit")
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Cap Cut To'plam</b>\n\n"
        "Karakter yoki mavzuni yozing:\n\n"
        "Misol: <code>Spider-Man</code>\n"
        "Yoki: <code>Minecraft Steve</code>\n\n"
        "Bot PNG · Background · GIF · Video · Musiqa · SFX —\n"
        "barchasini yuklab, to'plam holida yuboradi:"
    )
    await callback.answer()


# ── entry: character page ─────────────────────────────────────────

@router.callback_query(F.data.startswith("vidkit:"))
async def on_char_video_kit(callback: CallbackQuery) -> None:
    from telegram_bot.services.character_service import char_service

    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    _, cat_id, char_id = parts

    char = char_service.get_character(cat_id, char_id)
    if not char:
        await callback.answer("Topilmadi", show_alert=True)
        return

    back_cb = f"vidkit:{cat_id}:{char_id}"
    await callback.answer()

    uid = callback.from_user.id if callback.from_user else 0
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎬 <b>{char.name}</b> uchun Video Kit tayyorlanmoqda...",
    )

    await _deliver_kit(callback.message, char.name, back_cb, user_id=uid)  # type: ignore[arg-type]


# ── text input handler ────────────────────────────────────────────

@router.message(VideoKitStates.waiting_for_topic)
async def on_kit_topic(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    query = (message.text or "").strip()
    back_cb = data.get("back_cb", "menu:video_kit")

    if not query:
        await message.answer("❌ Bo'sh so'rov. Qayta urining.")
        return

    uid = message.from_user.id if message.from_user else 0
    await _deliver_kit(message, query, back_cb, user_id=uid)
