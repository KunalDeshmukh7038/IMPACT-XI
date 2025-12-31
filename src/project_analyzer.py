import os
import re

# --- Classification Keywords ---
CATEGORIES = {
    "Data Cleaning": [
        "dropna", "fillna", "replace", "isnull", "astype", "clean", "preprocess", "remove"
    ],
    "Data Merging / Joining": [
        "merge", "join", "concat", "append", "combine", "left_on", "right_on"
    ],
    "ML Model Training": [
        "RandomForest", "LinearRegression", "train_test_split", "fit(", "predict(", "model"
    ],
    "Feature Engineering": [
        "LabelEncoder", "OneHotEncoder", "feature", "transform", "scaler", "StandardScaler"
    ],
    "Visualization / EDA": [
        "plot", "matplotlib", "seaborn", "plt.", "hist", "pairplot", "heatmap"
    ],
    "File I/O": [
        "read_csv", "to_csv", "open(", "write", "load", "save", "json", "yaml"
    ],
    "Configuration": [
        ".env", "config", "settings", "path", "BASE_DIR"
    ],
    "Utility Functions": [
        "def ", "utils", "helper", "function", "class "
    ]
}

ALLOWED_EXTENSIONS = [".py", ".txt", ".json", ".csv", ".yml", ".yaml", ".ipynb"]

# --- Core Logic ---
def classify_content(content):
    detected = set()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in content.lower():
                detected.add(category)
    return list(detected)

def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        return None

    categories = classify_content(content)

    # Get sample lines
    sample = "\n".join(content.split("\n")[:5])

    return {
        "file": filepath,
        "categories": categories,
        "sample": sample
    }

def scan_project(root_folder):
    report = []

    for root, dirs, files in os.walk(root_folder):
        for filename in files:
            ext = os.path.splitext(filename)[1]
            if ext.lower() in ALLOWED_EXTENSIONS:

                filepath = os.path.join(root, filename)
                print(f"Analyzing: {filepath}")

                result = analyze_file(filepath)
                if result:
                    report.append(result)

    return report

# --- Run Script ---
if __name__ == "__main__":
    project_path = input("Enter your project root folder path: ").strip()

    print("\n🔍 Scanning project...\n")
    results = scan_project(project_path)

    print("\n\n📘 ==== PROJECT ANALYSIS REPORT ====\n")

    for r in results:
        print(f"\n📄 File: {r['file']}")
        print(f"➡️ Categories detected: {', '.join(r['categories']) if r['categories'] else 'Unknown'}")
        print("📌 Sample code:")
        print(r["sample"])
        print("-" * 70)
