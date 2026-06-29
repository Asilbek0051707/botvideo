"""Content Generator Service — template-based text generation.

All functions return the same shapes regardless of backend.
Replace any function body with an AI API call and the router code
stays the same (same function name, same return type).

Template placeholders always use {t} for topic/character name.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────
# SCRIPT GENERATOR
# ─────────────────────────────────────────────────────────────────

SCRIPT_TYPES: list[tuple[str, str]] = [
    ("shorts",       "📱 Shorts Script"),
    ("long",         "🎬 Long Video"),
    ("story",        "📖 Story Script"),
    ("narration",    "🎙 Narration"),
    ("educational",  "📚 Educational"),
    ("funny",        "😂 Funny"),
    ("gaming",       "🎮 Gaming"),
    ("challenge",    "🏆 Challenge"),
    ("battle",       "⚔️ Battle"),
    ("transformation","✨ Transformation"),
    ("char_story",   "🦸 Character Story"),
    ("top10",        "🔟 Top 10"),
    ("comparison",   "⚖️ Comparison"),
    ("facts",        "💡 Facts"),
    ("mystery",      "🔮 Mystery"),
    ("horror",       "👻 Horror"),
    ("kids",         "🧸 Kids"),
    ("motivation",   "💪 Motivation"),
    ("ai_story",     "🤖 AI Story"),
    ("quiz",         "❓ Quiz"),
    ("guess",        "🎯 Guess Challenge"),
]

_SCRIPTS: dict[str, str] = {
    "shorts": (
        "📱 <b>Shorts Script: {t}</b>\n\n"
        "<b>[HOOK 0:00–0:03]</b>\n"
        "\"Wait... {t} just changed EVERYTHING! 😱\"\n"
        "[Dramatic close-up, unexpected moment]\n\n"
        "<b>[SETUP 0:03–0:08]</b>\n"
        "\"{t} faces the ultimate challenge...\"\n"
        "[Introduce conflict clearly]\n\n"
        "<b>[ACTION 0:08–0:50]</b>\n"
        "Scene 1 (0:08): {t} discovers the problem\n"
        "Scene 2 (0:20): First attempt — epic fail!\n"
        "Scene 3 (0:32): Unexpected twist appears\n"
        "Scene 4 (0:42): {t} unlocks true power\n\n"
        "<b>[TWIST 0:50–0:55]</b>\n"
        "\"But then... [shocking ending]!\"\n\n"
        "<b>[CTA 0:55–1:00]</b>\n"
        "\"Comment: could {t} survive this?! 👇\"\n"
        "\"Like & Subscribe for more {t}! 🔔\""
    ),
    "long": (
        "🎬 <b>Long Video Script: {t}</b>\n\n"
        "<b>[INTRO 0:00–0:30]</b>\n"
        "Hook: \"Today we're diving deep into {t}...\"\n"
        "Preview: Show 3 highlights from the video\n"
        "Subscribe reminder: \"Hit that bell icon!\"\n\n"
        "<b>[CHAPTER 1: Origin (0:30–3:00)]</b>\n"
        "\"Where did {t} come from?\"\n"
        "[Background story, origin details]\n\n"
        "<b>[CHAPTER 2: Powers (3:00–6:00)]</b>\n"
        "\"What makes {t} so special?\"\n"
        "[3 key abilities with demonstrations]\n\n"
        "<b>[CHAPTER 3: Greatest Moments (6:00–9:00)]</b>\n"
        "Top 5 iconic {t} moments, ranked\n"
        "[Commentary + reaction for each]\n\n"
        "<b>[CHAPTER 4: VS Battle (9:00–11:30)]</b>\n"
        "\"{t} vs [rival] — who wins?!\"\n"
        "[Analysis, power levels, verdict]\n\n"
        "<b>[OUTRO 11:30–12:00]</b>\n"
        "\"That's a wrap! Comment your thoughts!\"\n"
        "\"Subscribe for weekly {t} content!\""
    ),
    "story": (
        "📖 <b>Story Script: {t}</b>\n\n"
        "<b>[ACT 1 — The Call (0:00–0:15)]</b>\n"
        "Setting: [Establish world where {t} lives]\n"
        "\"One day, {t} received a mission nobody else could do...\"\n\n"
        "<b>[ACT 2 — The Journey (0:15–0:40)]</b>\n"
        "Challenge 1: {t} faces first obstacle\n"
        "Mentor: [Who helps {t} along the way?]\n"
        "Setback: \"Just when {t} thought it was over...\"\n\n"
        "<b>[ACT 3 — The Climax (0:40–0:53)]</b>\n"
        "\"This is the moment {t} was born for!\"\n"
        "[Epic showdown, all skills combined]\n\n"
        "<b>[ACT 4 — Resolution (0:53–1:00)]</b>\n"
        "\"And that's how {t} saved the day forever.\"\n"
        "Moral: [One clear lesson from the story]"
    ),
    "narration": (
        "🎙 <b>Narration Script: {t}</b>\n\n"
        "<b>[OPENING]</b>\n"
        "\"Ladies and gentlemen, today we explore {t}.\"\n"
        "\"What you're about to see will surprise you.\"\n\n"
        "<b>[MAIN NARRATION]</b>\n"
        "\"In the world of {t}, few things are as they seem.\"\n"
        "\"[Fact 1 about {t}] — and that's just the beginning.\"\n"
        "\"[Fact 2 about {t}] — scientists were stunned.\"\n"
        "\"[Fact 3 about {t}] — no one saw this coming.\"\n\n"
        "<b>[TRANSITION]</b>\n"
        "\"But what truly sets {t} apart is...\"\n"
        "[Reveal the most impressive aspect]\n\n"
        "<b>[CLOSING]</b>\n"
        "\"And that is the untold story of {t}.\"\n"
        "\"Like if this surprised you. Subscribe for more.\""
    ),
    "educational": (
        "📚 <b>Educational Script: {t}</b>\n\n"
        "<b>[ATTENTION HOOK 0:00–0:05]</b>\n"
        "\"Did you know {t} can do something incredible?\"\n"
        "[Surprising fact to open]\n\n"
        "<b>[LESSON INTRO 0:05–0:15]</b>\n"
        "\"Today you'll learn 3 things about {t}:\"\n"
        "✅ What makes {t} unique\n"
        "✅ How {t} works\n"
        "✅ Why {t} matters\n\n"
        "<b>[LESSON BODY 0:15–0:45]</b>\n"
        "Point 1: \"First, {t} is known for...\"\n"
        "[Visual example + simple explanation]\n"
        "Point 2: \"Second, the science behind {t}...\"\n"
        "[Animation + analogy for kids/beginners]\n"
        "Point 3: \"Third, {t} in real life means...\"\n"
        "[Real world application]\n\n"
        "<b>[RECAP + CTA 0:45–1:00]</b>\n"
        "\"So now you know {t}! Quiz: comment answer below!\""
    ),
    "funny": (
        "😂 <b>Funny Script: {t}</b>\n\n"
        "<b>[SETUP JOKE 0:00–0:05]</b>\n"
        "\"POV: You're {t} and life just got ridiculous 😂\"\n\n"
        "<b>[ESCALATING CHAOS 0:05–0:45]</b>\n"
        "Beat 1: {t} tries something simple → fails hilariously\n"
        "Beat 2: {t} tries to fix it → makes it 10x worse\n"
        "Beat 3: Random [unexpected character] shows up\n"
        "Beat 4: {t}'s reaction face — freeze frame\n"
        "Beat 5: The most absurd solution imaginable\n\n"
        "<b>[PUNCHLINE 0:45–0:55]</b>\n"
        "\"And THAT is why {t} never tries again! 💀\"\n"
        "[Hold on reaction face]\n\n"
        "<b>[CALLBACK 0:55–1:00]</b>\n"
        "\"Comment if this is you every day 👇\"\n"
        "\"More {t} fails? Subscribe! 🔔\""
    ),
    "gaming": (
        "🎮 <b>Gaming Script: {t}</b>\n\n"
        "<b>[INTRO 0:00–0:05]</b>\n"
        "\"Okay chat, today {t} is going CRAZY! 🔥\"\n"
        "[Start mid-action, no intro]\n\n"
        "<b>[GAMEPLAY COMMENTARY 0:05–0:45]</b>\n"
        "Moment 1: \"Wait wait wait — did that just happen?!\"\n"
        "Moment 2: \"CHAT WE'RE COOKED 💀\" [epic fail]\n"
        "Moment 3: \"Bro I can't believe I pulled that off\"\n"
        "Moment 4: \"This is the most insane {t} moment ever\"\n"
        "Moment 5: \"LETS GOOO\" [clutch win]\n\n"
        "<b>[HIGHLIGHT REPLAY 0:45–0:55]</b>\n"
        "\"Rewind... did you see that?!\"\n"
        "[Slow-mo of the best moment]\n\n"
        "<b>[END CARD 0:55–1:00]</b>\n"
        "\"Like if {t} is goated! Subscribe for daily gameplay! 🎮\""
    ),
    "challenge": (
        "🏆 <b>Challenge Script: {t}</b>\n\n"
        "<b>[CHALLENGE REVEAL 0:00–0:05]</b>\n"
        "\"I challenged {t} to do the IMPOSSIBLE! 😱\"\n"
        "[Show the challenge card / rules]\n\n"
        "<b>[ATTEMPT 1 0:05–0:20]</b>\n"
        "{t} first try → close but fails\n"
        "\"So close! But {t} won't give up...\"\n\n"
        "<b>[ATTEMPT 2 0:20–0:35]</b>\n"
        "{t} uses a strategy → unexpected problem\n"
        "\"Who would have thought THIS would happen!\"\n\n"
        "<b>[FINAL ATTEMPT 0:35–0:50]</b>\n"
        "\"Last chance! Everything on the line!\"\n"
        "[Build tension + dramatic music]\n"
        "{t} [succeeds/fails] — reaction shot\n\n"
        "<b>[VERDICT 0:50–1:00]</b>\n"
        "Result reveal + score\n"
        "\"Comment: could YOU do better than {t}? 👇\""
    ),
    "battle": (
        "⚔️ <b>Battle Script: {t}</b>\n\n"
        "<b>[FIGHTERS INTRO 0:00–0:08]</b>\n"
        "\"Today's battle: {t} vs [OPPONENT]! ⚔️\"\n"
        "[Show both fighters, stats comparison]\n\n"
        "<b>[ROUND 1 — POWER 0:08–0:25]</b>\n"
        "{t} attacks with signature move\n"
        "[Opponent counters]\n"
        "\"Round 1 goes to... {t}!\"\n\n"
        "<b>[ROUND 2 — SPEED 0:25–0:40]</b>\n"
        "Opponent reveals hidden ability\n"
        "{t} adapts strategy\n"
        "\"It's TIED! This is anyone's fight!\"\n\n"
        "<b>[FINAL ROUND 0:40–0:55]</b>\n"
        "\"ULTIMATE MOVE ACTIVATED!\"\n"
        "[Epic clash animation]\n"
        "[Dust settles...]\n\n"
        "<b>[WINNER 0:55–1:00]</b>\n"
        "\"The winner is... {t}! 🏆\"\n"
        "\"Comment: who should {t} fight next? 👇\""
    ),
    "transformation": (
        "✨ <b>Transformation Script: {t}</b>\n\n"
        "<b>[BEFORE 0:00–0:08]</b>\n"
        "\"This is {t}... in its weakest form.\"\n"
        "[Show original / base state clearly]\n\n"
        "<b>[TRIGGER 0:08–0:15]</b>\n"
        "\"But then something happened that changed {t} FOREVER...\"\n"
        "[The event/catalyst that triggers transformation]\n\n"
        "<b>[TRANSFORMATION 0:15–0:40]</b>\n"
        "Stage 1: Minor changes begin\n"
        "Stage 2: \"Wait... is that {t}?!\"\n"
        "Stage 3: [Full transformation reveal]\n"
        "\"The crowd couldn't believe their eyes!\"\n\n"
        "<b>[AFTER 0:40–0:55]</b>\n"
        "\"THIS is {t}'s TRUE power! 💥\"\n"
        "[New abilities demonstration]\n\n"
        "<b>[REACTION 0:55–1:00]</b>\n"
        "\"Comment: which form of {t} is stronger? 👇\""
    ),
    "char_story": (
        "🦸 <b>Character Story: {t}</b>\n\n"
        "<b>[ORIGIN 0:00–0:10]</b>\n"
        "\"Before {t} was a hero, they were just...\"\n"
        "[Humble/tragic backstory details]\n\n"
        "<b>[THE MOMENT 0:10–0:25]</b>\n"
        "\"Then one day, everything changed.\"\n"
        "[The event that created the character]\n"
        "\"From that moment, {t} vowed to...\"\n\n"
        "<b>[TRIALS 0:25–0:45]</b>\n"
        "Trial 1: First major failure\n"
        "Trial 2: Finding allies / mentor\n"
        "Trial 3: Greatest test of character\n\n"
        "<b>[HERO MOMENT 0:45–0:55]</b>\n"
        "\"And THAT is the day {t} truly became a legend.\"\n\n"
        "<b>[LEGACY 0:55–1:00]</b>\n"
        "\"Comment: what's YOUR favorite {t} moment? 👇\""
    ),
    "top10": (
        "🔟 <b>Top 10 Script: {t}</b>\n\n"
        "<b>[INTRO 0:00–0:05]</b>\n"
        "\"Top 10 most incredible things about {t}! 🔥\"\n\n"
        "<b>[COUNTDOWN 0:05–0:50]</b>\n"
        "#10: [Least impressive but still surprising fact]\n"
        "#9: [Something most people don't know]\n"
        "#8: [Unexpected ability/feature]\n"
        "#7: [Historic/record achievement]\n"
        "#6: [Something relatable/funny]\n"
        "#5: [Game-changing moment]\n"
        "#4: [Power/skill reveal]\n"
        "#3: [Fan-favorite moment]\n"
        "#2: [Almost the greatest thing]\n\n"
        "<b>[#1 REVEAL 0:50–0:58]</b>\n"
        "\"And the NUMBER ONE thing about {t}...\"\n"
        "[Dramatic pause + reveal]\n\n"
        "<b>[CTA 0:58–1:00]</b>\n"
        "\"Agree? Comment your #1! 👇\""
    ),
    "comparison": (
        "⚖️ <b>Comparison Script: {t}</b>\n\n"
        "<b>[INTRO 0:00–0:08]</b>\n"
        "\"{t} vs [RIVAL] — the ultimate comparison! ⚖️\"\n"
        "[Side-by-side stats display]\n\n"
        "<b>[ROUND 1: STRENGTH 0:08–0:22]</b>\n"
        "{t}: [strength score + demo]\n"
        "[RIVAL]: [strength score + demo]\n"
        "Winner: ___\n\n"
        "<b>[ROUND 2: SPEED 0:22–0:36]</b>\n"
        "{t}: [speed score + demo]\n"
        "[RIVAL]: [speed score + demo]\n"
        "Winner: ___\n\n"
        "<b>[ROUND 3: SPECIAL 0:36–0:50]</b>\n"
        "{t}'s special ability vs [RIVAL]'s\n"
        "Winner: ___\n\n"
        "<b>[FINAL SCORE 0:50–1:00]</b>\n"
        "\"Overall winner: ___! 🏆\"\n"
        "\"Comment: do you agree? 👇\""
    ),
    "facts": (
        "💡 <b>Facts Script: {t}</b>\n\n"
        "<b>[HOOK 0:00–0:05]</b>\n"
        "\"5 facts about {t} that will blow your mind! 💡\"\n\n"
        "<b>[FACT 1 0:05–0:15]</b>\n"
        "\"Fact #1: {t} actually... [surprising truth]\"\n"
        "[Visual proof/animation]\n\n"
        "<b>[FACT 2 0:15–0:25]</b>\n"
        "\"Did you know? {t} can... [hidden ability]\"\n"
        "[Demonstration]\n\n"
        "<b>[FACT 3 0:25–0:35]</b>\n"
        "\"Most people think {t} is... but actually...\"\n"
        "[Myth vs reality]\n\n"
        "<b>[FACT 4 0:35–0:45]</b>\n"
        "\"The record for {t} is... [impressive stat]\"\n\n"
        "<b>[FACT 5 0:45–0:58]</b>\n"
        "\"And the #1 fact: {t} once...\"\n"
        "[Most incredible fact saved for last]\n\n"
        "<b>[CTA 0:58–1:00]</b>\n"
        "\"Which fact surprised you most? Comment! 👇\""
    ),
    "mystery": (
        "🔮 <b>Mystery Script: {t}</b>\n\n"
        "<b>[HOOK 0:00–0:06]</b>\n"
        "\"Something strange is happening with {t}... 🔮\"\n"
        "[Ominous music, dark visuals]\n\n"
        "<b>[CLUE 1 0:06–0:20]</b>\n"
        "\"It started when {t} disappeared for [time period]...\"\n"
        "[First mysterious event]\n"
        "\"Nobody could explain it.\"\n\n"
        "<b>[CLUE 2 0:20–0:35]</b>\n"
        "\"Then witnesses reported...\"\n"
        "[Second unexplained occurrence]\n"
        "\"The evidence was undeniable.\"\n\n"
        "<b>[THE THEORY 0:35–0:50]</b>\n"
        "\"Here's what we think REALLY happened with {t}...\"\n"
        "[Reveal the mystery/theory]\n\n"
        "<b>[CLIFF HANGER 0:50–1:00]</b>\n"
        "\"But the truth about {t} is even darker...\"\n"
        "\"Comment your theory below! 👇\""
    ),
    "horror": (
        "👻 <b>Horror Script: {t}</b>\n\n"
        "<b>[SETUP 0:00–0:08]</b>\n"
        "\"Warning: {t}'s darkest secret is revealed... 👻\"\n"
        "[Creepy ambient, low lighting]\n\n"
        "<b>[RISING DREAD 0:08–0:30]</b>\n"
        "\"It was a normal day until {t} changed...\"\n"
        "[First sign something is wrong]\n"
        "Jumpscare moment: [sudden reveal]\n"
        "\"The horror of {t} had only begun.\"\n\n"
        "<b>[CLIMAX 0:30–0:50]</b>\n"
        "\"When {t} unleashed its true form...\"\n"
        "[Maximum tension, dramatic reveal]\n"
        "\"No one was prepared for this.\"\n\n"
        "<b>[ENDING 0:50–1:00]</b>\n"
        "\"And {t} was never the same again... 🕯️\"\n"
        "\"Like if this gave you chills! 👇\""
    ),
    "kids": (
        "🧸 <b>Kids Script: {t}</b>\n\n"
        "<b>[HELLO! 0:00–0:05]</b>\n"
        "\"Hi friends! Today {t} has a BIG adventure! 🌟\"\n"
        "[Bright colors, cheerful music]\n\n"
        "<b>[THE PROBLEM 0:05–0:20]</b>\n"
        "\"One day, {t} found a [problem/lost item]...\"\n"
        "\"Oh no! What should {t} do?\"\n"
        "[Simple relatable challenge]\n\n"
        "<b>[HELPING FRIENDS 0:20–0:40]</b>\n"
        "\"First, {t} asked [friend] for help!\"\n"
        "\"Together they tried...\"\n"
        "[Simple teamwork solution]\n\n"
        "<b>[SUCCESS! 0:40–0:55]</b>\n"
        "\"They did it! {t} is so happy! 🎉\"\n"
        "Lesson: \"Remember: asking for help is always okay!\"\n\n"
        "<b>[BYE! 0:55–1:00]</b>\n"
        "\"Bye bye friends! See you next time! 👋\""
    ),
    "motivation": (
        "💪 <b>Motivation Script: {t}</b>\n\n"
        "<b>[WAKE UP CALL 0:00–0:08]</b>\n"
        "\"{t} didn't start as a champion. Nobody does.\"\n"
        "[Show humble beginning]\n\n"
        "<b>[THE STRUGGLE 0:08–0:25]</b>\n"
        "\"They failed. They were told it was impossible.\"\n"
        "\"They doubted themselves every single day.\"\n"
        "[Show hardship montage]\n\n"
        "<b>[THE TURNING POINT 0:25–0:40]</b>\n"
        "\"But then {t} made ONE decision that changed everything:\"\n"
        "\"[The key mindset shift / action]\"\n\n"
        "<b>[THE RISE 0:40–0:55]</b>\n"
        "\"And now? Look at {t}.\"\n"
        "[Achievement montage]\n"
        "\"This could be you.\"\n\n"
        "<b>[CALL TO ACTION 0:55–1:00]</b>\n"
        "\"Your story isn't over. Start today.\"\n"
        "\"Like if {t} inspired you! 💪\""
    ),
    "ai_story": (
        "🤖 <b>AI Story Script: {t}</b>\n\n"
        "<b>[WORLD BUILDING 0:00–0:10]</b>\n"
        "\"In a world where AI and {t} coexist...\"\n"
        "[Futuristic setting established]\n\n"
        "<b>[THE AI ENCOUNTER 0:10–0:25]</b>\n"
        "\"{t} meets an AI that knows everything...\"\n"
        "AI: \"I have seen your future, {t}.\"\n"
        "{t}: \"Then tell me — how does this end?\"\n\n"
        "<b>[THE REVELATION 0:25–0:45]</b>\n"
        "AI reveals shocking prediction about {t}\n"
        "\"But there's one thing even I can't calculate:\"\n"
        "\"The power of human choice.\"\n\n"
        "<b>[DECISION MOMENT 0:45–0:57]</b>\n"
        "{t} chooses their own path, defying the AI\n"
        "\"Sometimes the best algorithm is the heart.\"\n\n"
        "<b>[ENDING 0:57–1:00]</b>\n"
        "\"What would YOU choose? Comment below! 🤖👇\""
    ),
    "quiz": (
        "❓ <b>Quiz Script: {t}</b>\n\n"
        "<b>[QUIZ INTRO 0:00–0:05]</b>\n"
        "\"How well do you REALLY know {t}? Let's find out! ❓\"\n"
        "[Show quiz timer / score board]\n\n"
        "<b>[QUESTION 1 0:05–0:20]</b>\n"
        "\"Question 1: What is {t}'s main superpower?\"\n"
        "A) [Option]  B) [Option]  C) [Option]\n"
        "[3 second pause...]\n"
        "\"The answer is...\"\n\n"
        "<b>[QUESTION 2 0:20–0:38]</b>\n"
        "\"Question 2: When was {t} first introduced?\"\n"
        "[Options + pause + reveal]\n\n"
        "<b>[QUESTION 3 0:38–0:55]</b>\n"
        "\"Final question — HARDEST: {t}'s secret weakness is...\"\n"
        "[Options + dramatic pause + reveal]\n\n"
        "<b>[SCORE 0:55–1:00]</b>\n"
        "\"3/3? You're a true {t} expert! Comment your score! 👇\""
    ),
    "guess": (
        "🎯 <b>Guess Challenge Script: {t}</b>\n\n"
        "<b>[CHALLENGE START 0:00–0:05]</b>\n"
        "\"Can you guess {t} from just 3 clues? 🎯\"\n"
        "[Upbeat music, challenge banner]\n\n"
        "<b>[CLUE 1 0:05–0:18]</b>\n"
        "\"Clue #1: This character [first vague hint]...\"\n"
        "[Silhouette / partial image]\n"
        "\"Still thinking? Here's clue 2!\"\n\n"
        "<b>[CLUE 2 0:18–0:33]</b>\n"
        "\"Clue #2: They are known for [more specific hint]...\"\n"
        "[More of the image revealed]\n"
        "\"Getting closer? One more!\"\n\n"
        "<b>[CLUE 3 0:33–0:48]</b>\n"
        "\"Clue #3: Their catchphrase is...\"\n"
        "[Near full reveal, almost obvious]\n\n"
        "<b>[REVEAL 0:48–1:00]</b>\n"
        "\"If you guessed {t}... YOU'RE RIGHT! 🎉\"\n"
        "\"Comment how many clues you needed! 👇\""
    ),
}


def generate_script(topic: str, script_type: str = "shorts") -> str:
    """Generate a script from template. Replace body with AI call to upgrade."""
    tmpl = _SCRIPTS.get(script_type, _SCRIPTS["shorts"])
    return tmpl.replace("{t}", topic)


# ─────────────────────────────────────────────────────────────────
# TITLE GENERATOR
# ─────────────────────────────────────────────────────────────────

TITLE_TYPES: list[tuple[str, str]] = [
    ("short",          "📌 Short Title"),
    ("long",           "📜 Long Title"),
    ("seo",            "📈 SEO Title"),
    ("clickbait",      "🎣 Clickbait"),
    ("educational",    "📚 Educational"),
    ("funny",          "😂 Funny"),
    ("gaming",         "🎮 Gaming"),
    ("kids",           "🧸 Kids"),
    ("challenge",      "🏆 Challenge"),
    ("reaction",       "😱 Reaction"),
    ("transformation", "✨ Transformation"),
    ("battle",         "⚔️ Battle"),
    ("questions",      "❓ Questions"),
    ("curiosity",      "🔮 Curiosity"),
    ("numbers",        "🔢 Numbers"),
    ("lists",          "📋 Lists"),
]

_TITLE_TEMPLATES: dict[str, list[str]] = {
    "short": [
        "{t} 😱 #Shorts",
        "{t} vs EVERYONE! ⚔️",
        "{t} WINS! 🏆",
        "{t} Transformation ✨",
        "{t} Goes CRAZY! 🔥",
        "{t} Secret REVEALED 💀",
        "{t} BABY Form! 👶",
        "{t} vs EVIL Twin! 😈",
    ],
    "long": [
        "The Complete {t} Story: From Zero to Legend (Full Documentary)",
        "Everything You Need to Know About {t} in 2024",
        "{t} vs ALL Characters: The Ultimate Power Ranking (Ranked)",
        "The Untold Truth Behind {t} That Nobody Talks About",
        "I Spent 30 Days Studying {t} — Here's What I Found",
        "{t} Evolution 2000–2024: Every Change Explained",
        "Why {t} Is The Most Powerful Character Ever Created",
        "The Dark Side of {t} That Creators Never Wanted You To See",
    ],
    "seo": [
        "{t} Powers Explained | Complete Guide 2024",
        "How Strong Is {t}? | Power Level Analysis",
        "{t} vs [CHARACTER] | Who Would Win?",
        "Best {t} Moments | Top 10 Compilation",
        "{t} Origin Story | Everything You Missed",
        "{t} Evolution | All Transformations Ranked",
        "Is {t} The Strongest? | Facts & Evidence",
        "{t} Secrets | Hidden Details You Never Noticed",
    ],
    "clickbait": [
        "{t} Did The IMPOSSIBLE And Nobody Noticed 😱",
        "Nobody Expected {t} To Do THIS! 😮",
        "I Can't Believe {t} Actually Did This... 💀",
        "{t} DESTROYED Everyone And It Wasn't Even Close 🔥",
        "The Moment {t} Changed EVERYTHING! 😨",
        "{t} SECRET That Will SHOCK You! (Not Clickbait)",
        "What {t} Does When Nobody's Watching... 😳",
        "{t} Just BROKE The Internet And Here's Why 📱",
    ],
    "educational": [
        "What Is {t}? Complete Beginner's Guide",
        "5 Things About {t} Every Fan Should Know",
        "The Science Behind {t} Explained Simply",
        "{t} Powers: Real vs Fantasy (Truth Revealed)",
        "How {t} Works: A Step-by-Step Breakdown",
        "Understanding {t}: For Kids and Adults",
        "{t} History Timeline: Every Major Event",
        "Why {t} Matters: The Big Picture Explained",
    ],
    "funny": [
        "{t} Having The Worst Day EVER 😂",
        "{t} Tries To Be Normal For 5 Minutes (Fails)",
        "POV: You're {t} And Nothing Is Working 💀",
        "{t} Discovers Modern Life And Regrets It 😭",
        "When {t} Tries Cooking For The First Time 🍳",
        "{t} vs Gravity (Gravity Wins) 😂",
        "Nobody Told {t} How Stairs Work 🙃",
        "The Many Failures of {t} (A Documentary) 📹",
    ],
    "gaming": [
        "{t} Gameplay — Insane Moments #Shorts",
        "This {t} Play Should Be ILLEGAL 🎮",
        "{t} Clutch That Saved The Game! ⚡",
        "Nobody Plays {t} Like This (Insane Skill) 🔥",
        "{t} World Record BROKEN! (New High Score) 🏆",
        "The {t} Strategy Nobody Knows About (Win Every Time)",
        "{t} Boss Fight In Under 60 Seconds! ⏱️",
        "I Beat {t} Using Only ONE Move 😤",
    ],
    "kids": [
        "{t} Makes New Friends! 🌈",
        "{t}'s Big Adventure Begins! 🎒",
        "Can {t} Save The Day? 🦸",
        "{t} Learns To Share! ❤️",
        "Silly {t} And The Funny Surprise! 😄",
        "{t}'s Colorful World! 🎨",
        "Goodnight {t}! 🌙 Bedtime Story",
        "{t} And Friends: Teamwork Time! 🤝",
    ],
    "challenge": [
        "I Challenged {t} To The IMPOSSIBLE 😱",
        "{t} 24 HOUR Challenge! (Gone Wrong)",
        "The {t} Challenge No One Could Complete",
        "{t} vs 100 People Challenge! 🏆",
        "I Tried The Hardest {t} Challenge...",
        "{t} Speed Challenge! Can They Beat 60 Seconds?",
        "Only 1% Can Complete This {t} Challenge",
        "{t} Takes The Viral Challenge! (Watch This)",
    ],
    "reaction": [
        "{t} Reacts To Their OWN Evolution! 😱",
        "First Time Seeing {t} — People Can't Believe It!",
        "Experts React To {t}'s Power Level (Shocked)",
        "{t} Fans React To THAT Moment 😭",
        "The Internet Reacted To {t} And It's Hilarious 😂",
        "{t}'s Greatest Moment — Watch The Crowd Reaction",
        "Kids Discover {t} For The First Time 🥺",
        "Nobody Was Ready For This {t} Reveal 😮",
    ],
    "transformation": [
        "{t} Before vs After: The Complete Glow Up 💥",
        "{t} ULTIMATE Transformation! Every Form Ranked",
        "Watch {t} Transform In Real Time 😱",
        "{t} Evolution: Weakest To Strongest Form",
        "{t}'s FINAL Form Is Something Else... 💀",
        "Nobody Recognized {t} After THIS Transformation ✨",
        "{t} vs EVIL {t}: The Ultimate Form Battle",
        "The {t} Transformation That Shocked The World 🌍",
    ],
    "battle": [
        "{t} vs [CHARACTER]: The Ultimate Battle ⚔️ #Shorts",
        "Who Wins? {t} vs EVERYONE! 🏆",
        "{t} DESTROYS The Competition! 💥",
        "The Battle Nobody Expected: {t} vs [RIVAL]",
        "{t} vs 1000 Enemies — Can They Survive?",
        "Final Boss {t} vs Hero [NAME]: Epic Showdown",
        "{t} vs Strongest Villain — WHO SURVIVES? ⚡",
        "The LAST BATTLE: {t} vs [ULTIMATE ENEMY]",
    ],
    "questions": [
        "Can {t} REALLY Beat [CHARACTER]? Here's The Truth",
        "What Would Happen If {t} Had No Limits?",
        "Why Did {t} Do THAT? The Real Reason Explained",
        "Could {t} Exist In Real Life? (Science Explains)",
        "What Is {t} ACTUALLY Hiding? (Not Clickbait)",
        "How Did {t} Get So Powerful? The Full Story",
        "Is {t} The Strongest Ever? (Honest Analysis)",
        "What Happens When {t} Loses Control?",
    ],
    "curiosity": [
        "The {t} Secret That Changes Everything... 🔮",
        "You Won't Believe What {t} Is Hiding 😳",
        "{t}'s Hidden Power Was There All Along (Proof)",
        "This Is Why {t} Is Different From All Others",
        "Nobody Noticed This About {t} Until Now...",
        "The Truth About {t} That Will Surprise You",
        "What {t} Doesn't Want You To Know 👀",
        "The {t} Theory That Might Actually Be True 🤯",
    ],
    "numbers": [
        "10 Reasons {t} Is Unstoppable 🔟",
        "5 Things {t} Does Better Than Anyone",
        "Top 3 {t} Moments That Broke The Internet",
        "100 Days With {t}: What I Learned",
        "{t}'s 7 Hidden Abilities RANKED",
        "The #1 Thing About {t} Nobody Mentions",
        "25 Facts About {t} In 60 Seconds ⏱️",
        "{t}'s Power Level: 9000+ Explained 💪",
    ],
    "lists": [
        "All {t} Forms RANKED From Worst To Best",
        "{t} Powers List: Every Ability Explained",
        "Every {t} Enemy, Ranked By Strength",
        "The Complete {t} Timeline (All Events Listed)",
        "{t} Weapons & Gear: Full Tier List 🏅",
        "Best To Worst {t} Episodes — Full Ranking",
        "{t} Friends List: Who Can Be Trusted?",
        "{t} Achievements: Every Record Broken",
    ],
}


def generate_titles(topic: str, title_type: str = "short") -> list[str]:
    """Generate 8 title variations. Replace body with AI call to upgrade."""
    templates = _TITLE_TEMPLATES.get(title_type, _TITLE_TEMPLATES["short"])
    return [t.replace("{t}", topic) for t in templates]


# ─────────────────────────────────────────────────────────────────
# DESCRIPTION GENERATOR
# ─────────────────────────────────────────────────────────────────

DESC_TYPES: list[tuple[str, str]] = [
    ("seo",         "📈 SEO"),
    ("gaming",      "🎮 Gaming"),
    ("kids",        "🧸 Kids"),
    ("entertainment","🎭 Entertainment"),
    ("educational", "📚 Educational"),
    ("challenge",   "🏆 Challenge"),
    ("story",       "📖 Story"),
    ("shorts",      "📱 Shorts"),
    ("long_video",  "🎬 Long Video"),
    ("cta",         "📣 CTA Focus"),
    ("social",      "🌐 Social Links"),
    ("credits",     "©️ Credits"),
]

_DESC_TEMPLATES: dict[str, str] = {
    "seo": (
        "🎬 <b>SEO Description: {t}</b>\n\n"
        "<code>Welcome to our {t} video!\n\n"
        "In this video, we explore everything about {t} — "
        "from origins and powers to the most epic moments ever recorded.\n\n"
        "🔔 SUBSCRIBE for daily {t} content!\n"
        "👍 LIKE if you enjoyed!\n"
        "💬 COMMENT your thoughts below!\n\n"
        "━━━━━━━━━━━━━━\n"
        "🔑 KEYWORDS: {t}, {t} shorts, {t} animation, {t} 2024,\n"
        "{t} vs, {t} evolution, {t} funny, {t} highlights\n"
        "━━━━━━━━━━━━━━\n\n"
        "#{t_safe} #Shorts #Animation #Trending #YouTube\n\n"
        "© All characters belong to their respective owners.\n"
        "No copyright infringement intended. Fan-made content.</code>"
    ),
    "gaming": (
        "🎮 <b>Gaming Description: {t}</b>\n\n"
        "<code>Welcome to the BEST {t} gameplay channel! 🎮\n\n"
        "Today's video: EPIC {t} moments you've NEVER seen before!\n\n"
        "📌 SUBSCRIBE for daily gaming content!\n"
        "🔔 Turn on notifications — we post DAILY!\n"
        "💬 Drop your IGN below — let's play together!\n\n"
        "━━━━━━━━━━━━━━\n"
        "🎯 FEATURED GAME: {t}\n"
        "📊 DIFFICULTY: Expert\n"
        "⏱️ VIDEO LENGTH: ~60 seconds\n"
        "━━━━━━━━━━━━━━\n\n"
        "#{t_safe} #Gaming #Shorts #GamingShorts #Viral\n\n"
        "Business inquiries: [email]</code>"
    ),
    "kids": (
        "🧸 <b>Kids Description: {t}</b>\n\n"
        "<code>Hi friends! Welcome to our {t} channel! 🌈\n\n"
        "Today {t} goes on an amazing adventure!\n"
        "Perfect for kids ages 3-8!\n\n"
        "🌟 Subscribe for new {t} videos every week!\n"
        "👍 Ask a grown-up to like this video!\n"
        "💬 What's your favorite {t} color? Comment below!\n\n"
        "━━━━━━━━━━━━━━\n"
        "👨‍👩‍👧 PARENT INFO:\n"
        "✅ Kid-safe content\n"
        "✅ No violence or scary content\n"
        "✅ Educational and fun!\n"
        "━━━━━━━━━━━━━━\n\n"
        "#{t_safe} #KidsAnimation #CartoonForKids #Learning\n\n"
        "© {t} is property of its respective owners.</code>"
    ),
    "entertainment": (
        "🎭 <b>Entertainment Description: {t}</b>\n\n"
        "<code>You won't BELIEVE what {t} does in this video! 😱\n\n"
        "The most entertaining {t} content on the internet!\n"
        "Laugh, gasp, and enjoy every second!\n\n"
        "🔥 NEW videos dropping EVERY DAY!\n"
        "🔔 Hit SUBSCRIBE + Bell so you never miss one!\n"
        "👇 COMMENT which part surprised you most!\n\n"
        "#{t_safe} #Entertainment #Shorts #Viral #Trending\n\n"
        "© Fair use — fan-made entertainment content.</code>"
    ),
    "educational": (
        "📚 <b>Educational Description: {t}</b>\n\n"
        "<code>Learn everything about {t} in 60 seconds! 📚\n\n"
        "In this educational short, we cover:\n"
        "✅ What is {t}?\n"
        "✅ How does {t} work?\n"
        "✅ Why does {t} matter?\n\n"
        "Perfect for students, teachers, and curious minds!\n\n"
        "🎓 SUBSCRIBE for daily educational content!\n"
        "📖 Check our playlist: [{t} Complete Series]\n"
        "💬 Quiz answer: comment below!\n\n"
        "━━━━━━━━━━━━━━\n"
        "📌 SOURCES: [Add sources here]\n"
        "━━━━━━━━━━━━━━\n\n"
        "#{t_safe} #Education #Learning #Facts #School</code>"
    ),
    "challenge": (
        "🏆 <b>Challenge Description: {t}</b>\n\n"
        "<code>I took on the HARDEST {t} challenge ever! 🏆\n\n"
        "Rules:\n"
        "❌ No retries\n"
        "⏱️ 60 second time limit\n"
        "🔥 Everything on the line!\n\n"
        "Will {t} complete the challenge? Watch to find out!\n\n"
        "🎯 TRY THE CHALLENGE YOURSELF!\n"
        "💬 Comment your result below!\n"
        "🔔 Subscribe for more challenges!\n\n"
        "#{t_safe} #Challenge #Shorts #TryThis #Epic</code>"
    ),
    "story": (
        "📖 <b>Story Description: {t}</b>\n\n"
        "<code>The story of {t} that nobody has told before...\n\n"
        "Chapter summaries:\n"
        "📌 Act 1: The Beginning (0:00)\n"
        "📌 Act 2: The Journey (0:20)\n"
        "📌 Act 3: The Climax (0:45)\n"
        "📌 Ending (0:55)\n\n"
        "🔔 Subscribe for more {t} stories every week!\n"
        "💬 What story should we tell next?\n\n"
        "#{t_safe} #Story #Shorts #Animation #Storytelling</code>"
    ),
    "shorts": (
        "📱 <b>Shorts Description: {t}</b>\n\n"
        "<code>{t} 🔥\n\n"
        "#{t_safe} #Shorts #Viral #Trending #Animation\n\n"
        "🔔 Subscribe for daily {t} Shorts!</code>"
    ),
    "long_video": (
        "🎬 <b>Long Video Description: {t}</b>\n\n"
        "<code>━━ CHAPTERS ━━━━━━━━━━━━━━━━\n"
        "0:00 — Introduction\n"
        "1:30 — {t} Origin Story\n"
        "5:00 — Powers & Abilities\n"
        "9:00 — Greatest Moments\n"
        "12:00 — VS Battle\n"
        "15:00 — Verdict & Conclusion\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to the DEFINITIVE {t} video!\n"
        "Everything you need to know, all in one place.\n\n"
        "📌 SUBSCRIBE: [channel link]\n"
        "👍 LIKE for more deep-dives!\n"
        "🔔 BELL for notifications!\n"
        "💬 COMMENT your take!\n\n"
        "#{t_safe} #YouTube #Documentary #Explained #TopList</code>"
    ),
    "cta": (
        "📣 <b>CTA-Focused Description: {t}</b>\n\n"
        "<code>🔥 {t} content that goes HARD!\n\n"
        "━━ TAKE ACTION NOW! ━━━━━━━━━\n"
        "🔔 SUBSCRIBE — It's free and you won't regret it!\n"
        "👍 LIKE this video — takes 2 seconds!\n"
        "💬 COMMENT — We read every single one!\n"
        "📤 SHARE — Help us grow!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "New {t} video EVERY DAY at [time]!\n\n"
        "#{t_safe} #Shorts #Subscribe #Viral</code>"
    ),
    "social": (
        "🌐 <b>Social Links Description: {t}</b>\n\n"
        "<code>🌟 Welcome to the official {t} channel!\n\n"
        "━━ FOLLOW US EVERYWHERE ━━━━\n"
        "📸 Instagram: @[username]\n"
        "🎵 TikTok: @[username]\n"
        "🐦 Twitter/X: @[username]\n"
        "💬 Discord: discord.gg/[invite]\n"
        "🌐 Website: [website]\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✉️ Business: [business email]\n\n"
        "#{t_safe} #Shorts #Social #Community</code>"
    ),
    "credits": (
        "©️ <b>Credits Description: {t}</b>\n\n"
        "<code>{t} fan-made animation video.\n\n"
        "━━ CREDITS ━━━━━━━━━━━━━━━━\n"
        "🎬 Animation: [Creator Name]\n"
        "🎵 Music: [Artist] via [Platform]\n"
        "🎨 Assets: [Source] (Free to use)\n"
        "🎤 Voice: [Voice Actor / AI Tool]\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ DISCLAIMER:\n"
        "This is fan-made content. {t} and all related\n"
        "characters belong to their respective owners.\n"
        "No copyright infringement intended.\n\n"
        "#{t_safe} #FanMade #Animation #FairUse</code>"
    ),
}


def generate_description(topic: str, desc_type: str = "seo") -> str:
    """Generate structured description. Replace body with AI call to upgrade."""
    tmpl = _DESC_TEMPLATES.get(desc_type, _DESC_TEMPLATES["seo"])
    safe = topic.replace(" ", "")
    return tmpl.replace("{t}", topic).replace("{t_safe}", safe)


# ─────────────────────────────────────────────────────────────────
# TAG GENERATOR
# ─────────────────────────────────────────────────────────────────

TAG_TYPES: list[tuple[str, str]] = [
    ("main",      "🏷 Main Tags"),
    ("related",   "🔗 Related Tags"),
    ("long_tail", "📏 Long-tail Tags"),
    ("trending",  "🔥 Trending Tags"),
    ("search",    "🔍 Search Tags"),
    ("category",  "📂 Category Tags"),
]

_TAG_TEMPLATES: dict[str, list[str]] = {
    "main": [
        "{t}", "{t} shorts", "{t} animation", "{t} 2024", "{t} vs",
        "{t} evolution", "{t} funny", "{t} compilation", "{t} highlights",
        "{t} moments", "{t} best", "youtube shorts", "viral shorts",
    ],
    "related": [
        "{t} character", "{t} powers", "{t} story", "{t} origin",
        "{t} cartoon", "{t} anime", "{t} gameplay", "{t} challenge",
        "animation shorts", "cartoon shorts", "kids animation",
        "trending animation", "character shorts",
    ],
    "long_tail": [
        "{t} vs strongest character ever", "{t} full power revealed",
        "{t} secret abilities unlocked", "{t} evolution from weakest to strongest",
        "{t} funny moments compilation 2024", "{t} best battle ever",
        "{t} transformation complete", "how strong is {t} really",
        "{t} vs all characters fight", "{t} new form 2024",
    ],
    "trending": [
        "{t}", "viral shorts 2024", "trending animation", "shorts viral",
        "character battle", "anime fight", "cartoon funny", "kids youtube",
        "gaming shorts", "challenge shorts", "#shorts", "youtube trending",
        "viral video", "entertainment shorts",
    ],
    "search": [
        "{t} shorts", "{t} animation", "{t} funny", "{t} vs",
        "best {t} moments", "{t} explained", "{t} guide", "watch {t}",
        "{t} evolution", "{t} all forms", "{t} powers", "{t} full story",
    ],
    "category": [
        "animation", "cartoon", "kids content", "entertainment",
        "youtube shorts", "short video", "viral content", "trending",
        "gaming", "anime", "character", "superhero", "funny moments",
        "action animation", "kids animation", "family friendly",
    ],
}


def generate_tags(topic: str, tag_type: str = "main") -> list[str]:
    """Generate tag list. Replace body with AI call to upgrade."""
    templates = _TAG_TEMPLATES.get(tag_type, _TAG_TEMPLATES["main"])
    return [t.replace("{t}", topic) for t in templates]


# ─────────────────────────────────────────────────────────────────
# HASHTAG GENERATOR
# ─────────────────────────────────────────────────────────────────

HASHTAG_TYPES: list[tuple[str, str]] = [
    ("trending",  "🔥 Trending"),
    ("gaming",    "🎮 Gaming"),
    ("kids",      "🧸 Kids"),
    ("ai",        "🤖 AI"),
    ("story",     "📖 Story"),
    ("challenge", "🏆 Challenge"),
    ("shorts",    "📱 Shorts"),
    ("long",      "🎬 Long Video"),
    ("country",   "🌍 Country"),
    ("language",  "🌐 Language"),
]

_HASHTAG_TEMPLATES: dict[str, list[str]] = {
    "trending": [
        "#{t_safe}", "#Shorts", "#Viral", "#Trending", "#YouTube",
        "#Animation", "#Cartoon", "#2024", "#NewVideo", "#MustWatch",
        "#Subscribe", "#Entertainment", "#Funny", "#Epic",
    ],
    "gaming": [
        "#{t_safe}", "#Gaming", "#GameShorts", "#GamingShorts",
        "#Gameplay", "#GamingCommunity", "#Gamer", "#GamingContent",
        "#EpicGaming", "#GamePlay2024", "#ClipOfTheDay", "#GamingMoments",
    ],
    "kids": [
        "#{t_safe}", "#KidsAnimation", "#CartoonForKids", "#ChildrenVideo",
        "#KidsYouTube", "#FamilyFriendly", "#KidsContent", "#FunForKids",
        "#Learning", "#EducationalKids", "#Cartoon", "#KidsChannel",
    ],
    "ai": [
        "#{t_safe}", "#AIContent", "#ArtificialIntelligence", "#AIAnimation",
        "#GenerativeAI", "#AIShorts", "#FutureContent", "#TechShorts",
        "#AICreator", "#SmartContent", "#DigitalContent", "#AIArt",
    ],
    "story": [
        "#{t_safe}", "#Storytelling", "#Story", "#StoryTime", "#Narrative",
        "#Animation", "#CharacterStory", "#StoryShorts", "#Animated",
        "#FanMade", "#CreativeContent", "#Shorts", "#AnimatedStory",
    ],
    "challenge": [
        "#{t_safe}", "#Challenge", "#ChallengeAccepted", "#TryThis",
        "#Viral", "#TrendingChallenge", "#EpicChallenge", "#WinOrLose",
        "#GameChallenge", "#Impossible", "#BeatThe{t_safe}",
    ],
    "shorts": [
        "#{t_safe}", "#Shorts", "#YTShorts", "#YouTubeShorts",
        "#ShortsViral", "#ShortsAnimation", "#Short", "#QuickVideo",
        "#60Seconds", "#Vertical", "#MobileFriendly", "#ShortsCreator",
    ],
    "long": [
        "#{t_safe}", "#LongVideo", "#YouTube", "#Documentary",
        "#Explained", "#DeepDive", "#Analysis", "#FullVideo",
        "#Education", "#Commentary", "#Review", "#LongFormContent",
    ],
    "country": [
        "#{t_safe}", "#Uzbekistan", "#UzbekContent", "#UZ", "#O'zbek",
        "#CentralAsia", "#UzbekYouTube", "#UzbekCreator",
        "#UzbekAnimation", "#Uzbek", "#Tashkent", "#UzbekShorts",
    ],
    "language": [
        "#{t_safe}", "#English", "#MultiLanguage", "#GlobalContent",
        "#Bilingual", "#EnglishContent", "#InternationalContent",
        "#WorldwideAudience", "#GlobalReach", "#TranslatedContent",
    ],
}


def generate_hashtags(topic: str, hashtag_type: str = "trending") -> list[str]:
    """Generate hashtag list. Replace body with AI call to upgrade."""
    templates = _HASHTAG_TEMPLATES.get(hashtag_type, _HASHTAG_TEMPLATES["trending"])
    safe = topic.replace(" ", "")
    return [h.replace("{t}", topic).replace("{t_safe}", safe) for h in templates]


# ─────────────────────────────────────────────────────────────────
# MUSIC SUGGESTIONS
# ─────────────────────────────────────────────────────────────────

MUSIC_CATS: list[tuple[str, str]] = [
    ("action",    "💥 Action"),
    ("funny",     "😂 Funny"),
    ("kids",      "🧸 Kids"),
    ("gaming",    "🎮 Gaming"),
    ("epic",      "🎺 Epic"),
    ("sad",       "😢 Sad"),
    ("happy",     "😊 Happy"),
    ("adventure", "🗺 Adventure"),
    ("battle",    "⚔️ Battle"),
    ("mystery",   "🔮 Mystery"),
]

_MUSIC_DATA: dict[str, list[dict]] = {
    "action": [
        {"title": "Epic Action",      "source": "YouTube Audio Library", "mood": "Intense, fast-paced",   "bpm": "140+"},
        {"title": "Power Surge",      "source": "Pixabay (free)",        "mood": "Electric, aggressive",  "bpm": "130"},
        {"title": "Battle Ready",     "source": "Epidemic Sound",        "mood": "Cinematic, powerful",   "bpm": "128"},
        {"title": "Adrenaline Rush",  "source": "Free Music Archive",    "mood": "High energy",           "bpm": "145"},
        {"title": "Strike Force",     "source": "Artlist (licensed)",    "mood": "Dynamic, punchy",       "bpm": "138"},
    ],
    "funny": [
        {"title": "Benny Hill Theme",    "source": "Classic (public domain)", "mood": "Comedic chase",       "bpm": "170"},
        {"title": "Clown Loop",          "source": "YouTube Audio Library",   "mood": "Silly, playful",      "bpm": "120"},
        {"title": "Wacky Cartoon",       "source": "Pixabay (free)",          "mood": "Absurd, light",       "bpm": "110"},
        {"title": "Comedy Bumper",       "source": "Free Music Archive",      "mood": "Quirky, short",       "bpm": "130"},
        {"title": "Goofball Shuffle",    "source": "Artlist",                 "mood": "Fun, upbeat",         "bpm": "115"},
    ],
    "kids": [
        {"title": "Happy Little Kids",   "source": "YouTube Audio Library",   "mood": "Cheerful, innocent",  "bpm": "100"},
        {"title": "Playful Day",         "source": "Pixabay (free)",          "mood": "Warm, friendly",      "bpm": "95"},
        {"title": "Rainbow Adventure",   "source": "Free Music Archive",      "mood": "Bright, joyful",      "bpm": "105"},
        {"title": "Cartoon Morning",     "source": "Epidemic Sound",          "mood": "Sunny, uplifting",    "bpm": "98"},
        {"title": "Bubble Pop",          "source": "Artlist",                 "mood": "Cute, fun",           "bpm": "108"},
    ],
    "gaming": [
        {"title": "8-Bit Adventure",     "source": "YouTube Audio Library",   "mood": "Retro, energetic",    "bpm": "150"},
        {"title": "Level Up",            "source": "Pixabay (free)",          "mood": "Electronic, driven",  "bpm": "140"},
        {"title": "Boss Fight",          "source": "Epidemic Sound",          "mood": "Intense, dark",       "bpm": "155"},
        {"title": "Victory Theme",       "source": "Free Music Archive",      "mood": "Triumphant, short",   "bpm": "120"},
        {"title": "Neon Chase",          "source": "Artlist",                 "mood": "Synthwave, fast",     "bpm": "145"},
    ],
    "epic": [
        {"title": "Cinematic Epicness",  "source": "YouTube Audio Library",   "mood": "Grand, orchestral",   "bpm": "120"},
        {"title": "Hall of Heroes",      "source": "Epidemic Sound",          "mood": "Majestic, powerful",  "bpm": "115"},
        {"title": "Ascension",           "source": "Artlist",                 "mood": "Building, sweeping",  "bpm": "118"},
        {"title": "Final Stand",         "source": "Free Music Archive",      "mood": "Dramatic, massive",   "bpm": "125"},
        {"title": "Empire of Glory",     "source": "Pixabay (free)",          "mood": "Triumphant, cinematic","bpm": "112"},
    ],
    "sad": [
        {"title": "Sad Piano",           "source": "YouTube Audio Library",   "mood": "Melancholic, quiet",  "bpm": "70"},
        {"title": "Rain Drops",          "source": "Pixabay (free)",          "mood": "Somber, reflective",  "bpm": "65"},
        {"title": "Goodbye",             "source": "Epidemic Sound",          "mood": "Emotional, gentle",   "bpm": "72"},
        {"title": "Memories Fade",       "source": "Free Music Archive",      "mood": "Nostalgic, soft",     "bpm": "68"},
        {"title": "Empty Spaces",        "source": "Artlist",                 "mood": "Lonely, minimal",     "bpm": "60"},
    ],
    "happy": [
        {"title": "Good Vibes",          "source": "YouTube Audio Library",   "mood": "Cheerful, uplifting", "bpm": "120"},
        {"title": "Summer Fun",          "source": "Pixabay (free)",          "mood": "Light, breezy",       "bpm": "115"},
        {"title": "Positive Energy",     "source": "Epidemic Sound",          "mood": "Warm, motivating",    "bpm": "125"},
        {"title": "Sunshine Day",        "source": "Free Music Archive",      "mood": "Bright, friendly",    "bpm": "118"},
        {"title": "Celebration",         "source": "Artlist",                 "mood": "Festive, fun",        "bpm": "130"},
    ],
    "adventure": [
        {"title": "Epic Journey",        "source": "YouTube Audio Library",   "mood": "Adventurous, exciting","bpm": "128"},
        {"title": "New Horizons",        "source": "Pixabay (free)",          "mood": "Exploring, hopeful",  "bpm": "122"},
        {"title": "Discovery",           "source": "Epidemic Sound",          "mood": "Wonder, building",    "bpm": "120"},
        {"title": "Quest Begins",        "source": "Free Music Archive",      "mood": "Determined, energetic","bpm": "132"},
        {"title": "Into The Unknown",    "source": "Artlist",                 "mood": "Mysterious, epic",    "bpm": "118"},
    ],
    "battle": [
        {"title": "Clash of Warriors",   "source": "YouTube Audio Library",   "mood": "Intense, aggressive", "bpm": "160"},
        {"title": "War Drums",           "source": "Pixabay (free)",          "mood": "Tribal, powerful",    "bpm": "140"},
        {"title": "Combat Zone",         "source": "Epidemic Sound",          "mood": "Electronic, hard",    "bpm": "155"},
        {"title": "Showdown",            "source": "Free Music Archive",      "mood": "Tense, dramatic",     "bpm": "145"},
        {"title": "Steel and Fire",      "source": "Artlist",                 "mood": "Cinematic battle",    "bpm": "148"},
    ],
    "mystery": [
        {"title": "Dark Secrets",        "source": "YouTube Audio Library",   "mood": "Eerie, suspenseful",  "bpm": "90"},
        {"title": "Unsolved",            "source": "Pixabay (free)",          "mood": "Tense, curious",      "bpm": "85"},
        {"title": "Shadows Fall",        "source": "Epidemic Sound",          "mood": "Dark, atmospheric",   "bpm": "80"},
        {"title": "The Unknown",         "source": "Free Music Archive",      "mood": "Haunting, deep",      "bpm": "75"},
        {"title": "Hidden Truth",        "source": "Artlist",                 "mood": "Investigative, moody", "bpm": "88"},
    ],
}


def get_music_suggestions(category: str = "action") -> list[dict]:
    """Return music track suggestions for a category."""
    return _MUSIC_DATA.get(category, _MUSIC_DATA["action"])


# ─────────────────────────────────────────────────────────────────
# GAMEPLAY SUGGESTIONS
# ─────────────────────────────────────────────────────────────────

GAMEPLAY_TYPES: list[tuple[str, str]] = [
    ("tiles_hop",      "🎵 Tiles Hop"),
    ("subway",         "🚇 Subway Surfers"),
    ("minecraft",      "⛏️ Minecraft"),
    ("geometry",       "📐 Geometry Dash"),
    ("roblox",         "🧊 Roblox"),
    ("temple_run",     "🏃 Temple Run"),
    ("other",          "🎮 Other"),
]

_GAMEPLAY_DATA: dict[str, list[dict]] = {
    "tiles_hop": [
        {"tip": "Trend'dagi qo'shiq tanlang (oxirgi 2 hafta ichida chiqgan)"},
        {"tip": "Miss qilganda katta reaksiyon bering — kulgu yoki shok"},
        {"tip": "Birinchi 3 soniyada eng qiyin qismni ko'rsating"},
        {"tip": "5000+ ball — thumbnail'da yozing"},
        {"tip": "K-pop yoki viral anime soundtrack ishlatishni ko'ring"},
    ],
    "subway": [
        {"tip": "1000m+ masofani 30 soniya ichida ko'rsating"},
        {"tip": "Jetpack + megahead + score combo — viral formula"},
        {"tip": "CLOSE CALL momentlari — thumbnail'da freezeframe qiling"},
        {"tip": "Character va board kombinatsiyasi — trenddagi birini tanlang"},
        {"tip": "High score world record — raqamni sarlavhada ko'rsating"},
    ],
    "minecraft": [
        {"tip": "Parkour challenge — 60 soniyada qancha blok — qiziq format"},
        {"tip": "Speedrun challenge — world rekord urinishi"},
        {"tip": "Custom map — murakkab to'siqlar seriyasi"},
        {"tip": "One-block survival — noyob challenge format"},
        {"tip": "Build battle shorts — 30 soniyada kim yaxshiroq quriladi"},
    ],
    "geometry": [
        {"tip": "Demon level completion — 100% yetish momentini ko'rsating"},
        {"tip": "First attempt win — kutilmagan g'alaba viral bo'ladi"},
        {"tip": "Hardest level highlight — qiyin joydan boshlang"},
        {"tip": "Practice mode vs Normal mode comparison — ikki oyna"},
        {"tip": "Custom level showcase — o'z level'ingizni ko'rsating"},
    ],
    "roblox": [
        {"tip": "Obby completion speed run — tezlik muhim"},
        {"tip": "Trolling moments in popular games — kulgili reaksiyalar"},
        {"tip": "New game first look — trend wave'ni ushlang"},
        {"tip": "1v1 battle highlights — do'stlar bilan"},
        {"tip": "Rarest item showcase — collectors uchun viral"},
    ],
    "temple_run": [
        {"tip": "10M+ score — thumbnail'da kattal raqam ko'rsating"},
        {"tip": "Perfect run (no stumbles) — challenge format"},
        {"tip": "Character unlock montage — progress video"},
        {"tip": "Speedrun comparison — eski score vs yangi score"},
        {"tip": "Power-up combo strategy — educational + entertaining"},
    ],
    "other": [
        {"tip": "Eng yangi trenddagi o'yinni tanlang — hype wave'ni ishlating"},
        {"tip": "World record urinishi — maqsad qo'ying"},
        {"tip": "Failure compilation — kulgu uchun fail montaj qiling"},
        {"tip": "Beginners guide format — informative + funny"},
        {"tip": "Fan vs Pro challenge — skill gap ko'rsating"},
    ],
}


def get_gameplay_suggestions(category: str = "minecraft") -> list[dict]:
    """Return gameplay tips for a category."""
    return _GAMEPLAY_DATA.get(category, _GAMEPLAY_DATA["other"])
