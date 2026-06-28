"""Video Kit — one-tap complete material pack for CapCut / video editing.

Searches PNG + Background + GIF + Green Screen + Music + SFX in parallel
and delivers everything as organized photo albums inside the bot.
"""

from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile, CallbackQuery, InputMediaPhoto, Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="video_kit")


class VideoKitStates(StatesGroup):
    waiting_for_topic = State()


# ── helpers ───────────────────────────────────────────────────────

async def _gather_all(query: str) -> dict:
    """Run all material searches in parallel."""
    from telegram_bot.services.real_search import search_for_material
    (
        png_r, bg_r, gif_r,
        gs_r, mus_r, sfx_r,
    ) = await asyncio.gather(
        search_for_material(query, "png",  limit=3),
        search_for_material(query, "bg",   limit=3),
        search_for_material(query, "gif",  limit=3),
        search_for_material(query, "gs",   limit=3),
        search_for_material(query, "mus",  limit=3),
        search_for_material(query, "sfx",  limit=3),
    )
    return {
        "png": png_r, "bg": bg_r, "gif": gif_r,
        "gs": gs_r,   "mus": mus_r, "sfx": sfx_r,
    }


async def _send_image_album(
    message: Message,
    results: list,
    label: str,
    ext: str = "png",
) -> None:
    """Download + send DDG image results as a Telegram photo album."""
    from telegram_bot.services.real_search import download_images
    photos = await download_images(results, limit=len(results))
    if not photos:
        return
    media = []
    for i, (data, title) in enumerate(photos):
        cap = f"{label}" if i == 0 else None
        media.append(InputMediaPhoto(
            media=BufferedInputFile(data, filename=f"img_{i}.{ext}"),
            caption=cap,
            parse_mode="HTML",
        ))
    await message.answer_media_group(media)


async def _send_yt_album(
    message: Message,
    results: list,
    label: str,
) -> list:
    """Download YouTube thumbnails + send album. Returns (bytes, result) list."""
    from telegram_bot.services.real_search import download_yt_thumbnails
    photos = await download_yt_thumbnails(results, limit=len(results))
    if not photos:
        return []
    media = []
    for i, (data, r) in enumerate(photos):
        cap = f"{label}\n<i>{r.title}</i>" if i == 0 else f"<i>{r.title}</i>"
        if r.extra:
            cap += f"\n{r.extra}"
        media.append(InputMediaPhoto(
            media=BufferedInputFile(data, filename=f"yt_{i}.jpg"),
            caption=cap,
            parse_mode="HTML",
        ))
    await message.answer_media_group(media)
    return photos


async def _deliver_kit(message: Message, query: str, back_cb: str) -> None:
    """Core: search everything in parallel then send organized kit."""
    kit = await _gather_all(query)

    png_r  = kit["png"]
    bg_r   = kit["bg"]
    gif_r  = kit["gif"]
    gs_r   = kit["gs"]
    mus_r  = kit["mus"]
    sfx_r  = kit["sfx"]

    sent_any = False

    # ── 1. PNG images ──
    if png_r:
        await _send_image_album(message, png_r, "🖼 <b>PNG Rasmlar</b>", ext="png")
        sent_any = True

    # ── 2. Backgrounds ──
    if bg_r:
        await _send_image_album(message, bg_r, "🌄 <b>Backgroundlar</b>", ext="jpg")
        sent_any = True

    # ── 3. GIF / Animations ──
    if gif_r:
        await _send_image_album(message, gif_r, "🎞 <b>GIF / Animatsiyalar</b>", ext="gif")
        sent_any = True

    # ── 4. Green Screen / Video ──
    gs_photos: list = []
    if gs_r:
        gs_photos = await _send_yt_album(message, gs_r, "🟢 <b>Green Screen</b>")
        if gs_photos:
            sent_any = True

    # ── 5. Music ──
    mus_photos: list = []
    if mus_r:
        mus_photos = await _send_yt_album(message, mus_r, "🎵 <b>Musiqa</b>")
        if mus_photos:
            sent_any = True

    if not sent_any:
        await message.answer(
            f"❌ <b>{query}</b> uchun material topilmadi.\n\nBoshqa kalit so'z sinab ko'ring.",
            reply_markup=get_nav_keyboard(back_cb, "menu:materials"),
        )
        return

    # ── 6. Summary keyboard ──
    builder = InlineKeyboardBuilder()

    # Watch buttons for Green Screen
    if gs_photos:
        for i, (_, r) in enumerate(gs_photos, 1):
            builder.button(text=f"🟢 GS {i}. Ko'rish", url=r.url)

    # Watch buttons for Music
    if mus_photos:
        for i, (_, r) in enumerate(mus_photos, 1):
            builder.button(text=f"🎵 Musiqa {i}. Ko'rish", url=r.url)

    # SFX web links
    if sfx_r:
        for i, r in enumerate(sfx_r[:3], 1):
            label = r.title[:28] + ("…" if len(r.title) > 28 else "")
            builder.button(text=f"🔊 SFX {i}. {label}", url=r.url)

    builder.adjust(2)
    builder.row(
        *[
            __import__("aiogram").types.InlineKeyboardButton(
                text="🔄 Yangilash", callback_data=back_cb
            ),
            __import__("aiogram").types.InlineKeyboardButton(
                text="🏠 Bosh menyu", callback_data="menu:main"
            ),
        ]
    )

    # Count delivered materials
    total = (
        len(png_r) + len(bg_r) + len(gif_r) +
        len(gs_photos) + len(mus_photos) + len(sfx_r[:3])
    )

    await message.answer(
        f"✅ <b>{query}</b> uchun Video Kit tayyor!\n\n"
        f"📦 Jami: <b>{total}</b> ta material yuborildi\n\n"
        f"🖼 PNG: {len(png_r)} ta\n"
        f"🌄 Background: {len(bg_r)} ta\n"
        f"🎞 GIF: {len(gif_r)} ta\n"
        f"🟢 Green Screen: {len(gs_photos)} ta\n"
        f"🎵 Musiqa: {len(mus_photos)} ta\n"
        f"🔊 Sound FX: {len(sfx_r[:3])} ta",
        reply_markup=builder.as_markup(),
    )


# ── entry from materials menu ─────────────────────────────────────

@router.callback_query(F.data == "menu:video_kit")
async def on_video_kit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VideoKitStates.waiting_for_topic)
    await state.update_data(back_cb="menu:video_kit")
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Cap Cut To'plam</b>\n\n"
        "Kanal yo'nalishi yoki mavzuni yozing:\n\n"
        "Misol: <code>Spider-Man</code>\n"
        "Yoki: <code>Minecraft Steve</code>\n"
        "Yoki: <code>Skibidi Toilet</code>\n\n"
        "Bot barcha materiallarni topib, to'plam holida yuboradi:"
    )
    await callback.answer()


# ── entry from character page ─────────────────────────────────────

@router.callback_query(F.data.startswith("vidkit:"))
async def on_char_video_kit(callback: CallbackQuery) -> None:
    from telegram_bot.services.character_service import char_service

    # vidkit:cat_id:char_id
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

    wait_msg = await callback.message.answer(  # type: ignore[union-attr]
        f"🎬 <b>{char.name}</b> uchun Video Kit tayyorlanmoqda...\n\n"
        "⏳ Barcha materiallar parallel qidirilmoqda (10–20 soniya)..."
    )

    await _deliver_kit(wait_msg, char.name, back_cb)
    # Remove the wait message after kit is sent (it was used as anchor)
    try:
        await wait_msg.delete()
    except Exception:
        pass


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

    wait_msg = await message.answer(
        f"🎬 <b>{query}</b> uchun Video Kit tayyorlanmoqda...\n\n"
        "⏳ Barcha materiallar parallel qidirilmoqda (10–20 soniya)..."
    )

    await _deliver_kit(message, query, back_cb)
    try:
        await wait_msg.delete()
    except Exception:
        pass
