import pandas as pd

# File paths (already generated from merge step)
bat_file = "outputs/cleaned_data/odi_batting_merged.csv"
bowl_file = "outputs/cleaned_data/odi_bowling_merged.csv"


def compute_batting_score(row):
    """Compute batting score for a single row of stats."""
    try:
        avg_vs_opp = row["runs"] / row["dismissals"] if row["dismissals"] > 0 else row["runs"]
        sr_vs_opp = (row["runs"] / row["balls"] * 100) if row["balls"] > 0 else 0

        # Career average from Kaggle stats (already merged)
        career_avg = 0
        if pd.notna(row.get("average")):
            try:
                career_avg = float(row["average"])
            except:
                career_avg = 0

        # Weighted score formula
        score = (0.5 * avg_vs_opp) + (0.3 * career_avg) + (0.2 * sr_vs_opp)
        return round(score, 2)
    except Exception:
        return 0


def compute_bowling_score(row):
    """Compute bowling score for a single row of stats."""
    try:
        wickets = row["wickets"]
        econ_vs_opp = row["runs_conceded"] / (row["balls"] / 6) if row["balls"] > 0 else 10

        # Career wickets
        career_wickets = 0
        if pd.notna(row.get("wickets_career")):
            try:
                career_wickets = float(row["wickets_career"])
            except:
                career_wickets = 0

        # Weighted score formula
        score = (0.5 * wickets) + (0.3 * career_wickets) - (0.2 * econ_vs_opp)
        return round(score, 2)
    except Exception:
        return 0


def test_scoring_example():
    """Quick test for Kohli vs Australia"""
    bat_df = pd.read_csv(bat_file, low_memory=False)
    bowl_df = pd.read_csv(bowl_file, low_memory=False)

    kohli_bat = bat_df[(bat_df["player_clean"] == "v kohli") & (bat_df["opposition"] == "Australia")]
    kohli_bowl = bowl_df[(bowl_df["player_clean"] == "v kohli") & (bowl_df["opposition"] == "Australia")]

    print("\n=== Testing Scoring Engine ===")

    if not kohli_bat.empty:
        print("Kohli Batting Score vs Australia:", compute_batting_score(kohli_bat.iloc[0]))
    else:
        print("No batting records for Kohli vs Australia")

    if not kohli_bowl.empty:
        print("Kohli Bowling Score vs Australia:", compute_bowling_score(kohli_bowl.iloc[0]))
    else:
        print("No bowling records for Kohli vs Australia")


if __name__ == "__main__":
    test_scoring_example()
