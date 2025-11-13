import os
import re
import pandas as pd

SRC_FOLDER = "src"

# Keyword patterns to detect importance
CATEGORIES = {
    "CORE DATA CLEANING": [
        "clean", "preprocess", "batting", "bowling", "match", "raw"
    ],
    "DATA MERGING": [
        "merge", "combine", "master"
    ],
    "ML PIPELINE": [
        "train", "model", "feature", "ml", "predict"
    ],
    "PITCH / CONTEXT SYSTEM": [
        "pitch", "venue", "context", "opposition"
    ],
    "UTILITY / DEBUG": [
        "check", "analyze", "report", "test", "debug"
    ]
}

def categorize_file(filename):
    name = filename.lower()

    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in name:
                return category

    return "UNKNOWN / POSSIBLY UNUSED"


def scan_src_folder():
    files = [f for f in os.listdir(SRC_FOLDER) if f.endswith(".py")]

    results = []

    for file in files:
        category = categorize_file(file)

        results.append({
            "File Name": file,
            "Category": category,
            "Important": "YES" if category in [
                "CORE DATA CLEANING",
                "DATA MERGING",
                "ML PIPELINE",
                "PITCH / CONTEXT SYSTEM"
            ] else "NO"
        })

    df = pd.DataFrame(results)
    return df


if __name__ == "__main__":
    print("\n🔍 Scanning 'src/' folder for important project scripts...\n")

    df = scan_src_folder()
    print(df.to_string(index=False))

    # Save a copy to outputs folder
    output_path = "outputs/project_script_report.csv"
    df.to_csv(output_path, index=False)

    print(f"\n📁 Report saved to: {output_path}\n")
