# src/build_recent_form_dataset.py
import os
import pandas as pd

OUT_DIR = "outputs/context"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "recent_form.csv")

# Known per-match files (extend freely as you add more):
CANDIDATES = [
    "outputs/cleaned_data/odi_batting_merged.csv",   # has per-match rows
    # Add more if you later create them:
    "outputs/cleaned_data/t20_batting_merged.csv",   # optional per-match
    "outputs/cleaned_data/test_batting_merged.csv",  # optional per-match
]

def normalize_player_name(s: str) -> str:
    return (
        str(s)
        .lower()
        .replace(".", "")
        .strip()
    )

def load_per_match_frames():
    frames = []
    for path in CANDIDATES:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, low_memory=False)
                # Try to detect columns for player and runs:
                # ODI file has: 'player', 'runs', 'venue', 'opposition', 'date', ...
                cand_player = None
                for c in ["player", "Player", "name", "player_clean", "player_clean_career"]:
                    if c in df.columns:
                        cand_player = c
                        break
                if cand_player is None:
                    continue
                if "runs" not in df.columns:
                    # Some files might use Bat_Runs
                    if "Bat_Runs" in df.columns:
                        df["runs"] = pd.to_numeric(df["Bat_Runs"], errors="coerce")
                    else:
                        continue

                # Needed fields
                keep = {
                    "source": os.path.basename(path),
                    "player": df[cand_player].astype(str),
                    "runs": pd.to_numeric(df["runs"], errors="coerce"),
                    "date": pd.to_datetime(df["date"], errors="coerce") if "date" in df.columns else pd.NaT,
                }
                frame = pd.DataFrame(keep)
                frame["player_norm"] = frame["player"].apply(normalize_player_name)
                frame = frame.dropna(subset=["player_norm"])
                frames.append(frame)
                print(f"✅ Loaded per-match: {path} → rows={len(frame)}")
            except Exception as e:
                print(f"⚠️ Skipped {path}: {e}")
    return frames

def main():
    frames = load_per_match_frames()
    if not frames:
        # Create empty safe CSV
        print("⚠️ No per-match batting datasets found. Creating empty recent_form.csv")
        pd.DataFrame(columns=["player_norm","avg_runs_last10","matches_count"]).to_csv(OUT_FILE, index=False)
        print(f"💾 Saved empty {OUT_FILE}")
        return

    big = pd.concat(frames, ignore_index=True)
    # Sort by date if present, else keep as is
    if big["date"].notna().any():
        big = big.sort_values(["player_norm", "date"], ascending=[True, False])
    else:
        big = big.sort_values(["player_norm"], ascending=[True])

    # Take last 10 per player
    last10 = big.groupby("player_norm").head(10)
    agg = last10.groupby("player_norm").agg(
        avg_runs_last10=("runs", "mean"),
        matches_count=("runs", "size"),
    ).reset_index()

    agg["avg_runs_last10"] = agg["avg_runs_last10"].fillna(0).round(2)
    agg.to_csv(OUT_FILE, index=False)
    print(f"✅ Built recent form: {OUT_FILE} → rows={len(agg)}")
    print(agg.head(10))

if __name__ == "__main__":
    main()
