import pandas as pd
from rapidfuzz import process

# Paths
bat_file = "outputs/cleaned_data/odi_batting_merged.csv"
bowl_file = "outputs/cleaned_data/odi_bowling_merged.csv"

# ---------------- Helper Functions ----------------
def fuzzy_match(name: str, choices):
    """Find closest fuzzy match from a list of choices"""
    match, score, _ = process.extractOne(name.lower(), choices, score_cutoff=60)
    return match if match else None

def get_career_stats(df, player_clean, stat_cols):
    """Get career stats row for player from merged Kaggle data"""
    career_row = df[df["player_clean"] == player_clean].iloc[0]
    return {col: career_row[col] for col in stat_cols if col in career_row}

# ---------------- Main Query ----------------
def query_player_vs_team(player_name: str, opposition: str):
    # Load datasets
    bat_df = pd.read_csv(bat_file, low_memory=False)
    bowl_df = pd.read_csv(bowl_file, low_memory=False)

    # Build player + opposition choices
    player_choices = list(bat_df["player_clean"].dropna().unique()) + \
                     list(bowl_df["player_clean"].dropna().unique())
    opp_choices = list(bat_df["opposition"].dropna().unique())

    # Fuzzy match
    player_clean = fuzzy_match(player_name, player_choices)
    opposition_match = fuzzy_match(opposition, opp_choices)

    if not player_clean:
        print(f"No player found matching {player_name}")
        return
    if not opposition_match:
        print(f"No opposition found matching {opposition}")
        return

    print(f"\n=== ODI STATS for {player_name.title()} vs {opposition_match} ===\n")

    # ---------------- Batting ----------------
    bat_player = bat_df[
        (bat_df["player_clean"] == player_clean) &
        (bat_df["opposition"] == opposition_match)
    ]

    if not bat_player.empty:
        matches = bat_player["match_id"].nunique(

            
        )
        runs = bat_player["runs"].sum()
        balls = bat_player["balls"].sum()
        dismissals = bat_player["dismissals"].sum()

        # Fallback to Kaggle career avg if dismissals = 0
        if dismissals > 0:
            avg = runs / dismissals
        else:
            career_avg = get_career_stats(bat_df, player_clean, ["average"]).get("average", "N/A")
            avg = f"N/A (career {career_avg})"

        sr = (runs / balls * 100) if balls > 0 else "N/A"

        print("Batting Stats:")
        print(f" Matches: {matches}")
        print(f" Runs: {runs}, Balls: {balls}, Average: {avg}, SR: {sr if sr=='N/A' else round(sr,2)}")
    else:
        print("No Batting Records Found.")

    print()

    # ---------------- Bowling ----------------
    bowl_player = bowl_df[
        (bowl_df["player_clean"] == player_clean) &
        (bowl_df["opposition"] == opposition_match)
    ]

    if not bowl_player.empty:
        matches = bowl_player["match_id"].nunique()
        balls = bowl_player["balls"].sum()
        overs = balls // 6 + (balls % 6) / 10
        runs_conceded = bowl_player["runs_conceded"].sum()
        wickets = bowl_player["wickets"].sum()

        if wickets > 0:
            avg = runs_conceded / wickets
            sr = balls / wickets
        else:
            # Fallback to Kaggle bowling stats
            career_stats = get_career_stats(
                bowl_df, player_clean, ["average", "strike_rate"]
            )
            avg = f"N/A (career {career_stats.get('average','N/A')})"
            sr = f"N/A (career {career_stats.get('strike_rate','N/A')})"

        econ = runs_conceded / (balls / 6) if balls > 0 else "N/A"

        print("Bowling Stats:")
        print(f" Matches: {matches}")
        print(f" Overs: {overs}, Runs: {runs_conceded}, Wickets: {wickets}, "
              f"Average: {avg}, Econ: {econ if econ=='N/A' else round(econ,2)}, SR: {sr}")
    else:
        print("No Bowling Records Found.")

# ---------------- Run ----------------
if __name__ == "__main__":
    player = input("Enter player name: ")
    opposition = input("Enter opposition team: ")
    query_player_vs_team(player, opposition)
