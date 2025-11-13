# src/parse_cricsheet_matches.py
import os, json, math
import pandas as pd
from collections import defaultdict

# ---------------- CONFIG ----------------
DATA_FOLDER = "data/cricsheet_all_matches"   # <-- set your JSON folder here
FORMAT = "ODI"                            # <-- "ODI", "T20", or "Test"
OUTPUT_DIR = "outputs/cleaned_data"
MAX_FILES = None  # set to an int to test on small number of files, or None to process all
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d

def is_legal_delivery(deliv):
    """
    Heuristic: returns True if the delivery should count as a 'legal' ball for balls faced/balls bowled.
    Many JSONs indicate extras as keys like 'wides' or 'noballs' inside delivery['extras'] or delivery['wicket'] etc.
    We'll try common patterns; if unknown, we count as legal (conservative).
    """
    # delivery might include explicit extras breakdown in top-level keys or under 'extras' structure
    # check known keys:
    if not isinstance(deliv, dict):
        return True
    # Some formats use 'extras' as number under runs; some use 'extras' dict like {'wides':1}
    runs_obj = deliv.get("runs", {})
    # if runs_obj contains an 'extras' sub-dict with type keys
    if isinstance(runs_obj.get("extras"), dict):
        ex = runs_obj["extras"]
        for t in ("wides", "wide", "noball", "no_ball", "nb"):
            if t in ex and ex[t]:
                return False
    # sometimes extras recorded as delivery.get('extras', {'wides':1})
    if isinstance(deliv.get("extras"), dict):
        ex = deliv["extras"]
        for t in ("wides", "wide", "noball", "no_ball", "nb"):
            if t in ex and ex[t]:
                return False
    # fallback: some cricsheet formats don't expose type; assume legal
    return True

def process_file(path, batting_acc, bowling_acc):
    with open(path, "r", encoding="utf-8") as f:
        match = json.load(f)

    info = match.get("info", {})
    match_type = (info.get("match_type") or "").strip()
    if not match_type:
        # try legacy key
        match_type = (info.get("match_type_name") or "").strip()
    if not match_type:
        return  # unknown type

    # Normalize format check (user sets FORMAT)
    if match_type.upper() != FORMAT.upper():
        return

    match_id = info.get("match_type_number") or os.path.basename(path)
    date = safe_get(info, "dates", 0, default="")
    venue = info.get("venue", "")
    teams = info.get("teams", []) or info.get("teams", [])
    # innings could be either list of dicts with 'team' and 'overs' (modern JSON)
    # or list of {"1st innings": {...}} (older style)
    for inning in match.get("innings", []):
        # Modern style with 'team' and 'overs' (sample you sent)
        if isinstance(inning, dict) and "team" in inning and "overs" in inning:
            team = inning.get("team", "")
            opposition = [t for t in teams if t != team][0] if len(teams) == 2 else ""
            for over in inning.get("overs", []):
                for delivery in over.get("deliveries", []):
                    # in this style delivery is a dict like {"batter":..., "bowler":..., "runs": {...}}
                    batter = delivery.get("batter") or delivery.get("batsman")
                    bowler = delivery.get("bowler")
                    runs_batter = safe_get(delivery, "runs", "batter", default=0) or safe_get(delivery, "runs", "batsman", default=0) or 0
                    runs_total = safe_get(delivery, "runs", "total", default=0) or 0
                    # wicket info may be in delivery["wicket"]
                    wicket = delivery.get("wicket")
                    # aggregate batting
                    if batter:
                        key = (match_id, date, venue, team, opposition, batter)
                        batting_acc[key]["runs"] += int(runs_batter or 0)
                        if is_legal_delivery(delivery):
                            batting_acc[key]["balls"] += 1
                        if wicket and wicket.get("player_out") == batter:
                            batting_acc[key]["dismissals"] += 1
                    # aggregate bowling
                    if bowler:
                        keyb = (match_id, date, venue, team, opposition, bowler)
                        bowling_acc[keyb]["runs_conceded"] += int(runs_total or 0)
                        if is_legal_delivery(delivery):
                            bowling_acc[keyb]["balls"] += 1
                        if wicket:
                            # if wicket recorded and kind != 'run out' then award wicket to bowler
                            kind = wicket.get("kind", "").lower() if isinstance(wicket, dict) else ""
                            player_out = wicket.get("player_out") if isinstance(wicket, dict) else None
                            if kind and "run out" not in kind:
                                bowling_acc[keyb]["wickets"] += 1
                            else:
                                # some formats don't put 'kind' well; if player_out exists and not run out, assume bowler
                                if player_out and "run out" not in kind:
                                    bowling_acc[keyb]["wickets"] += 1

        else:
            # Older style: inning like {"1st innings": { "team": "...", "deliveries": [ { "0.1": {...} }, ... ] } }
            for inning_name, inning_data in inning.items():
                if not isinstance(inning_data, dict):
                    continue
                team = inning_data.get("team", "")
                opposition = [t for t in teams if t != team][0] if len(teams) == 2 else ""
                deliveries = inning_data.get("deliveries", []) or inning_data.get("overs", [])
                # if deliveries are in overs-style under older format, we handle similarly:
                # check if 'deliveries' is a list of dicts (older style) else if list of overs (modern)
                if deliveries and isinstance(deliveries[0], dict):
                    # older: each entry like {"0.1": { ... }}
                    for delivery in deliveries:
                        # each delivery dict has a single key
                        for ball_key, d in delivery.items():
                            batter = d.get("batsman") or d.get("batter")
                            bowler = d.get("bowler")
                            runs_batter = safe_get(d, "runs", "batsman", default=0) or safe_get(d, "runs", "batter", default=0) or 0
                            runs_total = safe_get(d, "runs", "total", default=0) or 0
                            wicket = d.get("wicket")
                            if batter:
                                key = (match_id, date, venue, team, opposition, batter)
                                batting_acc[key]["runs"] += int(runs_batter or 0)
                                if is_legal_delivery(d):
                                    batting_acc[key]["balls"] += 1
                                if wicket and isinstance(wicket, dict) and wicket.get("player_out") == batter:
                                    batting_acc[key]["dismissals"] += 1
                            if bowler:
                                keyb = (match_id, date, venue, team, opposition, bowler)
                                bowling_acc[keyb]["runs_conceded"] += int(runs_total or 0)
                                if is_legal_delivery(d):
                                    bowling_acc[keyb]["balls"] += 1
                                if wicket:
                                    kind = wicket.get("kind", "").lower() if isinstance(wicket, dict) else ""
                                    player_out = wicket.get("player_out") if isinstance(wicket, dict) else None
                                    if kind and "run out" not in kind:
                                        bowling_acc[keyb]["wickets"] += 1
                                    else:
                                        if player_out and "run out" not in kind:
                                            bowling_acc[keyb]["wickets"] += 1
                else:
                    # fallback if structure unexpected
                    pass

def aggregate_and_save(batting_acc, bowling_acc):
    # Build batting DataFrame
    bat_rows = []
    for key, agg in batting_acc.items():
        match_id, date, venue, team, opposition, player = key
        runs = agg["runs"]
        balls = agg["balls"]
        dismissals = agg["dismissals"]
        bat_rows.append({
            "match_id": match_id,
            "date": date,
            "venue": venue,
            "team": team,
            "opposition": opposition,
            "player": player,
            "runs": runs,
            "balls": balls,
            "dismissals": dismissals
        })
    bat_df = pd.DataFrame(bat_rows)
    bat_out = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    bat_df.to_csv(bat_out, index=False)
    print(f"Saved batting match-level data to {bat_out} ({len(bat_df)} rows)")

    # Build bowling DataFrame (convert balls -> overs float)
    bowl_rows = []
    for key, agg in bowling_acc.items():
        match_id, date, venue, team, opposition, player = key
        balls = agg["balls"]
        overs = (balls // 6) + (balls % 6) / 10.0  # crude overs representation like 4.2
        bowl_rows.append({
            "match_id": match_id,
            "date": date,
            "venue": venue,
            "team": team,
            "opposition": opposition,
            "player": player,
            "balls": balls,
            "overs": overs,
            "wickets": agg["wickets"],
            "runs_conceded": agg["runs_conceded"]
        })
    bowl_df = pd.DataFrame(bowl_rows)
    bowl_out = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")
    bowl_df.to_csv(bowl_out, index=False)
    print(f"Saved bowling match-level data to {bowl_out} ({len(bowl_df)} rows)")

def main():
    files = [os.path.join(DATA_FOLDER, f) for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    print(f"Found {len(files)} json files in {DATA_FOLDER}")
    if MAX_FILES:
        files = files[:MAX_FILES]
        print(f"Processing first {MAX_FILES} files for testing...")

    batting_acc = defaultdict(lambda: {"runs":0, "balls":0, "dismissals":0})
    bowling_acc = defaultdict(lambda: {"runs_conceded":0, "balls":0, "wickets":0})

    processed = 0
    for path in files:
        try:
            process_file(path, batting_acc, bowling_acc)
            processed += 1
            if processed % 200 == 0:
                print(f"Processed {processed} files...")
        except Exception as e:
            print(f"Error processing {path}: {e}")

    print(f"Processed {processed} files total.")
    aggregate_and_save(batting_acc, bowling_acc)

if __name__ == "__main__":
    main()
