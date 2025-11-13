import pandas as pd
import os

# ==========================================================
# CONFIG
# ==========================================================
BAT_PATH = "data/Batting/t20.csv"
BOWL_PATH = "data/Bowling/Bowling_t20.csv"
OUTPUT_PATH = "outputs/cleaned_data/t20_master_v2.csv"

# ==========================================================
# Helper: Clean player names
# ==========================================================
def clean_player_name(name):
    if pd.isna(name):
        return ""
    # Remove parentheses, country tags, asterisks, and extra spaces
    name = (
        str(name)
        .replace("*", "")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "")
        .replace("ICC", "")
        .replace("INDIA", "")
        .strip()
    )
    # Keep only letters and spaces
    import re
    name = re.sub(r"[^A-Za-z\s]", "", name)
    return name.strip().lower()

# ==========================================================
# Load datasets
# ==========================================================
if not os.path.exists(BAT_PATH) or not os.path.exists(BOWL_PATH):
    print("❌ One or both source files are missing.")
    exit()

bat = pd.read_csv(BAT_PATH)
bowl = pd.read_csv(BOWL_PATH)

print("🏏 T20 Batting shape:", bat.shape)
print("🏏 T20 Bowling shape:", bowl.shape)

# ==========================================================
# Clean Player names
# ==========================================================
bat["player_clean"] = bat["Player"].apply(clean_player_name)
bowl["player_clean"] = bowl["Player"].apply(clean_player_name)

# ==========================================================
# Select useful columns
# ==========================================================
bat_cols = ["player_clean", "Player", "Span", "Mat", "Inns", "Runs", "HS", "Ave", "BF", "SR", "100", "50", "4s", "6s"]
bowl_cols = ["player_clean", "Player", "Mat", "Inns", "Overs", "Runs", "Wkts", "Ave", "Econ", "SR", "4", "5"]

bat = bat[bat_cols]
bowl = bowl[bowl_cols]

# Rename columns for clarity
bat.columns = [
    "player_clean", "Player", "Bat_Span", "Bat_Mat", "Bat_Inns", "Bat_Runs",
    "Bat_HS", "Bat_Ave", "Bat_BF", "Bat_SR", "Bat_100", "Bat_50", "Bat_4s", "Bat_6s"
]

bowl.columns = [
    "player_clean", "Player", "Bowl_Mat", "Bowl_Inns", "Bowl_Overs",
    "Bowl_Runs", "Bowl_Wkts", "Bowl_Ave", "Bowl_Econ", "Bowl_SR", "Bowl_4w", "Bowl_5w"
]

# ==========================================================
# Merge batting + bowling on cleaned player name
# ==========================================================
merged = pd.merge(bat, bowl, on="player_clean", how="outer", suffixes=("_bat", "_bowl"))

# Deduplicate and clean final structure
merged = merged.drop_duplicates(subset=["player_clean"]).reset_index(drop=True)

# Add Format tag
merged["Format"] = "T20"

# ==========================================================
# Save the merged dataset
# ==========================================================
os.makedirs("outputs/cleaned_data", exist_ok=True)
merged.to_csv(OUTPUT_PATH, index=False)
print(f"\n✅ Saved merged T20 dataset → {OUTPUT_PATH}")
print("📊 Final shape:", merged.shape)

# ==========================================================
# Preview a few rows
# ==========================================================
print("\nSample data:")
print(merged.head(10).to_string(index=False))
