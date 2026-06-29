"""Material Library router — Saved Assets, Favorites, Collections, Quick Save.

Registered BEFORE materials.router so that mat:fav and mat:saved callbacks
are intercepted here before the generic mat:* handler in materials.py runs.

Callback scheme:
  mat:fav          — favorites list
  mat:saved        — all saved assets
  mlib:search      — search saved assets (FSM)
  mlib:col         — collections list
  mlib:col_new     — create new collection (FSM)
  mlib:col:{id}    — show collection contents
  mlib:history     — search history
  mlib:history_clr — clear search history
  mast_save        — quick-save: ask title (FSM)
  mast_del:{id}    — delete asset
  mast_fav:{id}    — toggle favorite star
  mast_col:{id}    — add asset to collection picker
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router(name="material_library")

_TYPE_ICONS: dict[str, str] = {
    "png": "🖼", "gif": "🎞", "mp4": "🎥", "webm": "🎬",
    "music": "🎵", "sfx": "🔊", "voice": "🎤", "bg": "🌄",
    "capcut": "📱", "premiere": "🎬", "ae": "🎞",
    "thumb_ref": "🎨", "prompt": "💡", "unknown": "📄",
}


class MatLibStates(StatesGroup):
    waiting_for_save_title  = State()
    waiting_for_save_url    = State()
    waiting_for_col_name    = State()
    waiting_for_lib_search  = State()


def _back_lib_kb():
    b = InlineKeyboardBuilder()
    b.button(text="⭐ Favorites",    callback_data="mat:fav")
    b.button(text="🗂 Saved",         callback_data="mat:saved")
    b.button(text="📦 Material",      callback_data="menu:materials")
    b.adjust(2, 1)
    return b.as_markup()


# ─────────────────────────────────────────────────────────────────
# ⭐ FAVORITES
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "mat:fav")
async def on_favorites(callback: CallbackQuery) -> None:
    from telegram_bot.services.asset_service import list_favorites, count_assets

    items = await list_favorites(limit=10)
    counts = await count_assets()

    b = InlineKeyboardBuilder()
    if not items:
        b.button(text="💾 Yangi saqlash", callback_data="mast_save")
        b.button(text="⬅ Materiallar",   callback_data="menu:materials")
        b.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "⭐ <b>Sevimlilar</b>\n\n"
            "Hali hech narsa yo'q.\n"
            "Qidiruvdan keyin <b>💾 Saqlash</b> tugmasini bosing.",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"⭐ <b>Sevimlilar</b> ({counts['favorites']} ta)\n"]
    for i, a in enumerate(items, 1):
        icon = _TYPE_ICONS.get(a.asset_type, "📄")
        lines.append(f"{i}. {icon} <b>{a.title[:42]}</b>")
        if a.source_url:
            lines.append(f"   🔗 <a href='{a.source_url}'>{a.source_name or 'Link'}</a>")

    for i, a in enumerate(items, 1):
        b.button(text=f"🗑 {i}", callback_data=f"mast_del:{a.id}")
    b.adjust(4)
    b.button(text="🔍 Qidirish",    callback_data="mlib:search")
    b.button(text="🗂 Saqlangan",    callback_data="mat:saved")
    b.button(text="⬅ Materiallar",  callback_data="menu:materials")
    b.adjust(4, 3)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines),
        reply_markup=b.as_markup(),
        disable_web_page_preview=True,
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────────────
# 🗂 SAVED ASSETS
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "mat:saved")
async def on_saved_assets(callback: CallbackQuery) -> None:
    from telegram_bot.services.asset_service import list_assets, count_assets

    items = await list_assets(limit=8)
    counts = await count_assets()

    b = InlineKeyboardBuilder()
    if not items:
        b.button(text="💾 Yangi saqlash", callback_data="mast_save")
        b.button(text="⬅ Materiallar",   callback_data="menu:materials")
        b.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "🗂 <b>Saqlangan Assetlar</b>\n\n"
            "Hali hech narsa saqlanmagan.\n"
            "Material qidiring va <b>💾 Saqlash</b> tugmasini bosing.",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"🗂 <b>Saqlangan</b> ({counts['total']} ta | ⭐ {counts['favorites']} sevimli)\n"]
    for i, a in enumerate(items, 1):
        icon = _TYPE_ICONS.get(a.asset_type, "📄")
        star = "⭐" if a.is_favorite else ""
        lines.append(f"{i}. {icon}{star} <b>{a.title[:40]}</b>")

    for i, a in enumerate(items, 1):
        b.button(text=f"⭐{i}" if a.is_favorite else f"☆{i}", callback_data=f"mast_fav:{a.id}")
    b.adjust(4)
    for i, a in enumerate(items, 1):
        b.button(text=f"🗑 {i}", callback_data=f"mast_del:{a.id}")
    b.adjust(4, 4)
    b.button(text="💾 Saqlash",     callback_data="mast_save")
    b.button(text="🔍 Qidirish",    callback_data="mlib:search")
    b.button(text="📁 To'plamlar",  callback_data="mlib:col")
    b.button(text="⬅ Materiallar", callback_data="menu:materials")
    b.adjust(4, 4, 2, 2)

    await callback.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines), reply_markup=b.as_markup()
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────────────
# 💾 QUICK SAVE — FSM
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "mast_save")
async def on_save_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MatLibStates.waiting_for_save_title)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "💾 <b>Asset Saqlash</b>\n\n"
        "Asset nomini yozing:\n"
        "Misol: <code>Spider-Man PNG transparent background</code>"
    )
    await callback.answer()


@router.message(MatLibStates.waiting_for_save_title)
async def on_save_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer("❌ Bo'sh. Nom yozing:")
        return
    await state.update_data(save_title=title)
    await state.set_state(MatLibStates.waiting_for_save_url)
    await message.answer(
        f"✅ <b>{title}</b>\n\n"
        "Manba URL yoki qisqa tavsif yozing:\n"
        "Misol: <code>https://freepngimg.com/...</code>\n"
        "Yoki: <code>Google qidiruvdan topildi</code>"
    )


@router.message(MatLibStates.waiting_for_save_url)
async def on_save_url(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.asset_service import save_asset

    url_or_note = (message.text or "").strip()
    data = await state.get_data()
    title = data.get("save_title", "Nomsiz asset")
    await state.clear()

    is_url = url_or_note.startswith("http")
    source_url  = url_or_note if is_url else ""
    notes       = "" if is_url else url_or_note

    asset_id = await save_asset(
        title=title,
        source_url=source_url,
        notes=notes,
        asset_type="unknown",
        category="general",
    )

    b = InlineKeyboardBuilder()
    b.button(text="⭐ Sevimlilarga",  callback_data=f"mast_fav:{asset_id}")
    b.button(text="🗂 Saqlangan",     callback_data="mat:saved")
    b.button(text="⬅ Materiallar",   callback_data="menu:materials")
    b.adjust(2, 1)
    await message.answer(
        f"✅ Saqlandi <b>#{asset_id}</b>: {title}\n"
        f"{'🔗 ' + source_url if source_url else '📝 ' + notes}",
        reply_markup=b.as_markup(),
    )


# ─────────────────────────────────────────────────────────────────
# 🗑 DELETE / ⭐ FAVORITE TOGGLE
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("mast_del:"))
async def on_delete_asset(callback: CallbackQuery) -> None:
    from telegram_bot.services.asset_service import delete_asset

    asset_id = int(callback.data.split(":", 1)[1])
    await delete_asset(asset_id)
    await callback.answer("🗑 O'chirildi")
    await on_saved_assets(callback)


@router.callback_query(F.data.startswith("mast_fav:"))
async def on_toggle_favorite(callback: CallbackQuery) -> None:
    from telegram_bot.services.asset_service import toggle_favorite

    asset_id = int(callback.data.split(":", 1)[1])
    is_now_fav = await toggle_favorite(asset_id)
    emoji = "⭐ Sevimlilarga qo'shildi" if is_now_fav else "☆ Sevimlilardan olib tashlandi"
    await callback.answer(emoji)
    await on_saved_assets(callback)


# ─────────────────────────────────────────────────────────────────
# 🔍 SEARCH SAVED ASSETS
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "mlib:search")
async def on_lib_search_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MatLibStates.waiting_for_lib_search)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔍 <b>Asset Qidirish</b>\n\nNom, karakter yoki kalit so'z yozing:"
    )
    await callback.answer()


@router.message(MatLibStates.waiting_for_lib_search)
async def on_lib_search_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.asset_service import search_assets

    query = (message.text or "").strip()
    await state.clear()
    if not query:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return

    results = await search_assets(query, limit=8)
    if not results:
        b = InlineKeyboardBuilder()
        b.button(text="🗂 Saqlangan",   callback_data="mat:saved")
        b.button(text="⬅ Materiallar", callback_data="menu:materials")
        b.adjust(2)
        await message.answer(
            f"🔍 <b>'{query}'</b> — topilmadi.", reply_markup=b.as_markup()
        )
        return

    lines = [f"🔍 <b>'{query}'</b> — {len(results)} ta\n"]
    for i, a in enumerate(results, 1):
        icon = _TYPE_ICONS.get(a.asset_type, "📄")
        star = "⭐" if a.is_favorite else ""
        lines.append(f"{i}. {icon}{star} <b>{a.title[:42]}</b>")

    b = InlineKeyboardBuilder()
    for i, a in enumerate(results, 1):
        b.button(text=f"🗑 {i}", callback_data=f"mast_del:{a.id}")
    b.adjust(4)
    b.button(text="🗂 Saqlangan",   callback_data="mat:saved")
    b.button(text="⬅ Materiallar", callback_data="menu:materials")
    b.adjust(4, 2)
    await message.answer("\n".join(lines), reply_markup=b.as_markup())


# ─────────────────────────────────────────────────────────────────
# 📁 COLLECTIONS
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "mlib:col")
async def on_collections(callback: CallbackQuery) -> None:
    from telegram_bot.services.collection_service import list_collections, PRESET_COLLECTIONS

    cols = await list_collections(limit=12)

    b = InlineKeyboardBuilder()
    if cols:
        lines = ["📁 <b>To'plamlar</b>\n"]
        for c in cols:
            lines.append(f"• <b>{c.name}</b> <i>({c.category})</i>")
            b.button(text=c.name[:30], callback_data=f"mlib:col:{c.id}")
        b.adjust(2)
    else:
        lines = [
            "📁 <b>To'plamlar</b>\n",
            "Hali to'plam yo'q. Namuna to'plamlar:\n",
        ]
        for name, _ in PRESET_COLLECTIONS:
            lines.append(f"• {name}")

    b.button(text="➕ Yangi to'plam",  callback_data="mlib:col_new")
    b.button(text="🗂 Saqlangan",      callback_data="mat:saved")
    b.button(text="⬅ Materiallar",    callback_data="menu:materials")
    b.adjust(2, 1, 2)

    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "mlib:col_new")
async def on_col_new_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MatLibStates.waiting_for_col_name)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📁 <b>Yangi To'plam</b>\n\n"
        "To'plam nomini yozing:\n"
        "Misol: <code>Marvel Pack</code>"
    )
    await callback.answer()


@router.message(MatLibStates.waiting_for_col_name)
async def on_col_name_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.collection_service import create_collection

    name = (message.text or "").strip()
    await state.clear()
    if not name:
        await message.answer("❌ Bo'sh nom. Qayta urining.")
        return

    col_id = await create_collection(name)
    b = InlineKeyboardBuilder()
    b.button(text="📁 To'plamlar",  callback_data="mlib:col")
    b.button(text="⬅ Materiallar", callback_data="menu:materials")
    b.adjust(2)
    await message.answer(
        f"✅ To'plam yaratildi: <b>{name}</b> (#{col_id})",
        reply_markup=b.as_markup(),
    )


@router.callback_query(F.data.startswith("mlib:col:"))
async def on_collection_view(callback: CallbackQuery) -> None:
    from telegram_bot.services.collection_service import list_collection_assets, list_collections

    col_id = int(callback.data.split(":", 2)[2])
    assets = await list_collection_assets(col_id, limit=10)

    # Get collection name
    cols = await list_collections(limit=50)
    col_name = next((c.name for c in cols if c.id == col_id), f"To'plam #{col_id}")

    b = InlineKeyboardBuilder()
    if not assets:
        lines = [f"📁 <b>{col_name}</b>\n\nHali asset yo'q."]
    else:
        lines = [f"📁 <b>{col_name}</b> ({len(assets)} ta)\n"]
        for i, a in enumerate(assets, 1):
            icon = _TYPE_ICONS.get(a.asset_type, "📄")
            lines.append(f"{i}. {icon} <b>{a.title[:42]}</b>")
        for i, a in enumerate(assets, 1):
            b.button(text=f"🗑 {i}", callback_data=f"mast_del:{a.id}")
        b.adjust(4)

    b.button(text="⬅ To'plamlar",  callback_data="mlib:col")
    b.button(text="⬅ Materiallar", callback_data="menu:materials")
    b.adjust(2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ─────────────────────────────────────────────────────────────────
# 🕓 SEARCH HISTORY
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "mlib:history")
async def on_history(callback: CallbackQuery) -> None:
    from telegram_bot.services.asset_service import list_search_history

    user_id = callback.from_user.id if callback.from_user else 0
    items = await list_search_history(user_id, limit=10)

    b = InlineKeyboardBuilder()
    if not items:
        b.button(text="⬅ Materiallar", callback_data="menu:materials")
        await callback.message.edit_text(  # type: ignore[union-attr]
            "🕓 <b>Qidiruv Tarixi</b>\n\nHali qidiruv yo'q.",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return

    lines = [f"🕓 <b>Qidiruv Tarixi</b> (so'nggi {len(items)} ta)\n"]
    for i, h in enumerate(items, 1):
        dt = h.created_at.strftime("%d.%m %H:%M")
        lines.append(f"{i}. <code>{h.query[:40]}</code> — {h.asset_type} <i>({dt})</i>")

    b.button(text="🗑 Tarixni tozalash", callback_data="mlib:history_clr")
    b.button(text="⬅ Materiallar",      callback_data="menu:materials")
    b.adjust(1, 1)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "mlib:history_clr")
async def on_clear_history(callback: CallbackQuery) -> None:
    from telegram_bot.services.asset_service import clear_search_history

    user_id = callback.from_user.id if callback.from_user else 0
    count = await clear_search_history(user_id)
    await callback.answer(f"🗑 {count} ta qidiruv o'chirildi")
    await on_history(callback)
