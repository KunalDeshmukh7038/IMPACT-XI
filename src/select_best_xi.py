# src/select_best_xi.py
import pandas as pd
import joblib
import os
import json
import numpy as np
from rapidfuzz import process, fuzz

# ==============================
# Alias dictionary
# ==============================
ALIASES = {
    "ms dhoni": "MS Dhoni",
    "dhoni": "MS Dhoni",
    "virat kohli": "V Kohli",
    "kohli": "V Kohli",
    "rohit sharma": "RG Sharma",
    "shikhar dhawan": "S Dhawan",
    "ajinkya rahane": "AM Rahane",
    "suresh raina": "SK Raina",
    "ravindra jadeja": "RA Jadeja",
    "ravichandran ashwin": "R Ashwin",
    "axar patel": "AY Patel",
    "stuart binny": "STR Binny",
    "bhuvneshwar kumar": "B Kumar",
    "umesh yadav": "UT Yadav",
    "mohammed shami": "Mohammed Shami",
    "mohit sharma": "Mohit Sharma"
}


# ==============================
# Utility: Clean numeric columns
# ==============================
def clean_numeric(df):
    numeric_df = df.copy()
    for col in numeric_df.columns:
        if numeric_df[col].dtype == "object":
            numeric_df[col] = (
                numeric_df[col]
                .astype(str)
                .str.replace(r"[^0-9.\-]", "", regex=True)
                .replace("", np.nan)
            )
            try:
                numeric_df[col] = pd.to_numeric(numeric_df[col])
            except Exception:
                pass
    return numeric_df


# ==============================
# Auto Role Detection
# ==============================
def auto_detect_role(row):
    role = str(row.get("playing_role", "")).lower()
    if "wicket" in role:
        return "wicketkeeper batter"
    if "bat" in role:
        return "batter"
    if "bowl" in role:
        return "bowler"
    if "allround" in role:
        return "allrounder"

    runs = row.get("runs", 0) or 0
    wkts = row.get("wickets", 0) or 0
    name = str(row.get("name", "")).lower()

    if "dhoni" in name:
        return "wicketkeeper batter"
    if runs > 1000 and wkts < 20:
        return "batter"
    if wkts > 50 and runs < 1000:
        return "bowler"
    if runs > 1000 and wkts > 50:
        return "allrounder"
    return "batter"


# ==============================
# Predict Runs & Wickets
# ==============================
def predict_performance(df, batting_model, bowling_model, features):
    df_clean = clean_numeric(df.copy())
    batting_features = features["batting"]
    bowling_features = features["bowling"]

    X_bat = df_clean.reindex(columns=batting_features).fillna(0)
    X_bowl = df_clean.reindex(columns=bowling_features).fillna(0)

    df["pred_runs"] = batting_model.predict(X_bat)
    df["pred_wkts"] = bowling_model.predict(X_bowl)
    return df


# ==============================
# Resolve Player Names
# ==============================
def resolve_player_name(user_input, df_names):
    clean = user_input.lower().strip()
    if clean in ALIASES:
        return ALIASES[clean]

    match = process.extractOne(user_input, df_names, scorer=fuzz.token_sort_ratio, score_cutoff=65)
    if match:
        print(f"✅ Matched: {user_input} → {match[0]} (score={match[1]:.1f})")
        return match[0]
    print(f"⚠️ Could not find a close match for: {user_input}")
    return None


# ==============================
# 🔁 Auto-fetch missing players
# ==============================
def fetch_missing_players(missing_names, master_df):
    raw_data_path = "outputs/raw_data/ODI_data.csv"
    if not os.path.exists(raw_data_path):
        print("⚠️ ODI_data.csv not found — skipping auto-fetch.")
        return master_df

    raw_df = pd.read_csv(raw_data_path)
    new_rows = []

    for name in missing_names:
        match = process.extractOne(name, raw_df["name"].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=70)
        if match:
            player_row = raw_df[raw_df["name"] == match[0]]
            if not player_row.empty:
                print(f"🔄 Added missing player: {name} → {match[0]} (from ODI_data.csv)")
                new_rows.append(player_row)
        else:
            print(f"❌ Still missing: {name}")

    if new_rows:
        master_df = pd.concat([master_df] + new_rows, ignore_index=True)

    return master_df


# ==============================
# Select Balanced Best XI
# ==============================
def select_best_xi(df):
    df["detected_role"] = df.apply(auto_detect_role, axis=1)
    df["impact_score"] = df["pred_runs"] + (df["pred_wkts"] * 20)

    best_xi_parts = []

    # 4 Batters
    batters = df[df["detected_role"].str.contains("batter", na=False)].sort_values("pred_runs", ascending=False).head(4)
    best_xi_parts.append(batters)

    # 1 Keeper
    keepers = df[df["detected_role"].str.contains("wicketkeeper", na=False)].sort_values("pred_runs", ascending=False).head(1)
    best_xi_parts.append(keepers)

    # 2 Allrounders
    allrounders = df[df["detected_role"].str.contains("allrounder", na=False)].sort_values("impact_score", ascending=False).head(2)
    best_xi_parts.append(allrounders)

    # 4 Bowlers
    bowlers = df[df["detected_role"].str.contains("bowler", na=False)].sort_values("pred_wkts", ascending=False).head(4)
    best_xi_parts.append(bowlers)

    best_xi = pd.concat(best_xi_parts).drop_duplicates(subset=["name"])

    if len(best_xi) < 11:
        remaining = df.drop(best_xi.index, errors="ignore").sort_values("impact_score", ascending=False)
        needed = 11 - len(best_xi)
        best_xi = pd.concat([best_xi, remaining.head(needed)])

    return best_xi.head(11)


# ==============================
# Main
# ==============================
def main():
    master_file = "outputs/cleaned_data/odi_master.csv"
    batting_model_file = "models/batting_model.pkl"
    bowling_model_file = "models/bowling_model.pkl"
    features_file = "models/features.json"

    if not os.path.exists(master_file):
        print(f"❌ Master file not found: {master_file}")
        return

    df = pd.read_csv(master_file)
    print(f"\n✅ Loaded Master Dataset - Shape: {df.shape}")

    batting_model = joblib.load(batting_model_file)
    bowling_model = joblib.load(bowling_model_file)
    with open(features_file, "r") as f:
        features = json.load(f)

    players_input = input("\nEnter 15-20 player names (comma separated): ")
    match_format = input("Enter format (ODI / T20 / Test): ").strip().upper()
    venue = input("Enter venue: ").strip()
    opposition = input("Enter opposition team: ").strip()

    players = [p.strip() for p in players_input.split(",") if p.strip()]

    resolved_players = []
    missing_players = []

    for p in players:
        match = resolve_player_name(p, df["name"].unique())
        if match:
            resolved_players.append(match)
        else:
            missing_players.append(p)

    # 🔁 Auto-fetch missing players from ODI_data.csv
    if missing_players:
        print(f"\n🔍 Trying to fetch {len(missing_players)} missing players from ODI_data.csv...")
        df = fetch_missing_players(missing_players, df)

    df_selected = df[df["name"].isin(resolved_players + missing_players)].copy()

    if df_selected.empty:
        print("❌ No valid players found even after fetching. Please check inputs.")
        return

    df_selected = predict_performance(df_selected, batting_model, bowling_model, features)
    best_xi = select_best_xi(df_selected)

    print(f"\n=== 🏆 IMPACT XI (Best {match_format} Team at {venue} vs {opposition}) ===\n")
    for _, row in best_xi.iterrows():
        print(f"{row['name']} ({row['detected_role']}) - Pred Runs: {row['pred_runs']:.1f}, Pred Wkts: {row['pred_wkts']:.1f}")

    os.makedirs("outputs", exist_ok=True)
    best_xi.to_csv("outputs/best_xi.csv", index=False)

    summary = {
        "format": match_format,
        "venue": venue,
        "opposition": opposition,
        "selected_players": list(best_xi["name"].dropna()),
        "team_summary": {
            "total_pred_runs": float(best_xi["pred_runs"].sum()),
            "total_pred_wkts": float(best_xi["pred_wkts"].sum()),
            "roles_breakdown": best_xi["detected_role"].value_counts().to_dict()
        }
    }

    with open("outputs/best_xi_report.json", "w") as f:
        json.dump(summary, f, indent=4)

    print("\n💾 Best XI saved to outputs/best_xi.csv")
    print("💾 Detailed report saved to outputs/best_xi_report.json")


if __name__ == "__main__":
    main()
