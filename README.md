# 🌾 Kilimo-Smart Decision Engine

**Climate-informed crop recommendations and agricultural credit-risk support for Kenyan cooperatives and lenders — built so every number is labeled by how much it should actually be trusted.**

## What it does

Given a county and season, Kilimo-Smart recommends which crops a cooperative should plant, estimates yield/profit, and can generate a loan-risk assessment for a bank or SACCO — all explained in plain language, not just numbers.

## Why it's different

An earlier version of this system produced clean, confident-looking outputs that were mostly fabricated or hand-typed placeholders, with no way to tell. This version doesn't hide that — it shows a **confidence score on every result**, breaks down exactly which inputs are real vs. estimated vs. still placeholder, and refuses to let a rule-based score masquerade as machine learning or an unvalidated formula masquerade as a bank-grade credit model.

## Current state (honest snapshot)

| Layer | Status |
|---|---|
| Rainfall | Real, aggregated from TAHMO station data |
| Temperature | Real (NASA POWER) *once you run* `scripts/rebuild_climate_data.py` — synthetic fallback otherwise |
| Crop suitability scoring | Transparent rule-based engine, fully explainable — not a black box |
| Crop economics (cost/yield/price) | Still placeholder, pending KALRO/AMIS citation |
| Market prices | Still placeholder — no public API exists for Kenyan market data yet |
| Credit-risk formula | Still uncalibrated — needs a real lender's default history |

**Overall confidence today: ~40–50%**, and the app says so out loud instead of pretending otherwise.

## Quickstart

```bash
git clone https://github.com/CarsonSila/ClimaCrop-Intelligence.git
cd ClimaCrop-Intelligence && git checkout doinggbits_ingestion
pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"   # confirm everything passes
python scripts/rebuild_climate_data.py                 # optional but recommended: pulls real weather
streamlit run app.py
```

## What's next

1. Curate a real market price snapshot (AMIS/KACE) — no clean API exists, needs manual sourcing.
2. Source real per-crop cost/price data from KALRO; cross-check yields via FAOSTAT.
3. Calibrate the credit-risk formula with a real lender, or keep it advisory-only.
4. Move from rule-based scoring to real ML once genuine yield-outcome data exists.

*Future direction (not yet built): connecting farmers directly to traders, a bank-facing recommendation feed, youth agribusiness programs, and greenhouse/climate-adaptation advisory once this system has a multi-year track record.*

---
Full technical detail, architecture diagrams, and formulas: see the complete `README.md`.
