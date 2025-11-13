# import pandas as pd
# import os

# OUTPUT_PATH = "outputs/pitch"
# os.makedirs(OUTPUT_PATH, exist_ok=True)

# # ===============================
# # Helper: Detect whether bowler is pacer or spinner
# # ===============================
# def classify_bowler(name):
#     """Very simple classifier based on common spin/pacer keywords in name."""
#     name = name.lower()
#     spin_keywords = ["ashwin", "jadeja", "chahal", "kuldeep", "ahar", "patel", "rashid", "zampa", "shakib", "mendis", "narine", "ahir"]
#     return "spin" if any(k in name for k in spin_keywords) else "pace"


# # ===============================
# # Load ODI batting & bowling datasets
# # ===============================
# bat_path = "outputs/cleaned_data/odi_batting_merged.csv"
# bowl_path = "outputs/cleaned_data/odi_bowling_merged.csv"

# bat = pd.read_csv(bat_path, low_memory=False)
# bowl = pd.read_csv(bowl_path, low_memory=False)

# print("✅ Loaded ODI datasets:")
# print("Batting rows:", len(bat))
# print("Bowling rows:", len(bowl))

# # ===============================
# # Preprocess bowling data
# # ===============================
# bowl["bowler_type"] = bowl["player"].astype(str).apply(classify_bowler)

# # ===============================
# # Aggregate per venue
# # ===============================
# venue_stats = bat.groupby("venue").agg(
#     total_runs=("runs", "sum"),
#     total_innings=("innings", "count")
# ).reset_index()

# bowl_stats = bowl.groupby("venue").agg(
#     total_wkts=("wickets", "sum"),
#     pace_wkts=("bowler_type", lambda x: (x == "pace").sum()),
#     spin_wkts=("bowler_type", lambda x: (x == "spin").sum()),
# ).reset_index()

# # Merge batting + bowling stats
# pitch_df = venue_stats.merge(bowl_stats, on="venue", how="left")

# # ===============================
# # Calculate metrics
# # ===============================
# pitch_df["avg_runs"] = (pitch_df["total_runs"] / pitch_df["total_innings"]).round(2)
# pitch_df["pace_wkts_pct"] = (pitch_df["pace_wkts"] / pitch_df["total_wkts"] * 100).round(2)
# pitch_df["spin_wkts_pct"] = (pitch_df["spin_wkts"] / pitch_df["total_wkts"] * 100).round(2)

# # ===============================
# # Auto classify pitch type
# # ===============================
# def classify_pitch(row):
#     if row["avg_runs"] > 300:
#         return "batting"
#     if row["pace_wkts_pct"] > 65:
#         return "pace"
#     if row["spin_wkts_pct"] > 60:
#         return "spin"
#     return "balanced"

# pitch_df["pitch_type"] = pitch_df.apply(classify_pitch, axis=1)

# # Save CSV
# output_csv = os.path.join(OUTPUT_PATH, "pitch_types.csv")
# pitch_df.to_csv(output_csv, index=False)

# print("\n✅ Pitch dataset generated!")
# print("📁 Saved to:", output_csv)
# print("\nSample output:")
# print(pitch_df.head())

# src/generate_pitch_dataset.py
import os
import numpy as np
import pandas as pd

OUT_DIR = "outputs/pitch"
os.makedirs(OUT_DIR, exist_ok=True)

BAT_PATH = "outputs/cleaned_data/odi_batting_merged.csv"
BOWL_PATH = "outputs/cleaned_data/odi_bowling_merged.csv"
OUT_PATH  = os.path.join(OUT_DIR, "pitch_types.csv")


def classify_pitch(avg_runs, pace_pct, spin_pct):
    """
    Rules you confirmed:
      - if avg_runs_per_innings > 32 → batting pitch
      - elif pace_wkts_pct > 70%     → pace pitch
      - elif spin_wkts_pct > 40%     → spin pitch
      - else                         → batting (balanced tilt)
    """
    if avg_runs > 32:
        return "batting"
    if pace_pct > 0.70:
        return "pace"
    if spin_pct > 0.40:
        return "spin"
    return "batting"


def main():
    # -------- Load ----------
    bat = pd.read_csv(BAT_PATH, low_memory=False)
    bowl = pd.read_csv(BOWL_PATH, low_memory=False)
    print("✅ Loaded ODI datasets:")
    print(f"Batting rows: {len(bat)}")
    print(f"Bowling rows: {len(bowl)}\n")

    # -------- Clean ----------
    # Make sure numeric
    for col in ["runs"]:
        if col in bat.columns:
            bat[col] = pd.to_numeric(bat[col], errors="coerce")

    for col in ["wickets"]:
        if col in bowl.columns:
            bowl[col] = pd.to_numeric(bowl[col], errors="coerce")

    # Normalize venue
    bat["venue_norm"]  = bat["venue"].astype(str).str.strip()
    bowl["venue_norm"] = bowl["venue"].astype(str).str.strip()

    # -------- Aggregate ----------
    # Batting: total runs & innings per venue (count a row as one innings)
    bat_agg = (
        bat.groupby("venue_norm", dropna=False)
           .agg(total_runs=("runs", "sum"),
                total_innings=("runs", "count"))
           .reset_index()
    )

    # Bowling: pace vs spin wickets per venue (naive split by style not available,
    # so we approximate with ALL wickets; we’ll keep pace/spin buckets as equal splits
    # unless best_bowling hints exist. Since merged bowling doesn’t have style,
    # we compute *actual* wickets and leave pace/spin split to 0; app will use venue class only.)
    bowl_agg = (
        bowl.groupby("venue_norm", dropna=False)
            .agg(total_wkts=("wickets", "sum"))
            .reset_index()
    )

    # Merge
    df = bat_agg.merge(bowl_agg, on="venue_norm", how="outer")

    # Compute averages
    df["avg_runs"] = (df["total_runs"] / df["total_innings"]).replace([np.inf, -np.inf], np.nan)

    # We cannot split pace vs spin reliably using this merged file,
    # so we estimate pace/spin using an opponent-agnostic heuristic:
    # use bowling wickets share from *all wickets* as 0.5/0.5 placeholders.
    # The class decision will be driven by avg_runs primarily (per your rule),
    # while pace/spin thresholds are hard to meet without split; they’ll fall back to batting.
    df["pace_wkts_pct"] = 0.5
    df["spin_wkts_pct"] = 0.5

    # Filter venues with enough data
    df["total_matches_proxy"] = df["total_innings"] // 2  # two innings per match (proxy)
    df = df[df["total_matches_proxy"] >= 5].copy()

    # Drop bad rows
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["avg_runs"])

    # Classify pitch type
    df["pitch_type"] = df.apply(
        lambda r: classify_pitch(r["avg_runs"], r["pace_wkts_pct"], r["spin_wkts_pct"]),
        axis=1,
    )

    # Prepare final
    df = df.rename(columns={"venue_norm": "venue"})
    df = df[["venue", "total_runs", "total_innings", "total_wkts",
             "avg_runs", "pace_wkts_pct", "spin_wkts_pct", "pitch_type"]].sort_values("venue")

    # Global baseline row
    global_row = pd.DataFrame([{
        "venue": "__GLOBAL__",
        "total_runs": df["total_runs"].sum(),
        "total_innings": df["total_innings"].sum(),
        "total_wkts": df["total_wkts"].sum(),
        "avg_runs": (df["total_runs"].sum() / max(1, df["total_innings"].sum())),
        "pace_wkts_pct": 0.5,
        "spin_wkts_pct": 0.5,
        "pitch_type": "batting"  # average ODI tends to be batting-favorable
    }])

    df_out = pd.concat([df, global_row], ignore_index=True)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df_out.to_csv(OUT_PATH, index=False)
    print("✅ Pitch dataset generated!")
    print(f"📁 Saved to: {OUT_PATH}\n")
    print("Sample output:")
    print(df_out.head(10))


if __name__ == "__main__":
    main()
