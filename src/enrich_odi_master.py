import pandas as pd
import os
from fuzzywuzzy import process
from tqdm import tqdm

# -------------------------------
# Utility: Fuzzy match player names
# -------------------------------
def fuzzy_match_name(name, choices, cutoff=90):
    match, score = process.extractOne(name, choices)
    if match and score >= cutoff:
        return match
    return None


# -------------------------------
# Step 1: Load base ODI master
# -------------------------------
def load_base_master():
    base_file = "outputs/cleaned_data/odi_master.csv"
    if not os.path.exists(base_file):
        raise FileNotFoundError(f"❌ Base file not found: {base_file}")
    df = pd.read_csv(base_file)
    print(f"✅ Loaded base ODI master - Shape: {df.shape}")
    return df


# -------------------------------
# Step 2: Load external ODI datasets
# -------------------------------
def load_external_data():
    data_files = {
        "odi_data": "data/Batting/ODI_data.csv",
        "bowling_odi": "data/Bowling/Bowling_ODI.csv",
        "odi_batting": "data/kaggle_datasets/ODI_batting.csv",
        "odi_bowling": "data/kaggle_datasets/ODI_bowling.csv",
        "cricketers": "data/kaggle_datasets/cricketers.csv"
    }
    data = {}
    for name, path in data_files.items():
        if os.path.exists(path):
            data[name] = pd.read_csv(path)
            print(f"📄 Loaded {name} - Shape: {data[name].shape}")
        else:
            print(f"⚠️ Missing: {path}")
    return data


# -------------------------------
# Step 3: Enrich ODI master
# -------------------------------
def enrich_odi_master(master_df, data):
    enriched_df = master_df.copy()
    name_column_master = "name"

    # For fuzzy matching reference lists
    all_names = {
        key: df.columns[df.columns.str.contains("Player|Name|player|name", case=False, regex=True)].tolist()
        for key, df in data.items()
    }

    for src, df in data.items():
        player_col = None
        for col in all_names[src]:
            player_col = col
            break

        if not player_col:
            print(f"⚠️ No player column found in {src}, skipping.")
            continue

        df[player_col] = df[player_col].astype(str).str.strip()

        new_cols = [c for c in df.columns if c.lower() not in [player_col.lower(), "unnamed: 0", "unnamed: 0.1", "span"]]
        merged = 0

        for i, row in tqdm(enriched_df.iterrows(), total=enriched_df.shape[0], desc=f"Merging {src}"):
            player_name = row[name_column_master]
            match = fuzzy_match_name(player_name, df[player_col].tolist(), cutoff=90)
            if match:
                matched_row = df[df[player_col] == match].iloc[0]
                for c in new_cols:
                    if c not in enriched_df.columns:
                        enriched_df[c] = pd.NA
                    enriched_df.at[i, c] = matched_row[c]
                merged += 1
        print(f"✅ {merged} players matched and merged from {src}")

    return enriched_df


# -------------------------------
# Step 4: Save final enriched master
# -------------------------------
def save_enriched(enriched_df):
    os.makedirs("outputs/cleaned_data", exist_ok=True)
    output_file = "outputs/cleaned_data/odi_master_enriched.csv"
    enriched_df.to_csv(output_file, index=False)
    print(f"💾 Saved enriched ODI master → {output_file}")
    print(f"Final shape: {enriched_df.shape}")


# -------------------------------
# Main Function
# -------------------------------
def main():
    master_df = load_base_master()
    data = load_external_data()
    enriched_df = enrich_odi_master(master_df, data)
    save_enriched(enriched_df)


if __name__ == "__main__":
    main()
