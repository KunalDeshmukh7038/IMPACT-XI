# app/impact_xi_app.py
import os
import json
import math
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from rapidfuzz import process, fuzz

# ------------------------------
# Page / Theme
# ------------------------------
st.set_page_config(page_title="IMPACT XI Selector", layout="wide")
# Dark theme hint (optional—Streamlit theme can also be set in .streamlit/config.toml)
st.markdown("""
<style>
/* compact top padding */
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
/* role chips */
.role-chip {
  display:inline-flex; align-items:center; gap:.4rem;
  padding:.22rem .6rem; border-radius:999px; font-weight:600; font-size:.85rem;
  background: #111418; color:#E4E6EB; border:1px solid #2a2f36;
}
.badge-bat { background: #16202b; border-color:#2a425b;}
.badge-bwl { background: #1a231a; border-color:#2a4b2a;}
.badge-ar  { background: #241c16; border-color:#4d3a27;}
.badge-wk  { background: #1f1a26; border-color:#41365a;}
/* small mono number */
.num {font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1;}
/* table tune */
thead tr th { background:#0e1117 !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Constants
# ------------------------------
DATA_DIR = "outputs/cleaned_data"
PITCH_PATH = os.path.join("outputs", "pitch", "pitch_types.csv")

FORMAT_FILES = {
    "ODI": [
        os.path.join(DATA_DIR, "odi_master_final.csv"),
        os.path.join(DATA_DIR, "odi_master_enriched.csv"),
        os.path.join(DATA_DIR, "odi_master.csv"),
    ],
    "T20": [
        os.path.join(DATA_DIR, "t20_master_v2.csv"),
        os.path.join(DATA_DIR, "t20_master.csv"),
    ],
    "TEST": [
        os.path.join(DATA_DIR, "test_master_v2.csv"),
        os.path.join(DATA_DIR, "test_master.csv"),
    ],
}

# ODI last-10 / context data (optional, best-effort)
ODI_LAST10_BAT = os.path.join(DATA_DIR, "odi_batting_merged.csv")
ODI_LAST10_BOWL = os.path.join(DATA_DIR, "odi_bowling_merged.csv")

# Desired balanced XI buckets
ROLE_TARGETS_DEFAULT = {"WK": 1, "BAT": 5, "AR": 2, "BWL": 3}

# ------------------------------
# Utilities
# ------------------------------
def first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def try_read_csv(path, **kwargs):
    if path and os.path.exists(path):
        try:
            return pd.read_csv(path, **kwargs)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def to_num(x, default=0.0):
    try:
        v = pd.to_numeric(x)
        if pd.isna(v).any() if isinstance(v, pd.Series) else pd.isna(v):
            return default
        return float(v) if not isinstance(v, (int, float)) else v
    except Exception:
        try:
            return float(x)
        except Exception:
            return default

def norm_text(s):
    return (
        str(s)
        .lower()
        .replace(".", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("-", " ")
        .strip()
    )

def initial_style_name(s):
    """Prefer initials + surname if present in dataset; else fallback to original."""
    s = str(s).strip()
    # already in initials? just return
    if len(s.split()) <= 3 and any(ch == "." for ch in s):
        return s
    # naive: keep as is
    return s

# ------------------------------
# Load Models & Features (resource cache ok)
# ------------------------------
@st.cache_resource
def load_models_for(format_type: str):
    fm = format_type.lower()
    bat_model_path = f"models/batting_model_{fm}.pkl"
    bowl_model_path = f"models/bowling_model_{fm}.pkl"
    feat_path = f"models/features_{fm}.json"

    if not (os.path.exists(bat_model_path) and os.path.exists(bowl_model_path) and os.path.exists(feat_path)):
        st.error(f"❌ Models or features missing for {format_type}. Please train first.")
        st.stop()

    bat = joblib.load(bat_model_path)
    bowl = joblib.load(bowl_model_path)
    with open(feat_path, "r") as f:
        feats = json.load(f)
    return bat, bowl, feats

# ------------------------------
# Load Master Dataset (robust to different schemas)
# ------------------------------
@st.cache_data
def load_master(format_type: str):
    path = first_existing(FORMAT_FILES.get(format_type, []))
    if not path:
        st.error(f"❌ No master dataset found for {format_type}.")
        st.stop()

    df = try_read_csv(path, low_memory=False)
    if df.empty:
        st.error(f"❌ Could not read master dataset for {format_type}.")
        st.stop()

    # Find a name column and unify to: display_name (for UI), name_norm (for match)
    name_candidates = [
        "display_name", "name", "Player", "player",
        "Bat_Player", "Player_bat", "player_clean",
        "Bowl_player_clean"
    ]
    found_name_col = next((c for c in name_candidates if c in df.columns), None)
    if not found_name_col:
        # try to infer by looking for any column that looks like player names
        for c in df.columns:
            if df[c].dtype == object and df[c].astype(str).str.contains(r"[A-Za-z]", na=False).mean() > 0.8:
                found_name_col = c
                break
    if not found_name_col:
        st.error("❌ Could not locate a player name column in the master dataset.")
        st.stop()

    df["display_name"] = df[found_name_col].fillna("").astype(str).apply(initial_style_name)
    df["name_norm"] = df[found_name_col].fillna("").astype(str).apply(norm_text)

    # numeric helpers (common keys)
    # (We don’t mutate originals—just create numeric facades used by role/pred)
    if format_type == "ODI":
        df["runs_facade"] = (
            df.get("runs", df.get("Runs", df.get("runs_odi_batting", 0))).apply(to_num)
        )
        df["wkts_facade"] = (
            df.get("wickets", df.get("Wkts", df.get("wk", 0))).apply(to_num)
        )
    else:
        # t20/test v2 columns
        df["runs_facade"] = (
            df.get("Bat_Runs", df.get("runs", df.get("Runs", 0))).apply(to_num)
        )
        df["wkts_facade"] = (
            df.get("Bowl_Wkts", df.get("wickets", df.get("Wkts", 0))).apply(to_num)
        )

    # playing role candidate columns
    df["role_raw"] = ""
    for rc in ["playing_role", "Role", "role", "Bat_Role", "Player_Type"]:
        if rc in df.columns:
            df["role_raw"] = df[rc].fillna("").astype(str)
            break

    return df

# ------------------------------
# ODI last-10 / context / pitch
# ------------------------------
@st.cache_data
def load_odi_context():
    bat = try_read_csv(ODI_LAST10_BAT, low_memory=False)
    bowl = try_read_csv(ODI_LAST10_BOWL, low_memory=False)
    # unify names
    if not bat.empty:
        name_col = "player" if "player" in bat.columns else ("Player" if "Player" in bat.columns else None)
        if name_col:
            bat["name_norm"] = bat[name_col].fillna("").astype(str).apply(norm_text)
    if not bowl.empty:
        name_col = "player" if "player" in bowl.columns else ("Player" if "Player" in bowl.columns else None)
        if name_col:
            bowl["name_norm"] = bowl[name_col].fillna("").astype(str).apply(norm_text)
    return bat, bowl

@st.cache_data
def load_pitch_types():
    df = try_read_csv(PITCH_PATH)
    if df.empty:
        return df
    # normalize
    if "venue" in df.columns:
        df["venue_norm"] = df["venue"].fillna("").astype(str).str.lower().str.strip()
    else:
        df["venue_norm"] = ""
    # sanitize metrics
    for c in ["avg_runs", "pace_wkts_pct", "spin_wkts_pct"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# ------------------------------
# Matching
# ------------------------------
def match_inputs_to_dataset(user_inputs, df_master):
    """Return list of matched normalized names in the dataset (only those present)."""
    names_in_ds = df_master["name_norm"].unique().tolist()

    matched = []
    mapping_rows = []
    for raw in user_inputs:
        cleaned = norm_text(raw)
        choice = process.extractOne(
            cleaned,
            names_in_ds,
            scorer=fuzz.WRatio,
            score_cutoff=70
        )
        if choice:
            matched.append(choice[0])
            mapping_rows.append({"input": raw, "matched_name": df_master[df_master["name_norm"] == choice[0]]["display_name"].iloc[0]})
        else:
            mapping_rows.append({"input": raw, "matched_name": None})

    return matched, pd.DataFrame(mapping_rows)

# ------------------------------
# Role Detection
# ------------------------------
def detect_role_row(row):
    # explicit role
    r = str(row.get("role_raw", "")).lower()
    name = str(row.get("display_name", "")).lower()

    runs = to_num(row.get("runs_facade", 0), 0)
    wkts = to_num(row.get("wkts_facade", 0), 0)

    # wicketkeeper check
    if any(k in r for k in ["wicket", "wk"]) or any(k in name for k in [" dhoni", " pant", " karthik", " saha", " de kock", " buttler", " bairstow", " rizwan"]):
        return "WK"
    # explicit hints
    if "allround" in r:
        return "AR"
    if "bowl" in r:
        return "BWL"
    if "bat" in r:
        return "BAT"

    # stat-based heuristic
    # (these thresholds are gentle; adapt per format below)
    if runs >= 1500 and wkts < 30:
        return "BAT"
    if wkts >= 100 and runs < 1500:
        return "BWL"
    if runs >= 1200 and wkts >= 50:
        return "AR"
    # fallback:
    return "BAT"

def detect_role_by_format(row, fmt):
    base = detect_role_row(row)
    runs = to_num(row.get("runs_facade", 0), 0)
    wkts = to_num(row.get("wkts_facade", 0), 0)

    if fmt == "T20":
        if "WK" == base:
            return "WK"
        if wkts >= 60 and runs < 1200:
            return "BWL"
        if runs >= 1800 and wkts < 30:
            return "BAT"
        if runs >= 1400 and wkts >= 40:
            return "AR"
        return base
    if fmt == "TEST":
        if "WK" == base:
            return "WK"
        if wkts >= 200 and runs < 2500:
            return "BWL"
        if runs >= 3000 and wkts < 60:
            return "BAT"
        if runs >= 2500 and wkts >= 100:
            return "AR"
        return base
    # ODI default
    return base

# ------------------------------
# Predictions (safe)
# ------------------------------
def safe_predict(model, X):
    try:
        preds = model.predict(X)
        if isinstance(preds, (list, np.ndarray, pd.Series)):
            return np.asarray(preds, dtype=float)
        return np.zeros(len(X))
    except Exception:
        return np.zeros(len(X))

def features_matrix(df, features):
    cols = features if isinstance(features, list) else (features or [])
    X = df.reindex(columns=cols).copy()
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    X = X.fillna(0.0)
    return X

# ------------------------------
# Last-10 (ODI only) + Context
# ------------------------------
def last10_for_player_odi(name_norm, bat_ctx, bowl_ctx):
    """Return (last10_runs, last10_wkts) for ODI; 0 if unavailable."""
    l10_runs = 0.0
    l10_wkts = 0.0

    if not bat_ctx.empty and "name_norm" in bat_ctx.columns:
        sub = bat_ctx[bat_ctx["name_norm"] == name_norm].copy()
        if not sub.empty:
            # sort by date if present
            if "date" in sub.columns:
                sub["date_ord"] = pd.to_datetime(sub["date"], errors="coerce")
                sub = sub.sort_values("date_ord", ascending=False)
            sub["runs_num"] = pd.to_numeric(sub.get("runs", 0), errors="coerce").fillna(0.0)
            l10_runs = float(sub["runs_num"].head(10).sum())

    if not bowl_ctx.empty and "name_norm" in bowl_ctx.columns:
        subb = bowl_ctx[bowl_ctx["name_norm"] == name_norm].copy()
        if not subb.empty:
            if "date" in subb.columns:
                subb["date_ord"] = pd.to_datetime(subb["date"], errors="coerce")
                subb = subb.sort_values("date_ord", ascending=False)
            subb["wkts_num"] = pd.to_numeric(subb.get("wickets", 0), errors="coerce").fillna(0.0)
            l10_wkts = float(subb["wkts_num"].head(10).sum())

    return l10_runs, l10_wkts

def opponent_factor_odi(name_norm, opponent, bat_ctx, bowl_ctx):
    if not opponent:
        return 1.0
    op_norm = norm_text(opponent)
    factor = 1.0

    if not bat_ctx.empty and "name_norm" in bat_ctx.columns and "opposition" in bat_ctx.columns:
        sub = bat_ctx[(bat_ctx["name_norm"] == name_norm)]
        if not sub.empty:
            m = sub[sub["opposition"].astype(str).str.lower().str.contains(op_norm, na=False)]
            if not m.empty:
                r = pd.to_numeric(m.get("runs", 0), errors="coerce").fillna(0.0).mean()
                if r > 40: factor += 0.08
                elif r < 20: factor -= 0.05

    if not bowl_ctx.empty and "name_norm" in bowl_ctx.columns and "opposition" in bowl_ctx.columns:
        subb = bowl_ctx[(bowl_ctx["name_norm"] == name_norm)]
        if not subb.empty:
            m2 = subb[subb["opposition"].astype(str).str.lower().str.contains(op_norm, na=False)]
            if not m2.empty:
                w = pd.to_numeric(m2.get("wickets", 0), errors="coerce").fillna(0.0).mean()
                if w > 2: factor += 0.06
                elif w < 1: factor -= 0.03

    return max(0.85, min(1.15, factor))

def pitch_factor(venue, pitch_df, role_tag: str):
    """Return a multiplier based on pitch & role."""
    if venue is None or pitch_df.empty:
        return 1.0
    vnorm = str(venue).lower().strip()
    row = pitch_df[pitch_df["venue_norm"] == vnorm]
    if row.empty:
        # try contains
        row = pitch_df[pitch_df["venue_norm"].str.contains(vnorm, na=False)]
    if row.empty:
        return 1.0

    avg_runs = float(row["avg_runs"].fillna(0).iloc[0]) if "avg_runs" in row.columns else 0.0
    pace_pct = float(row["pace_wkts_pct"].fillna(np.nan).iloc[0]) if "pace_wkts_pct" in row.columns else np.nan
    spin_pct = float(row["spin_wkts_pct"].fillna(np.nan).iloc[0]) if "spin_wkts_pct" in row.columns else np.nan

    # Heuristic:
    # High avg_runs => batting-friendly
    # Higher pace_pct or spin_pct => bowler leaning; we don't distinguish pace vs spin role here
    f = 1.0
    if avg_runs >= 30:
        if role_tag == "BAT" or role_tag == "WK":
            f += 0.10
        elif role_tag in ("BWL", "AR"):
            f -= 0.03
    elif avg_runs <= 22 and not math.isnan(avg_runs):
        if role_tag == "BWL":
            f += 0.08
        elif role_tag in ("BAT", "WK"):
            f -= 0.04

    # If we know it's pace/spin heavy, give a small extra nudge to bowlers & AR
    if not math.isnan(pace_pct) and pace_pct >= 60:
        if role_tag in ("BWL", "AR"):
            f += 0.04
    if not math.isnan(spin_pct) and spin_pct >= 60:
        if role_tag in ("BWL", "AR"):
            f += 0.04

    return max(0.85, min(1.18, f))

# ------------------------------
# Balanced XI builder
# ------------------------------
def build_balanced_xi(df, targets):
    df = df.copy()
    xi = []

    def take_role(rtag, k):
        sub = df[df["Role"] == rtag].sort_values("Score", ascending=False)
        chosen = sub.head(k)
        return chosen

    # Primary fills
    for role_tag, need in targets.items():
        got = take_role(role_tag, need)
        xi.append(got)
        # remove chosen rows
        df = df.drop(got.index)

    xi_df = pd.concat(xi) if xi else pd.DataFrame()

    # If less than 11, fill with best available
    if len(xi_df) < 11:
        extra = df.sort_values("Score", ascending=False).head(11 - len(xi_df))
        xi_df = pd.concat([xi_df, extra])

    # If >11 because of overlaps (unlikely), trim
    return xi_df.sort_values("Score", ascending=False).head(11)

# ------------------------------
# UI — Sidebar
# ------------------------------
with st.sidebar:
    st.image("logo.png", use_container_width=True) if os.path.exists("logo.png") else None
    st.header("⚙️ Settings")

    format_type = st.selectbox("Match Format", ["ODI", "T20", "TEST"])
    venue = st.text_input("Venue (required)", "Wankhede Stadium")
    opponent = st.text_input("Opposition Team (required)", "Australia")

    default_names = (
        "Virat Kohli, Rohit Sharma, Shikhar Dhawan, MS Dhoni, Hardik Pandya, "
        "Ravindra Jadeja, Bhuvneshwar Kumar, Kuldeep Yadav, Jasprit Bumrah, KL Rahul, "
        "Suryakumar Yadav, R Ashwin, Rishabh Pant, Mohammed Shami, Axar Patel"
    )
    raw_players = st.text_area("Enter 15–20 player names (comma separated)", default_names, height=120)

    st.markdown("**Balanced XI Targets**")
    cols = st.columns(4)
    with cols[0]:
        tgt_wk = st.number_input("WK", min_value=0, max_value=3, value=ROLE_TARGETS_DEFAULT["WK"], step=1)
    with cols[1]:
        tgt_bat = st.number_input("BAT", min_value=0, max_value=8, value=ROLE_TARGETS_DEFAULT["BAT"], step=1)
    with cols[2]:
        tgt_ar = st.number_input("AR", min_value=0, max_value=5, value=ROLE_TARGETS_DEFAULT["AR"], step=1)
    with cols[3]:
        tgt_bwl = st.number_input("BWL", min_value=0, max_value=8, value=ROLE_TARGETS_DEFAULT["BWL"], step=1)

    do_go = st.button("⚡ Generate Best XI")

st.title("🏏 IMPACT XI — Smart Cricket Team Selector")
st.caption("Select your 15–20 names. The team is picked **only** from your inputs, and adjusted for **pitch, opponent, and format**.")

# ------------------------------
# Main Run
# ------------------------------
if do_go:

    # Basic validations
    if not venue.strip() or not opponent.strip():
        st.error("Please provide both **Venue** and **Opposition Team**.")
        st.stop()

    bat_model, bowl_model, feats = load_models_for(format_type)
    df_master = load_master(format_type)
    pitch_df = load_pitch_types()
    bat_ctx, bowl_ctx = load_odi_context() if format_type == "ODI" else (pd.DataFrame(), pd.DataFrame())

    # Parse inputs
    input_names = [n.strip() for n in raw_players.split(",") if n.strip()]
    matched_norms, mapping = match_inputs_to_dataset(input_names, df_master)

    st.subheader(f"Matched {sum(mapping['matched_name'].notna())} / {len(input_names)} inputs.")
    st.dataframe(mapping, use_container_width=True)

    if not matched_norms:
        st.error("None of your players were found in the dataset.")
        st.stop()

    # Keep ONLY matched players
    df_sel = df_master[df_master["name_norm"].isin(matched_norms)].copy()
    if df_sel.empty:
        st.error("None of your players matched after normalization.")
        st.stop()

    # Role detection per format
    df_sel["Role"] = df_sel.apply(lambda r: detect_role_by_format(r, format_type), axis=1)

    # Build feature matrices
    X_bat = features_matrix(df_sel, feats.get("batting", []))
    X_bwl = features_matrix(df_sel, feats.get("bowling", []))

    # Predictions (arrays have same length as df_sel)
    pred_runs = safe_predict(bat_model, X_bat)
    pred_wkts = safe_predict(bowl_model, X_bwl)

    # Attach predictions
    df_sel["Predicted Runs"] = pred_runs
    df_sel["Predicted Wickets"] = np.maximum(0.0, pred_wkts)  # clamp negatives to 0

    # Last-10 (ODI) overrides (Runs/Wkts Shown) else 0 where none
    df_sel["Last10 Runs"] = 0.0
    df_sel["Last10 Wkts"] = 0.0
    if format_type == "ODI":
        for idx, row in df_sel.iterrows():
            l10r, l10w = last10_for_player_odi(row["name_norm"], bat_ctx, bowl_ctx)
            df_sel.at[idx, "Last10 Runs"] = l10r
            df_sel.at[idx, "Last10 Wkts"] = l10w

    # Final “shown” values
    # If last-10 available and > 0, use those; else predicted; else 0
    df_sel["Runs Shown"] = np.where(df_sel["Last10 Runs"] > 0, df_sel["Last10 Runs"], df_sel["Predicted Runs"])
    df_sel["Wkts Shown"] = np.where(df_sel["Last10 Wkts"] > 0, df_sel["Last10 Wkts"], df_sel["Predicted Wickets"])

    # Career totals (best-effort)
    df_sel["Career Runs"] = df_sel["runs_facade"].apply(to_num)
    df_sel["Career Wkts"] = df_sel["wkts_facade"].apply(to_num)

    # Context multipliers: pitch + opposition (ODI precise, others generic)
    df_sel["PitchFactor"] = df_sel["Role"].apply(lambda r: pitch_factor(venue, pitch_df, r))
    if format_type == "ODI":
        df_sel["OppFactor"] = df_sel["name_norm"].apply(lambda nm: opponent_factor_odi(nm, opponent, bat_ctx, bowl_ctx))
    else:
        # simple generic: mild factor
        df_sel["OppFactor"] = 1.0

    # Aggregate Score (you can tune weights)
    # Base from Shown metrics; apply context
    df_sel["Score"] = (df_sel["Runs Shown"] + 20.0 * df_sel["Wkts Shown"]) * df_sel["PitchFactor"] * df_sel["OppFactor"]

    # Balanced XI selection
    targets = {"WK": int(tgt_wk), "BAT": int(tgt_bat), "AR": int(tgt_ar), "BWL": int(tgt_bwl)}
    best_xi = build_balanced_xi(df_sel, targets)

    st.subheader(f"🏆 Best {format_type} XI for {venue} vs {opponent}")

    # Pretty role chip (no raw HTML in dataframe -> we’ll map to emoji text)
    role_emoji = {"BAT": "🏏 BAT", "BWL": "🎯 BOWL", "AR": "🧰 AR", "WK": "🧤 WK"}
    best_xi = best_xi.copy()
    best_xi["RoleChip"] = best_xi["Role"].map(role_emoji).fillna("")

    show_cols = [
        "display_name", "RoleChip",
        "Career Runs", "Career Wkts",
        "Runs Shown", "Wkts Shown",
        "PitchFactor", "OppFactor", "Score"
    ]
    st.dataframe(
        best_xi[show_cols].rename(columns={"display_name":"Player", "RoleChip":"Role"}),
        use_container_width=True
    )

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(best_xi, x="display_name", y="Runs Shown", color="Role", title="Runs (Last10 or Predicted)")
        fig1.update_layout(showlegend=True, xaxis_title="", yaxis_title="Runs")
        st.plotly_chart(fig1, config={"responsive": True})

    with c2:
        fig2 = px.bar(best_xi, x="display_name", y="Wkts Shown", color="Role", title="Wickets (Last10 or Predicted)")
        fig2.update_layout(showlegend=True, xaxis_title="", yaxis_title="Wickets")
        st.plotly_chart(fig2, config={"responsive": True})


    # Download
    st.download_button(
        "⬇️ Download Best XI CSV",
        best_xi[["display_name","Role","Career Runs","Career Wkts","Runs Shown","Wkts Shown","PitchFactor","OppFactor","Score"]]
        .rename(columns={"display_name":"Player"}).to_csv(index=False),
        file_name=f"best_{format_type.lower()}_xi.csv",
        mime="text/csv"
    )

    st.success("✅ Team generated using your inputs only, adjusted for **pitch**, **opposition**, and **format**.")



