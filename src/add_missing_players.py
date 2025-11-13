import os
import pandas as pd
from datetime import datetime
from fetch_player_stats import fetch_player_stats

# ====================================================
# Helper: Save backup of ODI master before updating
# ====================================================
def backup_master(master_file):
    if not os.path.exists(master_file):
        print(f"❌ Master file not found: {master_file}")
        return None

    backup_dir = "outputs/backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"odi_master_backup_{timestamp}.csv")

    pd.read_csv(master_file).to_csv(backup_path, index=False)
    print(f"🗄️  Backup created: {backup_path}")
    return backup_path


# ====================================================
# Main logic
# ====================================================
def main():
    master_file = "outputs/cleaned_data/odi_master.csv"
    log_dir = "outputs/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "missing_player_report.txt")

    if not os.path.exists(master_file):
        print(f"❌ Master dataset not found: {master_file}")
        return

    # 1️⃣ Load master dataset
    master_df = pd.read_csv(master_file)
    print(f"\n✅ Loaded master dataset: {master_df.shape}")

    # 2️⃣ Ask user for player names
    player_input = input("Enter missing player names (comma separated): ").strip()
    player_names = [p.strip() for p in player_input.split(",") if p.strip()]

    # 3️⃣ Backup current master
    backup_master(master_file)

    # 4️⃣ Iterate and fetch stats for missing players
    added_players = []
    not_found = []

    for player in player_names:
        if player.lower() in master_df["name"].str.lower().values:
            print(f"✅ {player} already exists in master.")
            continue

        print(f"\n🔍 Fetching stats for: {player} ...")
        try:
            df_new = fetch_player_stats(player)
            if df_new is not None and not df_new.empty:
                master_df = pd.concat([master_df, df_new], ignore_index=True)
                added_players.append(player)
                print(f"✅ Added {player} to master dataset.")
            else:
                not_found.append(player)
                print(f"⚠️ Could not fetch stats for {player}.")
        except Exception as e:
            print(f"❌ Error fetching {player}: {e}")
            not_found.append(player)

    # 5️⃣ Save updated master dataset
    master_df.to_csv(master_file, index=False)
    print(f"\n💾 Updated master dataset saved → {master_file}")
    print(f"📊 New shape: {master_df.shape}")

    # 6️⃣ Log summary
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=== Missing Player Report ===\n")
        f.write(f"Run Time: {datetime.now()}\n\n")
        if added_players:
            f.write("✅ Added Players:\n")
            f.write("\n".join(added_players) + "\n\n")
        if not_found:
            f.write("⚠️ Not Found:\n")
            f.write("\n".join(not_found) + "\n\n")
    print(f"\n🧾 Log saved to {log_file}")


if __name__ == "__main__":
    main()
