import requests
from tabulate import tabulate
# === CONFIGURATION ===
LEAGUE_ID = "1255668983974072320"  # Replace with your Sleeper league ID
WEEKS = 5  # Set to your league's regular season length


# === STEP 1: Fetch league data ===
def fetch_rosters(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    return requests.get(url).json()


def fetch_users(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    return requests.get(url).json()


def fetch_matchups(league_id, week):
    url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
    return requests.get(url).json()


rosters = fetch_rosters(LEAGUE_ID)
users = fetch_users(LEAGUE_ID)

# Map roster_id -> owner_id
roster_to_owner = {r['roster_id']: r['owner_id'] for r in rosters}

# Map owner_id -> team name
owner_to_team = {user['user_id']: user['display_name'] for user in users}

# Initialize all-play wins tracker
all_play_wins = {r['owner_id']: 0 for r in rosters}

# === STEP 2: Calculate all-play wins ===
for week in range(1, WEEKS + 1):
    weekly_matchups = fetch_matchups(LEAGUE_ID, week)

    # Build a list of (owner_id, points)
    weekly_scores = [(roster_to_owner[m['roster_id']], m['points']) for m in weekly_matchups]

    # Compare every team against every other team
    for i, (team_a, score_a) in enumerate(weekly_scores):
        for j, (team_b, score_b) in enumerate(weekly_scores):
            if i == j:
                continue
            if score_a > score_b:
                all_play_wins[team_a] += 1

# === STEP 3: Calculate All Play Win % ===
num_teams = len(rosters)
max_all_play_wins = (num_teams - 1) * WEEKS

all_play_pct = {
    owner_id: wins / max_all_play_wins
    for owner_id, wins in all_play_wins.items()
}

# === STEP 4: Build and display leaderboard ===
leaderboard = sorted(
    [(owner_to_team[owner_id], pct) for owner_id, pct in all_play_pct.items()],
    key=lambda x: x[1],
    reverse=True
)

print("=== Sleeper Fantasy League Power Rankings (All Play Win %) ===")
# Prepare table rows
table = []
for rank, (team, pct) in enumerate(leaderboard, 1):
    table.append([rank, team, f"{pct:.3f}"])

# Print leaderboard using tabulate
print(tabulate(table, headers=["Rank", "Team", "All Play Win %"], tablefmt="grid"))