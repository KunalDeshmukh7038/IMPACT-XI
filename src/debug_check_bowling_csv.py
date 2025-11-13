# src/debug_check_bowling_csv.py
import pandas as pd
import os

OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"

bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")

print("📂 Loading:", bowl_file)
df = pd.read_csv(bowl_file)

print("\nTotal rows in bowling file:", len(df))
print("Columns:", df.columns.tolist())

# Show first 10 rows
print("\nSample rows:")
print(df.head(10))

# Check for Bumrah and Starc specifically
for name in ["Bumrah", "JJ Bumrah", "Starc", "MA Starc"]:
    subset = df[df["player"].str.contains(name, case=False, na=False)]
    print(f"\nRows for {name}: {len(subset)}")
    if not subset.empty:
        print(subset.head())
