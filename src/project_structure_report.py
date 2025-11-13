import os
import pandas as pd

# Root directory of your project
PROJECT_ROOT = os.path.abspath(".")

# Keywords to categorize files
CATEGORY_MAP = {
    ".py": "Python Script",
    ".csv": "Dataset / Cleaned Data",
    ".pkl": "Trained ML Model",
    ".json": "Feature Config / Metadata",
    ".png": "Image / Logo",
    ".jpg": "Image / Logo",
    ".jpeg": "Image / Logo",
    ".ipynb": "Jupyter Notebook",
    ".md": "Documentation",
    ".toml": "Streamlit / Config",
    ".txt": "Text / Notes",
}

# Main files to highlight (custom logic)
MAIN_FILE_HINTS = [
    "impact_xi_app.py",
    "merge_",
    "generate_",
    "pitch_types.csv",
    "odi_master",
    "t20_master",
    "test_master",
    "models/",
    "outputs/",
    "requirements.txt"
]

# --------------------------------------
# Helper: classify file
# --------------------------------------
def classify_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    category = CATEGORY_MAP.get(ext, "Other")
    
    # Heuristic description
    desc = ""
    fname = os.path.basename(file_path).lower()
    
    if "impact_xi_app" in fname:
        desc = "Main Streamlit App"
    elif "merge" in fname:
        desc = "Data merging or preprocessing script"
    elif "generate_pitch" in fname:
        desc = "Pitch dataset generator"
    elif "model" in fname and ext == ".pkl":
        desc = "Trained ML model for batting/bowling prediction"
    elif "feature" in fname and ext == ".json":
        desc = "Feature metadata for ML model"
    elif "master" in fname and ext == ".csv":
        desc = "Final cleaned master dataset"
    elif "merged" in fname and ext == ".csv":
        desc = "Merged dataset (batting + bowling)"
    elif "pitch" in fname and ext == ".csv":
        desc = "Pitch metrics (batting/bowling conditions)"
    elif "requirements" in fname:
        desc = "Python dependencies list"
    elif "logo" in fname:
        desc = "App logo image"
    elif "readme" in fname:
        desc = "Project documentation (README)"
    elif "cleaned_data" in file_path:
        desc = "Processed/clean datasets"
    elif "src" in file_path and ext == ".py":
        desc = "Backend data-processing or utility script"
    elif "outputs" in file_path and ext == ".csv":
        desc = "Final output datasets"
    
    return category, desc or "Unclassified"

# --------------------------------------
# Collect file info
# --------------------------------------
records = []
for root, dirs, files in os.walk(PROJECT_ROOT):
    for file in files:
        if file.startswith("."):  # ignore hidden
            continue
        fpath = os.path.join(root, file)
        relpath = os.path.relpath(fpath, PROJECT_ROOT)
        category, desc = classify_file(relpath)
        size_kb = round(os.path.getsize(fpath) / 1024, 2)
        main_flag = any(hint in relpath.lower() for hint in MAIN_FILE_HINTS)
        records.append({
            "File Path": relpath,
            "Type": category,
            "Description": desc,
            "Size (KB)": size_kb,
            "Main File?": "✅" if main_flag else ""
        })

# --------------------------------------
# Create report DataFrame
# --------------------------------------
df_report = pd.DataFrame(records).sort_values(["Main File?", "Type"], ascending=[False, True])
print("\n📂 Project File Structure Summary:\n")
print(df_report.to_string(index=False))

# --------------------------------------
# Save report to CSV
# --------------------------------------
os.makedirs("reports", exist_ok=True)
report_path = os.path.join("reports", "project_file_report.csv")
df_report.to_csv(report_path, index=False)
print(f"\n✅ Report saved to: {report_path}")
