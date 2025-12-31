import os

# Classification keywords
CATEGORIES = {
    "Data Cleaning": ["dropna", "fillna", "replace", "clean", "preprocess", "remove", "isnull"],
    "Data Merging": ["merge", "join", "concat", "append", "combine"],
    "Machine Learning Model": ["fit(", "predict(", "RandomForest", "XGB", "LGBM", "train_test_split"],
    "Feature Engineering": ["LabelEncoder", "OneHotEncoder", "scaler", "transform", "feature"],
    "EDA / Visualization": ["plt.", "plot(", "matplotlib", "seaborn", "heatmap", "hist"],
    "File Input/Output": ["read_csv", "to_csv", "open(", "json", "load", "save"],
    "Utilities / Helpers": ["def ", "class ", "utils", "helper"],
    "Configuration": ["config", "settings", ".env", "path"]
}

ALLOWED = [".py", ".ipynb", ".json", ".csv", ".txt", ".yml", ".yaml"]

def classify_content(content):
    detected = []
    for cat, keys in CATEGORIES.items():
        for k in keys:
            if k.lower() in content.lower():
                detected.append(cat)
                break
    return detected

def scan_src_folder(src_path="src"):
    report = []
    print(f"\n🔍 Scanning folder: {src_path}\n")

    for root, _, files in os.walk(src_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in ALLOWED:
                full_path = os.path.join(root, f)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                except:
                    continue

                cats = classify_content(content)

                report.append((full_path, cats))

                print(f"📄 File: {full_path}")
                print(f"➡️ Detected Categories: {cats if cats else ['Unknown']}")
                print("-" * 60)

    return report


if __name__ == "__main__":
    scan_src_folder("src")
