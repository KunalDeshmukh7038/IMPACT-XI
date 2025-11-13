# src/merge_t20_test_datasets.py
import os
import pandas as pd

def safe_merge(base_df, career_df):
    """Merge batting/bowling data with career data using player name or id."""
    base_cols = base_df.columns
    career_cols = career_df.columns

    # Detect player or id column
    player_col = None
    for col in ["player", "Player", "name", "Name", "id", "ID"]:
        if col in base_cols:
            player_col = col
            break

    if not player_col:
        print("❌ No suitable key column ('player' or 'id') found in base dataset.")
        return base_df

    if player_col in ["player", "Player", "name", "Name"]:
        base_df["merge_key"] = (
            base_df[player_col]
            .astype(str)
            .str.lower()
            .str.replace(r"[^a-z\s]", "", regex=True)
            .str.strip()
        )
        if "player" in career_cols:
            career_df["merge_key"] = (
                career_df["player"]
                .astype(str)
                .str.lower()
                .str.replace(r"[^a-z\s]", "", regex=True)
                .str.strip()
            )
        elif "id" in career_cols:
            career_df["merge_key"] = career_df["id"].astype(str)
        else:
            print("⚠️ No merge key found in career dataset, skipping merge.")
            return base_df
    else:
        # merge using ID
        base_df["merge_key"] = base_df[player_col].astype(str)
        if "id" in career_cols:
            career_df["merge_key"] = career_df["id"].astype(str)
        else:
            print("⚠️ No 'id' found in career dataset, skipping merge.")
            return base_df

    merged = pd.merge(base_df, career_df, on="merge_key", how="left", suffixes=("", "_career"))
    print(f"✅ Merged using key '{player_col}' — Result shape: {merged.shape}")
    return merged


def merge_format(fmt):
    """Merge batting, bowling, and career data for T20 or Test."""
    base_dir = "data/kaggle_datasets"
    out_dir = "outputs/cleaned_data"
    os.makedirs(out_dir, exist_ok=True)

    fmt_lower = fmt.lower()
    bat_path = os.path.join(base_dir, f"{fmt_lower}_batting.csv")
    bowl_path = os.path.join(base_dir, f"{fmt_lower}_bowling.csv")
    career_path = os.path.join(base_dir, "personal_male.csv")

    if not (os.path.exists(bat_path) and os.path.exists(bowl_path)):
        print(f"⚠️ Missing files for {fmt}. Skipping...")
        return

    print(f"\n🏏 Processing {fmt} data...")

    bat = pd.read_csv(bat_path)
    bowl = pd.read_csv(bowl_path)
    career = pd.read_csv(career_path)

    print(f"📂 Batting: {bat.shape}, Bowling: {bowl.shape}, Career: {career.shape}")

    merged_bat = safe_merge(bat, career)
    merged_bowl = safe_merge(bowl, career)

    bat_out = os.path.join(out_dir, f"{fmt_lower}_batting_merged.csv")
    bowl_out = os.path.join(out_dir, f"{fmt_lower}_bowling_merged.csv")

    merged_bat.to_csv(bat_out, index=False)
    merged_bowl.to_csv(bowl_out, index=False)

    print(f"💾 Saved → {bat_out}")
    print(f"💾 Saved → {bowl_out}")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🔄 Starting merge for T20 and Test formats...\n")
    merge_format("T20")
    merge_format("TEST")
    print("\n✅ Merge completed for all formats!\n")
