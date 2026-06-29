"""Video Kit — complete material pack for Cap Cut / Premiere / After Effects.

Delivery strategy:
  Images (PNG/BG/GIF) → media albums via URL  (Telegram fetches, ~instant)
  Green Screen        → YouTube link          (no download, instant)
  Music               → YouTube links         (no download, instant)
  SFX                 → YouTube links         (no download, instant)

Total time: ~15s (search) + ~5s (send) = done in ≤25s, never hangs.
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

from telegram_bot.keyboards.navigation import get_nav_keyboard

router = Router(name="video_kit")


class VideoKitStates(StatesGroup):
    waiting_for_topic = State()


# ── helpers ────────────────────────────────────────────────────────

async def _safe(coro, timeout: float = 15.0) -> list:
    """Run search coroutine with hard timeout — never hangs."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except Exception:
        return []


async def _send_image_album(message: Message, results: list, label: str) -> int:
    """Send images via URL — Telegram fetches them directly, zero download time."""
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
    try:
        await asyncio.wait_for(message.answer_media_group(media), timeout=20)
        return len(media)
    except Exception:
        # Fallback: send as clickable links
        lines = [label]
        for r in results[:4]:
            lines.append(f"• <a href='{r.url}'>{r.title[:60]}</a>")
        try:
            await message.answer("\n".join(lines))
        except Exception:
            pass
        return 0


async def _send_yt_links(message: Message, results: list, label: str) -> int:
    """Send YouTube results as clickable links — instant, no download."""
    if not results:
        return 0
    lines = [f"{label}\n"]
    for r in results:
        extra = f" <i>{r.extra}</i>" if getattr(r, "extra", "") else ""
        lines.append(f"▶ <a href='{r.url}'>{r.title[:60]}</a>{extra}")
    try:
        await message.answer("\n".join(lines))
        return len(results)
    except Exception:
        return 0


# ── main kit delivery ──────────────────────────────────────────────

async def _deliver_kit(message: Message, query: str, back_cb: str, user_id: int = 0) -> None:
    from telegram_bot.services.real_search import search_for_material, search_youtube

    status = await message.answer(
        f"📦 <b>{query}</b>\n\n"
        "🔍 Materiallar qidirilmoqda..."
    )

    # ── 1. Parallel search — all 6 types at once, 15s max each ──
    png_r, bg_r, gif_r, gs_r, mus_r, sfx_r = await asyncio.gather(
        _safe(search_for_material(query, "png", limit=4, user_id=user_id)),
        _safe(search_for_material(query, "bg",  limit=4, user_id=user_id)),
        _safe(search_for_material(query, "gif", limit=3, user_id=user_id)),
        _safe(search_youtube(f"{query} green screen free",             limit=3, user_id=user_id)),
        _safe(search_youtube(f"{query} background music no copyright", limit=4, user_id=user_id)),
        _safe(search_youtube(f"{query} sound effect free",             limit=3, user_id=user_id)),
    )

    found = sum(len(x) for x in [png_r, bg_r, gif_r, gs_r, mus_r, sfx_r])
    await status.edit_text(
        f"📦 <b>{query}</b>\n\n"
        f"✅ {found} ta material topildi. Yuborilmoqda..."
    )

    counts = {"png": 0, "bg": 0, "gif": 0, "gs": 0, "mus": 0, "sfx": 0}

    # ── 2. Send image albums in parallel via URL (no download) ──
    img_results = await asyncio.gather(
        _send_image_album(message, png_r, "🖼 <b>PNG Rasmlar</b>"),
        _send_image_album(message, bg_r,  "🌄 <b>Backgroundlar</b>"),
        _send_image_album(message, gif_r, "🎞 <b>GIF / Animatsiyalar</b>"),
        return_exceptions=True,
    )
    counts["png"] = img_results[0] if isinstance(img_results[0], int) else 0
    counts["bg"]  = img_results[1] if isinstance(img_results[1], int) else 0
    counts["gif"] = img_results[2] if isinstance(img_results[2], int) else 0

    # ── 3. Send YT links for video/music/sfx (instant, no download) ──
    yt_results = await asyncio.gather(
        _send_yt_links(message, gs_r,  "🟢 <b>Green Screen videolar:</b>"),
        _send_yt_links(message, mus_r, "🎵 <b>Musiqa (no copyright):</b>"),
        _send_yt_links(message, sfx_r, "🔊 <b>Sound Effects:</b>"),
        return_exceptions=True,
    )
    counts["gs"]  = yt_results[0] if isinstance(yt_results[0], int) else 0
    counts["mus"] = yt_results[1] if isinstance(yt_results[1], int) else 0
    counts["sfx"] = yt_results[2] if isinstance(yt_results[2], int) else 0

    # ── 4. Final summary ──
    total = sum(counts.values())

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Yangilash",  callback_data=back_cb)
    builder.button(text="🏠 Bosh menyu", callback_data="menu:main")
    builder.adjust(2)

    if total == 0:
        summary = (
            f"⚠️ <b>{query}</b> uchun material topilmadi.\n\n"
            "Boshqa mavzu bilan urinib ko'ring."
        )
    else:
        summary = (
            f"✅ <b>{query}</b> — Video Kit tayyor!\n\n"
            f"🖼 PNG rasmlar: {counts['png']} ta\n"
            f"🌄 Backgroundlar: {counts['bg']} ta\n"
            f"🎞 GIF/Animatsiya: {counts['gif']} ta\n"
            f"🟢 Green Screen: {counts['gs']} ta havolа\n"
            f"🎵 Musiqa: {counts['mus']} ta havola\n"
            f"🔊 Sound Effects: {counts['sfx']} ta havola\n\n"
            f"📦 Jami: <b>{total}</b> ta material"
        )

    await status.edit_text(summary, reply_markup=builder.as_markup())


# ── entry: materials menu ──────────────────────────────────────────

@router.callback_query(F.data == "menu:video_kit")
async def on_video_kit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VideoKitStates.waiting_for_topic)
    await state.update_data(back_cb="menu:video_kit")
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Cap Cut To'plam</b>\n\n"
        "Karakter yoki mavzuni yozing:\n\n"
        "Misol: <code>Spider-Man</code>\n"
        "Yoki: <code>Minecraft Steve</code>\n\n"
        "🖼 PNG · Background · GIF → rasm sifatida\n"
        "🟢 Green Screen · 🎵 Musiqa · 🔊 SFX → YouTube havolalar"
    )
    await callback.answer()


# ── entry: character page ──────────────────────────────────────────

@router.callback_query(F.data.startswith("vidkit:"))
async def on_char_video_kit(callback: CallbackQuery) -> None:
    from telegram_bot.services.character_service import char_service

    parts = callback.data.split(":", 2)  # type: ignore[union-attr]
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
    uid = callback.from_user.id if callback.from_user else 0  # type: ignore[union-attr]

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎬 <b>{char.name}</b> — materiallar qidirilmoqda..."
    )
    await _deliver_kit(callback.message, char.name, back_cb, user_id=uid)  # type: ignore[arg-type]


# ── text input handler ─────────────────────────────────────────────

@router.message(VideoKitStates.waiting_for_topic)
async def on_kit_topic(message: Message, state: FSMContext) -> None:
    data  = await state.get_data()
    await state.clear()
    query = (message.text or "").strip()
    if not query:
        await message.answer("❌ Bo'sh so'rov. Qayta urining.")
        return
    uid      = message.from_user.id if message.from_user else 0  # type: ignore[union-attr]
    back_cb  = data.get("back_cb", "menu:video_kit")
    await _deliver_kit(message, query, back_cb, user_id=uid)
