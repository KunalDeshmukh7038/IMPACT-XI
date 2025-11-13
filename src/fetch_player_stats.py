# src/fetch_player_stats.py

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

def fetch_player_stats(player_name: str, format_type: str = "ODI") -> pd.DataFrame:
    """
    Fetch summary stats for the given player_name from ESPN Cricinfo.
    Only returns a single row DataFrame with fields aligned to your master dataset.
    format_type defaults to “ODI”.
    """

    # 1. Search for the player
    search_url = f"https://www.espncricinfo.com/player/{player_name.replace(' ', '-')}-0"
    # Note: The above URL may not directly work for all players; we may need to use search result page instead.
    # As fallback:
    fallback_search = (
        "https://www.espncricinfo.com/ci/content/player/search.html?search="
        + player_name.replace(" ", "+")
    )

    resp = requests.get(fallback_search, timeout=10)
    if resp.status_code != 200:
        print(f"⚠️ Search page request failed for {player_name} (status {resp.status_code})")
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    # Find first valid player profile link
    link = soup.select_one("a[href*='/player/']")
    if not link:
        print(f"⚠️ Could not locate profile link for {player_name}")
        return None

    profile_url = "https://www.espncricinfo.com" + link["href"]
    print(f"🔗 Found profile URL: {profile_url}")

    resp2 = requests.get(profile_url, timeout=10)
    if resp2.status_code != 200:
        print(f"⚠️ Profile page request failed for {player_name} (status {resp2.status_code})")
        return None

    soup2 = BeautifulSoup(resp2.text, "lxml")
    # Extract player ID from URL
    match_id = re.search(r'/player/(\d+)', link["href"])
    player_id = match_id.group(1) if match_id else None

    # Prepare the result dict with your fields
    data = {
        "id": player_id,
        "name": player_name,
        "matches": None,
        "innings": None,
        "runs": None,
        "average_score": None,
        "strike_rate": None,
        "100s": None,
        "50": None,
        "wickets": None,
        "bowling_avg": None,
        "bowling_econ": None,
        "bowling_sr": None,
        "playing_role": None
    }

    # 2. Find ODI batting and bowling summary tables
    tables = soup2.select("table.engineTable")
    for table in tables:
        header = table.find_previous_sibling("h5")
        if header:
            txt = header.get_text().strip()
            if format_type in txt and "batting" in txt.lower():
                # batting summary table
                df_bat = pd.read_html(str(table))[0]
                # Example row: columns like Mat, Inns, NO, Runs, HS, Ave, SR etc.
                # We pick first row
                row = df_bat.iloc[0]
                data.update({
                    "matches": int(row["Mat"]) if pd.notna(row["Mat"]) else None,
                    "innings": int(row["Inns"]) if pd.notna(row["Inns"]) else None,
                    "runs": int(row["Runs"].replace("*","")) if isinstance(row["Runs"], str) else row["Runs"],
                    "average_score": float(row["Ave"]) if row["Ave"] not in ["-", None] else None,
                    "strike_rate": float(row["SR"]) if row["SR"] not in ["-", None] else None,
                    "100s": int(row["100s"]) if "100s" in row and pd.notna(row["100s"]) else None,
                    "50": int(row["50"]) if "50" in row and pd.notna(row["50"]) else None
                })
            if format_type in txt and "bowling" in txt.lower():
                # bowling summary
                df_bowl = pd.read_html(str(table))[0]
                row = df_bowl.iloc[0]
                data.update({
                    "wickets": int(row["Wkts"]) if pd.notna(row["Wkts"]) else None,
                    "bowling_avg": float(row["Ave"]) if row["Ave"] not in ["-", None] else None,
                    "bowling_econ": float(row["Econ"]) if row["Econ"] not in ["-", None] else None,
                    "bowling_sr": float(row["SR"]) if row["SR"] not in ["-", None] else None
                })

    # 3. Try to detect playing role from bio section
    bio_tag = soup2.select_one("p.PlayerBiography__Bio")
    if bio_tag:
        bio_text = bio_tag.get_text().lower()
        if "all-rounder" in bio_text or "all-rounder" in bio_text:
            data["playing_role"] = "allrounder"
        elif "bowler" in bio_text:
            data["playing_role"] = "bowler"
        elif "wicketkeeper" in bio_text or "keeper" in bio_text:
            data["playing_role"] = "wicketkeeper batter"
        else:
            data["playing_role"] = "batter"

    # 4. Convert to DataFrame
    df_out = pd.DataFrame([data])
    return df_out

# If run as script
if __name__ == "__main__":
    name = input("Enter player name to fetch: ").strip()
    df_player = fetch_player_stats(name)
    if df_player is not None:
        print(df_player.to_string(index=False))
        df_player.to_csv(f"fetched_{name.replace(' ', '_')}.csv", index=False)
