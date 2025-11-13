import pandas as pd

# File paths
BATTING_FILE = "outputs/cleaned_data/odi_batting_clean.csv"
BOWLING_FILE = "outputs/cleaned_data/odi_bowling_clean.csv"

def get_player_batting(search_name):
    df = pd.read_csv(BATTING_FILE)
    result = df[df["player"].str.contains(search_name, case=False, na=False)]
    return result

def get_player_bowling(search_name):
    df = pd.read_csv(BOWLING_FILE)
    result = df[df["player"].str.contains(search_name, case=False, na=False)]
    return result

if __name__ == "__main__":
    player = input("Enter player name (or part of name): ").strip()
    
    print("\n=== Batting Stats ===")
    bat_stats = get_player_batting(player)
    if not bat_stats.empty:
        print(bat_stats.to_string(index=False))
    else:
        print("No batting record found for", player)

    print("\n=== Bowling Stats ===")
    bowl_stats = get_player_bowling(player)
    if not bowl_stats.empty:
        print(bowl_stats.to_string(index=False))
    else:
        print("No bowling record found for", player)
