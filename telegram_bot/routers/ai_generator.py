"""AI Generator router — 🤖 template-based content generators with FSM."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.keyboards.navigation import add_nav_row, get_nav_keyboard

router = Router(name="ai_generator")


class AIGenStates(StatesGroup):
    waiting_for_script_topic = State()
    waiting_for_title_topic = State()
    waiting_for_desc_topic = State()
    waiting_for_tags_topic = State()
    waiting_for_image_char = State()
    waiting_for_thumb_char = State()
    waiting_for_video_char = State()
    waiting_for_voice_char = State()
    waiting_for_seo_niche = State()


_ITEMS: list[tuple[str, str]] = [
    ("📝 Script Generator",   "ai:script"),
    ("🏷 Title Generator",    "ai:title"),
    ("📄 Description",        "ai:description"),
    ("#️⃣ Tags Generator",     "ai:tags"),
    ("🖼 Image Prompt",       "ai:image_prompt"),
    ("🎨 Thumbnail Prompt",   "ai:thumbnail_prompt"),
    ("🎬 Video Prompt",       "ai:video_prompt"),
    ("🎤 Voice Prompt",       "ai:voice_prompt"),
    ("📈 SEO Generator",      "ai:seo"),
]

_LABEL: dict[str, str] = {data: label for label, data in _ITEMS}


def _ai_keyboard():
    builder = InlineKeyboardBuilder()
    for label, data in _ITEMS:
        builder.button(text=label, callback_data=data)
    builder.adjust(3)
    add_nav_row(builder, current="menu:ai_generator")
    return builder.as_markup()


def _back_keyboard(current: str):
    return get_nav_keyboard(current=current, parent="menu:ai_generator")


# ── main grid ─────────────────────────────────────────────────────


@router.callback_query(F.data == "menu:ai_generator")
async def on_ai_generator(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🤖 <b>AI Generator</b>\n\nChoose a generator:",
        reply_markup=_ai_keyboard(),
    )
    await callback.answer()


# ── Script Generator ──────────────────────────────────────────────


@router.callback_query(F.data == "ai:script")
async def on_script(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_script_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📝 <b>Script Generator</b>\n\n"
        "Enter character name + video concept\n"
        "Example: <i>Spider-Man vs Batman</i>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_script_topic)
async def on_script_input(message: Message, state: FSMContext) -> None:
    topic = (message.text or "").strip()
    await state.clear()
    if not topic:
        await message.answer("❌ Empty. Tap Script Generator to try again.")
        return

    script = (
        f"📝 <b>Script: {topic}</b>\n\n"
        f"<b>[HOOK - 0:00–0:03]</b>\n"
        f"\"Wait... {topic} just changed EVERYTHING!\"\n"
        f"[Show dramatic moment / unexpected action]\n\n"
        f"<b>[SETUP - 0:03–0:08]</b>\n"
        f"[Introduce the main conflict or challenge]\n"
        f"\"{topic} faces the ultimate challenge...\"\n\n"
        f"<b>[ACTION - 0:08–0:35]</b>\n"
        f"[Main content — show the battle / transformation / challenge]\n"
        f"[3–5 rapid-cut scenes, each 3–5 seconds]\n"
        f"[Add sound effects and music]\n\n"
        f"<b>[TWIST - 0:35–0:50]</b>\n"
        f"\"But then... [unexpected outcome]!\"\n"
        f"[Surprising ending that makes viewer comment]\n\n"
        f"<b>[CTA - 0:50–0:60]</b>\n"
        f"\"Comment who would WIN! 👇\"\n"
        f"\"Like & Follow for more {topic}! 🔔\""
    )
    await message.answer(script, reply_markup=_back_keyboard("ai:script"))


# ── Title Generator ───────────────────────────────────────────────


@router.callback_query(F.data == "ai:title")
async def on_title(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_title_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🏷 <b>Title Generator</b>\n\n"
        "Enter character or video topic:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_title_topic)
async def on_title_input(message: Message, state: FSMContext) -> None:
    topic = (message.text or "").strip()
    await state.clear()
    if not topic:
        await message.answer("❌ Empty. Tap Title Generator to try again.")
        return

    titles = (
        f"🏷 <b>Titles for: {topic}</b>\n\n"
        f"1. {topic} vs ALL Characters! 😱 #Shorts\n"
        f"2. {topic} Evolution 1990–2024 🔥 #Shorts\n"
        f"3. {topic} BABY vs ADULT Form! 👶 #Shorts\n"
        f"4. {topic} IMPOSSIBLE Challenge! ⚡ #Shorts\n"
        f"5. Who is the STRONGEST {topic}? 🏆 #Shorts\n"
        f"6. {topic} Funny Moments Compilation 😂 #Shorts\n"
        f"7. {topic} REAL Power Level Revealed! 💪 #Shorts\n"
        f"8. {topic} vs EVIL Version! 👿 #Shorts"
    )
    await message.answer(titles, reply_markup=_back_keyboard("ai:title"))


# ── Description Generator ─────────────────────────────────────────


@router.callback_query(F.data == "ai:description")
async def on_description(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_desc_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📄 <b>Description Generator</b>\n\n"
        "Enter your video topic or character:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_desc_topic)
async def on_desc_input(message: Message, state: FSMContext) -> None:
    topic = (message.text or "").strip()
    await state.clear()
    if not topic:
        await message.answer("❌ Empty. Tap Description to try again.")
        return

    desc = (
        f"📄 <b>Description: {topic}</b>\n\n"
        f"<code>🎮 Welcome to our {topic} video!\n\n"
        f"In this video, we explore the world of {topic} "
        f"in an epic and entertaining way!\n\n"
        f"👇 COMMENT below: Who is your favorite?\n\n"
        f"🔔 Subscribe for daily {topic} content!\n"
        f"👍 Like if you enjoyed this video!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"#Shorts #{topic.replace(' ', '')} #YouTube #Trending #Animation\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"© All characters belong to their respective owners.</code>"
    )
    await message.answer(desc, reply_markup=_back_keyboard("ai:description"))


# ── Tags Generator ────────────────────────────────────────────────


@router.callback_query(F.data == "ai:tags")
async def on_tags(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_tags_topic)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "#️⃣ <b>Tags Generator</b>\n\n"
        "Enter your character or video topic:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_tags_topic)
async def on_tags_input(message: Message, state: FSMContext) -> None:
    topic = (message.text or "").strip()
    await state.clear()
    if not topic:
        await message.answer("❌ Empty. Tap Tags Generator to try again.")
        return

    safe = topic.replace(" ", "")
    tags = (
        f"#️⃣ <b>Tags for: {topic}</b>\n\n"
        f"<code>{topic}, {safe}, {topic} shorts, {topic} animation, "
        f"{topic} funny, {topic} vs, {topic} evolution, {topic} 2024, "
        f"{topic} cartoon, {topic} characters, {topic} compilation, "
        f"youtube shorts, animation shorts, cartoon shorts, kids animation, "
        f"trending shorts, viral shorts, funny animation, "
        f"character shorts, gaming shorts, anime shorts, "
        f"short video, shorts 2024, trending 2024</code>"
    )
    await message.answer(tags, reply_markup=_back_keyboard("ai:tags"))


# ── Image Prompt ──────────────────────────────────────────────────


@router.callback_query(F.data == "ai:image_prompt")
async def on_image_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_image_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🖼 <b>Image Prompt Generator</b>\n\n"
        "Enter the character name:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_image_char)
async def on_image_char_input(message: Message, state: FSMContext) -> None:
    char = (message.text or "").strip()
    await state.clear()
    if not char:
        await message.answer("❌ Empty. Tap Image Prompt to try again.")
        return

    prompt = (
        f"🖼 <b>Image Prompt: {char}</b>\n\n"
        f"<code>{char} full body character, "
        f"high quality digital art, vibrant colors, "
        f"transparent background, PNG format, "
        f"4K resolution, clean linework, "
        f"no text, no watermark, studio lighting, "
        f"anime/cartoon style, sharp details</code>"
    )
    await message.answer(prompt, reply_markup=_back_keyboard("ai:image_prompt"))


# ── Thumbnail Prompt ──────────────────────────────────────────────


@router.callback_query(F.data == "ai:thumbnail_prompt")
async def on_thumb_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_thumb_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎨 <b>Thumbnail Prompt Generator</b>\n\n"
        "Enter the character name:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_thumb_char)
async def on_thumb_char_input(message: Message, state: FSMContext) -> None:
    char = (message.text or "").strip()
    await state.clear()
    if not char:
        await message.answer("❌ Empty. Tap Thumbnail Prompt to try again.")
        return

    prompt = (
        f"🎨 <b>Thumbnail Prompt: {char}</b>\n\n"
        f"<code>{char} dramatic close-up face expression, "
        f"shocked or angry emotion, "
        f"YouTube thumbnail style, epic cinematic lighting, "
        f"vibrant neon colors, high contrast, "
        f"text space on the right side, "
        f"16:9 aspect ratio, 1280x720px, "
        f"photorealistic or hyper-detailed cartoon, "
        f"no text included, professional quality</code>"
    )
    await message.answer(prompt, reply_markup=_back_keyboard("ai:thumbnail_prompt"))


# ── Video Prompt ──────────────────────────────────────────────────


@router.callback_query(F.data == "ai:video_prompt")
async def on_video_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_video_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎬 <b>Video Prompt Generator</b>\n\n"
        "Enter the character name:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_video_char)
async def on_video_char_input(message: Message, state: FSMContext) -> None:
    char = (message.text or "").strip()
    await state.clear()
    if not char:
        await message.answer("❌ Empty. Tap Video Prompt to try again.")
        return

    prompt = (
        f"🎬 <b>Video Prompt: {char}</b>\n\n"
        f"<code>{char} action sequence, "
        f"cinematic camera movement, dynamic angles, "
        f"smooth animation, 24fps, "
        f"vibrant color grading, dramatic lighting, "
        f"epic background environment, "
        f"no text overlay, looping motion, "
        f"YouTube Shorts format 9:16 vertical, "
        f"30–60 seconds duration</code>"
    )
    await message.answer(prompt, reply_markup=_back_keyboard("ai:video_prompt"))


# ── Voice Prompt ──────────────────────────────────────────────────


@router.callback_query(F.data == "ai:voice_prompt")
async def on_voice_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_voice_char)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "🎤 <b>Voice Prompt Generator</b>\n\n"
        "Enter the character name:"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_voice_char)
async def on_voice_char_input(message: Message, state: FSMContext) -> None:
    char = (message.text or "").strip()
    await state.clear()
    if not char:
        await message.answer("❌ Empty. Tap Voice Prompt to try again.")
        return

    prompt = (
        f"🎤 <b>Voice Prompt: {char}</b>\n\n"
        f"<code>{char} character voice, "
        f"energetic and expressive tone, "
        f"clear pronunciation, "
        f"suitable for kids YouTube content, "
        f"dramatic and exciting delivery, "
        f"no background noise, "
        f"natural speech rhythm, "
        f"English language, "
        f"studio quality audio</code>"
    )
    await message.answer(prompt, reply_markup=_back_keyboard("ai:voice_prompt"))


# ── SEO Generator ─────────────────────────────────────────────────


@router.callback_query(F.data == "ai:seo")
async def on_seo(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIGenStates.waiting_for_seo_niche)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📈 <b>SEO Generator</b>\n\n"
        "Enter your channel niche or topic\n"
        "Example: <i>Minecraft kids animation</i>"
    )
    await callback.answer()


@router.message(AIGenStates.waiting_for_seo_niche)
async def on_seo_input(message: Message, state: FSMContext) -> None:
    niche = (message.text or "").strip()
    await state.clear()
    if not niche:
        await message.answer("❌ Empty. Tap SEO Generator to try again.")
        return

    safe = niche.replace(" ", "")
    seo = (
        f"📈 <b>SEO Package: {niche}</b>\n\n"
        f"<b>🔑 Primary keywords:</b>\n"
        f"<code>{niche} shorts, {niche} 2024, {niche} animation, "
        f"best {niche}, {niche} funny moments</code>\n\n"
        f"<b>#️⃣ Hashtags (copy-paste):</b>\n"
        f"<code>#{safe} #Shorts #Animation #Trending "
        f"#{safe}2024 #KidsAnimation #YouTubeShorts "
        f"#ViralShorts #Cartoon #FunnyMoments</code>\n\n"
        f"<b>📌 Channel keywords:</b>\n"
        f"<code>{niche}, {niche} channel, {niche} videos, "
        f"best {niche} shorts, {niche} compilation, "
        f"daily {niche}, {niche} funny, {niche} animation</code>\n\n"
        f"<b>💡 Title formula:</b>\n"
        f"<code>[Character] + [Action/Emotion] + ! + #Shorts</code>\n"
        f"Example: <i>{niche} vs EVERYONE! 😱 #Shorts</i>"
    )
    await message.answer(seo, reply_markup=_back_keyboard("ai:seo"))
