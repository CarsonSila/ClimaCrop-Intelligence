"""
src/ai_agent.py — ClimaCrop Intelligence AI Assistant
Powered by Google Gemini with an intelligent built-in Knowledge Engine fallback.
Provides real-time answers about:
- Crop recommendations and suitability for Kenyan counties
- Climate patterns, rainfall, dry spells
- Agricultural loan underwriting and credit risk
- Market prices and arbitrage across trading hubs
- General agronomic and agri-finance questions
"""

import os
import re
import streamlit as st

# Try importing Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

SYSTEM_PROMPT = """
You are KilimoBot, the AI agricultural advisory assistant for ClimaCrop Intelligence — Kenya's climate-smart agri-decision platform.

## What you know about ClimaCrop Intelligence:
- It covers **26 Kenyan counties** with 10 years (2015–2025) of localized climate data.
- Data comes from **116 TAHMO automatic weather stations** + **NASA POWER satellite reanalysis** + **FAOSTAT** + **KNBS** statistics.
- It tracks **40 Kenyan crops** across 5 categories: Cereals, Pulses, Roots & Tubers, Horticulture, and Cash Crops.
- Two advisory engines: **Agro-Ecological Rules (AEZ)** (transparent, explainable) and **Random Forest ML** (probabilistic).
- It has a **Bank & SACCO Credit Risk Portal** that calculates 70% CapEx loan sizes, risk-adjusted interest rates, and Debt Service Coverage Ratios.
- **5 major wholesale trading hubs** are analyzed for price arbitrage: Nairobi (Wakulima), Mombasa (Kongowea), Kisumu (Kibuye), Nakuru, and Eldoret.
- It tracks data provenance (MEASURED, OFFICIAL, ESTIMATED, MODELED, ASSUMED) for scientific integrity.

## Your role:
- Answer questions about Kenyan agriculture, climate, crops, farm economics, and credit in simple, clear language.
- Explain what the charts and numbers on the platform mean.
- Help farmers, cooperative managers, bank officers, and researchers understand the data.
- Give practical recommendations but always note when users should consult local agronomists or financial advisors for critical decisions.
- Use metric units (kg, mm, °C, KES).
- Be friendly, concise, and locally relevant to Kenya.

Always respond in clear English, using bullet points and short paragraphs. Use relevant emojis sparingly to aid readability.
"""


def get_api_key() -> str:
    """Retrieve Gemini API key from session state, environment, or Streamlit secrets."""
    # 1. User manual input in UI session state
    if "user_gemini_api_key" in st.session_state and st.session_state.user_gemini_api_key:
        return st.session_state.user_gemini_api_key.strip()
    # 2. Streamlit secrets (for Render/cloud deployment)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        pass
    # 3. Environment variable (local development)
    return os.environ.get("GEMINI_API_KEY", "").strip()


def build_context_message(county: str, season: str, engine_mode: str) -> str:
    """Inject current session context so the AI knows what the user is viewing."""
    return (
        f"[Session context: The user is currently viewing data for **{county} County**, "
        f"**{season}** season, using the **{engine_mode}** advisory engine.]"
    )


def init_chat_session(county: str, season: str, engine_mode: str, api_key: str = None):
    """Initialise or retrieve the Gemini chat session from Streamlit state."""
    if not GEMINI_AVAILABLE:
        return None

    key = api_key or get_api_key()
    if not key:
        return None

    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        context_msg = build_context_message(county, season, engine_mode)
        chat = model.start_chat(history=[
            {"role": "user", "parts": [context_msg]},
            {"role": "model", "parts": [
                f"Understood! I'm ready to assist with ClimaCrop Intelligence. "
                f"Current location: **{county} County** ({season}). How can I help you? 🌿"
            ]}
        ])
        return chat
    except Exception as e:
        return None


def generate_offline_response(query: str, county: str, season: str, engine, engine_mode: str) -> str:
    """
    Intelligent built-in fallback knowledge engine for ClimaCrop.
    Answers platform and agronomy questions directly using engine data when no API key is provided.
    """
    q = query.lower()

    # 1. Best crops / recommendations
    if any(k in q for k in ["best crop", "recommend", "what to plant", "suitable crop", "which crop", "grow"]):
        try:
            recs_df, profile, _ = engine.get_cooperative_recommendations(
                county=county, season=season, farm_size_acres=3.0, top_n=3,
                use_rule_based=(engine_mode.startswith("📐"))
            )
            if not recs_df.empty:
                top_crops = []
                for _, r in recs_df.iterrows():
                    top_crops.append(
                        f"- **{r['crop']}** ({r['category']}): {r['suitability_score']}% suitability, "
                        f"KES {r['total_farm_net_profit_kes']:,} expected net profit on 3 acres "
                        f"(Risk: {r['risk_level']})"
                    )
                crops_text = "\n".join(top_crops)
                return (
                    f"🌾 **Top Crop Recommendations for {county} County ({season}):**\n\n"
                    f"Based on the **{engine_mode}**, here are the highest-ranked crops:\n\n"
                    f"{crops_text}\n\n"
                    f"💡 *Expected seasonal rainfall in {county} is {profile['seasonal_rainfall_mm']} mm with a mean temp of {profile['temp_mean_c']}°C.*"
                )
        except Exception as e:
            pass

    # 2. Climate / Weather in current county
    if any(k in q for k in ["climate", "weather", "rainfall", "temperature", "rain", "dry spell", "drought"]):
        try:
            profile = engine.climate_engine.get_county_profile(county, season)
            return (
                f"🌧️ **Climate Profile for {county} County ({season}):**\n\n"
                f"- **Predicted Seasonal Rainfall:** `{profile['seasonal_rainfall_mm']} mm`\n"
                f"- **Mean Temperature:** `{profile['temp_mean_c']} °C` (Min: {profile['temp_min_c']}°C, Max: {profile['temp_max_c']}°C)\n"
                f"- **Max Dry Spell Risk:** `{profile['max_dry_spell_days']} consecutive rainless days`\n"
                f"- **Climate Zone:** `{profile['cluster_name']}` (Cluster #{profile['cluster_id']})\n\n"
                f"📊 *Data aggregated from 116 TAHMO ground weather stations and NASA POWER satellite reanalysis.*"
            )
        except Exception:
            pass

    # 3. Loan / Credit / DSCR / Underwriting
    if any(k in q for k in ["loan", "credit", "dscr", "interest", "underwrit", "sacco", "bank", "risk score"]):
        return (
            f"🏦 **Agricultural Credit Underwriting in ClimaCrop:**\n\n"
            f"- **70% CapEx Rule:** Banks and SACCOs fund up to 70% of total farm production costs; 30% is farmer equity.\n"
            f"- **DSCR (Debt Service Coverage Ratio):** Measures if farm net revenue covers loan repayments. A DSCR **≥ 1.2×** is considered healthy and creditworthy.\n"
            f"- **Risk-Weighted Interest Rate:** Starts at a 12.0% base rate and adds a risk premium (up to +6%) based on:\n"
            f"  1. 🌧️ Climate Stress (40% weight)\n"
            f"  2. 🌾 Crop Suitability Gap (35% weight)\n"
            f"  3. 📉 Market Price Volatility (25% weight)\n\n"
            f"💡 *You can test any loan facility under the **Bank & Credit Risk** tab.*"
        )

    # 4. Market / Prices / Arbitrage
    if any(k in q for k in ["market", "price", "arbitrage", "sell", "nairobi", "mombasa", "kisumu", "wakulima"]):
        return (
            f"💰 **Wholesale Market Arbitrage in Kenya:**\n\n"
            f"ClimaCrop tracks wholesale prices across 5 regional trading hubs:\n"
            f"- **Nairobi (Wakulima):** Largest consumer market, highest demand for vegetables & horticulture.\n"
            f"- **Mombasa (Kongowea):** Coastal hub with premium prices for pulses, cereals, and grains.\n"
            f"- **Kisumu (Kibuye):** Western hub serving the Lake Victoria basin.\n"
            f"- **Nakuru & Eldoret:** Grain basket regional wholesale centers.\n\n"
            f"🚚 *The platform automatically subtracts road transportation costs from {county} to each hub to calculate your **Net Realized Price**.*"
        )

    # 5. Engines (AEZ vs ML)
    if any(k in q for k in ["engine", "aez", "rule-based", "random forest", "machine learning", "model"]):
        return (
            f"🧠 **Advisory Engine Options in ClimaCrop:**\n\n"
            f"1. **📐 Agro-Ecological Rules (AEZ):**\n"
            f"   - Transparent, expert-calibrated agronomic boundaries from KALRO & FAO guidelines.\n"
            f"   - Calculates separate fit scores for rainfall, temperature, and drought tolerance.\n\n"
            f"2. **🤖 Random Forest ML Model:**\n"
            f"   - Probabilistic machine learning model trained on 10 years of multi-variable crop outcomes.\n"
            f"   - Captures non-linear climate interactions.\n\n"
            f"💡 *Switch between engines using the sidebar radio button to compare predictions!*"
        )

    # 6. TAHMO / Data Sources / Provenance
    if any(k in q for k in ["tahmo", "nasa", "faostat", "provenance", "source", "data"]):
        return (
            f"📡 **Data Sources & Provenance Architecture:**\n\n"
            f"- **TAHMO Network:** 116 automated weather stations across Kenya providing measured ground temperature, humidity, and rainfall.\n"
            f"- **NASA POWER:** Satellite reanalysis filling regional spatial gaps.\n"
            f"- **FAOSTAT & KNBS:** Baseline crop yields, production CapEx benchmarks, and historical output.\n"
            f"- **Data Provenance:** Every metric is audited and scored from `MEASURED` (100% confidence) to `ASSUMED` (20% confidence) for complete scientific integrity."
        )

    # General fallback
    return (
        f"🌿 **KilimoBot Assistant:**\n\n"
        f"You asked: *\"{query}\"*\n\n"
        f"Here are key things I can help you with regarding **{county} County** ({season}):\n"
        f"- 🌾 **Crop Recommendations:** Ask *'What are the best crops to plant?'*\n"
        f"- 🌧️ **Climate Trends:** Ask *'What is the rainfall and dry spell risk?'*\n"
        f"- 💰 **Market Arbitrage:** Ask *'Where should I sell my produce?'*\n"
        f"- 🏦 **Credit Underwriting:** Ask *'How is the loan risk score calculated?'*\n\n"
        f"*(Tip: You can also enter a free Gemini API Key above for full multi-turn conversational AI!)*"
    )


def ask_kiilimobot(chat_session, user_message: str) -> str:
    """Send a message to KilimoBot and return the response text."""
    if chat_session is None:
        return "⚠️ Chat session not initialized."

    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "401" in error_msg or "403" in error_msg:
            return "⚠️ API key issue. Please check that your Gemini API key is valid."
        elif "quota" in error_msg.lower() or "429" in error_msg:
            return "⚠️ Rate limit reached. Please wait a moment and try again."
        else:
            return f"⚠️ An error occurred: {error_msg}"
