import pandas as pd
import os

OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"

bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_batting_clean.csv")
bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_bowling_clean.csv")

bat_df = pd.read_csv(bat_file)
bowl_df = pd.read_csv(bowl_file)

print("\n📊 Batting Kaggle Columns:", list(bat_df.columns))
print("First 5 rows (batting):")
print(bat_df.head())

print("\n📊 Bowling Kaggle Columns:", list(bowl_df.columns))
print("First 5 rows (bowling):")
print(bowl_df.head())
