import os
import pandas as pd

OUTPUT_DIR = "outputs/cleaned_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_dataframe(df, prefix):
    # Standardize player name
    name_col = None
    for possible in ["Player", "player", "Name", "name"]:
        if possible in df.columns:
            name_col = possible
            break

    if not name_col:
        raise ValueError("No valid 'Player' or 'name' column found.")

    df = df.rename(columns={name_col: "name"})
    df["name"] = df["name"].astype(str).str.strip()

    # Drop unnamed columns and empty cols
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    df = df.dropna(how="all", axis=1)

    # Add prefix to stats columns except name
    df = df.rename(columns={col: f"{prefix}_{col}" for col in df.columns if col != "name"})
    return df

def build_master(format_type, bat_path, bowl_path, field_path):
    print(f"\n🏏 Building master dataset for: {format_type}")

    bat = clean_dataframe(pd.read_csv(bat_path), "Bat")
    bowl = clean_dataframe(pd.read_csv(bowl_path), "Bowl")
    field = clean_dataframe(pd.read_csv(field_path), "Field")

    master = bat.merge(bowl, on="name", how="outer").merge(field, on="name", how="outer")

    master["Format"] = format_type
    master = master.drop_duplicates(subset=["name"])

    out_path = os.path.join(OUTPUT_DIR, f"{format_type.lower()}_master.csv")
    master.to_csv(out_path, index=False)
    print(f"✅ Saved: {out_path} → Shape: {master.shape}")

# ===== Main Execution =====
if __name__ == "__main__":
    FORMATS = {
        "T20": {
            "bat": "data/Batting/t20.csv",
            "bowl": "data/Bowling/Bowling_t20.csv",
            "field": "data/Fielding/Fielding_t20.csv"
        },
        "Test": {
            "bat": "data/Batting/test.csv",
            "bowl": "data/Bowling/Bowling_test.csv",
            "field": "data/Fielding/Fielding_test.csv"
        }
    }

    for fmt, files in FORMATS.items():
        if all(os.path.exists(path) for path in files.values()):
            build_master(fmt, files["bat"], files["bowl"], files["field"])
        else:
            print(f"⚠️ Missing one or more files for {fmt} format.")
