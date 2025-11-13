# src/debug_check_values.py
import pandas as pd

bat_file = "outputs/cleaned_data/odi_batting_merged.csv"
bowl_file = "outputs/cleaned_data/odi_bowling_merged.csv"

print("📂 Loading merged batting + bowling...")
bat_df = pd.read_csv(bat_file, low_memory=False)
bowl_df = pd.read_csv(bowl_file, low_memory=False)

print("\n=== Batting: Unique Players (first 20) ===")
print(bat_df["player_clean"].dropna().unique()[:20])

print("\n=== Batting: Unique Oppositions ===")
print(bat_df["opposition"].dropna().unique()[:20])

print("\n=== Sample rows for Kohli ===")
print(bat_df[bat_df["player_clean"].str.contains("kohli", na=False)].head(10))

print("\n=== Bowling: Unique Players (first 20) ===")
print(bowl_df["player_clean"].dropna().unique()[:20])

print("\n=== Bowling: Unique Oppositions ===")
print(bowl_df["opposition"].dropna().unique()[:20])

print("\n=== Sample rows for Kohli (bowling) ===")
print(bowl_df[bowl_df["player_clean"].str.contains("kohli", na=False)].head(10))
