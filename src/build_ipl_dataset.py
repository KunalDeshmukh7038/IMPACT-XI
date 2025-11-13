# src/build_ipl_dataset.py
import os
import pandas as pd

OUT_DIR = "outputs/context"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "ipl_stats.csv")

# Try common Kaggle-style IPL files. Add more if you have them.
CANDIDATES = [
    "data/kaggle_datasets/ipl_batting.csv",
    "data/kaggle_datasets/ipl_batsmen.csv",
    "data/kaggle_datasets/ipl_per_match_batting.csv",
]

def normalize_player_name(s: str) -> str:
    return (
        str(s)
        .lower()
        .replace(".", "")
        .strip()
    )

def main():
    frames = []
    for path in CANDIDATES:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, low_memory=False)
                cand_player = None
                for c in ["player", "batsman", "Player", "name"]:
                    if c in df.columns:
                        cand_player = c
                        break
                if cand_player is None:
                    continue

                # runs column
                cand_runs = None
                for c in ["runs", "batsman_runs", "total_runs", "Bat_Runs"]:
                    if c in df.columns:
                        cand_runs = c
                        break
                if cand_runs is None:
                    continue

                tmp = pd.DataFrame({
                    "player": df[cand_player].astype(str),
                    "runs": pd.to_numeric(df[cand_runs], errors="coerce"),
                })
                tmp["player_norm"] = tmp["player"].apply(normalize_player_name)
                tmp = tmp.dropna(subset=["player_norm"])
                frames.append(tmp)
                print(f"✅ Loaded IPL file: {path} rows={len(tmp)}")
            except Exception as e:
                print(f"⚠️ Skipped {path}: {e}")

    if not frames:
        print("⚠️ No IPL data found. Creating empty ipl_stats.csv")
        pd.DataFrame(columns=["player_norm", "ipl_avg", "ipl_matches"]).to_csv(OUT_FILE, index=False)
        print(f"💾 Saved empty {OUT_FILE}")
        return

    big = pd.concat(frames, ignore_index=True)
    agg = big.groupby("player_norm").agg(
        ipl_avg=("runs","mean"),
        ipl_matches=("runs","size")
    ).reset_index()
    agg["ipl_avg"] = agg["ipl_avg"].fillna(0).round(2)
    agg.to_csv(OUT_FILE, index=False)
    print(f"✅ Built IPL stats: {OUT_FILE} → rows={len(agg)}")
    print(agg.head(10))

if __name__ == "__main__":
    main()
