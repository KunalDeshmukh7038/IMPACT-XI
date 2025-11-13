import os
import shutil

def update_master_dataset():
    base_path = "outputs/cleaned_data"
    old_file = os.path.join(base_path, "odi_master.csv")
    new_file = os.path.join(base_path, "odi_master_final.csv")
    backup_file = os.path.join(base_path, "odi_master_backup.csv")

    # Check if new file exists
    if not os.path.exists(new_file):
        print("❌ Enriched file not found. Please ensure 'odi_master_final.csv' exists.")
        return

    # Backup old file (if exists)
    if os.path.exists(old_file):
        shutil.copy(old_file, backup_file)
        print(f"🗄️  Backup created: {backup_file}")

    # Replace old file with the new one
    shutil.copy(new_file, old_file)
    print(f"✅ Replaced old master file with enriched version.")
    print(f"📄 Active master file: {old_file}")

    # Verify
    print("\n🔍 Verification:")
    print(f" - New file size: {os.path.getsize(new_file)} bytes")
    print(f" - Active file size: {os.path.getsize(old_file)} bytes")
    print("\n✅ Dataset update complete — ready for retraining!")


if __name__ == "__main__":
    update_master_dataset()
