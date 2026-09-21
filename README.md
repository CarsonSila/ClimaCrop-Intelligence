# 🌾ClimaCrop Intelligence (Kilimo-Smart)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B) ![scikit-learn](https://img.shields.io/badge/scikit--learn-models-F7931E) ![Tests](https://img.shields.io/badge/tests-27%20passing-brightgreen) ![License](https://img.shields.io/badge/License-MIT-green)

**Smarter crops. Fairer loans.** A climate and credit decision-support platform for Kenyan agriculture that turns 10 years of station-level weather data into a ranked planting plan for cooperatives and a single, plain risk score for banks.

Built for the Power Learn Project (PLP) Capstone 2026.

<!-- Live demo: add the link here once deployed (Render or Streamlit Cloud). -->

> **Honest-labelling notice.** Every number the app shows carries a provenance tag (measured, official, estimated, modeled or assumed) so you can see how far to trust it. Market prices and crop economics are a static, estimated snapshot, not a live feed. See [What's real vs. estimated](#whats-real-vs-estimated).

<!-- SCREENSHOTS: add 2-3 images to docs/images/ and uncomment.
![Cooperative advisory](docs/images/advisory.png)
![Bank and credit risk view](docs/images/bank-risk.png)
![Climate trends](docs/images/climate-trends.png)
-->

---

## The problem

Agriculture contributes over 33% of Kenya's GDP and employs about 70% of the rural population, yet climate, crop choice and credit decisions are made in isolation:

- **Farmers and cooperatives** mostly plant out of habit, without ten years of rain, heat and dry-spell data for their land.
- **Banks and Agri-SACCOs** price loans on instinct, with no single honest view of climate risk, crop fit and market swings.
- **Researchers and policy makers** have station-level weather data across 35 counties that sits unused.

## What it does

The app answers a different question for each audience, from the same underlying engines:

| Audience | Question answered |
|---|---|
| Cooperatives | What should our members plant this season, what yield and profit per acre can we expect, and which market pays the most? |
| Banks and SACCOs | What is the climate and crop risk of financing this farmer, what loan can they get, and at what risk-adjusted rate? |
| Researchers | How do 10 years of rainfall and temperature data compare between a transparent rule-based model and a machine-learning model? |

## Key facts

| Item | Value |
|---|---|
| Weather stations | 116 TAHMO stations mapped to counties |
| Counties in the data | 35 (26 selectable in the current UI) |
| Climate history | 10 years, 559 county-season rows (Long Rains and Short Rains) |
| Crops modelled | 40 across 5 commercial classes |
| Markets compared | 5 (Nairobi, Nakuru, Eldoret, Kisumu, Mombasa), 200 price rows |
| User roles | 4 (Cooperative, Bank/SACCO Officer, Researcher, Admin) |
| Automated tests | 27 passing |

## Architecture

```
[TAHMO station data]  [40-crop catalog]  [5-market prices]
        \                   |                  /
         +------ Data layer, every value carries a provenance tag ------+
                                   |
        +--------------------------+---------------------------+
        v                          v                           v
[Climate pattern           [Crop suitability            [Market arbitrage
 clustering (K-Means)]      rule-based (default)         and price comparison]
                            or Random Forest (legacy)]
        +--------------------------+---------------------------+
                                   v
              [Financial decision engine: cooperative sizing,
               composite risk index, loan pricing, portfolio stress test]
                                   |
                                   v
        [Role-aware Streamlit app + KilimoBot assistant]
```

| Layer | Technology |
|---|---|
| App | Streamlit, Plotly |
| Analytics and ML | Pandas, NumPy, scikit-learn (K-Means, Random Forest), joblib |
| Assistant | KilimoBot: Google Gemini with an offline rule-based fallback |
| Auth | Role-based access, JSON-backed user store |
| Deployment | Docker (Render-compatible `$PORT`) |

## How recommendations and risk scores are built

**Crop suitability.** The default engine is **rule-based**: it scores each crop against transparent agro-ecological rain and temperature bands, with no synthetic training data. A Random Forest mode is kept for side-by-side comparison only, because it is trained on samples generated from the same thresholds it is later scored against (a circularity), so its output is always tagged `MODELED`.

**Composite agricultural risk index:**

```
R_agri = 0.40 x R_climate + 0.35 x (1 - CropFit / 100) + 0.25 x MarketVolatility
```

**Loan sizing and pricing** (in `src/financial_engine.py`):

```
Eligible facility   = 70% x production cost per acre x acres
Interest rate       = 12% base + (R_agri x 8%)
Default probability = min(35%, max(3%, R_agri x 24%))
```

The Bank tab also reports a Debt Service Coverage Ratio per loan and runs a portfolio stress test across borrowers, crops and counties.

## Data provenance

Every reported value can carry one of five tags, each with a confidence weight:

| Tag | Meaning | Weight |
|---|---|---|
| `MEASURED` | Directly observed, such as a station reading | 1.00 |
| `OFFICIAL` | From an official published source | 0.90 |
| `ESTIMATED` | Estimated by a documented method | 0.65 |
| `MODELED` | Output of a model | 0.50 |
| `ASSUMED` | Unverified placeholder | 0.20 |

A `ProvenanceReport` combines the tags behind a result into an overall confidence, and the app turns it into a plain-language caveat next to the numbers. Treat any output with low confidence as a starting point for discussion, not a lending or planting decision.

## Roles and demo accounts

| Role | Username | Password | Default view |
|---|---|---|---|
| Cooperative Member | `coop_user` | `kilimo2025` | Cooperative Advisory |
| Bank/SACCO Officer | `bank_officer` | `sacco2025` | Bank and Credit Risk |
| Researcher | `researcher` | `tahmo2025` | Climate Trends |
| Admin | `admin` | `admin2025` | All views |

New accounts can self-register in the app. **These are demo credentials only.** Passwords are hashed with SHA-256 and one application-wide salt, which is fine for a capstone demo but not for real user data (see [Known limitations](#known-limitations)).

## Quick start

```bash
git clone https://github.com/CarsonSila/ClimaCrop-Intelligence.git
cd ClimaCrop-Intelligence

python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

Open http://localhost:8501 and sign in with a demo account above.

**Optional: enable Gemini for KilimoBot.** KilimoBot works without any key, using its offline knowledge engine. For Gemini answers, set `GEMINI_API_KEY` as an environment variable or in `.streamlit/secrets.toml`. Never commit the key.

**Optional: retrain the models** after changing the CSVs in `data/`:
```bash
python train_models.py
```

**Docker:**
```bash
docker build -t climacrop-intelligence .
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key-here" climacrop-intelligence
```

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

27 tests cover roles and login, registration, invalid credentials, data integrity (40 crops, 200 market rows) and end-to-end engine outputs.

## What's real vs. estimated

- **Real:** the role-based access, all three analytics engines, the provenance system, the financial and risk calculations, and the automated tests.
- **Static or estimated:** market prices are a manually refreshed snapshot, and crop economics are baselines informed by KNBS and FAO figures, each row carrying a source and confidence value.
- **Modeled:** the legacy Random Forest suitability output.
- **Built but not switched on:** live data clients for TAHMO, NASA POWER and FAOSTAT exist in `src/data_sources/` but are not wired into the app, and the yield-outcome model refuses to train until real multi-year yield records are supplied.

## Known limitations

- The legacy Random Forest suitability model is circular, so treat it as a sanity check only.
- Market prices are a static snapshot, not a live feed.
- Authentication is demo-grade: one hardcoded salt, SHA-256 instead of bcrypt or argon2, and demo passwords in source.
- The UI offers 26 counties, while the dataset covers 35.
- `YieldOutcomeModel` is not used by the app yet.

## Repository layout

```
app.py                Streamlit app: login, role-aware tabs, all views
train_models.py       Trains and saves the models to models/
data/                 Climate, crop, market and station CSVs
models/               Trained models (joblib)
src/                  Auth, engines, provenance, KilimoBot, live-data clients
tests/                Unit and pipeline tests
Dockerfile            Container build
```

## Roadmap

1. **Pilot:** partner with one cooperative and one bank or SACCO for a full growing season, connect live weather feeds for the pilot area, run real recommendations and loan decisions together, then measure what farmers planted and what banks saw in defaults.
2. Replace the static price snapshot with real market data (KAMIS ingestion is in development).
3. Train the yield-outcome model once real multi-year yield records are available.
4. Expose all 35 counties in the UI and move authentication to bcrypt or argon2.
5. Longer term: crop export advice, and greenhouse and other climate solutions once there are 5+ years of system data behind the need.

## Team

Carson Sila, Charlene Kamunyu, Brian Mugambi, Emmanuel Brian

## License

MIT. See [LICENSE](LICENSE).
