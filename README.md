# 🏏 IMPACT XI — Smart Cricket Team Selector

An ML-powered cricket team selection app built with Python and Streamlit. Enter a squad of 15–20 players and IMPACT XI picks the optimal Best XI — adjusted for **match format**, **pitch conditions**, and **opposition**.

---

## What It Does

- Takes 15–20 player names as input
- Uses trained machine learning models to predict each player's expected runs and wickets
- Adjusts scores based on **venue/pitch type** and **opposition team**
- Selects a **balanced XI** (WK + Batters + All-rounders + Bowlers)
- Supports all three formats: **ODI, T20, and Test**
- Displays interactive charts and lets you download the selected team as a CSV

---

## Demo

| Setting | Example |
|---|---|
| Format | ODI |
| Venue | Wankhede Stadium |
| Opposition | Australia |
| Squad input | Virat Kohli, Rohit Sharma, Jasprit Bumrah... |

The app fuzzy-matches player names, detects roles (BAT / BWL / AR / WK), applies pitch and opponent multipliers, and outputs the top 11.

---

## Project Structure

```
IMPACT XI/
├── app/
│   └── impact_xi_app.py          # Main Streamlit app
├── src/
│   ├── ml_player_performance.py  # Model training script
│   ├── select_best_xi.py         # XI selection logic
│   ├── scoring_engine.py         # Player scoring
│   ├── data_loader.py            # Data loading utilities
│   ├── clean_odi_data.py         # Data cleaning
│   ├── generate_pitch_dataset.py # Pitch type builder
│   └── ...                       # Other helper scripts
├── models/
│   ├── batting_model_odi.pkl     # Trained batting model (ODI)
│   ├── batting_model_t20.pkl     # Trained batting model (T20)
│   ├── batting_model_test.pkl    # Trained batting model (Test)
│   ├── bowling_model_odi.pkl     # Trained bowling model (ODI)
│   ├── bowling_model_t20.pkl     # Trained bowling model (T20)
│   ├── bowling_model_test.pkl    # Trained bowling model (Test)
│   ├── features_odi.json         # Feature names for ODI models
│   ├── features_t20.json         # Feature names for T20 models
│   └── features_test.json        # Feature names for Test models
├── outputs/
│   └── cleaned_data/             # Processed master datasets (see Kaggle)
├── data/
│   ├── Batting/                  # Raw batting CSVs
│   ├── Bowling/                  # Raw bowling CSVs
│   └── kaggle_datasets/          # Source datasets (see Kaggle)
├── .gitignore
└── README.md
```

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/KunalDeshmukh7038/IMPACT-XI.git
cd IMPACT-XI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit pandas numpy plotly joblib scikit-learn rapidfuzz
```

### 4. Download the datasets

The datasets are hosted on Kaggle (too large for GitHub). Download and place them in the correct folders:

> **Kaggle Dataset:** *(add your Kaggle dataset link here)*

Place the files as follows:
```
outputs/cleaned_data/odi_master_final.csv
outputs/cleaned_data/t20_master_v2.csv
outputs/cleaned_data/test_master_v2.csv
outputs/pitch/pitch_types.csv
```

### 5. Run the app

```bash
streamlit run app/impact_xi_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## How It Works

### Machine Learning Models

Separate Random Forest models are trained for **batting** and **bowling** performance across all three formats. Features include career statistics such as runs, batting average, strike rate, wickets, economy rate, and bowling average.

### Scoring Formula

Each player receives a composite score:

```
Score = (Predicted Runs + 20 × Predicted Wickets) × Pitch Factor × Opposition Factor
```

- **Pitch Factor** — adjusts scores based on historical average runs and pace/spin distribution at the venue
- **Opposition Factor** (ODI only) — adjusts based on the player's historical record against the selected team

### Role Detection

Players are assigned roles (BAT / BWL / AR / WK) using a combination of explicit role labels from the dataset and statistical thresholds tuned per format.

### Balanced XI Selection

The app fills the XI according to customisable role targets (default: 1 WK, 5 BAT, 2 AR, 3 BWL). If a role bucket can't be filled from the squad, it falls back to the next best available player.

---

## Data Sources

| Dataset | Description |
|---|---|
| Batting / ODI, T20, Test | Career batting statistics per player per format |
| Bowling / ODI, T20, Test | Career bowling statistics per player per format |
| Kaggle datasets | People, cricketers, all-round stats from public cricket data |
| Cricsheet JSON | Ball-by-ball match data used to build cleaned master datasets |
| Pitch types CSV | Venue-level averages and pace/spin wicket percentages |

Raw and cleaned datasets are available on Kaggle: *(add link here)*

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11+ | Core language |
| Streamlit | Web app framework |
| Pandas / NumPy | Data processing |
| Scikit-learn | ML model training |
| Joblib | Model serialisation |
| Plotly | Interactive charts |
| RapidFuzz | Fuzzy player name matching |

---

## Configuration

You can adjust the balanced XI targets directly in the sidebar of the app. No code changes needed.

To change default player names or venue, edit the constants at the top of `app/impact_xi_app.py`.

---

## Author

**Kunal Deshmukh**
GitHub: [@KunalDeshmukh7038](https://github.com/KunalDeshmukh7038)

---

## License

This project is for educational and personal use. Dataset licenses follow their respective sources on Kaggle and Cricsheet.