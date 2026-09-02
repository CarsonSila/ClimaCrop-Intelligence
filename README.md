# 🌾 ClimaCrop Intelligence: Climate-Smart Decision Support & Agri-Fintech De-Risking Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Bridging the gap between 10-year localized climate patterns, optimal 40-crop selection, and institutional credit underwriting for Kenyan agriculture.**

---

## 📌 1. Project Overview & Problem Statement

Smallholder agriculture accounts for over 33% of Kenya's GDP and employs 70% of the rural population. However, climate volatility—characterized by shifting seasonal rain onsets, extended dry spells, and rising temperatures (+0.08°C/year)—has rendered traditional farming calendars obsolete.

Traditional weather apps only answer: *"Will it rain tomorrow?"*

**ClimaCrop Intelligence** answers:
1. **For Agricultural Cooperatives:** *"Given the shifting 10-year climate trends, what should our members plant this season, what is the expected yield and profit per acre, and which regional wholesale market offers the highest net margin?"*
2. **For Banks & Agri-SACCOs:** *"What is the composite climate and agricultural risk of financing a farmer or cooperative, what loan facility is eligible, and what is the risk-adjusted interest rate and expected default probability?"*

---

## 🏗️ 2. End-to-End System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               1. DATA INGESTION LAYER                                   │
│  • 116 TAHMO Meteorological Stations across Kenya (10-Year 5-min Precipitation Series) │
│  • 40-Crop Benchmark Agronomic & Economics Matrix (KNBS & FAO agricultural baselines)  │
│  • 5-Market Regional Pricing Database (Nairobi, Nakuru, Eldoret, Kisumu, Mombasa)     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             2. ANALYTICS & ML ENGINES                                  │
│  ┌─────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐ │
│  │   Climate Pattern       │   │     40-Crop Suitability  │   │   Market Arbitrage   │ │
│  │   Clustering (K-Means)  │──▶│   Classifier (Random     │──▶│   & Price Forecaster │ │
│  │ • 559 County Seasons    │   │   Forest Model)          │   │ • Transport Matrix   │ │
│  │ • Normal / Flood / Dry  │   │ • Yield Scaling Formula  │   │ • Net Margin Ranks   │ │
│  └─────────────────────────┘   └──────────────────────────┘   └──────────────────────┘ │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             3. FINTECH & DECISION LOGIC                                │
│  • Cooperative Sizing: Total CapEx, Net Farm Profit, Benefit-Cost Ratio (BCR)          │
│  • Composite Risk Underwriting: R_agri = 0.40(Climate) + 0.35(CropFit) + 0.25(Market) │
│  • Facility Sizing: 70% CapEx Loan @ [Base Rate (12%) + Risk Premium (2% - 6%)]        │
│  • Portfolio Simulator: Weighted Yield, Default Probability, and Portfolio Net ROI     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              4. DUAL-VIEW STREAMLIT APP                                │
│         🌱 Agricultural Cooperative Hub      🏦 Bank & SACCO Underwriting Portal       │
│         🌍 10-Year Climate Intelligence      📊 40-Crop & Market Price Catalog         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. The 40-Crop Kenyan Agronomic & Financial Catalog

The system evaluates **40 major crops** categorized into 5 commercial classes:

| Category | Crops Included |
| :--- | :--- |
| **1. Cereals (6)** | Maize, Sorghum, Finger Millet, Pearl Millet, Wheat, Rice |
| **2. Pulses / Legumes (6)** | Common Beans, Cowpeas (Kunde), Green Grams (Ndengu), Pigeon Peas, Soybeans, Groundnuts |
| **3. Roots & Tubers (4)** | Irish Potatoes, Sweet Potatoes, Cassava, Arrowroots (Nduma) |
| **4. Horticulture (12)** | Tomatoes, Bulb Onions, Cabbage, Kales (Sukuma Wiki), Spinach, Capsicum (Hoho), French Beans, Carrots, Watermelon, Butternut Squash, Pumpkin, Garden Peas |
| **5. Cash & Tree Crops (12)** | Coffee (Arabica), Tea, Sugarcane, Avocado (Hass), Mangoes, Bananas, Macadamia, Cotton, Pyrethrum, Cashew Nuts, Passion Fruit, Miraa (Khat) |

---

## 💰 4. Fintech Underwriting & Risk Formulas

### A. Composite Agricultural Risk Index ($R_{\text{agri}}$)
$$R_{\text{agri}} = 0.40 \cdot R_{\text{climate}} + 0.35 \cdot \left(1 - \frac{S_c}{100}\right) + 0.25 \cdot V_{\text{market}}$$
*where $R_{\text{climate}}$ is derived from rainfall anomaly and dry spell length, $S_c$ is crop suitability probability, and $V_{\text{market}}$ is price volatility ($CV$).*

### B. Loan Facility Sizing & Risk-Adjusted Pricing
$$\text{Eligible Facility} = 0.70 \times \text{Production Cost per Acre} \times \text{Acres}$$
$$\text{Interest Rate} = 12.0\% + \left(R_{\text{agri}} \times 8.0\%\right)$$
$$\text{Expected Default Probability} = \min\left(35\%, \max\left(3\%, R_{\text{agri}} \times 24\%\right)\right)$$

---

## 🛠️ 5. Project Structure

```
ClimaCrop-Intelligence/
│
├── app.py                      # Interactive Web Frontend (Streamlit & Plotly)
├── train_models.py             # ML Training & Persistence Pipeline
├── requirements.txt            # Python Dependencies
├── README.md                   # System Documentation & Architecture
│
├── data/                       # Processed Clean Datasets
│   ├── county_climate_historical.csv  # 10-Year Seasonal Climate across 35 Counties
│   ├── crops_database.csv             # 40-Crop Agronomic & Financial Benchmark
│   ├── market_prices.csv              # 5-Market Wholesale Price Series (200 records)
│   └── stations_with_counties.csv     # 116 Weather Stations with GPS Coordinates
│
├── models/                     # Trained Serialized Machine Learning Models
│   ├── climate_pattern_engine.joblib
│   ├── crop_suitability_engine.joblib
│   └── market_arbitrage_engine.joblib
│
├── src/                        # Core Backend Logic
│   ├── data_processing.py      # Station Ingestion & Feature Engineering
│   ├── ml_models.py            # ML Estimators (Clustering, Random Forest, Arbitrage)
│   └── financial_engine.py     # Cooperative Profit & Bank Credit Underwriter
│
└── tests/                      # Automated Unit & Integration Test Suite
    └── test_pipeline.py
```

---

## 🚀 6. Installation & Quickstart

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/CarsonSila/ClimaCrop-Intelligence.git
cd ClimaCrop-Intelligence
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 4. Launch the Interactive Dashboard
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 👥 7. Authors & Capstone Team

- **Carson Sila** & Project Team
- *Capstone Project: Climate-Smart Agricultural Decision Support & Agri-Fintech De-Risking Platform*

