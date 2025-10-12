#!/usr/bin/env python3
"""
Fetch Sleeper league data and write data/leaderboard.json for Hugo.
Reads LEAGUE_ID and WEEKS from environment variables (Netlify UI or local env).
"""

import os
import sys
import json
import requests
from pathlib import Path

LEAGUE_ID = os.environ.get("LEAGUE_ID")
WEEKS = int(os.environ.get("WEEKS", "14"))  # default 14 weeks

if not LEAGUE_ID:
    print("ERROR: LEAGUE_ID env var not set.", file=sys.stderr)
    sys.exit(2)

OUT_DIR = Path("data")
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / "leaderboard.json"

def fetch_json(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_rosters(league_id):
    return fetch_json(f"https://api.sleeper.app/v1/league/{league_id}/rosters")

def fetch_users(league_id):
    return fetch_json(f"https://api.sleeper.app/v1/league/{league_id}/users")

def fetch_matchups(league_id, week):
    return fetch_json(f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}")

def calculate_all_play(league_id, weeks):
    rosters = fetch_rosters(league_id)
    users = fetch_users(league_id)

    # roster_id -> owner_id
    roster_to_owner = {int(r['roster_id']): r.get('owner_id') for r in rosters}
    # owner_id -> display name (fallback to user_id if missing)
    owner_to_team = {u['user_id']: u.get('display_name') or u['user_id'] for u in users}

    # initialize all-play wins
    all_play_wins = {r.get('owner_id'): 0 for r in rosters}

    for week in range(1, weeks + 1):
        try:
            weekly_matchups = fetch_matchups(league_id, week)
        except requests.HTTPError as e:
            # If a week does not exist (e.g., future weeks), skip it
            print(f"Warning: could not fetch week {week}: {e}", file=sys.stderr)
            continue

        # Build list of (owner_id, points) for all rosters that have a score this week.
        weekly_scores = []
        for m in weekly_matchups:
            roster_id = int(m.get('roster_id'))
            owner = roster_to_owner.get(roster_id)
            if owner is None:
                # skip rosters we can't map
                continue
            points = m.get('points', 0) or 0
            weekly_scores.append((owner, float(points)))

        # compare each team against every other team (all-play)
        n = len(weekly_scores)
        for i, (team_a, score_a) in enumerate(weekly_scores):
            for j, (team_b, score_b) in enumerate(weekly_scores):
                if i == j:
                    continue
                if score_a > score_b:
                    all_play_wins[team_a] = all_play_wins.get(team_a, 0) + 1
                elif score_a == score_b:
                    # Half win for ties (optional). Uncomment if you prefer half-wins:
                    # all_play_wins[team_a] = all_play_wins.get(team_a, 0) + 0.5
                    pass

    num_teams = len(rosters)
    max_all_play_wins = (num_teams - 1) * weeks if num_teams > 1 else 1

    # Build leaderboard list of dicts
    leaderboard = []
    for owner_id, wins in all_play_wins.items():
        pct = wins / max_all_play_wins if max_all_play_wins else 0
        team_name = owner_to_team.get(owner_id, owner_id)
        leaderboard.append({
            "owner_id": owner_id,
            "team": team_name,
            "all_play_wins": wins,
            "all_play_pct": round(pct, 4)
        })

    # Sort desc by pct, then by wins
    leaderboard.sort(key=lambda x: (x['all_play_pct'], x['all_play_wins']), reverse=True)
    return leaderboard

def main():
    leaderboard = calculate_all_play(LEAGUE_ID, WEEKS)
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump({"league_id": LEAGUE_ID, "weeks": WEEKS, "leaderboard": leaderboard}, f, indent=2)
    print(f"Wrote {OUT_FILE}")

if __name__ == "__main__":
    main()
