# 🌾 ClimaCrop Intelligence: Climate-Smart Decision Support & Agri-Fintech De-Risking Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.0-orange.svg)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Bridging localized 10-year climate patterns, a 40-crop suitability matrix, and institutional credit underwriting for Kenyan agriculture — with role-based access and transparent data provenance.**

---

## 📌 1. Project Overview & Problem Statement

Smallholder agriculture accounts for over 33% of Kenya's GDP and employs 70% of the rural population. Climate volatility — shifting seasonal rain onsets, extended dry spells, and rising temperatures — has made traditional farming calendars unreliable.

Traditional weather apps only answer: *"Will it rain tomorrow?"*

**ClimaCrop Intelligence** is a role-based Streamlit application built to answer:

1. **For Agricultural Cooperatives:** *"Given local climate trends, what should our members plant this season, what yield and profit per acre can we expect, and which regional wholesale market pays the most?"*
2. **For Banks & Agri-SACCOs:** *"What is the composite climate and agricultural risk of financing a farmer or cooperative, what loan facility are they eligible for, and what is the risk-adjusted interest rate and expected default probability?"*
3. **For Researchers:** *"How do 10 years of station-level rainfall and temperature data compare against a transparent rule-based advisory model versus a probabilistic ML model?"*

The system logs in users under one of **four roles** (Cooperative Member, Bank/SACCO Credit Officer, Researcher, Admin), each landing on a tailored view of the same underlying engines, and every derived number carries a **provenance tag** (measured / official / estimated / modeled / assumed) so users know how much to trust it.

---

## 🏗️ 2. End-to-End System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          0. AUTH & ROLE-BASED ACCESS (src/auth.py)                       │
│  • 4 personas: Cooperative · Bank/SACCO Officer · Researcher · Admin                     │
│  • SHA-256 salted password hashing, JSON-backed user store (data/users.json)             │
│  • Each role sees a different subset of tabs and a personalized landing view             │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               1. DATA INGESTION LAYER                                    │
│  • 116 TAHMO weather stations mapped to 35 Kenyan counties (10-yr seasonal aggregates)   │
│  • Optional live pullers for TAHMO, NASA POWER, FAOSTAT (src/data_sources/)              │
│  • 40-crop agronomic & economics matrix (KNBS/FAO-informed baselines)                    │
│  • 5-market regional pricing database (Nairobi, Nakuru, Eldoret, Kisumu, Mombasa)        │
│  • Every ingested/derived value wrapped in a Provenance tag (src/provenance.py)          │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          2. ADVISORY & ANALYTICS ENGINES                                 │
│  ┌────────────────────┐  ┌─────────────────────────────┐  ┌───────────────────────────┐ │
│  │ Climate Pattern    │  │  Crop Suitability (2 modes)  │  │   Market Arbitrage &      │ │
│  │ Clustering         │  │  📐 Rule-based AEZ (default,  │  │   Price Forecaster        │ │
│  │ (K-Means, k=3)     │─▶│     transparent, no synthetic │─▶│  • Transport-adjusted     │ │
│  │ • 559 county-       │  │     training data)            │  │    net margin ranking    │ │
│  │   seasons          │  │  🤖 Random Forest (legacy,     │  │  • 5-hub price comparison │ │
│  │ • Normal/Flood/Dry │  │     synthetic-trained, audit-  │  │                           │ │
│  └────────────────────┘  │     only, tagged MODELED)      │  └───────────────────────────┘ │
│                           └─────────────────────────────┘                                │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          3. FINTECH & DECISION LOGIC (src/financial_engine.py)            │
│  • Cooperative Sizing: Total CapEx, Net Farm Profit, Benefit-Cost Ratio (BCR)             │
│  • Composite Risk Underwriting: R_agri = 0.40(Climate) + 0.35(1 - CropFit) + 0.25(Market) │
│  • Facility Sizing: 70% CapEx Loan @ [Base Rate (12%) + Risk Premium (up to 8%)]          │
│  • Portfolio Simulator: weighted yield, expected default rate, portfolio net ROI          │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        4. ROLE-AWARE STREAMLIT APP (app.py)                              │
│   🌱 Cooperative Advisory   🏦 Bank & Credit Risk   🌍 Climate Trends                    │
│   📊 Crop & Market Catalog   🤖 KilimoBot AI Assistant (Gemini + offline fallback)       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

**Note on the two suitability engines:** `FinancialDecisionEngine` defaults to `suitability_mode="rule_based"` (the `RuleBasedSuitabilityEngine`), because the Random Forest classifier is trained on synthetic samples generated from the same agronomic thresholds it's scored against — a circularity that makes it unsuitable as the primary source of truth. The ML mode is kept for side-by-side comparison and every output produced under it is tagged `Provenance.MODELED` with an explanatory caveat. The Streamlit sidebar lets any user toggle between the two ("📐 Agro-Ecological Rules" vs "🤖 Machine Learning").

---

## 👥 3. Roles & Access

| Role | Username (demo) | Default view | Can do |
|---|---|---|---|
| 🌱 Cooperative Member | `coop_user` | Cooperative Advisory | Crop recommendations, farm profit calculator, market arbitrage |
| 🏦 Bank/SACCO Officer | `bank_officer` | Bank & Credit Risk | Loan underwriting, DSCR, portfolio stress testing |
| 🌍 Researcher | `researcher` | Climate Trends | 10-yr climate trends, rule-based vs ML benchmarking, read-only Cooperative view |
| 👑 Admin | `admin` | Cooperative Advisory | All tabs, all four persona views |

Demo credentials are seeded in `src/auth.py` (`DEFAULT_USERS`) and persisted to `data/users.json` on first run. New accounts can self-register through the app.

> ⚠️ **Security note:** passwords are hashed with SHA-256 and a single hardcoded application-wide salt (`SALT` in `src/auth.py`), not a per-user salt or a slow hash like bcrypt/argon2, and the demo passwords are visible in source. This is adequate for a demo/capstone deployment but **should not be used as-is for real user credentials in production**.

---

## 📊 4. The 40-Crop Kenyan Agronomic & Financial Catalog

`data/crops_database.csv` evaluates **40 crops** across 5 commercial classes, each row carrying `min/max_rain_mm`, `min/max_temp_c`, `growth_days`, `drought_tolerance`, `cost_per_acre_kes`, `yield_per_acre_kg`, `base_price_kes_per_kg`, and a `source`/`confidence` provenance pair:

| Category | Crops Included |
| --- | --- |
| **1. Cereals (6)** | Maize, Sorghum, Finger Millet, Pearl Millet, Wheat, Rice |
| **2. Pulses / Legumes (6)** | Common Beans, Cowpeas (Kunde), Green Grams (Ndengu), Pigeon Peas, Soybeans, Groundnuts |
| **3. Roots & Tubers (4)** | Irish Potatoes, Sweet Potatoes, Cassava, Arrowroots (Nduma) |
| **4. Horticulture (12)** | Tomatoes, Bulb Onions, Cabbage, Kales (Sukuma Wiki), Spinach, Capsicum (Hoho), French Beans, Carrots, Watermelon, Butternut Squash, Pumpkin, Garden Peas |
| **5. Cash & Tree Crops (12)** | Coffee (Arabica), Tea, Sugarcane, Avocado (Hass), Mangoes, Bananas, Macadamia, Cotton, Pyrethrum, Cashew Nuts, Passion Fruit, Miraa (Khat) |

A companion file, `data/crops_database_without_provenance.csv`, holds the same matrix stripped of its source/confidence columns for lightweight consumers that don't need provenance metadata.

---

## 🌍 5. Climate & Market Data

- `data/stations_with_counties.csv` — 116 TAHMO station records (id, name, lat/lon, elevation, install date) mapped to Kenyan counties.
- `data/county_climate_historical.csv` — 559 county-season rows across **35 counties**, with `seasonal_rainfall_mm`, `rainy_days`, `heavy_rain_days`, `max_dry_spell_days`, `onset_week`, `temp_mean/max/min_c`, `elevation_m`, and a `drought_risk_index`, for the two Kenyan rainfall seasons (Long Rains MAM, Short Rains OND).
- `data/market_prices.csv` — 200 rows (40 crops × 5 markets: Nairobi/Wakulima, Nakuru, Eldoret, Kisumu/Jubilee, Mombasa/Kongowea) with `base_price`, `market_price`, `peak_harvest_price`, `off_season_price`, and `volatility_cv`.

> ℹ️ **Counties: 35 in the data, 26 exposed in the UI.** The historical dataset covers 35 counties, but the Streamlit sidebar's county selector (`app.py`) currently offers a curated list of 26. If you need the remaining counties available in the UI, extend `counties_list` in `app.py`.

**Live data pulls (optional):** `src/data_sources/` contains thin, credential-gated clients for refreshing data from source rather than relying on the static CSVs:
- `tahmo_ingest.py` — TAHMO DataHub API (requires `TAHMO_API_KEY` / `TAHMO_API_SECRET`; TAHMO access is by request, not public self-serve).
- `nasa_power_ingest.py` — NASA POWER satellite reanalysis (no key required) for a fixed set of county centroids.
- `faostat_ingest.py` — FAOSTAT crop yield API for Kenya.
- `market_prices_ingest.py` — loads a manually curated price snapshot CSV and **deliberately refuses to run** (raises `SnapshotNotFound`) if no real snapshot is supplied, rather than silently synthesizing prices.

These ingestion modules are not wired into `app.py` at runtime — they exist to regenerate/refresh the CSVs in `data/` on demand, and are the intended path to replacing the static/estimated data with sourced data over time.

---

## 🧭 6. Data Provenance Model

Every value the system reports (a rainfall figure, a suitability score, a loan interest rate) can be wrapped as a `SourcedValue` (`src/provenance.py`) with a `Provenance` tag:

| Tag | Meaning | Confidence weight |
| --- | --- | --- |
| `MEASURED` | Directly observed (e.g. a station reading) | 1.00 |
| `OFFICIAL` | From an official published source | 0.90 |
| `ESTIMATED` | Estimated via a documented method | 0.65 |
| `MODELED` | Output of a model (e.g. the legacy ML classifier) | 0.50 |
| `ASSUMED` | Unverified placeholder | 0.20 |

A `ProvenanceReport` aggregates the `SourcedValue`s behind a given result and exposes an `overall_confidence`, which `src/humanize.py` turns into a plain-language caveat (e.g. *"This is mostly guesswork right now — good for exploring ideas, not for making a real planting or lending decision yet."*) shown to the user alongside the numbers. This is the system's main defense against numbers looking more authoritative than the underlying data supports — check it before treating an output as decision-grade.

There is also a forward-looking `src/ml_pipeline_ready.py` (`YieldOutcomeModel`, a Gradient Boosting regressor) that intentionally **refuses to train** unless given real observed yield outcomes across at least 3 distinct years — it will not fit on synthetic or estimated data. It is not yet wired into the app; it's scaffolding for when real KALRO/census/farmer-reported yield data becomes available.

---

## 💰 7. Fintech Underwriting & Risk Formulas

Implemented in `src/financial_engine.py` (`FinancialDecisionEngine.underwrite_agricultural_loan` / `simulate_loan_portfolio`).

### A. Composite Agricultural Risk Index ($R_{\text{agri}}$)

$$R_{\text{agri}} = 0.40 \cdot R_{\text{climate}} + 0.35 \cdot \left(1 - \frac{S_c}{100}\right) + 0.25 \cdot V_{\text{market}}$$

*where $R_{\text{climate}}$ is derived from rainfall anomaly and dry spell length, $S_c$ is the crop suitability score (0–100, from whichever suitability engine is active), and $V_{\text{market}}$ is price volatility (coefficient of variation).*

### B. Loan Facility Sizing & Risk-Adjusted Pricing

$$\text{Eligible Facility} = 0.70 \times \text{Production Cost per Acre} \times \text{Acres}$$

$$\text{Interest Rate} = 12.0\% + \left(R_{\text{agri}} \times 8.0\%\right)$$

$$\text{Expected Default Probability} = \min\left(35\%, \max\left(3\%, R_{\text{agri}} \times 24\%\right)\right)$$

The Bank & Credit Risk tab also computes a **Debt Service Coverage Ratio (DSCR)** per loan and supports a **portfolio stress test** across multiple borrowers/crops/counties at once, returning weighted expected yield, blended default probability, and portfolio-level net ROI.

---

## 🤖 8. KilimoBot AI Assistant

`src/ai_agent.py` implements **KilimoBot**, the chat assistant surfaced in the "KilimoBot AI Assistant" tab, available to every role.

- **Primary path:** Google Gemini (`google-generativeai` SDK), seeded with a system prompt that describes the platform's data (116 stations, 35 counties, 40 crops, 5 markets, provenance tags) so answers stay grounded in what the system actually contains.
- **Offline fallback (`generate_offline_response`):** if no Gemini API key is configured or the SDK isn't installed, KilimoBot answers from a built-in rule/keyword-based knowledge engine instead of failing — so the assistant tab still works without any external API key, with reduced conversational range.
- **API key resolution order** (`get_api_key`): (1) a key entered directly in the UI for the session, (2) `st.secrets["GEMINI_API_KEY"]` (for Streamlit Cloud / Render deployments), (3) the `GEMINI_API_KEY` environment variable (for local development).

---

## 🛠️ 9. Project Structure

```
ClimaCrop-Intelligence/
│
├── app.py                              # Streamlit frontend: auth gate, role-aware tab navigation, all 5 views
├── train_models.py                     # Trains & persists the 3 core ML/clustering models to models/
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Container build (python:3.11-slim, Streamlit on $PORT)
├── README.md                           # System documentation & architecture (this file)
│
├── .streamlit/                         # Streamlit configuration (theme, server settings)
│
├── data/
│   ├── county_climate_historical.csv   # 559 rows, 35 counties x 2 seasons, 10-yr aggregates
│   ├── crops_database.csv              # 40-crop agronomic & financial benchmark, with provenance
│   ├── crops_database_without_provenance.csv  # Same matrix, provenance columns stripped
│   ├── market_prices.csv               # 200 rows: 40 crops x 5 markets
│   ├── stations_with_counties.csv      # 116 TAHMO stations with GPS + county mapping
│   └── users.json                      # Auto-created on first run; persisted user accounts (git-ignored)
│
├── models/                             # Trained, serialized models (joblib)
│   ├── climate_pattern_engine.joblib
│   ├── crop_suitability_engine.joblib  # Legacy Random Forest (audit/comparison only)
│   └── market_arbitrage_engine.joblib
│
├── src/
│   ├── auth.py                         # RBAC: 4 roles, salted-hash auth, registration, JSON user store
│   ├── ai_agent.py                     # KilimoBot: Gemini-backed chat + offline knowledge-engine fallback
│   ├── data_processing.py              # Station→county mapping, crop/market DB construction, TAHMO aggregation
│   ├── ml_models.py                    # ClimatePatternEngine (K-Means), CropSuitabilityEngine (Random Forest, legacy), MarketArbitrageEngine
│   ├── rule_based_suitability.py       # RuleBasedSuitabilityEngine — the default, transparent AEZ-band scorer
│   ├── ml_pipeline_ready.py            # YieldOutcomeModel — gradient-boosted model gated on real outcome data (not yet wired into app.py)
│   ├── financial_engine.py             # FinancialDecisionEngine: orchestrates engines into cooperative/bank decisions
│   ├── provenance.py                   # Provenance enum, SourcedValue, ProvenanceReport
│   ├── humanize.py                     # Turns scores/confidence/loan decisions into plain-language summaries
│   └── data_sources/                   # Optional live-data clients (TAHMO, NASA POWER, FAOSTAT, market snapshot loader)
│       ├── tahmo_ingest.py
│       ├── nasa_power_ingest.py
│       ├── faostat_ingest.py
│       └── market_prices_ingest.py
│
└── tests/
    ├── test_auth.py                    # Roles, demo-account login, registration, invalid-credential handling
    └── test_pipeline.py                # Data integrity (40 crops, 200 market rows) + end-to-end engine outputs
```

---

## 🚀 10. Installation & Quickstart

### Prerequisites

- Python 3.10 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/CarsonSila/ClimaCrop-Intelligence.git
cd ClimaCrop-Intelligence
```

### 2. Set Up a Virtual Environment & Install Dependencies

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. (Optional) Configure the AI Assistant

KilimoBot works out of the box using its offline knowledge engine. To enable Gemini-backed responses, set an environment variable or Streamlit secret:

```bash
export GEMINI_API_KEY="your-key-here"          # macOS/Linux
setx GEMINI_API_KEY "your-key-here"             # Windows
```

or add it to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key-here"
```

### 4. (Optional) Retrain the Models

Pretrained models already ship in `models/`. Retrain them from the CSVs in `data/` if you change the underlying data:

```bash
python train_models.py
```

### 5. Run Automated Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 6. Launch the Interactive Dashboard

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` and sign in with a demo account:

| Role | Username | Password |
| --- | --- | --- |
| Cooperative | `coop_user` | `kilimo2025` |
| Bank/SACCO Officer | `bank_officer` | `sacco2025` |
| Researcher | `researcher` | `tahmo2025` |
| Admin | `admin` | `admin2025` |

### 7. Docker (Optional)

```bash
docker build -t climacrop-intelligence .
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key-here" climacrop-intelligence
```

The container reads `$PORT` (defaults to 8501), which matches Render's convention as well as local Docker use.

---

## ⚠️ 11. Known Limitations

- **Legacy ML suitability model is circular.** `CropSuitabilityEngine` (Random Forest) is trained on synthetic samples generated from the same rain/temperature bands it's later scored against, so treat its output as a sanity check against the rule-based engine, not an independent signal. This is why `rule_based` is the default `suitability_mode`.
- **Market prices are a static snapshot**, not a live feed; `data/market_prices.csv` needs to be refreshed manually (or via `market_prices_ingest.py` against a real AMIS/KACE/RATIN source) to stay current.
- **Auth is demo-grade.** Single hardcoded salt, SHA-256 (not bcrypt/argon2), and plaintext demo credentials in source — fine for a capstone/demo, not for production user data.
- **UI county list (26) is narrower than the dataset (35 counties).**
- **`YieldOutcomeModel` (src/ml_pipeline_ready.py) is not yet used by the app** — it's a real-data-only model waiting on actual multi-year yield outcome records.

---

## 👥 12. Authors & Capstone Team

- **Carson Sila** & Project Team
- *Capstone Project: Climate-Smart Agricultural Decision Support & Agri-Fintech De-Risking Platform*
