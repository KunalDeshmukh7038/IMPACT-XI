# src/ml_player_performance.py
import pandas as pd
import joblib
import os
import json
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# =========================================================
# Helper: Clean dataframe safely
# =========================================================
# def clean_dataframe(df):
#     print("🧹 Cleaning dataframe...")

#     # Drop completely empty columns
#     df = df.dropna(axis=1, how="all")

#     # Replace unwanted symbols
#     df.replace(["-", "–", "DNB", "NaN", "n/a", "N/A"], pd.NA, inplace=True)

#     # Remove '*' from numeric strings
#     for col in df.columns:
#         try:
#             df[col] = df[col].astype(str).str.replace("*", "", regex=False)
#         except Exception:
#             continue

#     # Convert to numeric where possible
#     for col in df.columns:
#         try:
#             df[col] = pd.to_numeric(df[col], errors="coerce")
#         except Exception:
#             pass

#     print(f"✅ Cleaning completed. Shape: {df.shape}")
#     return df
def clean_dataframe(df):
    print("🧹 Cleaning dataframe...")

    # Work on a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Drop completely empty columns
    df = df.dropna(axis=1, how="all")

    # Replace unwanted symbols
    df = df.replace(["-", "–", "DNB", "NaN", "n/a", "N/A"], pd.NA)

    # Remove '*' from numeric strings
    for col in df.columns:
        try:
            df.loc[:, col] = df[col].astype(str).str.replace("*", "", regex=False)
        except Exception:
            continue

    # Convert to numeric where possible
    for col in df.columns:
        try:
            df.loc[:, col] = pd.to_numeric(df[col], errors="coerce")
        except Exception:
            pass

    print(f"✅ Cleaning completed. Shape: {df.shape}")
    return df



# =========================================================
# Helper: Train and evaluate models
# =========================================================
def train_and_select_model(X, y, models):
    best_model, best_score, best_name = None, -1, None

    for name, model in models.items():
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        score = r2_score(y_test, y_pred)
        print(f"✅ {name} R²: {score:.4f}")

        if score > best_score:
            best_model, best_score, best_name = model, score, name

    print(f"🎯 Using {best_name} (R²={best_score:.4f})")
    return best_model


# =========================================================
# Core Function: Train for each format
# =========================================================
def train_for_format(fmt):
    fmt_lower = fmt.lower()
    data_path = f"outputs/cleaned_data/{fmt_lower}_master.csv"

    if not os.path.exists(data_path):
        print(f"❌ Dataset not found for {fmt}: {data_path}")
        return

    print(f"\n🏏 Training models for {fmt} format...")
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {data_path} — Shape: {df.shape}\n")

    df = clean_dataframe(df)

    # =====================================================
    # Format-specific column mappings
    # =====================================================
    if fmt == "ODI":
        batting_target = "runs"
        bowling_target = "wickets"
        batting_candidates = [
            "matches", "innings", "runs", "average_score", "strike_rate",
            "high_score", "100s", "50", "not_out", "ball_faced", "4s", "6s"
        ]
        bowling_candidates = [
            "matches", "innings", "wickets", "bowling_avg", "bowling_econ",
            "bowling_sr", "4", "5"
        ]

    elif fmt == "T20":
        batting_target = "Bat_Runs"
        bowling_target = "Bowl_Wkts"
        batting_candidates = [
            "Bat_Mat", "Bat_Inns", "Bat_Runs", "Bat_Ave", "Bat_SR",
            "Bat_100", "Bat_50", "Bat_4s", "Bat_6s"
        ]
        bowling_candidates = [
            "Bowl_Mat", "Bowl_Inns", "Bowl_Wkts", "Bowl_Ave",
            "Bowl_Econ", "Bowl_SR", "Bowl_4", "Bowl_5"
        ]

    elif fmt == "TEST":
        batting_target = "Bat_Runs"
        bowling_target = "Bowl_Wkts"
        batting_candidates = [
            "Bat_Mat", "Bat_Inns", "Bat_Runs", "Bat_Ave",
            "Bat_100", "Bat_50", "Bat_0"
        ]
        bowling_candidates = [
            "Bowl_Mat", "Bowl_Inns", "Bowl_Wkts", "Bowl_Ave",
            "Bowl_Econ", "Bowl_SR", "Bowl_5", "Bowl_10"
        ]
    else:
        print(f"⚠️ Unknown format: {fmt}")
        return

    # =====================================================
    # Train Batting Model
    # =====================================================
    if batting_target in df.columns:
        print("🏏 Training Batting Model...")
        batting_features = [c for c in batting_candidates if c in df.columns]
        bat_df = df.dropna(subset=[batting_target]).copy()
        X_bat = bat_df[batting_features].fillna(0)
        y_bat = bat_df[batting_target]

        batting_models = {
            "LinearRegression": LinearRegression(),
            "RandomForest": RandomForestRegressor(random_state=42),
            "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42),
        }

        best_bat_model = train_and_select_model(X_bat, y_bat, batting_models)
        joblib.dump(best_bat_model, f"models/batting_model_{fmt_lower}.pkl")
        print(f"💾 Saved Batting model → models/batting_model_{fmt_lower}.pkl\n")
    else:
        print(f"⚠️ No '{batting_target}' column found. Skipping batting model.\n")

    # =====================================================
    # Train Bowling Model
    # =====================================================
    if bowling_target in df.columns:
        print("🎯 Training Bowling Model...")
        bowling_features = [c for c in bowling_candidates if c in df.columns]
        bowl_df = df.dropna(subset=[bowling_target]).copy()
        X_bowl = bowl_df[bowling_features].fillna(0)
        y_bowl = bowl_df[bowling_target]

        bowling_models = {
            "LinearRegression": LinearRegression(),
            "RandomForest": RandomForestRegressor(random_state=42),
            "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42),
        }

        best_bowl_model = train_and_select_model(X_bowl, y_bowl, bowling_models)
        joblib.dump(best_bowl_model, f"models/bowling_model_{fmt_lower}.pkl")
        print(f"💾 Saved Bowling model → models/bowling_model_{fmt_lower}.pkl\n")
    else:
        print(f"⚠️ No '{bowling_target}' column found. Skipping bowling model.\n")

    # =====================================================
    # Save Features
    # =====================================================
    features = {
        "batting": batting_candidates,
        "bowling": bowling_candidates,
    }
    with open(f"models/features_{fmt_lower}.json", "w") as f:
        json.dump(features, f, indent=4)
    print(f"💾 Saved feature list → models/features_{fmt_lower}.json")

    print(f"✅ Completed model training for {fmt} format!")
    print("=" * 80)


# =========================================================
# Main Execution
# =========================================================
if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    formats = ["ODI", "T20", "TEST"]

    for fmt in formats:
        train_for_format(fmt)
