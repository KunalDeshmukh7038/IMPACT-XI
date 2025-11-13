# src/merge_test_from_batting_bowling.py
import pandas as pd
import os

print(">>\n🏏 Starting merge for Test datasets...\n")

bat_path = "data/Batting/test.csv"
bowl_path = "data/Bowling/Bowling_test.csv"
output_path = "outputs/cleaned_data/test_master_v2.csv"

# Load batting
if not os.path.exists(bat_path):
    print(f"❌ Missing file: {bat_path}")
    exit()
if not os.path.exists(bowl_path):
    print(f"❌ Missing file: {bowl_path}")
    exit()

bat = pd.read_csv(bat_path)
bowl = pd.read_csv(bowl_path)

print(f"📊 Test Batting shape: {bat.shape}")
print(f"📊 Test Bowling shape: {bowl.shape}")

# Clean Player names
bat["player_clean"] = (
    bat["Player"]
    .astype(str)
    .str.lower()
    .str.replace(r"[^a-z\s]", "", regex=True)
    .str.strip()
)

bowl["player_clean"] = (
    bowl["Player"]
    .astype(str)
    .str.lower()
    .str.replace(r"[^a-z\s]", "", regex=True)
    .str.strip()
)

# Merge on player_clean
merged = pd.merge(
    bat.add_prefix("Bat_"),
    bowl.add_prefix("Bowl_"),
    left_on="Bat_player_clean",
    right_on="Bowl_player_clean",
    how="outer"
)

merged["Format"] = "TEST"

# Drop duplicates and irrelevant unnamed columns
merged = merged.loc[:, ~merged.columns.str.contains("^Unnamed")]
merged = merged.drop_duplicates(subset=["Bat_player_clean"], keep="first")

# Save merged file
os.makedirs(os.path.dirname(output_path), exist_ok=True)
merged.to_csv(output_path, index=False)

print(f"✅ Saved merged Test dataset → {output_path}")
print(f"📊 Final shape: {merged.shape}")

print("\nSample data:")
print(merged.head(10))
