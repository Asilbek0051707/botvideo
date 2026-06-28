"""Character detail router — full material/prompt/ideas pages."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.db.repository import favourite_repo, project_repo
from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard
from telegram_bot.services.character_service import char_service
from telegram_bot.services.prompt_service import prompt_service
from telegram_bot.services.search_service import search_service
from telegram_bot.services.video_ideas_service import video_ideas_service

router = Router(name="characters")

# ── material button definitions ───────────────────────────────────

_MATERIALS = [
    ("🖼 PNG",           "png"),
    ("🟢 Green Screen",  "gs"),
    ("🎬 Animation",     "anim"),
    ("🎞 GIF",           "gif"),
    ("🎥 Videos",        "vid"),
    ("🌄 Background",    "bg"),
    ("🎵 Music",         "mus"),
    ("🔊 Sound Effects", "sfx"),
    ("🎤 AI Voices",     "voice"),
    ("✨ Effects",       "fx"),
    ("🖌 Thumbnail",     "thumb"),
]


def _char_page_keyboard(cat_id: str, char_id: str, is_fav: bool = False):
    """Full character page keyboard: materials + prompts + ideas + nav."""
    back_cb = f"trends:{cat_id}:0"
    curr_cb = f"char:{cat_id}:{char_id}"

    builder = InlineKeyboardBuilder()
    # Material buttons
    for label, mat in _MATERIALS:
        builder.button(text=label, callback_data=f"charmat:{mat}:{cat_id}:{char_id}")
    builder.adjust(2)

    # Action row
    fav_label = "💛 Saved" if is_fav else "⭐ Favourite"
    builder.row(
        InlineKeyboardButton(text=fav_label,      callback_data=f"charfav:{cat_id}:{char_id}"),
        InlineKeyboardButton(text="🎨 AI Prompts", callback_data=f"charprompts:{cat_id}:{char_id}"),
        InlineKeyboardButton(text="📝 Video Ideas",callback_data=f"charvideas:{cat_id}:{char_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🎬 Video Kit",     callback_data=f"vidkit:{cat_id}:{char_id}"),
        InlineKeyboardButton(text="🌐 Search Online", callback_data=f"charmat:search:{cat_id}:{char_id}"),
        InlineKeyboardButton(text="📁 New Project",   callback_data=f"charprojcreate:{cat_id}:{char_id}"),
    )
    add_nav_row(builder, current=curr_cb, parent=back_cb)
    return builder.as_markup()


def _material_search_keyboard(char_name: str, mat_code: str, cat_id: str, char_id: str):
    """Provider link buttons + nav for a material search page."""
    back_cb = f"char:{cat_id}:{char_id}"
    curr_cb = f"charmat:{mat_code}:{cat_id}:{char_id}"

    builder = InlineKeyboardBuilder()
    for label, url in search_service.build_links(char_name, mat_code):
        builder.button(text=label, url=url)
    builder.adjust(1)
    add_nav_row(builder, current=curr_cb, parent=back_cb)
    return builder.as_markup()


# ── character detail page ─────────────────────────────────────────


@router.callback_query(F.data.startswith("char:"))
async def on_character(callback: CallbackQuery) -> None:
    parts = callback.data.split(":", 2)   # char:cat_id:char_id
    if len(parts) < 3:
        await callback.answer("Bad callback")
        return
    _, cat_id, char_id = parts

    cat  = char_service.get_category(cat_id)
    char = char_service.get_character(cat_id, char_id)

    if not char:
        await callback.answer("Character not found", show_alert=True)
        return

    is_fav = await favourite_repo.is_saved("character", f"{cat_id}:{char_id}")
    cat_name = cat.name if cat else cat_id.title()
    cat_icon = cat.icon if cat else "🎭"

    aliases_text = ""
    if char.aliases:
        aliases_text = f"\n🔤 <i>Also known as: {', '.join(char.aliases[:3])}</i>"

    text = (
        f"{cat_icon} <b>{char.name}</b>\n"
        f"📂 Category: <b>{cat_name}</b>{aliases_text}\n\n"
        "Choose a material type or action:"
    )
    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=_char_page_keyboard(cat_id, char_id, is_fav),
    )
    await callback.answer()


# ── favourite toggle ──────────────────────────────────────────────


@router.callback_query(F.data.startswith("charfav:"))
async def on_char_favourite(callback: CallbackQuery) -> None:
    parts = callback.data.split(":", 2)   # charfav:cat_id:char_id
    if len(parts) < 3:
        await callback.answer()
        return
    _, cat_id, char_id = parts

    char = char_service.get_character(cat_id, char_id)
    if not char:
        await callback.answer("Not found", show_alert=True)
        return

    fav_id = f"{cat_id}:{char_id}"
    already = await favourite_repo.is_saved("character", fav_id)

    if already:
        await favourite_repo.remove("character", fav_id)
        await callback.answer(f"💔 Removed from favourites: {char.name}")
    else:
        cat = char_service.get_category(cat_id)
        await favourite_repo.add(
            item_type="character",
            item_id=fav_id,
            item_name=char.name,
            category_id=cat_id,
            meta={"cat_name": cat.name if cat else cat_id},
        )
        await callback.answer(f"⭐ Saved to favourites: {char.name}")

    # Refresh the character page
    is_fav = await favourite_repo.is_saved("character", fav_id)
    cat  = char_service.get_category(cat_id)
    cat_name = cat.name if cat else cat_id.title()
    cat_icon = cat.icon if cat else "🎭"
    char_obj = char_service.get_character(cat_id, char_id)
    aliases_text = ""
    if char_obj and char_obj.aliases:
        aliases_text = f"\n🔤 <i>Also known as: {', '.join(char_obj.aliases[:3])}</i>"
    text = (
        f"{cat_icon} <b>{char.name}</b>\n"
        f"📂 Category: <b>{cat_name}</b>{aliases_text}\n\n"
        "Choose a material type or action:"
    )
    try:
        await callback.message.edit_text(  # type: ignore[union-attr]
            text,
            reply_markup=_char_page_keyboard(cat_id, char_id, is_fav),
        )
    except Exception:
        pass


# ── material search page ──────────────────────────────────────────


_MAT_NAMES = {
    "png":    "PNG Images",    "gs":    "Green Screen",
    "anim":   "Animations",   "gif":   "GIF",
    "vid":    "Videos",       "bg":    "Backgrounds",
    "mus":    "Music",        "sfx":   "Sound Effects",
    "voice":  "AI Voices",   "fx":    "Visual Effects",
    "thumb":  "Thumbnails",   "search":"Search Online",
}

IMAGE_CODES = {"png", "bg", "thumb", "gif"}

_MAT_ICONS = {
    "png": "🖼", "gs": "🟢", "anim": "🎬", "gif": "🎞", "vid": "🎥",
    "bg": "🌄", "mus": "🎵", "sfx": "🔊", "voice": "🎤", "fx": "✨",
    "thumb": "🖌", "search": "🌐",
}


@router.callback_query(F.data.startswith("charmat:"))
async def on_char_material(callback: CallbackQuery) -> None:
    # charmat:mat_code:cat_id:char_id
    parts = callback.data.split(":", 3)
    if len(parts) < 4:
        await callback.answer()
        return
    _, mat_code, cat_id, char_id = parts

    # AI Prompts and Video Ideas get their own pages
    if mat_code == "prompts":
        await _show_prompts(callback, cat_id, char_id)
        return
    if mat_code == "videas":
        await _show_video_ideas(callback, cat_id, char_id)
        return

    from telegram_bot.services.real_search import (
        IMAGE_MAT_CODES, download_images, search_for_material,
    )
    from aiogram.types import BufferedInputFile, InputMediaPhoto

    char = char_service.get_character(cat_id, char_id)
    if not char:
        await callback.answer("Not found", show_alert=True)
        return

    mat_name = _MAT_NAMES.get(mat_code, mat_code)
    mat_icon = _MAT_ICONS.get(mat_code, "📦")
    back_cb = f"char:{cat_id}:{char_id}"
    curr_cb = f"charmat:{mat_code}:{cat_id}:{char_id}"

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{mat_icon} <b>{mat_name}</b> — {char.name}\n\n🔍 Qidirilmoqda..."
    )
    await callback.answer()

    results = await search_for_material(char.name, mat_code, limit=4)

    if not results:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{mat_icon} <b>{mat_name}</b> — {char.name}\n\n"
            "❌ Natija topilmadi. Keyinroq urinib ko'ring.",
            reply_markup=get_nav_keyboard(curr_cb, back_cb),
        )
        return

    # Image types — download and send as actual photos
    if mat_code in IMAGE_CODES:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{mat_icon} <b>{mat_name}</b> — {char.name}\n\n⬇️ Rasmlar yuklanmoqda..."
        )
        photos = await download_images(results, limit=4)
        if photos:
            media = []
            for i, (data, title) in enumerate(photos):
                ext = "gif" if mat_code == "gif" else "png"
                f = BufferedInputFile(data, filename=f"img_{i+1}.{ext}")
                cap = f"{mat_icon} <b>{mat_name}</b> — {char.name}" if i == 0 else None
                media.append(InputMediaPhoto(media=f, caption=cap, parse_mode="HTML"))
            await callback.message.answer_media_group(media)  # type: ignore[union-attr]
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="🔄 Yangilash", callback_data=curr_cb),
                InlineKeyboardButton(text="⬅ Orqaga",    callback_data=back_cb),
            )
            await callback.message.edit_text(  # type: ignore[union-attr]
                f"{mat_icon} <b>{mat_name}</b> — {char.name}\n\n✅ {len(photos)} ta rasm yuborildi",
                reply_markup=builder.as_markup(),
            )
            return

    # Video types — show YouTube thumbnails as photo album
    from telegram_bot.services.real_search import VIDEO_MAT_CODES, download_yt_thumbnails
    if mat_code in VIDEO_MAT_CODES:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"{mat_icon} <b>{mat_name}</b> — {char.name}\n\n⬇️ Video ko'rinishlar yuklanmoqda..."
        )
        yt_photos = await download_yt_thumbnails(results, limit=4)
        if yt_photos:
            media = []
            for i, (data, r) in enumerate(yt_photos):
                if i == 0:
                    cap = f"{mat_icon} <b>{mat_name}</b> — {char.name}\n<i>{r.title}</i>"
                else:
                    cap = f"<i>{r.title}</i>"
                if r.extra:
                    cap += f"\n{r.extra}"
                media.append(InputMediaPhoto(
                    media=BufferedInputFile(data, filename=f"vid_{i}.jpg"),
                    caption=cap,
                    parse_mode="HTML",
                ))
            await callback.message.answer_media_group(media)  # type: ignore[union-attr]
            builder = InlineKeyboardBuilder()
            for i, (_, r) in enumerate(yt_photos, 1):
                builder.button(text=f"▶️ {i}. Ko'rish", url=r.url)
            builder.adjust(2)
            builder.row(
                InlineKeyboardButton(text="🔄 Yangilash", callback_data=curr_cb),
                InlineKeyboardButton(text="⬅ Orqaga",    callback_data=back_cb),
            )
            await callback.message.edit_text(  # type: ignore[union-attr]
                f"{mat_icon} <b>{mat_name}</b> — {char.name}\n\n✅ {len(yt_photos)} ta video topildi:",
                reply_markup=builder.as_markup(),
            )
            return

    # Text/link fallback
    lines = [f"{mat_icon} <b>{mat_name}</b> — {char.name}\n"]
    for i, r in enumerate(results, 1):
        src = f" <i>({r.source})</i>" if r.source else ""
        extra = f"\n   {r.extra}" if r.extra else ""
        lines.append(f"{i}. <b>{r.title}</b>{src}{extra}")

    builder = InlineKeyboardBuilder()
    for i, r in enumerate(results, 1):
        builder.button(text=f"{i}. {r.title[:35]}{'…' if len(r.title) > 35 else ''}", url=r.url)
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="🔄 Yangilash", callback_data=curr_cb),
        InlineKeyboardButton(text="⬅ Orqaga",   callback_data=back_cb),
    )

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines),
        reply_markup=builder.as_markup(),
    )


# ── AI prompts page ───────────────────────────────────────────────


async def _show_prompts(callback: CallbackQuery, cat_id: str, char_id: str) -> None:
    char = char_service.get_character(cat_id, char_id)
    cat  = char_service.get_category(cat_id)
    if not char:
        await callback.answer("Not found", show_alert=True)
        return

    cat_name = cat.name if cat else cat_id.title()
    text = prompt_service.format_for_telegram(char.name, cat_name)
    back_cb = f"char:{cat_id}:{char_id}"
    curr_cb = f"charprompts:{cat_id}:{char_id}"

    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=get_nav_keyboard(current=curr_cb, parent=back_cb),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("charprompts:"))
async def on_char_prompts(callback: CallbackQuery) -> None:
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    _, cat_id, char_id = parts
    await _show_prompts(callback, cat_id, char_id)


# ── video ideas page ──────────────────────────────────────────────


async def _show_video_ideas(callback: CallbackQuery, cat_id: str, char_id: str) -> None:
    char = char_service.get_character(cat_id, char_id)
    cat  = char_service.get_category(cat_id)
    if not char:
        await callback.answer("Not found", show_alert=True)
        return

    cat_name = cat.name if cat else cat_id.title()
    text = video_ideas_service.format_for_telegram(char.name, cat_name)
    back_cb = f"char:{cat_id}:{char_id}"
    curr_cb = f"charvideas:{cat_id}:{char_id}"

    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=get_nav_keyboard(current=curr_cb, parent=back_cb),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("charvideas:"))
async def on_char_video_ideas(callback: CallbackQuery) -> None:
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    _, cat_id, char_id = parts
    await _show_video_ideas(callback, cat_id, char_id)


# ── create project ────────────────────────────────────────────────


@router.callback_query(F.data.startswith("charprojcreate:"))
async def on_char_create_project(callback: CallbackQuery) -> None:
    # charprojcreate:cat_id:char_id
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    _, cat_id, char_id = parts

    char = char_service.get_character(cat_id, char_id)
    cat  = char_service.get_category(cat_id)
    if not char:
        await callback.answer("Not found", show_alert=True)
        return

    cat_name = cat.name if cat else cat_id.title()
    proj = await project_repo.create(
        name=f"{char.name} — {cat_name}",
        category_id=cat_id,
        category_name=cat_name,
        character_id=char_id,
        character_name=char.name,
    )

    back_cb = f"char:{cat_id}:{char_id}"
    text = (
        f"✅ <b>Project created!</b>\n\n"
        f"📁 <b>Name:</b> {proj.name}\n"
        f"📂 <b>Category:</b> {cat_name}\n"
        f"👤 <b>Character:</b> {char.name}\n"
        f"🆔 <b>ID:</b> #{proj.id}\n\n"
        "View all projects in 📁 Projects menu."
    )
    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=get_nav_keyboard(current=back_cb, parent=back_cb),
    )
    await callback.answer(f"✅ Project #{proj.id} created!")
