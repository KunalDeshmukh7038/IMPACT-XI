import pandas as pd

files = [
    "data/Batting/ODI_data.csv",
    "data/Bowling/Bowling_ODI.csv",
    "data/kaggle_datasets/ODI_batting.csv",
    "data/kaggle_datasets/ODI_bowling.csv",
    "data/kaggle_datasets/cricketers.csv"
]

for f in files:
    try:
        df = pd.read_csv(f)
        print(f"\n📄 {f}")
        print(df.columns.tolist()[:10])
        print(df.head(2))
    except Exception as e:
        print(f"⚠️ Error reading {f}: {e}")
