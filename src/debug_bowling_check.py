import pandas as pd

df = pd.read_csv("outputs/cleaned_data/odi_match_bowling.csv")

# Check for Bumrah anywhere
print("🔎 Unique players containing 'Bumrah':")
print(df[df["player"].str.contains("Bumrah", case=False, na=False)]["player"].unique())

# Check if he played vs Australia
sub = df[(df["player"].str.contains("Bumrah", case=False, na=False)) &
         (df["opposition"].str.contains("Australia", case=False, na=False))]
print(f"\nRows found for Bumrah vs Australia: {len(sub)}")
print(sub.head())
