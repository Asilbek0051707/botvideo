"""Configurable Viral Score Engine.

Rules are data-driven so weights can be adjusted without touching UI code.
Architecture is ready for future AI/ML integration (replace SCORE_RULES
with a learned model that returns the same (score, verdict, reasons) tuple).
"""

from __future__ import annotations

import random
from typing import Any

from telegram_bot.services.character_service import char_service

# ── Rule table — edit weights here without touching handlers ──────

SCORE_RULES: list[dict[str, Any]] = [
    {"name": "char_in_db",          "weight": 30, "desc": "✅ Bazada mavjud karakter"},
    {"name": "trending_char_match", "weight": 25, "desc": "🔥 Trending karakter mos keldi"},
    {"name": "trending_movie",      "weight": 20, "desc": "🎬 Trending kino/multfilm"},
    {"name": "short_name_10",       "weight": 10, "desc": "📏 Qisqa, yodda qoladigan nom (≤10)"},
    {"name": "short_name_20",       "weight":  5, "desc": "📏 Yaxshi nom uzunligi (≤20)"},
    {"name": "viral_keyword",       "weight":  8, "desc": "🎯 Viral kalit so'z mavjud"},
    {"name": "multi_keyword",       "weight":  6, "desc": "💡 Bir nechta viral kalit so'z"},
    {"name": "luck_factor",         "weight":  7, "desc": "🎲 Omad faktori"},   # ±7
]

_VIRAL_KEYWORDS = [
    "vs", "evolution", "all characters", "funny", "challenge",
    "transformation", "baby", "minecraft", "roblox", "shorts",
    "animation", "compilation", "trending", "viral", "epic",
    "battle", "war", "rescue", "mystery", "hidden", "secret",
    "impossible", "scary", "cursed", "ultra", "ultra instinct",
    "sigma", "rizz", "skibidi", "brainrot", "ohio",
]

_TRENDING_CHARS_POOL = [
    "spider-man", "batman", "goku", "sonic", "pikachu",
    "minecraft", "steve", "roblox", "skibidi", "huggy wuggy",
    "bluey", "paw patrol", "chase", "mario", "luigi", "peach",
    "optimus prime", "transformers", "tmnt", "ninja turtles",
]

_TRENDING_MOVIES_POOL = [
    "moana", "inside out", "frozen", "despicable me", "puss in boots",
    "elemental", "wish", "the wild robot", "migration", "trolls",
    "kung fu panda", "sonic the hedgehog", "detective pikachu",
    "super mario bros", "transformers", "teenage mutant ninja turtles",
    "minions", "encanto", "turning red", "brave",
]


def calculate(
    topic: str,
    rules: list[dict] | None = None,
) -> tuple[int, str, list[str]]:
    """
    Calculate viral score for a topic.

    :param topic: Video topic, character name, or idea title.
    :param rules: Optional rule table override (for future AI tuning).
    :return: (score 0-100, verdict_text, reasons_list)
    """
    active_rules = rules or SCORE_RULES
    rule_map = {r["name"]: r for r in active_rules}

    score = 0
    reasons: list[str] = []
    tl = topic.lower()

    # ── char_in_db ──
    w = rule_map.get("char_in_db", {}).get("weight", 0)
    if w and char_service.search(tl, limit=1):
        score += w
        reasons.append(f"{rule_map['char_in_db']['desc']} (+{w})")

    # ── trending_char_match ──
    w = rule_map.get("trending_char_match", {}).get("weight", 0)
    if w and any(c in tl for c in _TRENDING_CHARS_POOL):
        score += w
        reasons.append(f"{rule_map['trending_char_match']['desc']} (+{w})")

    # ── trending_movie ──
    w = rule_map.get("trending_movie", {}).get("weight", 0)
    if w and any(m in tl for m in _TRENDING_MOVIES_POOL):
        score += w
        reasons.append(f"{rule_map['trending_movie']['desc']} (+{w})")

    # ── short_name_10 / short_name_20 ──
    if len(topic) <= 10:
        w = rule_map.get("short_name_10", {}).get("weight", 0)
        if w:
            score += w
            reasons.append(f"{rule_map['short_name_10']['desc']} (+{w})")
    elif len(topic) <= 20:
        w = rule_map.get("short_name_20", {}).get("weight", 0)
        if w:
            score += w
            reasons.append(f"{rule_map['short_name_20']['desc']} (+{w})")

    # ── viral_keyword + multi_keyword ──
    matched = [kw for kw in _VIRAL_KEYWORDS if kw in tl]
    if matched:
        w = rule_map.get("viral_keyword", {}).get("weight", 0)
        if w:
            score += w
            reasons.append(f"{rule_map['viral_keyword']['desc']} '{matched[0]}' (+{w})")
        if len(matched) > 1:
            w2 = rule_map.get("multi_keyword", {}).get("weight", 0)
            if w2:
                score += w2
                reasons.append(f"{rule_map['multi_keyword']['desc']} (+{w2})")

    # ── luck_factor ──
    max_luck = rule_map.get("luck_factor", {}).get("weight", 7)
    rng = random.randint(-max_luck, max_luck)
    score += rng
    if rng > 0:
        reasons.append(f"🎲 Omadli vaqt (+{rng})")
    elif rng < 0:
        reasons.append(f"🎲 Raqobat qattiq ({rng})")

    score = max(5, min(95, score))

    if score >= 75:
        verdict = "🔥 YUQORI — olg'a!"
    elif score >= 55:
        verdict = "📈 O'RTA-YUQORI — yaxshi imkon"
    elif score >= 40:
        verdict = "📊 O'RTA — trending hook qo'shing"
    elif score >= 25:
        verdict = "⚠️ PAST — viral element kerak"
    else:
        verdict = "❌ JUDA PAST — mavzuni o'zgartiring"

    return score, verdict, reasons
