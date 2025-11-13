import os, json
from collections import Counter

# Path to your CricSheet folder
DATA_FOLDER = "data/cricsheet_all_matches"

def check_match_types(limit=2000):
    cnt = Counter()
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]

    for i, f in enumerate(files[:limit], start=1):
        path = os.path.join(DATA_FOLDER, f)
        try:
            with open(path, "r", encoding="utf-8") as file:
                match = json.load(file)
            match_type = match.get("info", {}).get("match_type", "UNKNOWN")
            cnt[match_type] += 1
        except Exception as e:
            print(f"⚠️ Skipped {f}: {e}")

        if i % 500 == 0:
            print(f"Processed {i} files...")

    print("\n📊 Match type distribution:")
    for k, v in cnt.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    check_match_types(limit=5000)  # check first 2000 files
