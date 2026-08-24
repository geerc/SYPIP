from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd


def _table(frame: pd.DataFrame, hidden: tuple[str, ...] = ()) -> str:
    display = frame.drop(columns=[column for column in hidden if column in frame], errors="ignore").copy()
    display.insert(0, "Rank", display.index)
    return display.to_html(index=False, border=0, classes="rankings-table", escape=True)


def render_site(*, output: Path, title: str, league_name: str, season: str, week: int, rankings: pd.DataFrame, summary: str | None, playoffs: pd.DataFrame | None, standings: pd.DataFrame, luck: pd.DataFrame) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    summary_html = f'<section class="recap"><h2>Week {week} recap</h2><div class="prose">{escape(summary).replace(chr(10), "<br>")}</div></section>' if summary else '<p class="note">AI recap omitted. Add <code>OPENAI_API_KEY</code> to enable it.</p>'
    playoffs_html = f'<section><h2>Playoff probabilities</h2>{_table(playoffs)}</section>' if playoffs is not None else ""
    generated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Weekly Sleeper fantasy football power rankings for {escape(league_name)}">
<title>{escape(title)}</title><link rel="stylesheet" href="assets/site.css"></head>
<body><header class="hero"><div class="wrap"><p class="eyebrow">{escape(season)} · Week {week}</p><h1>{escape(title)}</h1><p>{escape(league_name)} · Powered by Sleeper results and KeepTradeCut roster values</p></div></header>
<main class="wrap"><section><div class="section-title"><div><p class="eyebrow">The table</p><h2>Power rankings</h2></div><p class="note">Performance gains weight as the season progresses.</p></div>{_table(rankings, ("roster_id", "Performance Score", "Roster Value"))}</section>
{summary_html}{playoffs_html}<section><h2>Projected standings</h2>{_table(standings)}</section><section><h2>Luck index</h2><p class="note">Positive means fortunate; negative means unlucky. Based on opponent draw, score consistency, and close-game outcomes.</p>{_table(luck)}</section>
<footer>Generated {generated}. Data updates when the scheduled GitHub workflow runs.</footer></main></body></html>'''
    (output / "index.html").write_text(html, encoding="utf-8")
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "site.css").write_text(CSS, encoding="utf-8")
    return output / "index.html"


CSS = """
:root{--ink:#17231d;--muted:#617067;--paper:#f5f1e7;--card:#fffdf7;--line:#d8d3c6;--accent:#ee5b2b;--green:#1d6949}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{width:min(1120px,calc(100% - 32px));margin:auto}.hero{padding:72px 0 64px;background:var(--ink);color:#fff;border-bottom:8px solid var(--accent)}.hero h1{font:800 clamp(2.8rem,8vw,6.5rem)/.92 Georgia,serif;max-width:900px;margin:.12em 0}.hero p:last-child{color:#cad3cd}.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-weight:800;font-size:.78rem;color:var(--accent)}main{padding:36px 0 72px}section{margin:0 0 48px;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:clamp(18px,4vw,38px);box-shadow:0 14px 40px #17231d0d}h2{font:800 clamp(1.8rem,5vw,3rem)/1 Georgia,serif;margin:.2em 0 .7em}.section-title{display:flex;align-items:end;justify-content:space-between;gap:24px}.note{color:var(--muted);font-size:.92rem}.rankings-table{width:100%;border-collapse:collapse;display:block;overflow-x:auto}.rankings-table th{background:var(--ink);color:#fff;text-align:left;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase}.rankings-table th,.rankings-table td{padding:13px 15px;border-bottom:1px solid var(--line);white-space:nowrap}.rankings-table tr:nth-child(even) td{background:#f5f1e780}.rankings-table td:first-child{font-weight:900;color:var(--accent)}.prose{max-width:800px;color:#324238}footer{color:var(--muted);font-size:.82rem;text-align:center}@media(max-width:650px){.hero{padding:52px 0 42px}.section-title{display:block}section{border-radius:12px;padding:18px}.rankings-table th,.rankings-table td{padding:10px 11px;font-size:.86rem}}
"""

