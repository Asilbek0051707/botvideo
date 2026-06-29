"""AI Content Generator — 17-item complete engine (STEP 6).

Template-based, AI-ready: replace any service function body with an
AI API call — same signature, no router changes needed.

Callback data (all ≤64 bytes):
  menu:ai_generator — main grid
  ai:{name}         — sub-feature entry
  ag_sc:{type}      — script type
  ag_ti:{type}      — title type
  ag_de:{type}      — description type
  ag_tg:{type}      — tag type
  ag_ht:{type}      — hashtag type
  ag_th:{prov}      — thumbnail provider
  ag_im:{aspect}    — image aspect
  ag_vp:{prov}      — video provider
  ag_an:{type}      — animation type
  ag_vs:{type}      — voice script type
  ag_vo:{type}      — voice prompt type
  ag_mu:{cat}       — music category
  ag_gp:{type}      — gameplay type
  ag_cp:{type}      — content planner type
  ag_save           — save last generated content to DB
  ag_del:{id}       — delete saved item
  ag_tmpl_search    — enter search query
"""
from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="ai_generator")


# ── FSM States ────────────────────────────────────────────────────

class AIGenStates(StatesGroup):
    waiting_for_script_topic  = State()
    waiting_for_title_topic   = State()
    waiting_for_desc_topic    = State()
    waiting_for_tags_topic    = State()
    waiting_for_hashtag_topic = State()
    waiting_for_image_char    = State()
    waiting_for_thumb_char    = State()
    waiting_for_video_char    = State()
    waiting_for_anim_char     = State()
    waiting_for_voice_script  = State()
    waiting_for_voice_char    = State()
    waiting_for_planner_topic = State()
    waiting_for_package_topic = State()
    waiting_for_seo_niche     = State()
    waiting_for_tmpl_search   = State()


# ── Menu items ────────────────────────────────────────────────────

_ITEMS: list[tuple[str, str]] = [
    ("📝 Script",       "ai:script"),
    ("🏷 Title",        "ai:title"),
    ("📄 Description",  "ai:description"),
    ("#️⃣ Tags",         "ai:tags"),
    ("🔥 Hashtags",     "ai:hashtags"),
    ("🎨 Thumbnail",    "ai:thumbnail_prompt"),
    ("🖼 Image Prompt", "ai:image_prompt"),
    ("🎬 Video Prompt", "ai:video_prompt"),
    ("🎥 Animation",    "ai:animation_prompt"),
    ("🎙 Voice Script", "ai:voice_script"),
    ("🎤 Voice Prompt", "ai:voice_prompt"),
    ("🎵 Music",        "ai:music"),
    ("🎮 Gameplay",     "ai:gameplay"),
    ("📈 SEO",          "ai:seo"),
    ("📅 Planner",      "ai:planner"),
    ("📦 Full Package", "ai:package"),
    ("⭐ Saved",        "ai:saved"),
]

_TYPE_LABELS: dict[str, str] = {
    "script": "📝", "title": "🏷", "desc": "📄", "tags": "#️⃣",
    "hashtags": "🔥", "thumb_prompt": "🎨", "image_prompt": "🖼",
    "video_prompt": "🎬", "anim_prompt": "🎥", "voice_script": "🎙",
    "voice_prompt": "🎤", "seo": "📈", "planner": "📅",
}


# ── Shared helpers ────────────────────────────────────────────────

def _ai_keyboard():
    b = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        b.button(text=label, callback_data=data)
    b.adjust(3)
    add_nav_row(b, current="menu:ai_generator")
    return b.as_markup()


def _save_kb():
    b = InlineKeyboardBuilder()
    b.button(text="💾 Saqlash",       callback_data="ag_save")
    b.button(text="⬅ AI Generator",  callback_data="menu:ai_generator")
    b.adjust(2)
    return b.as_markup()


def _type_kb(items: list[tuple[str, str]], prefix: str, back: str = "menu:ai_generator"):
    b = InlineKeyboardBuilder()
    for code, label in items:
        b.button(text=label, callback_data=f"{prefix}:{code}")
    b.adjust(2)
    b.button(text="⬅ Orqaga", callback_data=back)
    return b.as_markup()


async def _set_subtype_and_ask(
    callback: CallbackQuery, state: FSMContext,
    fsm_state, label: str, prompt: str
) -> None:
    await state.set_state(fsm_state)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"{prompt}\n\nMisol: <code>Spider-Man</code>"
    )
    await callback.answer()


# ── Main menu ─────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:ai_generator")
async def on_ai_generator(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🤖 <b>AI Content Generator</b>\n\n"
        "Kontent turini tanlang — shablon asosida yaratiladi.\n"
        "<i>Har bir generator kelajakda AI bilan kuchaytiriladi.</i>",
        reply_markup=_ai_keyboard(),
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────────────
# 1. SCRIPT GENERATOR
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:script")
async def on_script(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import SCRIPT_TYPES
    b = InlineKeyboardBuilder()
    for code, label in SCRIPT_TYPES[:10]:
        b.button(text=label, callback_data=f"ag_sc:{code}")
    b.button(text="📋 Ko'proq...", callback_data="ag_sc:more")
    b.adjust(2)
    b.button(text="⬅ Orqaga", callback_data="menu:ai_generator")
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📝 <b>Script Generator</b>\n\nScript turini tanlang:",
        reply_markup=b.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_sc:"))
async def on_script_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import SCRIPT_TYPES
    code = callback.data.split(":", 1)[1]
    if code == "more":
        b = InlineKeyboardBuilder()
        for c, lbl in SCRIPT_TYPES[10:]:
            b.button(text=lbl, callback_data=f"ag_sc:{c}")
        b.adjust(2)
        b.button(text="⬅ Orqaga", callback_data="ai:script")
        await callback.message.edit_text(  # type: ignore[union-attr]
            "📝 <b>Script — Barcha turlar</b>", reply_markup=b.as_markup()
        )
        await callback.answer()
        return
    label = dict(SCRIPT_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_script_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📝 <b>Script — {label}</b>\n\n"
        "Mavzu yoki karakter nomini yozing:\n"
        "Misol: <code>Spider-Man vs Batman</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_script_topic)
async def on_script_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import generate_script
    data = await state.get_data()
    sub = data.get("sub_type", "shorts")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_script(topic, sub)
    await state.update_data(last_gen={"type": "script", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 2. TITLE GENERATOR
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:title")
async def on_title(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import TITLE_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🏷 <b>Title Generator</b>\n\nSarlavha turini tanlang:",
        reply_markup=_type_kb(TITLE_TYPES, "ag_ti"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_ti:"))
async def on_title_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import TITLE_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(TITLE_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_title_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🏷 <b>Title — {label}</b>\n\n"
        "Mavzu yoki karakter nomini yozing:\n"
        "Misol: <code>Spider-Man</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_title_topic)
async def on_title_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import generate_titles, TITLE_TYPES
    data = await state.get_data()
    sub = data.get("sub_type", "short")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    label = dict(TITLE_TYPES).get(sub, sub)
    titles = generate_titles(topic, sub)
    lines = [f"🏷 <b>Sarlavhalar — {topic} ({label})</b>\n"]
    lines += [f"{i}. <code>{t}</code>" for i, t in enumerate(titles, 1)]
    result = "\n".join(lines)
    await state.update_data(last_gen={"type": "title", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 3. DESCRIPTION GENERATOR
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:description")
async def on_description(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import DESC_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📄 <b>Description Generator</b>\n\nTavsif turini tanlang:",
        reply_markup=_type_kb(DESC_TYPES, "ag_de"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_de:"))
async def on_desc_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import DESC_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(DESC_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_desc_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📄 <b>Tavsif — {label}</b>\n\nMavzu yoki karakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_desc_topic)
async def on_desc_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import generate_description
    data = await state.get_data()
    sub = data.get("sub_type", "seo")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_description(topic, sub)
    await state.update_data(last_gen={"type": "desc", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 4. TAG GENERATOR
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:tags")
async def on_tags(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import TAG_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "#️⃣ <b>Tag Generator</b>\n\nTag turini tanlang:",
        reply_markup=_type_kb(TAG_TYPES, "ag_tg"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_tg:"))
async def on_tag_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import TAG_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(TAG_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_tags_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"#️⃣ <b>Teglar — {label}</b>\n\nMavzu yoki karakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_tags_topic)
async def on_tags_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import generate_tags, TAG_TYPES
    data = await state.get_data()
    sub = data.get("sub_type", "main")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    label = dict(TAG_TYPES).get(sub, sub)
    tags = generate_tags(topic, sub)
    result = f"#️⃣ <b>Teglar — {topic} ({label})</b>\n\n<code>{', '.join(tags)}</code>"
    await state.update_data(last_gen={"type": "tags", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 5. HASHTAG GENERATOR
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:hashtags")
async def on_hashtags(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import HASHTAG_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🔥 <b>Hashtag Generator</b>\n\nHashtag turini tanlang:",
        reply_markup=_type_kb(HASHTAG_TYPES, "ag_ht"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_ht:"))
async def on_hashtag_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import HASHTAG_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(HASHTAG_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_hashtag_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🔥 <b>Hashtaglar — {label}</b>\n\nMavzu yoki karakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_hashtag_topic)
async def on_hashtag_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import generate_hashtags, HASHTAG_TYPES
    data = await state.get_data()
    sub = data.get("sub_type", "trending")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    label = dict(HASHTAG_TYPES).get(sub, sub)
    tags = generate_hashtags(topic, sub)
    result = f"🔥 <b>Hashtaglar — {topic} ({label})</b>\n\n<code>{' '.join(tags)}</code>"
    await state.update_data(last_gen={"type": "hashtags", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 6. THUMBNAIL PROMPT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:thumbnail_prompt")
async def on_thumb_prompt(callback: CallbackQuery) -> None:
    from telegram_bot.services.prompt_gen_service import THUMB_PROVIDERS
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎨 <b>Thumbnail Prompt</b>\n\nAI provayderini tanlang:",
        reply_markup=_type_kb(THUMB_PROVIDERS, "ag_th"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_th:"))
async def on_thumb_provider(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import THUMB_PROVIDERS
    code = callback.data.split(":", 1)[1]
    label = dict(THUMB_PROVIDERS).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_thumb_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎨 <b>Thumbnail — {label}</b>\n\n"
        "Karakter nomini yozing:\n"
        "Misol: <code>Spider-Man</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_thumb_char)
async def on_thumb_char_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import generate_thumbnail_prompt
    data = await state.get_data()
    sub = data.get("sub_type", "gpt")
    char = (message.text or "").strip()
    if not char:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_thumbnail_prompt(char, sub)
    await state.update_data(last_gen={"type": "thumb_prompt", "sub": sub, "topic": char, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 7. IMAGE PROMPT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:image_prompt")
async def on_image_prompt(callback: CallbackQuery) -> None:
    from telegram_bot.services.prompt_gen_service import IMAGE_ASPECTS
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🖼 <b>Image Prompt</b>\n\nRasm turini tanlang:",
        reply_markup=_type_kb(IMAGE_ASPECTS, "ag_im"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_im:"))
async def on_image_aspect(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import IMAGE_ASPECTS
    code = callback.data.split(":", 1)[1]
    label = dict(IMAGE_ASPECTS).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_image_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🖼 <b>Image Prompt — {label}</b>\n\nKarakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_image_char)
async def on_image_char_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import generate_image_prompt
    data = await state.get_data()
    sub = data.get("sub_type", "character")
    char = (message.text or "").strip()
    if not char:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_image_prompt(char, sub)
    await state.update_data(last_gen={"type": "image_prompt", "sub": sub, "topic": char, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 8. VIDEO PROMPT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:video_prompt")
async def on_video_prompt(callback: CallbackQuery) -> None:
    from telegram_bot.services.prompt_gen_service import VIDEO_PROVIDERS
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Video Prompt</b>\n\nAI video provayderini tanlang:",
        reply_markup=_type_kb(VIDEO_PROVIDERS, "ag_vp"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_vp:"))
async def on_video_provider(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import VIDEO_PROVIDERS
    code = callback.data.split(":", 1)[1]
    label = dict(VIDEO_PROVIDERS).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_video_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎬 <b>Video Prompt — {label}</b>\n\nKarakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_video_char)
async def on_video_char_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import generate_video_prompt
    data = await state.get_data()
    sub = data.get("sub_type", "runway")
    char = (message.text or "").strip()
    if not char:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_video_prompt(char, sub)
    await state.update_data(last_gen={"type": "video_prompt", "sub": sub, "topic": char, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 9. ANIMATION PROMPT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:animation_prompt")
async def on_animation_prompt(callback: CallbackQuery) -> None:
    from telegram_bot.services.prompt_gen_service import ANIMATION_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎥 <b>Animation Prompt</b>\n\nAnimatsiya turini tanlang:",
        reply_markup=_type_kb(ANIMATION_TYPES, "ag_an"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_an:"))
async def on_anim_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import ANIMATION_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(ANIMATION_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_anim_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎥 <b>Animation — {label}</b>\n\nKarakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_anim_char)
async def on_anim_char_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import generate_animation_prompt
    data = await state.get_data()
    sub = data.get("sub_type", "idle")
    char = (message.text or "").strip()
    if not char:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_animation_prompt(char, sub)
    await state.update_data(last_gen={"type": "anim_prompt", "sub": sub, "topic": char, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 10. VOICE SCRIPT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:voice_script")
async def on_voice_script(callback: CallbackQuery) -> None:
    from telegram_bot.services.prompt_gen_service import VOICE_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎙 <b>Voice Script</b>\n\nOvoz uslubini tanlang:",
        reply_markup=_type_kb(VOICE_TYPES, "ag_vs"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_vs:"))
async def on_voice_script_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import VOICE_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(VOICE_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_voice_script)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎙 <b>Voice Script — {label}</b>\n\n"
        "Mavzuni yozing:\nMisol: <code>Spider-Man vs Batman</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_voice_script)
async def on_voice_script_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import generate_voice_script
    data = await state.get_data()
    sub = data.get("sub_type", "narration")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_voice_script(topic, sub)
    await state.update_data(last_gen={"type": "voice_script", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 11. VOICE PROMPT
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:voice_prompt")
async def on_voice_prompt(callback: CallbackQuery) -> None:
    from telegram_bot.services.prompt_gen_service import VOICE_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎤 <b>Voice Prompt</b>\n\nOvoz turini tanlang:",
        reply_markup=_type_kb(VOICE_TYPES, "ag_vo"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_vo:"))
async def on_voice_type(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import VOICE_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(VOICE_TYPES).get(code, code)
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_voice_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"🎤 <b>Voice Prompt — {label}</b>\n\nKarakter nomini yozing:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_voice_char)
async def on_voice_char_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.prompt_gen_service import generate_voice_prompt
    data = await state.get_data()
    sub = data.get("sub_type", "narration")
    char = (message.text or "").strip()
    if not char:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    result = generate_voice_prompt(char, sub)
    await state.update_data(last_gen={"type": "voice_prompt", "sub": sub, "topic": char, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 12. MUSIC SUGGESTIONS
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:music")
async def on_music(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import MUSIC_CATS
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎵 <b>Music Suggestions</b>\n\nKategoriya tanlang:",
        reply_markup=_type_kb(MUSIC_CATS, "ag_mu"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_mu:"))
async def on_music_category(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import get_music_suggestions, MUSIC_CATS
    code = callback.data.split(":", 1)[1]
    label = dict(MUSIC_CATS).get(code, code)
    tracks = get_music_suggestions(code)
    lines = [f"🎵 <b>Music — {label}</b>\n"]
    for i, t in enumerate(tracks, 1):
        lines.append(f"{i}. <b>{t['title']}</b>\n   📦 {t['source']}\n   🎭 {t['mood']} | 🥁 {t['bpm']} BPM\n")
    b = InlineKeyboardBuilder()
    b.button(text="⬅ Kategoriyalar", callback_data="ai:music")
    b.button(text="⬅ AI Generator",  callback_data="menu:ai_generator")
    b.adjust(2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ─────────────────────────────────────────────────────────────────
# 13. GAMEPLAY SUGGESTIONS
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:gameplay")
async def on_gameplay(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import GAMEPLAY_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎮 <b>Gameplay Suggestions</b>\n\nO'yin turini tanlang:",
        reply_markup=_type_kb(GAMEPLAY_TYPES, "ag_gp"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_gp:"))
async def on_gameplay_type(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_gen_service import get_gameplay_suggestions, GAMEPLAY_TYPES
    code = callback.data.split(":", 1)[1]
    label = dict(GAMEPLAY_TYPES).get(code, code)
    tips = get_gameplay_suggestions(code)
    lines = [f"🎮 <b>Gameplay Tips — {label}</b>\n"]
    lines += [f"{i}. {tip['tip']}" for i, tip in enumerate(tips, 1)]
    b = InlineKeyboardBuilder()
    b.button(text="⬅ O'yinlar",     callback_data="ai:gameplay")
    b.button(text="⬅ AI Generator", callback_data="menu:ai_generator")
    b.adjust(2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


# ─────────────────────────────────────────────────────────────────
# 14. SEO GENERATOR
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:seo")
async def on_seo(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_seo_niche)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>SEO Generator</b>\n\n"
        "Kanal yo'nalishi yoki video mavzusini yozing:\n"
        "Misol: <code>Spider-Man animation shorts</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_seo_niche)
async def on_seo_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_gen_service import generate_titles, generate_tags, generate_hashtags
    niche = (message.text or "").strip()
    await state.clear()
    if not niche:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    titles = generate_titles(niche, "seo")[:5]
    tags   = generate_tags(niche, "main")[:10]
    htags  = generate_hashtags(niche, "trending")[:8]
    result = (
        f"📈 <b>SEO Paketi: {niche}</b>\n\n"
        "<b>🏷 SEO Sarlavhalar:</b>\n"
        + "\n".join(f"  {i}. <code>{t}</code>" for i, t in enumerate(titles, 1))
        + f"\n\n<b>🔑 Asosiy teglar:</b>\n<code>{', '.join(tags)}</code>\n\n"
        f"<b># Hashtaglar:</b>\n<code>{' '.join(htags)}</code>\n\n"
        f"<b>💡 Sarlavha formulasi:</b>\n"
        f"<code>[Karakter] + [Harakat] + ! + #Shorts</code>\n"
        f"Misol: <i>{niche} vs EVERYONE! 😱 #Shorts</i>"
    )
    await state.update_data(last_gen={"type": "seo", "sub": "full", "topic": niche, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 15. CONTENT PLANNER
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:planner")
async def on_planner(callback: CallbackQuery) -> None:
    from telegram_bot.services.content_planner_service import PLANNER_TYPES
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📅 <b>Content Planner</b>\n\nReja turini tanlang:",
        reply_markup=_type_kb(PLANNER_TYPES, "ag_cp"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ag_cp:"))
async def on_planner_type(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 1)[1]
    if code == "checklist":
        from telegram_bot.services.content_planner_service import get_publishing_checklist
        b = InlineKeyboardBuilder()
        b.button(text="⬅ Planner",      callback_data="ai:planner")
        b.button(text="⬅ AI Generator", callback_data="menu:ai_generator")
        b.adjust(2)
        await callback.message.edit_text(get_publishing_checklist(), reply_markup=b.as_markup())  # type: ignore[union-attr]
        await callback.answer()
        return
    labels = {"daily": "Kunlik", "weekly": "Haftalik", "monthly": "Oylik"}
    await state.update_data(sub_type=code)
    await state.set_state(AIGenStates.waiting_for_planner_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📅 <b>Content Planner — {labels.get(code, code)}</b>\n\n"
        "Asosiy mavzuni yozing:\nMisol: <code>Spider-Man animation</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_planner_topic)
async def on_planner_topic(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.content_planner_service import (
        generate_daily_plan, generate_weekly_plan, generate_monthly_plan,
    )
    data = await state.get_data()
    sub = data.get("sub_type", "daily")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    _fn = {"daily": generate_daily_plan, "weekly": generate_weekly_plan, "monthly": generate_monthly_plan}
    result = _fn.get(sub, generate_daily_plan)(topic)
    await state.update_data(last_gen={"type": "planner", "sub": sub, "topic": topic, "content": result})
    await state.set_state(None)
    await message.answer(result, reply_markup=_save_kb())


# ─────────────────────────────────────────────────────────────────
# 16. FULL VIDEO PACKAGE
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:package")
async def on_package(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_package_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📦 <b>Full Video Package</b>\n\n"
        "Karakter yoki video mavzusini yozing —\n"
        "bot barcha generatorlarni bir vaqtda ishlatadi:\n\n"
        "Misol: <code>Spider-Man vs Batman</code>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_package_topic)
async def on_package_topic(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.package_service import (
        generate_full_package, format_package_summary, save_package,
    )
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    wait_msg = await message.answer("📦 Package generatsiya qilinmoqda...")
    await state.clear()
    pkg = await asyncio.to_thread(generate_full_package, topic)
    pkg_id = await save_package(pkg)
    summary = format_package_summary(pkg)
    b = InlineKeyboardBuilder()
    b.button(text="📝 Script",     callback_data="ai:script")
    b.button(text="🏷 Sarlavha",  callback_data="ai:title")
    b.button(text="📄 Tavsif",    callback_data="ai:description")
    b.button(text="🎨 Thumbnail", callback_data="ai:thumbnail_prompt")
    b.button(text="⭐ Saqlangan", callback_data="ai:saved")
    b.button(text="⬅ AI",        callback_data="menu:ai_generator")
    b.adjust(2, 2, 2)
    await wait_msg.edit_text(
        summary + f"\n\n💾 <i>Saqlandi #{pkg_id}</i>",
        reply_markup=b.as_markup(),
    )


# ─────────────────────────────────────────────────────────────────
# 17. SAVED TEMPLATES
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ai:saved")
async def on_saved(callback: CallbackQuery) -> None:
    from telegram_bot.services.template_library_service import list_generated, count_saved
    items = await list_generated(limit=8)
    counts = await count_saved()
    if not items:
        b = InlineKeyboardBuilder()
        b.button(text="📝 Script yarating", callback_data="ai:script")
        b.button(text="⬅ AI Generator",    callback_data="menu:ai_generator")
        b.adjust(1)
        await callback.message.edit_text(  # type: ignore[union-attr]
            "⭐ <b>Saqlangan Kontentlar</b>\n\n"
            "Hali hech narsa saqlanmagan.\n"
            "Har qanday generatordan 💾 Saqlash tugmasini bosing!",
            reply_markup=b.as_markup(),
        )
        await callback.answer()
        return
    lines = [f"⭐ <b>Saqlangan</b> ({counts['generated']} ta)\n"]
    for i, item in enumerate(items, 1):
        icon = _TYPE_LABELS.get(item.gen_type, "📄")
        dt = item.created_at.strftime("%d.%m %H:%M")
        lines.append(f"{i}. {icon} <b>{item.topic[:38]}</b> <i>({dt})</i>")
    b = InlineKeyboardBuilder()
    for i, item in enumerate(items, 1):
        b.button(text=f"🗑 {i}", callback_data=f"ag_del:{item.id}")
    b.adjust(4)
    b.button(text="🔍 Qidirish",    callback_data="ag_tmpl_search")
    b.button(text="⬅ AI Generator", callback_data="menu:ai_generator")
    b.adjust(4, 2)
    await callback.message.edit_text("\n".join(lines), reply_markup=b.as_markup())  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "ag_tmpl_search")
async def on_tmpl_search_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_tmpl_search)
    await callback.message.edit_text("🔍 <b>Qidirish</b>\n\nMavzu yoki kalit so'z yozing:")  # type: ignore[union-attr]
    await callback.answer()


@router.message(AIGenStates.waiting_for_tmpl_search)
async def on_tmpl_search_input(message: Message, state: FSMContext) -> None:
    from telegram_bot.services.template_library_service import search_generated
    query = (message.text or "").strip()
    await state.clear()
    if not query:
        await message.answer("❌ Bo'sh. Qayta urining.")
        return
    results = await search_generated(query, limit=6)
    if not results:
        b = InlineKeyboardBuilder()
        b.button(text="⬅ Saqlangan", callback_data="ai:saved")
        await message.answer(f"🔍 <b>'{query}'</b> — topilmadi.", reply_markup=b.as_markup())
        return
    lines = [f"🔍 <b>'{query}'</b> — {len(results)} ta\n"]
    for i, r in enumerate(results, 1):
        icon = _TYPE_LABELS.get(r.gen_type, "📄")
        lines.append(f"{i}. {icon} <b>{r.topic[:42]}</b>")
    b = InlineKeyboardBuilder()
    for i, r in enumerate(results, 1):
        b.button(text=f"🗑 {i}", callback_data=f"ag_del:{r.id}")
    b.adjust(3)
    b.button(text="⬅ Saqlangan", callback_data="ai:saved")
    b.button(text="⬅ AI",        callback_data="menu:ai_generator")
    b.adjust(3, 2)
    await message.answer("\n".join(lines), reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("ag_del:"))
async def on_delete_generated(callback: CallbackQuery) -> None:
    from telegram_bot.services.template_library_service import delete_generated
    item_id = int(callback.data.split(":", 1)[1])
    await delete_generated(item_id)
    await callback.answer("🗑 O'chirildi")
    await on_saved(callback)


# ─────────────────────────────────────────────────────────────────
# SAVE HANDLER — shared by all generators
# ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ag_save")
async def on_save_last(callback: CallbackQuery, state: FSMContext) -> None:
    from telegram_bot.services.template_library_service import save_generated
    data = await state.get_data()
    last = data.get("last_gen")
    if not last:
        await callback.answer("❌ Saqlash uchun kontent yo'q", show_alert=True)
        return
    item_id = await save_generated(
        gen_type=last.get("type", "unknown"),
        sub_type=last.get("sub", "default"),
        topic=last.get("topic", ""),
        content=last.get("content", ""),
    )
    await callback.answer(f"✅ Saqlandi #{item_id} — ⭐ Saved bo'limida ko'ring")
