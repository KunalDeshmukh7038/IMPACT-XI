import os, json
import pandas as pd
from collections import defaultdict

# ---------------- CONFIG ----------------
DATA_FOLDER = "data/cricsheet_all_matches"   # folder with ALL matches
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # 🔄 Change to "ODI", "T20", "Test"
MAX_FILES = None  # limit for testing, None = all
# ----------------------------------------

def parse_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_all_matches():
    records = []

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    if MAX_FILES:
        files = files[:MAX_FILES]

    for idx, file in enumerate(files, 1):
        path = os.path.join(DATA_FOLDER, file)
        match = parse_json_file(path)

        info = match.get("info", {})
        match_type = info.get("match_type", "").upper()
        if match_type != FORMAT.upper():
            continue

        match_id = info.get("match_type_number", file)
        date = info.get("dates", [""])[0]
        venue = info.get("venue", "")
        teams = info.get("teams", [])

        for inning in match.get("innings", []):
            team = inning.get("team")
            opposition = [t for t in teams if t != team][0] if len(teams) == 2 else ""

            for over in inning.get("overs", []):
                for delivery in over.get("deliveries", []):
                    batter = delivery.get("batter") or delivery.get("batsman")
                    bowler = delivery.get("bowler")
                    runs_batter = delivery.get("runs", {}).get("batter", 0)
                    dismissal = delivery.get("wicket", {})

                    if not batter or not bowler:
                        continue

                    records.append({
                        "match_id": match_id,
                        "date": date,
                        "venue": venue,
                        "team": team,
                        "opposition": opposition,
                        "batter": batter,
                        "bowler": bowler,
                        "runs": runs_batter,
                        "ball": 1,
                        "out": 1 if dismissal.get("player_out") == batter else 0
                    })

        if idx % 500 == 0:
            print(f"Processed {idx} files...")

    # Convert to DataFrame
    df = pd.DataFrame(records)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_batter_vs_bowler.csv")
    df.to_csv(output_file, index=False)

    print(f"\n✅ Saved batter vs bowler stats to {output_file}")
    print(df.head())

if __name__ == "__main__":
    parse_all_matches()
