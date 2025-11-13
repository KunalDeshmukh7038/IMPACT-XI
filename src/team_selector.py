import pandas as pd

# Path to master dataset
MASTER_FILE = "outputs/cleaned_data/odi_master.csv"

def load_master():
    """Load the master ODI dataset."""
    df = pd.read_csv(MASTER_FILE)
    return df

def rank_batters(df):
    """Rank batters based on Runs, Average, and Strike Rate."""
    bat_df = df[df["playing_role"].str.contains("bat", case=False, na=False)].copy()
    bat_df["bat_score"] = (
        (bat_df["runs"].fillna(0) / 1000) +
        (bat_df["average_score"].fillna(0) / 50) +
        (bat_df["strike_rate"].fillna(0) / 100)
    )
    return bat_df.sort_values("bat_score", ascending=False)

def rank_bowlers(df):
    """Rank bowlers based on Wickets, Economy, and Bowling Average."""
    bowl_df = df[df["playing_role"].str.contains("bowl", case=False, na=False)].copy()
    bowl_df["bowl_score"] = (
        (bowl_df["wickets"].fillna(0) / 50) +
        (50 / (bowl_df["bowling_avg"].replace(0, pd.NA).fillna(50))) +
        (5 / (bowl_df["bowling_econ"].replace(0, pd.NA).fillna(5)))
    )
    return bowl_df.sort_values("bowl_score", ascending=False)

def rank_allrounders(df):
    """Rank allrounders combining batting and bowling contribution."""
    ar_df = df[df["playing_role"].str.contains("allround", case=False, na=False)].copy()
    ar_df["allround_score"] = (
        (ar_df["runs"].fillna(0) / 500) +
        (ar_df["wickets"].fillna(0) / 20)
    )
    return ar_df.sort_values("allround_score", ascending=False)

def rank_wicketkeepers(df):
    """Rank wicketkeeper batters by batting stats and dismissals if available."""
    wk_df = df[df["playing_role"].str.contains("wicketkeeper", case=False, na=False)].copy()
    wk_df["wk_score"] = (
        (wk_df["runs"].fillna(0) / 500) +
        (wk_df["average_score"].fillna(0) / 30)
    )
    return wk_df.sort_values("wk_score", ascending=False)

def select_best_xi(df):
    """Select the best XI players based on role constraints."""
    batters = rank_batters(df).head(4)
    allrounders = rank_allrounders(df).head(2)
    keeper = rank_wicketkeepers(df).head(1)
    bowlers = rank_bowlers(df).head(4)

    xi = pd.concat([batters, allrounders, keeper, bowlers])
    return xi[["name", "country_id", "playing_role"]]

if __name__ == "__main__":
    print("\n🏏 Building Best XI from odi_master.csv...\n")
    df = load_master()
    best_xi = select_best_xi(df)
    print(best_xi.to_string(index=False))
