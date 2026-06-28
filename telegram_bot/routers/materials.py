"""Material Finder — real search via DuckDuckGo + yt-dlp, results shown in bot."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile, CallbackQuery, InputMediaPhoto, Message, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.services.real_search import IMAGE_MAT_CODES

router = Router(name="materials")


class MatSearchStates(StatesGroup):
    waiting_for_query = State()


_ITEMS: list[tuple[str, str]] = [
    ("🎬 Cap Cut To'plam",  "menu:video_kit"),   # ← new kit button
    ("🖼 PNG Images",       "mat:png"),
    ("🟢 Green Screen",     "mat:gs"),
    ("🎞 Animations",       "mat:anim"),
    ("🎞 GIF",              "mat:gif"),
    ("🎥 Videos",           "mat:vid"),
    ("🌄 Backgrounds",      "mat:bg"),
    ("🎵 Music",            "mat:mus"),
    ("🔊 Sound Effects",    "mat:sfx"),
    ("🎤 AI Voices",        "mat:voice"),
    ("✨ Visual Effects",   "mat:fx"),
    ("🖌 Thumbnail Assets", "mat:thumb"),
    ("🎨 AI Prompts",       "mat:prompts"),
    ("📂 Material Packs",   "mat:pack"),
    ("🌐 Internet Search",  "mat:search"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}

_MAT_HINT: dict[str, str] = {
    "mat:png":    "Masalan: <code>Spider-Man</code> yoki <code>Minecraft Steve</code>",
    "mat:gs":     "Masalan: <code>Spider-Man</code> yoki <code>Batman</code>",
    "mat:anim":   "Masalan: <code>Goku animation</code>",
    "mat:gif":    "Masalan: <code>Sonic running</code>",
    "mat:vid":    "Masalan: <code>Spider-Man fight scene</code>",
    "mat:bg":     "Masalan: <code>Minecraft world background</code>",
    "mat:mus":    "Masalan: <code>epic battle music</code> yoki <code>kids cartoon</code>",
    "mat:sfx":    "Masalan: <code>sword hit sound</code>",
    "mat:voice":  "Masalan: <code>Goku voice</code>",
    "mat:fx":     "Masalan: <code>fire explosion effect</code>",
    "mat:thumb":  "Masalan: <code>Spider-Man thumbnail</code>",
    "mat:prompts":"Masalan: <code>Spider-Man Midjourney prompt</code>",
    "mat:pack":   "Masalan: <code>cartoon character pack</code>",
    "mat:search": "Nima qidiryapsiz?",
}


def _materials_keyboard():
    builder = InlineKeyboardBuilder()
    # First item (Video Kit) gets full width
    kit_label, kit_data = _ITEMS[0]
    builder.button(text=kit_label, callback_data=kit_data)
    builder.adjust(1)
    # Rest in 2 columns
    for label, data in _ITEMS[1:]:
        builder.button(text=label, callback_data=data)
    builder.adjust(1, *([2] * ((len(_ITEMS) - 1 + 1) // 2 + 1)))
    add_nav_row(builder, current="menu:materials")
    return builder.as_markup()


def _results_keyboard(results, current: str):
    builder = InlineKeyboardBuilder()
    for i, r in enumerate(results, 1):
        label = f"{i}. {r.title[:35]}{'…' if len(r.title) > 35 else ''}"
        builder.button(text=label, url=r.url)
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="🔄 Qayta qidirish", callback_data=current),
        InlineKeyboardButton(text="🏠 Home",           callback_data="menu:main"),
    )
    return builder.as_markup()


# ── main grid ─────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:materials")
async def on_materials(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📦 <b>Material Finder</b>\n\nMaterial turini tanlang:",
        reply_markup=_materials_keyboard(),
    )
    await callback.answer()


# ── material type selected → ask query ───────────────────────────

@router.callback_query(F.data.startswith("mat:"))
async def on_material_item(callback: CallbackQuery, state: FSMContext) -> None:
    mat_cb = callback.data
    label = _LABEL.get(mat_cb, "Material")
    mat_code = mat_cb.split(":")[1]
    hint = _MAT_HINT.get(mat_cb, "Qidiruv so'zini yozing:")

    await state.set_state(MatSearchStates.waiting_for_query)
    await state.update_data(mat_code=mat_code, mat_label=label, mat_cb=mat_cb)

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{label}\n\n"
        f"🔍 Nima qidiramiz?\n\n"
        f"{hint}"
    )
    await callback.answer()


# ── user types query → real search → show results ─────────────────

@router.message(MatSearchStates.waiting_for_query)
async def on_mat_query(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.real_search import search_for_material

    data = await state.get_data()
    await state.clear()

    query = (message.text or "").strip()
    mat_code = data.get("mat_code", "search")
    mat_label = data.get("mat_label", "Material")
    mat_cb = data.get("mat_cb", "menu:materials")

    if not query:
        await message.answer("❌ Bo'sh so'rov. Qayta urinib ko'ring.")
        return

    wait_msg = await message.answer(f"🔍 <b>{query}</b> qidirilmoqda...")

    results = await search_for_material(query, mat_code, limit=4)

    if not results:
        await wait_msg.edit_text(
            f"❌ <b>{query}</b> bo'yicha natija topilmadi.\n\nBoshqa kalit so'z bilan urining.",
            reply_markup=get_nav_keyboard(mat_cb, "menu:materials"),
        )
        return

    # Image types — download and send as actual photos
    if mat_code in IMAGE_MAT_CODES:
        from telegram_bot.services.real_search import download_images
        await wait_msg.edit_text(f"⬇️ <b>{query}</b> rasmlari yuklanmoqda...")
        photos = await download_images(results, limit=4)
        if photos:
            await wait_msg.delete()
            media = []
            for i, (data, title) in enumerate(photos):
                ext = "gif" if mat_code == "gif" else "png"
                f = BufferedInputFile(data, filename=f"image_{i+1}.{ext}")
                cap = f"{mat_label} — <b>{query}</b>" if i == 0 else None
                media.append(InputMediaPhoto(media=f, caption=cap, parse_mode="HTML"))
            await message.answer_media_group(media)
            builder = InlineKeyboardBuilder()
            builder.button(text="🔄 Qayta qidirish", callback_data=mat_cb)
            builder.button(text="🏠 Home",           callback_data="menu:main")
            builder.adjust(2)
            await message.answer("Yuqoridagi rasmlar:", reply_markup=builder.as_markup())
            return

    # Video types — download YouTube thumbnails and send as photo album
    from telegram_bot.services.real_search import VIDEO_MAT_CODES, download_yt_thumbnails
    if mat_code in VIDEO_MAT_CODES:
        await wait_msg.edit_text(f"⬇️ <b>{query}</b> — video ko'rinishlar yuklanmoqda...")
        yt_photos = await download_yt_thumbnails(results, limit=4)
        if yt_photos:
            await wait_msg.delete()
            media = []
            for i, (data, r) in enumerate(yt_photos):
                if i == 0:
                    cap = f"{mat_label} — <b>{query}</b>\n<i>{r.title}</i>"
                else:
                    cap = f"<i>{r.title}</i>"
                if r.extra:
                    cap += f"\n{r.extra}"
                media.append(InputMediaPhoto(
                    media=BufferedInputFile(data, filename=f"vid_{i+1}.jpg"),
                    caption=cap,
                    parse_mode="HTML",
                ))
            await message.answer_media_group(media)
            builder = InlineKeyboardBuilder()
            for i, (_, r) in enumerate(yt_photos, 1):
                builder.button(text=f"▶️ {i}. Ko'rish", url=r.url)
            builder.adjust(2)
            builder.button(text="🔄 Qayta qidirish", callback_data=mat_cb)
            builder.button(text="🏠 Home",           callback_data="menu:main")
            builder.adjust(2)
            await message.answer("Videolarni ko'rish:", reply_markup=builder.as_markup())
            return

    # Fallback — show link buttons
    lines = [f"{mat_label} — <b>{query}</b>\n"]
    for i, r in enumerate(results, 1):
        source = f" <i>({r.source})</i>" if r.source else ""
        extra = f"\n   {r.extra}" if r.extra else ""
        lines.append(f"{i}. <b>{r.title}</b>{source}{extra}")

    await wait_msg.edit_text(
        "\n".join(lines),
        reply_markup=_results_keyboard(results, mat_cb),
    )
