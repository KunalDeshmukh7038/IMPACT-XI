import os, json
import pandas as pd
from collections import defaultdict

# ---------------- CONFIG ----------------
DATA_FOLDER = "data/cricsheet_all_matches"   # folder with ALL matches
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # 🔄 Change to "T20" or "Test" when needed
MAX_FILES = None   # None = process all
# ----------------------------------------

def parse_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_all_matches():
    batting_acc = defaultdict(lambda: {"runs":0, "balls":0, "dismissals":0})
    records = []

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    if MAX_FILES:
        files = files[:MAX_FILES]

    for file in files:
        path = os.path.join(DATA_FOLDER, file)
        match = parse_json_file(path)

        info = match.get("info", {})
        match_type = info.get("match_type", "").upper()

        # 🔎 filter only the format we want
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
                    runs_batter = delivery.get("runs", {}).get("batter", 0) or delivery.get("runs", {}).get("batsman", 0)

                    if not batter:
                        continue

                    # update stats
                    key = (match_id, date, venue, team, opposition, batter)
                    batting_acc[key]["runs"] += runs_batter
                    batting_acc[key]["balls"] += 1

                    # ✅ Fix: check wicket info
                    if "wicket" in delivery:
                        wicket_info = delivery["wicket"]
                        if wicket_info.get("player_out") == batter:
                            batting_acc[key]["dismissals"] += 1

    # Convert to DataFrame
    for key, val in batting_acc.items():
        match_id, date, venue, team, opposition, player = key
        records.append({
            "match_id": match_id,
            "date": date,
            "venue": venue,
            "team": team,
            "opposition": opposition,
            "player": player,
            "runs": val["runs"],
            "balls": val["balls"],
            "dismissals": val["dismissals"]
        })

    df = pd.DataFrame(records)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    df.to_csv(output_file, index=False)

    print(f"✅ Saved {FORMAT} batting stats to {output_file}")
    print(df.head())

if __name__ == "__main__":
    parse_all_matches()
