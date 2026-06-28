"""Report Generator — create, save and retrieve channel analysis reports.

Generates structured reports from channel/video data.
Ready for AI enhancement: replace _score_channel() with an AI call
that returns the same ReportData shape.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ReportData:
    report_type: str
    title: str
    subject: str                              # channel URL or video URL
    summary: str
    scores: dict                              # {"health": 72, "growth": 60, ...}
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    notes: str = ""
    project_id: int | None = None


# ── Channel scoring ───────────────────────────────────────────────

def _score_channel(ch) -> tuple[int, list[str], list[str], list[str]]:
    """
    Score a ChannelInfo and return (overall, strengths, weaknesses, recs).
    Uses rule-based heuristics. Replace with AI for better accuracy.
    """
    from telegram_bot.services.youtube_service import ChannelInfo

    strengths:       list[str] = []
    weaknesses:      list[str] = []
    recommendations: list[str] = []
    score = 0

    subs = ch.subscriber_count or 0
    views = ch.view_count or 0
    videos = ch.video_count or 1
    avg_views = views // max(videos, 1)

    # Subscriber score (max 25)
    if subs >= 1_000_000:
        score += 25
        strengths.append(f"👥 1M+ obunachi — katta kanal")
    elif subs >= 100_000:
        score += 20
        strengths.append(f"👥 {subs//1000}K obunachi — o'rta-katta kanal")
    elif subs >= 10_000:
        score += 15
        strengths.append(f"👥 {subs//1000}K obunachi — o'sib kelayotgan kanal")
    elif subs >= 1_000:
        score += 8
        weaknesses.append(f"👥 {subs} obunachi — yangi kanal, o'sish kerak")
    else:
        score += 3
        weaknesses.append(f"👥 {subs} obunachi — juda kam, muntazam yuklash kerak")

    # Views per video (max 25)
    if avg_views >= 1_000_000:
        score += 25
        strengths.append(f"👁 O'rtacha {avg_views//1000}K ko'rish — viral darajada")
    elif avg_views >= 100_000:
        score += 20
        strengths.append(f"👁 O'rtacha {avg_views//1000}K ko'rish — juda yaxshi")
    elif avg_views >= 10_000:
        score += 12
        strengths.append(f"👁 O'rtacha {avg_views//1000}K ko'rish — yaxshi")
    elif avg_views >= 1_000:
        score += 7
        weaknesses.append(f"👁 O'rtacha {avg_views} ko'rish — thumbnail/SEO yaxshilang")
    else:
        score += 2
        weaknesses.append(f"👁 O'rtacha {avg_views} ko'rish — juda kam")

    # Video count (max 15)
    if videos >= 100:
        score += 15
        strengths.append(f"🎥 {videos} ta video — katta kontent bazasi")
    elif videos >= 50:
        score += 12
        strengths.append(f"🎥 {videos} ta video — yaxshi kontent miqdori")
    elif videos >= 20:
        score += 8
    elif videos >= 5:
        score += 4
        weaknesses.append(f"🎥 {videos} ta video — ko'proq kontent kerak")
    else:
        score += 1
        weaknesses.append(f"🎥 {videos} ta video — yangi kanal, tezkor yuring")

    # Description (max 10)
    if ch.description and len(ch.description) > 100:
        score += 10
        strengths.append("📝 Kanal tavsifi yaxshi to'ldirilgan")
    elif ch.description:
        score += 5
        recommendations.append("📝 Kanal tavsifini 200+ belgiga uzaytiring")
    else:
        weaknesses.append("📝 Kanal tavsifi yo'q — SEO yo'qoladi")

    # Country info (max 5)
    if ch.country and ch.country != "—":
        score += 5
        strengths.append(f"🌍 Mamlakat belgilangan: {ch.country}")
    else:
        score += 2
        recommendations.append("🌍 Kanal sozlamalarida mamlakat kiriting")

    # Recent videos (max 10)
    if ch.recent_videos:
        score += min(10, len(ch.recent_videos) * 2)
        strengths.append(f"🕐 So'nggi {len(ch.recent_videos)} ta video mavjud")

    # Recommendations
    if subs > 0 and views > 0:
        ratio = views / max(subs, 1)
        if ratio < 5:
            recommendations.append("📊 Ko'rish/Obunachi nisbati past — CTR yaxshilang")
        elif ratio > 50:
            strengths.append("📊 Ko'rish/Obunachi nisbati ajoyib!")

    recommendations += [
        "🔥 Haftada kamida 3–5 Shorts yuklang",
        "🎯 Thumbnail A/B testini boshlang",
        "📅 Doimiy jadval saqlang — algoritm sevadi",
    ]

    overall = min(95, max(10, score))

    if overall >= 70:
        grade = "A"
    elif overall >= 55:
        grade = "B"
    elif overall >= 40:
        grade = "C"
    else:
        grade = "D"

    return overall, strengths[:5], weaknesses[:4], recommendations[:5]


# ── Report generators ─────────────────────────────────────────────

def generate_channel_report(ch) -> ReportData:
    """Generate a channel analysis report from ChannelInfo."""
    overall, strengths, weaknesses, recs = _score_channel(ch)

    subs = ch.subscriber_count
    views = ch.view_count
    videos = ch.video_count
    avg = views // max(videos, 1)

    summary = (
        f"Kanal: {ch.title}\n"
        f"Obunachi: {_fmt(subs)} | Ko'rishlar: {_fmt(views)} | Videolar: {videos}\n"
        f"O'rtacha ko'rish: {_fmt(avg)} | Umumiy ball: {overall}/100"
    )

    scores = {
        "health":      overall,
        "engagement":  min(95, max(5, overall - 5 + (5 if ch.description else -10))),
        "content":     min(95, max(5, min(videos, 100))),
        "growth":      min(95, max(5, overall - 10)),
        "consistency": min(95, max(5, len(ch.recent_videos or []) * 15)),
    }

    return ReportData(
        report_type="channel",
        title=f"Kanal hisoboti: {ch.title}",
        subject=ch.channel_url,
        summary=summary,
        scores=scores,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recs,
    )


def generate_video_report(v) -> ReportData:
    """Generate a video analysis report from VideoInfo."""
    from telegram_bot.services.seo_service import calculate_seo_score

    seo = calculate_seo_score(v.title, v.description, v.tags)

    strengths:       list[str] = []
    weaknesses:      list[str] = []
    recommendations: list[str] = []
    score = 0

    if v.view_count >= 1_000_000:
        score += 30; strengths.append(f"👁 {_fmt(v.view_count)} ko'rish — viral!")
    elif v.view_count >= 100_000:
        score += 22; strengths.append(f"👁 {_fmt(v.view_count)} ko'rish — yaxshi")
    elif v.view_count >= 10_000:
        score += 14; weaknesses.append(f"👁 {_fmt(v.view_count)} ko'rish — o'rta")
    else:
        score += 5;  weaknesses.append(f"👁 {_fmt(v.view_count)} ko'rish — kam")

    if v.like_count > 0 and v.view_count > 0:
        like_rate = v.like_count / v.view_count * 100
        if like_rate >= 5:
            score += 20; strengths.append(f"👍 Like nisbati {like_rate:.1f}% — ajoyib!")
        elif like_rate >= 2:
            score += 12; strengths.append(f"👍 Like nisbati {like_rate:.1f}% — yaxshi")
        else:
            score += 4;  weaknesses.append(f"👍 Like nisbati {like_rate:.1f}% — past")

    score += min(25, seo.score // 4)
    if seo.score >= 60:
        strengths.append(f"🎯 SEO ball: {seo.score}/100 — yaxshi")
    else:
        weaknesses.append(f"🎯 SEO ball: {seo.score}/100 — yaxshilash kerak")
        recommendations += seo.suggestions[:3]

    if v.tags:
        score += 10; strengths.append(f"🏷 {len(v.tags)} ta tag qo'yilgan")
    else:
        weaknesses.append("🏷 Tag yo'q — SEO zaif")
        recommendations.append("🏷 Videoga 5–15 ta tag qo'shing")

    overall = min(95, max(10, score))
    scores = {
        "overall": overall,
        "seo": seo.score,
        "engagement": min(95, max(0, int(v.like_count / max(v.view_count, 1) * 1000))),
    }

    summary = (
        f"Video: {v.title[:60]}\n"
        f"Ko'rishlar: {_fmt(v.view_count)} | Layklar: {_fmt(v.like_count)}\n"
        f"SEO: {seo.score}/100 | Umumiy ball: {overall}/100"
    )

    return ReportData(
        report_type="video",
        title=f"Video hisoboti: {v.title[:60]}",
        subject=f"https://youtu.be/{v.video_id}",
        summary=summary,
        scores=scores,
        strengths=strengths[:4],
        weaknesses=weaknesses[:3],
        recommendations=recommendations[:4],
    )


# ── Format for Telegram ───────────────────────────────────────────

def format_report(rd: ReportData) -> str:
    lines = [f"📊 <b>{rd.title}</b>\n"]
    lines.append(f"📋 <b>Xulosa:</b>\n{rd.summary}\n")

    if rd.scores:
        lines.append("<b>🎯 Ballar:</b>")
        for k, v in rd.scores.items():
            bar = "█" * round(v / 10) + "░" * (10 - round(v / 10))
            lines.append(f"  {k.title()}: <code>[{bar}]</code> {v}/100")

    if rd.strengths:
        lines.append("\n<b>✅ Kuchli tomonlar:</b>")
        for s in rd.strengths:
            lines.append(f"  • {s}")

    if rd.weaknesses:
        lines.append("\n<b>⚠️ Zaif tomonlar:</b>")
        for w in rd.weaknesses:
            lines.append(f"  • {w}")

    if rd.recommendations:
        lines.append("\n<b>💡 Tavsiyalar:</b>")
        for r in rd.recommendations:
            lines.append(f"  → {r}")

    return "\n".join(lines)


# ── DB persistence ────────────────────────────────────────────────

def _save_report_sync(rd: ReportData) -> int:
    from telegram_bot.db.channel_models import AnalysisReport
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rep = AnalysisReport(
            report_type=rd.report_type,
            title=rd.title[:300],
            subject=rd.subject[:500],
            summary=rd.summary,
            scores=json.dumps(rd.scores),
            strengths=json.dumps(rd.strengths),
            weaknesses=json.dumps(rd.weaknesses),
            recommendations=json.dumps(rd.recommendations),
            notes=rd.notes,
            project_id=rd.project_id,
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)
        return rep.id


async def save_report(rd: ReportData) -> int:
    return await asyncio.to_thread(_save_report_sync, rd)


def _list_reports_sync(limit: int = 10, report_type: str | None = None) -> list:
    from telegram_bot.db.channel_models import AnalysisReport
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(AnalysisReport)
        if report_type:
            q = q.filter_by(report_type=report_type)
        return q.order_by(AnalysisReport.created_at.desc()).limit(limit).all()


async def list_reports(limit: int = 10, report_type: str | None = None) -> list:
    return await asyncio.to_thread(_list_reports_sync, limit, report_type)


def _delete_report_sync(report_id: int) -> bool:
    from telegram_bot.db.channel_models import AnalysisReport
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rep = db.get(AnalysisReport, report_id)
        if not rep:
            return False
        db.delete(rep)
        db.commit()
        return True


async def delete_report(report_id: int) -> bool:
    return await asyncio.to_thread(_delete_report_sync, report_id)


def _fmt(n: int | None) -> str:
    if n is None:
        return "Yashirin"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


# ── Channel history ───────────────────────────────────────────────

def _save_channel_sync(ch) -> int:
    from telegram_bot.db.channel_models import ChannelRecord
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        rec = ChannelRecord(
            url=ch.channel_url,
            handle=ch.channel_url.split("/")[-1],
            name=ch.title,
            subs=ch.subscriber_count,
            total_views=ch.view_count,
            video_count=ch.video_count,
            avg_views=ch.view_count // max(ch.video_count, 1),
            country=ch.country if ch.country != "—" else "",
            description=ch.description[:500],
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec.id


async def save_channel_to_history(ch) -> int:
    return await asyncio.to_thread(_save_channel_sync, ch)


def _list_channel_history_sync(limit: int = 5) -> list:
    from telegram_bot.db.channel_models import ChannelRecord
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.query(ChannelRecord).order_by(ChannelRecord.analyzed_at.desc()).limit(limit).all()


async def list_channel_history(limit: int = 5) -> list:
    return await asyncio.to_thread(_list_channel_history_sync, limit)
