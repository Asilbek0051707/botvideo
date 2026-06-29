"""Integrations router — External Provider Management.

Entry: menu:integrations  (also linked from set:integrations in settings)

Main menu (6 items):
  📡 Providers    int:providers
  🩺 Health Check int:health
  📋 Logs         int:logs
  🗄 Cache        int:cache
  📊 Sync History int:sync
  ⚙ Settings     int:cfg

Provider detail: int:detail:{slug}
Health check one: int:hc1:{slug}
Clear cache: int:cc:{slug}  /  int:ccall
Toggle enable: int:tog:{slug}
"""
from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="integrations")

_MENU: list[tuple[str, str]] = [
    ("📡 Provayderlar",  "int:providers"),
    ("🩺 Health Check",  "int:health"),
    ("📋 Loglar",        "int:logs"),
    ("🗄 Kesh",          "int:cache"),
    ("📊 Sync tarixi",   "int:sync"),
    ("⚙ Sozlamalar",    "int:cfg"),
]

_CATEGORY_LABEL = {
    "ai":     "🤖 AI",
    "trends": "📈 Trends",
    "video":  "🎬 Video",
    "search": "🔍 Search",
    "audio":  "🎵 Audio",
    "news":   "📰 News",
    "general":"🌐 General",
}


# ── helpers ────────────────────────────────────────────────────────────

def _main_kb():
    b = InlineKeyboardBuilder()
    for label, data in _MENU:
        b.button(text=label, callback_data=data)
    b.adjust(2)
    add_nav_row(b, current="menu:integrations")
    return b.as_markup()


def _back_integration_kb():
    return get_nav_keyboard(current="int:back", parent="menu:integrations")


def _status_icon(status: str, is_configured: bool) -> str:
    if not is_configured:
        return "⚪"
    if status == "ok":
        return "✅"
    if status == "error":
        return "❌"
    return "🔄"


# ── main menu ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:integrations")
async def on_integrations_menu(cb: CallbackQuery) -> None:
    from telegram_bot.services.integration_manager import manager
    from telegram_bot.services.cache_service import cache_stats

    providers  = manager.list_all()
    configured = sum(1 for p in providers if p.is_configured)
    stats      = await cache_stats()

    text = (
        "🔌 <b>Tashqi integratsiyalar</b>\n\n"
        f"📡 Jami provayderlar: <b>{len(providers)}</b>\n"
        f"✅ Sozlangan: <b>{configured}</b>\n"
        f"⚪ Sozlanmagan: <b>{len(providers) - configured}</b>\n"
        f"🗄 Kesh yozuvlari: <b>{stats.get('live', 0)}</b>\n\n"
        "Boshqarish uchun tugmani tanlang:"
    )
    await cb.message.edit_text(text, reply_markup=_main_kb())  # type: ignore[union-attr]
    await cb.answer()


# ── providers list ─────────────────────────────────────────────────────

@router.callback_query(F.data == "int:providers")
async def on_providers_list(cb: CallbackQuery) -> None:
    from telegram_bot.services.integration_manager import manager, list_provider_rows

    rows = await list_provider_rows()
    prov_map = {r.slug: r for r in rows}

    b = InlineKeyboardBuilder()
    lines = ["📡 <b>Barcha provayderlar</b>\n"]

    for p in manager.list_all():
        row = prov_map.get(p.config.slug)
        status = row.last_status if row else "unknown"
        icon   = _status_icon(status, p.is_configured)
        cat    = _CATEGORY_LABEL.get(p.config.category, p.config.category)
        cfg_txt = "✅ Sozlangan" if p.is_configured else "⚪ Sozlanmagan"
        lines.append(f"{icon} <b>{p.config.name}</b> ({cat})\n   {cfg_txt}")
        b.button(text=f"{icon} {p.config.name}", callback_data=f"int:detail:{p.config.slug}")

    b.adjust(1)
    b.row()
    b.button(text="◀ Orqaga", callback_data="menu:integrations")
    await cb.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines), reply_markup=b.as_markup()
    )
    await cb.answer()


# ── provider detail ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("int:detail:"))
async def on_provider_detail(cb: CallbackQuery) -> None:
    from telegram_bot.services.integration_manager import manager, list_provider_rows

    slug = cb.data.split("int:detail:", 1)[1]  # type: ignore[union-attr]
    prov = manager.get(slug)
    if not prov:
        await cb.answer("Provayder topilmadi", show_alert=True)
        return

    rows = await list_provider_rows()
    prov_map = {r.slug: r for r in rows}
    row    = prov_map.get(slug)
    status = row.last_status if row else "unknown"
    icon   = _status_icon(status, prov.is_configured)

    checked_str = "—"
    if row and row.last_checked:
        checked_str = row.last_checked.strftime("%Y-%m-%d %H:%M")

    text = (
        f"{icon} <b>{prov.config.name}</b>\n\n"
        f"🔑 Env: <code>{prov.config.api_key_env or '—'}</code>\n"
        f"✅ Holat: {'Sozlangan' if prov.is_configured else 'Sozlanmagan'}\n"
        f"📊 Status: <b>{status}</b>\n"
        f"🕐 Tekshirilgan: {checked_str}\n"
        f"⏱ Timeout: {prov.config.timeout}s\n"
        f"🔄 Retry: {prov.config.retry_count}x\n"
        f"🗄 Cache TTL: {prov.config.cache_ttl}s\n"
    )
    if row and row.last_message:
        text += f"\n💬 <i>{row.last_message}</i>"

    b = InlineKeyboardBuilder()
    b.button(text="🩺 Tekshirish", callback_data=f"int:hc1:{slug}")
    b.button(text="🗄 Keshni tozalash", callback_data=f"int:cc:{slug}")
    b.adjust(2)
    b.row()
    b.button(text="◀ Provayderlar", callback_data="int:providers")
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


# ── health check all ───────────────────────────────────────────────────

@router.callback_query(F.data == "int:health")
async def on_health_check_all(cb: CallbackQuery) -> None:
    await cb.message.edit_text("🩺 <b>Health check boshlandi...</b>")  # type: ignore[union-attr]
    await cb.answer()

    from telegram_bot.services.integration_manager import manager

    results = await manager.health_check_all()
    lines = ["🩺 <b>Health Check Natijalari</b>\n"]
    for slug, (ok, msg) in results.items():
        prov = manager.get(slug)
        name = prov.config.name if prov else slug
        icon = "✅" if ok else "❌"
        lines.append(f"{icon} <b>{name}</b>\n   <i>{msg}</i>")

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Qayta tekshirish", callback_data="int:health")
    b.button(text="◀ Orqaga", callback_data="menu:integrations")
    b.adjust(2)
    await cb.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines), reply_markup=b.as_markup()
    )


# ── health check one ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("int:hc1:"))
async def on_health_check_one(cb: CallbackQuery) -> None:
    slug = cb.data.split("int:hc1:", 1)[1]  # type: ignore[union-attr]
    await cb.message.edit_text(f"🩺 <b>{slug}</b> tekshirilmoqda...")  # type: ignore[union-attr]
    await cb.answer()

    from telegram_bot.services.integration_manager import manager

    ok, msg = await manager.health_check_one(slug)
    icon = "✅" if ok else "❌"
    prov = manager.get(slug)
    name = prov.config.name if prov else slug

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Qayta", callback_data=f"int:hc1:{slug}")
    b.button(text="◀ Detail", callback_data=f"int:detail:{slug}")
    b.adjust(2)
    await cb.message.edit_text(  # type: ignore[union-attr]
        f"{icon} <b>{name}</b>\n\n{msg}",
        reply_markup=b.as_markup(),
    )


# ── logs ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "int:logs")
async def on_logs(cb: CallbackQuery) -> None:
    from telegram_bot.services.integration_manager import list_logs

    logs = await list_logs(limit=15)
    if not logs:
        text = "📋 <b>Loglar</b>\n\nHozircha hech narsa yo'q."
    else:
        lines = ["📋 <b>So'nggi 15 ta log yozuvi</b>\n"]
        for log in logs:
            icon = "ℹ" if log.level == "info" else ("⚠" if log.level == "warn" else "❌")
            ts   = log.created_at.strftime("%m-%d %H:%M")
            lines.append(f"{icon} [{ts}] <b>{log.provider_slug}</b>: {log.message[:100]}")
        text = "\n".join(lines)

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Yangilash", callback_data="int:logs")
    b.button(text="◀ Orqaga",    callback_data="menu:integrations")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


# ── cache ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "int:cache")
async def on_cache_info(cb: CallbackQuery) -> None:
    from telegram_bot.services.cache_service import cache_stats

    stats = await cache_stats()
    text = (
        "🗄 <b>Kesh holati</b>\n\n"
        f"📦 Jami yozuv: <b>{stats['total']}</b>\n"
        f"✅ Faol: <b>{stats['live']}</b>\n"
        f"⌛ Muddati o'tgan: <b>{stats['expired']}</b>\n"
    )
    b = InlineKeyboardBuilder()
    b.button(text="🗑 Hammasini tozalash", callback_data="int:ccall")
    b.button(text="🧹 Muddati o'tganlarni",callback_data="int:ccexp")
    b.button(text="🔄 Yangilash",          callback_data="int:cache")
    b.button(text="◀ Orqaga",              callback_data="menu:integrations")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


@router.callback_query(F.data.startswith("int:cc:"))
async def on_clear_provider_cache(cb: CallbackQuery) -> None:
    slug = cb.data.split("int:cc:", 1)[1]  # type: ignore[union-attr]
    from telegram_bot.services.cache_service import clear_provider_cache

    count = await clear_provider_cache(slug)
    await cb.answer(f"✅ {count} ta kesh yozuvi o'chirildi", show_alert=True)
    # refresh detail
    from aiogram.types import CallbackQuery as CQ
    cb.data = f"int:detail:{slug}"  # type: ignore[union-attr]
    await on_provider_detail(cb)


@router.callback_query(F.data == "int:ccall")
async def on_clear_all_cache(cb: CallbackQuery) -> None:
    from telegram_bot.services.cache_service import clear_all_cache

    count = await clear_all_cache()
    await cb.answer(f"✅ {count} ta kesh yozuvi tozalandi", show_alert=True)
    cb.data = "int:cache"  # type: ignore[union-attr]
    await on_cache_info(cb)


@router.callback_query(F.data == "int:ccexp")
async def on_clear_expired_cache(cb: CallbackQuery) -> None:
    from telegram_bot.services.cache_service import cleanup_expired

    count = await cleanup_expired()
    await cb.answer(f"✅ {count} ta muddati o'tgan yozuv o'chirildi", show_alert=True)
    cb.data = "int:cache"  # type: ignore[union-attr]
    await on_cache_info(cb)


# ── sync history ───────────────────────────────────────────────────────

@router.callback_query(F.data == "int:sync")
async def on_sync_history(cb: CallbackQuery) -> None:
    from telegram_bot.services.integration_manager import list_sync_history

    history = await list_sync_history(limit=10)
    if not history:
        text = "📊 <b>Sync tarixi</b>\n\nHozircha hech narsa yo'q."
    else:
        lines = ["📊 <b>So'nggi 10 ta sync</b>\n"]
        for h in history:
            icon = "✅" if h.status == "success" else "❌"
            ts   = h.started_at.strftime("%m-%d %H:%M")
            lines.append(
                f"{icon} [{ts}] <b>{h.provider_slug}</b> — {h.sync_type}"
                f" ({h.records_synced} yozuv)"
            )
        text = "\n".join(lines)

    b = InlineKeyboardBuilder()
    b.button(text="🔄 Yangilash", callback_data="int:sync")
    b.button(text="◀ Orqaga",    callback_data="menu:integrations")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())  # type: ignore[union-attr]
    await cb.answer()


# ── settings ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "int:cfg")
async def on_integration_cfg(cb: CallbackQuery) -> None:
    from telegram_bot.services.integration_manager import manager
    import os

    lines = ["⚙ <b>Provayder sozlamalari</b>\n", "<i>(.env orqali boshqariladi)</i>\n"]
    for p in manager.list_all():
        if p.config.api_key_env:
            val = os.getenv(p.config.api_key_env)
            icon = "✅" if val else "⚪"
            masked = ("***" + val[-4:]) if val else "— (o'rnatilmagan)"
            lines.append(f"{icon} <code>{p.config.api_key_env}</code> = {masked}")
        else:
            lines.append(f"✅ <b>{p.config.name}</b> — kalit shart emas")

    b = InlineKeyboardBuilder()
    b.button(text="◀ Orqaga", callback_data="menu:integrations")
    await cb.message.edit_text(  # type: ignore[union-attr]
        "\n".join(lines), reply_markup=b.as_markup()
    )
    await cb.answer()


# ── settings link (from set:integrations) ─────────────────────────────

@router.callback_query(F.data == "set:integrations")
async def on_set_integrations_redirect(cb: CallbackQuery) -> None:
    cb.data = "menu:integrations"  # type: ignore[union-attr]
    await on_integrations_menu(cb)
