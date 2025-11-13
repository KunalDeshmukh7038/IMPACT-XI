import os, json
import pandas as pd
from collections import defaultdict

DATA_FOLDER = "data/cricsheet_all_matches"
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"
MAX_FILES = None  # process all

def parse_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_all_matches():
    bowling_acc = defaultdict(lambda: {"balls":0, "runs_conceded":0, "wickets":0})
    records = []

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    if MAX_FILES:
        files = files[:MAX_FILES]

    for file in files:
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
            batting_team = inning.get("team", "")
            bowling_team = [t for t in teams if t != batting_team][0] if len(teams) == 2 else ""

            for over in inning.get("overs", []):
                for delivery in over.get("deliveries", []):
                    bowler = delivery.get("bowler")
                    runs_total = delivery.get("runs", {}).get("total", 0)
                    wicket = delivery.get("wicket", {})

                    if not bowler:
                        continue

                    key = (match_id, date, venue, bowling_team, batting_team, bowler)
                    bowling_acc[key]["balls"] += 1
                    bowling_acc[key]["runs_conceded"] += runs_total
                    if wicket and wicket.get("kind") not in ["run out", "retired hurt"]:
                        bowling_acc[key]["wickets"] += 1

    for key, val in bowling_acc.items():
        match_id, date, venue, team, opposition, player = key
        records.append({
            "match_id": match_id,
            "date": date,
            "venue": venue,
            "team": team,           # bowler's team
            "opposition": opposition, # batting team (fix ✅)
            "player": player,
            "balls": val["balls"],
            "runs_conceded": val["runs_conceded"],
            "wickets": val["wickets"]
        })

    df = pd.DataFrame(records)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")
    df.to_csv(output_file, index=False)

    print(f"✅ Saved {FORMAT} bowling stats to {output_file}")
    print(df.head())

if __name__ == "__main__":
    parse_all_matches()
