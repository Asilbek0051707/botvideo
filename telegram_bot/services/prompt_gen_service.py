"""AI Prompt Generator Service — provider-specific prompt templates.

All generators return plain text prompts ready to paste into AI tools.
Replace any function body with an AI call — same return type, no router changes.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────
# THUMBNAIL PROMPT GENERATOR
# ─────────────────────────────────────────────────────────────────

THUMB_PROVIDERS: list[tuple[str, str]] = [
    ("gpt",       "🤖 GPT Image"),
    ("midjourney","🎨 Midjourney"),
    ("flux",      "⚡ Flux"),
    ("leonardo",  "🦁 Leonardo"),
    ("ideogram",  "💡 Ideogram"),
    ("firefly",   "🔥 Firefly"),
    ("stable",    "🌀 Stable Diffusion"),
]

_THUMB_PROMPTS: dict[str, str] = {
    "gpt": (
        "<b>GPT Image — Thumbnail Prompt</b>\n\n"
        "<code>Create a YouTube thumbnail for a video about {c}.\n"
        "Style: hyper-detailed cartoon, dramatic cinematic lighting.\n"
        "Character: {c} with shocked or intense facial expression, close-up.\n"
        "Background: dynamic gradient (red to orange), speed lines.\n"
        "Composition: 16:9, 1280×720px, face taking 60% of frame.\n"
        "Text space: leave right 30% empty for title overlay.\n"
        "Colors: high contrast, vibrant, eye-catching.\n"
        "Quality: 4K, sharp edges, no blur, professional.</code>"
    ),
    "midjourney": (
        "<b>Midjourney — Thumbnail Prompt</b>\n\n"
        "<code>{c} dramatic face expression, shocked eyes, YouTube thumbnail style, "
        "cinematic lighting, red and orange gradient background, "
        "hyper detailed cartoon character, vibrant neon colors, "
        "close-up portrait, 16:9 aspect ratio, "
        "professional thumbnail design, "
        "high contrast, sharp focus, no text --ar 16:9 --v 6 --style raw</code>"
    ),
    "flux": (
        "<b>Flux — Thumbnail Prompt</b>\n\n"
        "<code>{c} character, extreme close-up face, "
        "shocked or angry expression, "
        "YouTube thumbnail composition, "
        "cinematic dramatic lighting, "
        "vibrant background with energy particles, "
        "cartoon superhero art style, "
        "hyper detailed, 4K quality, "
        "no text, no watermark, "
        "aspect ratio 16:9</code>"
    ),
    "leonardo": (
        "<b>Leonardo — Thumbnail Prompt</b>\n\n"
        "<code>Prompt: {c} dramatic YouTube thumbnail\n"
        "Style: Cartoon Epic\n"
        "Expression: shocked/intense close-up face\n"
        "Background: cinematic gradient (dark red → bright orange)\n"
        "Effects: rim lighting, glowing eyes, speed lines\n"
        "Resolution: 1280×720\n"
        "Negative: text, watermark, blur, low quality</code>"
    ),
    "ideogram": (
        "<b>Ideogram — Thumbnail Prompt</b>\n\n"
        "<code>{c} character YouTube thumbnail, "
        "dramatic close-up facial expression, "
        "shocked or intense emotion, "
        "vibrant cartoon style, "
        "cinematic lighting from below, "
        "orange-red gradient background, "
        "high detail, sharp focus, "
        "professional content creator thumbnail, "
        "16:9 format</code>"
    ),
    "firefly": (
        "<b>Adobe Firefly — Thumbnail Prompt</b>\n\n"
        "<code>Subject: {c} cartoon character, dramatic close-up\n"
        "Expression: shocked, intense, wide eyes\n"
        "Lighting: cinematic, high contrast, dramatic shadows\n"
        "Background: vibrant gradient with energy aura\n"
        "Style: hyper-detailed animation, professional YouTube thumbnail\n"
        "Aspect ratio: 16:9 (1280×720)\n"
        "Exclude: text, watermarks, blurriness</code>"
    ),
    "stable": (
        "<b>Stable Diffusion — Thumbnail Prompt</b>\n\n"
        "<code>Positive prompt:\n"
        "{c}, cartoon character, dramatic face expression, "
        "YouTube thumbnail style, cinematic lighting, "
        "vibrant colors, red orange gradient background, "
        "hyper detailed, sharp focus, 4k, close up portrait, "
        "no text, professional quality, anime cartoon hybrid\n\n"
        "Negative prompt:\n"
        "text, watermark, blur, low quality, bad anatomy, "
        "ugly, deformed, extra limbs, realistic photo, 3d render</code>"
    ),
}


def generate_thumbnail_prompt(character: str, provider: str = "gpt") -> str:
    """Generate thumbnail prompt for a specific AI provider. Replace body with AI call."""
    tmpl = _THUMB_PROMPTS.get(provider, _THUMB_PROMPTS["gpt"])
    return tmpl.replace("{c}", character)


# ─────────────────────────────────────────────────────────────────
# IMAGE PROMPT GENERATOR
# ─────────────────────────────────────────────────────────────────

IMAGE_ASPECTS: list[tuple[str, str]] = [
    ("character",   "🦸 Character"),
    ("background",  "🌄 Background"),
    ("scene",       "🎬 Scene"),
    ("action",      "💥 Action"),
    ("effects",     "✨ Effects"),
    ("lighting",    "💡 Lighting"),
    ("camera",      "📷 Camera Angle"),
    ("environment", "🌍 Environment"),
    ("mood",        "🎭 Mood"),
    ("palette",     "🎨 Color Palette"),
]

_IMAGE_PROMPTS: dict[str, str] = {
    "character": (
        "<b>Character Image Prompt</b>\n\n"
        "<code>{c} full body character design, "
        "high quality digital art, vibrant colors, "
        "transparent background, PNG format, "
        "4K resolution, clean linework, "
        "no text, no watermark, studio lighting, "
        "anime/cartoon hybrid style, "
        "sharp detailed edges, front view pose, "
        "dynamic hero stance</code>"
    ),
    "background": (
        "<b>Background Image Prompt</b>\n\n"
        "<code>Epic background for {c} YouTube video, "
        "cinematic environment, dramatic lighting, "
        "no characters, just scenery, "
        "vibrant colors, detailed, "
        "16:9 aspect ratio, 4K resolution, "
        "matching the tone of {c}'s world, "
        "fantasy/sci-fi/adventure setting, "
        "high detail, no text</code>"
    ),
    "scene": (
        "<b>Scene Image Prompt</b>\n\n"
        "<code>{c} in an epic scene, "
        "full cinematic composition, "
        "wide-angle shot, environmental storytelling, "
        "dramatic lighting, particle effects, "
        "hyper-detailed background and character, "
        "action-ready pose, "
        "16:9 cinematic frame, "
        "movie quality digital art, "
        "no text overlay</code>"
    ),
    "action": (
        "<b>Action Image Prompt</b>\n\n"
        "<code>{c} in mid-action pose, "
        "explosive energy effects, motion blur on limbs, "
        "speed lines behind character, "
        "intense facial expression, "
        "dynamic angle (45-degree tilt), "
        "vibrant power aura, "
        "debris and particles flying, "
        "4K anime action art style, "
        "high contrast lighting</code>"
    ),
    "effects": (
        "<b>Effects Image Prompt</b>\n\n"
        "<code>{c} surrounded by dramatic visual effects, "
        "glowing energy aura, electric sparks, "
        "fire and ice elements combined, "
        "shockwave expanding outward, "
        "particles and debris floating, "
        "dramatic lighting from multiple sources, "
        "color contrast: dark background vs bright effects, "
        "4K resolution, hyper-detailed</code>"
    ),
    "lighting": (
        "<b>Lighting Setup Prompt</b>\n\n"
        "<code>{c} with dramatic cinematic lighting, "
        "3-point lighting setup: key light (left, warm), "
        "fill light (right, cool blue), "
        "rim light (behind, bright highlight), "
        "deep shadows on unlit side, "
        "volumetric light rays, "
        "god rays from above, "
        "moody atmospheric lighting, "
        "dark vignette edges</code>"
    ),
    "camera": (
        "<b>Camera Angle Prompt</b>\n\n"
        "<code>{c} shot from low angle (worm's eye view), "
        "looking up at the character to emphasize power, "
        "slight wide-angle lens distortion, "
        "dramatic perspective, "
        "character dominates frame, "
        "sky or epic background visible, "
        "depth of field: sharp foreground, soft background, "
        "cinematic letterbox crop optional</code>"
    ),
    "environment": (
        "<b>Environment Image Prompt</b>\n\n"
        "<code>{c}'s home environment, "
        "fully realized world-building scene, "
        "detailed architecture matching character's theme, "
        "atmospheric lighting (golden hour / storm / night), "
        "environmental storytelling details everywhere, "
        "realistic scale showing character in world, "
        "4K wide establishing shot, "
        "no text, photorealistic or painterly style</code>"
    ),
    "mood": (
        "<b>Mood/Atmosphere Prompt</b>\n\n"
        "<code>{c} with intense dramatic mood, "
        "atmospheric haze, "
        "emotional color grading (teal and orange / red and blue), "
        "tension in body language, "
        "environment reflects inner state, "
        "moody shadows, isolated feeling, "
        "cinematic color palette, "
        "high emotional impact, "
        "storytelling through visuals alone</code>"
    ),
    "palette": (
        "<b>Color Palette Prompt</b>\n\n"
        "<code>{c} with specific color palette:\n"
        "Primary: Vibrant red (#FF2D2D) + electric blue (#00B4FF)\n"
        "Accent: Gold (#FFD700) for highlights\n"
        "Shadow: Deep purple (#1A0033)\n"
        "Background: Dark gradient (black → deep navy)\n"
        "Glow effects: Matching primary colors\n"
        "Contrast ratio: Maximum (dark bg, bright character)\n"
        "Saturation: High (cartoon-style vivid)</code>"
    ),
}


def generate_image_prompt(character: str, aspect: str = "character") -> str:
    """Generate image prompt for an aspect. Replace body with AI call."""
    tmpl = _IMAGE_PROMPTS.get(aspect, _IMAGE_PROMPTS["character"])
    return tmpl.replace("{c}", character)


# ─────────────────────────────────────────────────────────────────
# VIDEO PROMPT GENERATOR
# ─────────────────────────────────────────────────────────────────

VIDEO_PROVIDERS: list[tuple[str, str]] = [
    ("runway",     "✈️ Runway"),
    ("veo",        "🎬 Veo (Google)"),
    ("kling",      "🇨🇳 Kling"),
    ("luma",       "🌙 Luma"),
    ("pika",       "⚡ Pika"),
    ("higgsfield", "🔬 Higgsfield"),
]

_VIDEO_PROMPTS: dict[str, str] = {
    "runway": (
        "<b>Runway — Video Prompt</b>\n\n"
        "<code>{c} action sequence, dynamic movement, "
        "cinematic camera pan from left to right, "
        "smooth animation, 24fps, "
        "vibrant color grading, dramatic lighting, "
        "epic background environment, "
        "no text overlay, "
        "YouTube Shorts format 9:16 vertical, "
        "duration: 5-6 seconds, "
        "motion: character runs/jumps/attacks</code>"
    ),
    "veo": (
        "<b>Veo (Google) — Video Prompt</b>\n\n"
        "<code>Animated short video featuring {c}.\n"
        "Scene: {c} performing a powerful attack or jump.\n"
        "Camera: Low angle, slow-motion pull-back.\n"
        "Lighting: Dramatic cinematic with particle effects.\n"
        "Style: High-quality anime/cartoon animation.\n"
        "Duration: 5-8 seconds.\n"
        "Format: Vertical 9:16 for YouTube Shorts.\n"
        "Mood: Epic, powerful, awe-inspiring.</code>"
    ),
    "kling": (
        "<b>Kling — Video Prompt</b>\n\n"
        "<code>{c} character animation, "
        "full body movement, "
        "epic transformation sequence or battle pose, "
        "particle effects and energy aura, "
        "dramatic zoom-in on face at peak moment, "
        "smooth 24fps animation, "
        "vibrant cartoon style, "
        "vertical 9:16 format, "
        "5-second clip</code>"
    ),
    "luma": (
        "<b>Luma — Video Prompt</b>\n\n"
        "<code>Subject: {c} animated character\n"
        "Action: Epic power-up or battle sequence\n"
        "Camera movement: Slow orbit around character\n"
        "Lighting: Cinematic with multiple colored lights\n"
        "Style: High-quality cartoon animation\n"
        "Effects: Energy particles, speed lines, glow\n"
        "Duration: 6 seconds\n"
        "Output format: 9:16 vertical MP4</code>"
    ),
    "pika": (
        "<b>Pika — Video Prompt</b>\n\n"
        "<code>{c} dramatic action scene, "
        "character explodes with power, "
        "camera starts close on face then pulls back wide, "
        "energy beams and particle effects, "
        "anime-style animation quality, "
        "dark dramatic background with bright character, "
        "9:16 vertical, 5 seconds, "
        "smooth motion, no artifacts</code>"
    ),
    "higgsfield": (
        "<b>Higgsfield — Video Prompt</b>\n\n"
        "<code>Scene description: {c} in epic moment\n"
        "Action: Power transformation / battle stance\n"
        "Camera: Dynamic tracking shot with motion blur\n"
        "Effects: Shockwave, debris, energy trails\n"
        "Art style: Premium anime/cartoon hybrid\n"
        "Lighting: Rim + key + atmospheric particles\n"
        "Duration: 6-8 seconds loop\n"
        "Resolution: 9:16 (1080×1920)</code>"
    ),
}


def generate_video_prompt(character: str, provider: str = "runway") -> str:
    """Generate video prompt for a provider. Replace body with AI call."""
    tmpl = _VIDEO_PROMPTS.get(provider, _VIDEO_PROMPTS["runway"])
    return tmpl.replace("{c}", character)


# ─────────────────────────────────────────────────────────────────
# ANIMATION PROMPT GENERATOR
# ─────────────────────────────────────────────────────────────────

ANIMATION_TYPES: list[tuple[str, str]] = [
    ("walking",       "🚶 Walking"),
    ("running",       "🏃 Running"),
    ("jump",          "🦘 Jump"),
    ("dance",         "💃 Dance"),
    ("transformation","✨ Transformation"),
    ("battle",        "⚔️ Battle"),
    ("idle",          "🧍 Idle"),
    ("talking",       "💬 Talking"),
    ("happy",         "😊 Happy"),
    ("sad",           "😢 Sad"),
    ("attack",        "💥 Attack"),
    ("victory",       "🏆 Victory"),
]

_ANIM_PROMPTS: dict[str, str] = {
    "walking": (
        "<b>Walking Animation Prompt</b>\n\n"
        "<code>{c} walking animation loop, "
        "smooth natural gait, 8-frame loop, "
        "weight distribution realistic, "
        "arms swing naturally, "
        "side view or 3/4 view, "
        "cartoon style with squash and stretch, "
        "seamless loop, "
        "no background needed, "
        "24fps character sheet format</code>"
    ),
    "running": (
        "<b>Running Animation Prompt</b>\n\n"
        "<code>{c} running at full speed, "
        "leaning forward 15 degrees, "
        "exaggerated cartoon run cycle, "
        "speed lines trailing behind, "
        "hair and cape (if any) flowing back, "
        "6-frame loop, smooth motion, "
        "dust particles under feet, "
        "dynamic energy, side profile view</code>"
    ),
    "jump": (
        "<b>Jump Animation Prompt</b>\n\n"
        "<code>{c} jump animation sequence:\n"
        "Frame 1-3: Crouch/anticipation (squash down)\n"
        "Frame 4-8: Launch upward (stretch tall)\n"
        "Frame 9-12: Peak height (spread arms)\n"
        "Frame 13-16: Falling with slight rotation\n"
        "Frame 17-20: Landing impact (squash + dust)\n"
        "Style: Exaggerated cartoon physics\n"
        "Effect: Motion trail during ascent</code>"
    ),
    "dance": (
        "<b>Dance Animation Prompt</b>\n\n"
        "<code>{c} dance animation, "
        "fun and expressive movement, "
        "16-32 frame loop, "
        "arms, hips, and head all move together, "
        "rhythm and bounce feel, "
        "cartoon exaggeration with smooth interpolation, "
        "joyful facial expression, "
        "could be: floss, pop, or unique character dance, "
        "full body visible, front view</code>"
    ),
    "transformation": (
        "<b>Transformation Animation Prompt</b>\n\n"
        "<code>{c} transformation sequence animation:\n"
        "Phase 1 (0-0.5s): Energy gathers around character\n"
        "Phase 2 (0.5-1.5s): Flash of light, silhouette changes\n"
        "Phase 3 (1.5-2.5s): New form revealed piece by piece\n"
        "Phase 4 (2.5-3s): Final form pose with energy burst\n"
        "Effects: glowing aura, particle explosion, shockwave ring\n"
        "Color shift: original colors → new palette\n"
        "Dramatic music cue point: Phase 4</code>"
    ),
    "battle": (
        "<b>Battle Animation Prompt</b>\n\n"
        "<code>{c} battle sequence animation:\n"
        "Move 1: Signature stance/guard pose\n"
        "Move 2: Quick dash forward (motion blur)\n"
        "Move 3: Powerful attack (weapon or fist)\n"
        "Impact: Flash + shockwave + screen shake hint\n"
        "Move 4: Back-flip dodge with style\n"
        "Move 5: Victory pose\n"
        "Style: Fluid anime action, 24fps\n"
        "Each move: 8-12 frames</code>"
    ),
    "idle": (
        "<b>Idle Animation Prompt</b>\n\n"
        "<code>{c} idle animation loop, "
        "subtle breathing motion (chest rises/falls), "
        "slight head bob or hair sway, "
        "weight shift left to right slowly, "
        "eyes blink every 3-4 seconds, "
        "finger tap or foot tap optional, "
        "16-frame seamless loop, "
        "character appears alive and aware, "
        "confident or calm expression</code>"
    ),
    "talking": (
        "<b>Talking Animation Prompt</b>\n\n"
        "<code>{c} talking animation, "
        "mouth movement synchronized to speech, "
        "6 mouth shapes: A, E, I, O, U, closed, "
        "eyebrow raises for emphasis, "
        "hand gesture on key words, "
        "head nod or tilt while speaking, "
        "natural blink pattern, "
        "subtle body sway, "
        "front or 3/4 view, "
        "cartoon lip-sync ready</code>"
    ),
    "happy": (
        "<b>Happy Animation Prompt</b>\n\n"
        "<code>{c} happy expression animation:\n"
        "Trigger: Realization of good news\n"
        "Frame 1-4: Eyes widen, small smile appears\n"
        "Frame 5-8: Big grin, cheeks puff out, stars/hearts near eyes\n"
        "Frame 9-12: Jump or fist pump in air\n"
        "Frame 13-16: Celebrating dance or spin\n"
        "Effects: sparkles, stars, color burst\n"
        "Duration: 2 seconds, then loop frames 13-16\n"
        "Sound cue: ding! or victory chime</code>"
    ),
    "sad": (
        "<b>Sad Animation Prompt</b>\n\n"
        "<code>{c} sad expression animation:\n"
        "Frame 1-4: Eyes drop, corners of mouth fall\n"
        "Frame 5-8: Head droops forward, shoulders slump\n"
        "Frame 9-12: Tear forms and drops from eye\n"
        "Frame 13-20: Sobbing motion with body shake\n"
        "Effect: Rain drops overlay, dark vignette\n"
        "Color shift: slightly desaturated\n"
        "Sound cue: soft violin or piano chord\n"
        "Loop: frames 13-20 until trigger changes</code>"
    ),
    "attack": (
        "<b>Attack Animation Prompt</b>\n\n"
        "<code>{c} signature attack animation:\n"
        "Phase 1 (windup): Draw back, energy charges, 0.3s\n"
        "Phase 2 (release): Full force forward, motion blur, 0.1s\n"
        "Phase 3 (impact): Flash frame white, shockwave, 0.2s\n"
        "Phase 4 (recovery): Pull back to stance, 0.3s\n"
        "Attack type: [punch/energy beam/weapon swing]\n"
        "Effect: Energy trail matching character colors\n"
        "Camera: Slight zoom in on impact\n"
        "Total duration: ~0.9 seconds</code>"
    ),
    "victory": (
        "<b>Victory Animation Prompt</b>\n\n"
        "<code>{c} victory celebration animation:\n"
        "Pose 1: Arms raised in V shape, confident smile\n"
        "Pose 2: Single fist pump upward\n"
        "Pose 3: Cross arms coolly, small smirk\n"
        "Pose 4: Wink to camera with finger guns (optional)\n"
        "Effects: Confetti rain, star burst, golden glow\n"
        "Background: Bright flash → cleared field\n"
        "Duration: 3-4 seconds\n"
        "End: Freeze on best pose</code>"
    ),
}


def generate_animation_prompt(character: str, anim_type: str = "idle") -> str:
    """Generate animation prompt. Replace body with AI call."""
    tmpl = _ANIM_PROMPTS.get(anim_type, _ANIM_PROMPTS["idle"])
    return tmpl.replace("{c}", character)


# ─────────────────────────────────────────────────────────────────
# VOICE GENERATORS
# ─────────────────────────────────────────────────────────────────

VOICE_TYPES: list[tuple[str, str]] = [
    ("narration",    "🎙 Narration"),
    ("kids",         "🧸 Kids"),
    ("male",         "👨 Male"),
    ("female",       "👩 Female"),
    ("funny",        "😂 Funny"),
    ("monster",      "👹 Monster"),
    ("robot",        "🤖 Robot"),
    ("horror",       "👻 Horror"),
    ("storytelling", "📖 Storytelling"),
]

_VOICE_SCRIPT_TEMPLATES: dict[str, str] = {
    "narration": (
        "🎙 <b>Narration Script: {t}</b>\n\n"
        "<code>[Speak clearly and evenly, pause at / marks]\n\n"
        "In a world where {t} reigns supreme... /\n"
        "few could have predicted what would happen next.\n\n"
        "The story of {t} / is not just about power.\n"
        "It's about the choices we make / "
        "when everything is on the line.\n\n"
        "Watch closely. / Because this... /\n"
        "is the moment that changed everything.\n\n"
        "[End with dramatic pause]</code>"
    ),
    "kids": (
        "🧸 <b>Kids Voice Script: {t}</b>\n\n"
        "<code>[Happy, excited voice — speak slowly and clearly]\n\n"
        "Hi hi hi! / Do you know who's here today?\n"
        "It's {t}! Yaaay! 🎉\n\n"
        "{t} is going on a super fun adventure!\n"
        "Will you come along? /\n"
        "Of course you will! You're so brave!\n\n"
        "Let's go! / Wheee! /\n"
        "See you next time, friends! Bye-bye! 👋\n\n"
        "[Keep energy HIGH throughout, never drop below cheerful]</code>"
    ),
    "male": (
        "👨 <b>Male Voice Script: {t}</b>\n\n"
        "<code>[Deep, confident voice — steady pace]\n\n"
        "{t}. / Just the name sends chills.\n\n"
        "But today... / everything changes.\n"
        "Because {t} has one mission / "
        "and nothing will stand in the way.\n\n"
        "Strength. / Speed. / Power. /\n"
        "This is {t} at full force.\n\n"
        "[Drop pitch on final line for maximum impact]</code>"
    ),
    "female": (
        "👩 <b>Female Voice Script: {t}</b>\n\n"
        "<code>[Clear, warm but powerful voice]\n\n"
        "They said {t} couldn't do it. /\n"
        "They were wrong.\n\n"
        "Every battle, every challenge, every obstacle /\n"
        "only made {t} stronger.\n\n"
        "And now? / The world watches. /\n"
        "Because {t} is just getting started.\n\n"
        "[Emphasize 'stronger' and 'getting started']</code>"
    ),
    "funny": (
        "😂 <b>Funny Voice Script: {t}</b>\n\n"
        "<code>[Comedic timing is everything — pause before punchlines]\n\n"
        "So... {t} woke up today / and decided...\n"
        "to be absolutely ridiculous. / Again.\n\n"
        "Like... why?! / WHY does {t} do this?!\n"
        "[Exasperated pause]\n"
        "We don't know. / Nobody knows.\n\n"
        "And honestly? / At this point... /\n"
        "we don't even care anymore. 💀\n\n"
        "[Voice crack optional on last line for extra comedy]</code>"
    ),
    "monster": (
        "👹 <b>Monster Voice Script: {t}</b>\n\n"
        "<code>[Deep, growling voice — add reverb effect if possible]\n\n"
        "[GROWL] ...{t}... has awakened.\n\n"
        "After years of silence / "
        "the beast... returns.\n\n"
        "Run. / Hide. /\n"
        "It won't matter.\n\n"
        "Because {t}... / "
        "cannot... / be... STOPPED.\n\n"
        "[ROAR]\n\n"
        "[Add bass boost + slight distortion to voice]</code>"
    ),
    "robot": (
        "🤖 <b>Robot Voice Script: {t}</b>\n\n"
        "<code>[Monotone, mechanical delivery — equal stress on all syllables]\n\n"
        "SYSTEM ONLINE. /\n"
        "SUBJECT: {t}. /\n"
        "ANALYZING... COMPLETE.\n\n"
        "RESULT: / POWER LEVEL — MAXIMUM. /\n"
        "THREAT ASSESSMENT: / EXTREME.\n\n"
        "INITIATING: / {t} SEQUENCE.\n"
        "ESTIMATED COMPLETION: / 3... 2... 1...\n\n"
        "EXECUTE. /\n\n"
        "[Add robotic filter: pitch shift + slight glitch effect]</code>"
    ),
    "horror": (
        "👻 <b>Horror Voice Script: {t}</b>\n\n"
        "<code>[Whisper then sudden loud moments — dynamic contrast]\n\n"
        "[Whisper] They thought {t} was gone. /\n"
        "[Whisper] They were wrong.\n\n"
        "It started with shadows. /\n"
        "Then the sounds. /\n"
        "Then... [PAUSE 3 seconds] /\n"
        "[LOUD] {t} APPEARED.\n\n"
        "[Whisper] And nothing... /\n"
        "was ever... /\n"
        "the same... again.\n\n"
        "[Add echo effect + soft ominous music under voice]</code>"
    ),
    "storytelling": (
        "📖 <b>Storytelling Voice Script: {t}</b>\n\n"
        "<code>[Warm, engaging narrator voice — vary pace for drama]\n\n"
        "Once upon a time... / in a world not so different from ours... /\n"
        "there lived a being unlike any other. /\n"
        "Their name... was {t}.\n\n"
        "Nobody knew where {t} came from. /\n"
        "But everyone knew one thing: /\n"
        "when {t} arrived... / "
        "the world... / changed.\n\n"
        "[Slow down pace here]\n"
        "And this... / is their story.\n\n"
        "[Pause 2 seconds before video starts]</code>"
    ),
}

_VOICE_PROMPTS: dict[str, str] = {
    "narration": (
        "<b>Narration Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} documentary narrator voice, "
        "deep resonant male baritone, "
        "calm and authoritative delivery, "
        "BBC documentary style, "
        "clear enunciation, "
        "no accent or minimal neutral accent, "
        "pace: 130 words per minute, "
        "add dramatic pauses at commas, "
        "tone: serious, informative, compelling</code>"
    ),
    "kids": (
        "<b>Kids Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} kids show host voice, "
        "high energy and enthusiastic, "
        "friendly and warm tone, "
        "slightly higher pitch than normal, "
        "clear and slow enunciation (kids can follow), "
        "lots of natural excitement and wonder, "
        "age: sounds like a fun adult teacher, "
        "no scary or intense elements, "
        "add laughter naturally where marked</code>"
    ),
    "male": (
        "<b>Male Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} male voice, "
        "confident and powerful delivery, "
        "deep-medium pitch, "
        "controlled and steady pacing, "
        "slight heroic quality, "
        "cinematic trailer voice style, "
        "American neutral accent, "
        "dramatic emphasis on key words, "
        "pace: 120 words per minute</code>"
    ),
    "female": (
        "<b>Female Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} female narrator voice, "
        "strong and confident delivery, "
        "warm but powerful tone, "
        "medium-low pitch for authority, "
        "natural and intelligent sounding, "
        "clear American English accent, "
        "empowering and inspiring quality, "
        "pace: 125 words per minute</code>"
    ),
    "funny": (
        "<b>Funny Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} comedic voice, "
        "exaggerated reactions and timing, "
        "slightly nasally or quirky quality, "
        "unpredictable pacing (fast then slow for punchlines), "
        "cartoon-like expressiveness, "
        "cracks on important moments, "
        "genuine sounding laughter where marked, "
        "relatable and loveable tone</code>"
    ),
    "monster": (
        "<b>Monster Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} monster/villain voice, "
        "very deep bass voice with gravel texture, "
        "slow menacing delivery, "
        "slight growl on consonants, "
        "echo/reverb effect applied, "
        "intimidating and powerful presence, "
        "deliberate pauses between words, "
        "sounds ancient and powerful</code>"
    ),
    "robot": (
        "<b>Robot Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} robotic AI voice, "
        "completely flat affect and monotone, "
        "equal stress on every syllable, "
        "no natural speech variation, "
        "slight metallic quality, "
        "precise and clinical delivery, "
        "add glitch effect at marked points, "
        "pace: exactly 100 words per minute</code>"
    ),
    "horror": (
        "<b>Horror Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} horror narrator voice, "
        "starts as whisper then builds to loud, "
        "creepy and unsettling quality, "
        "breathiness and tension in delivery, "
        "unpredictable pacing with long pauses, "
        "medium-low pitch, slight rasp, "
        "sends chills when combined with silence, "
        "sound like something is wrong</code>"
    ),
    "storytelling": (
        "<b>Storytelling Voice Prompt (for AI TTS)</b>\n\n"
        "<code>{c} bedtime storyteller voice, "
        "warm and engaging narrative quality, "
        "varies pace: slow for drama, faster for action, "
        "rich and expressive, "
        "feels like a master storyteller, "
        "slight theatrical quality without overdoing it, "
        "comfortable and trustworthy presence, "
        "perfect for animation narration</code>"
    ),
}


def generate_voice_script(topic: str, voice_type: str = "narration") -> str:
    """Generate voice script to read aloud. Replace body with AI call."""
    tmpl = _VOICE_SCRIPT_TEMPLATES.get(voice_type, _VOICE_SCRIPT_TEMPLATES["narration"])
    return tmpl.replace("{t}", topic)


def generate_voice_prompt(character: str, voice_type: str = "narration") -> str:
    """Generate voice prompt for AI TTS tools. Replace body with AI call."""
    tmpl = _VOICE_PROMPTS.get(voice_type, _VOICE_PROMPTS["narration"])
    return tmpl.replace("{c}", character)
