"""
ClimaCrop Intelligence: Kilimo-Smart Climate Decision Support & Agri-Fintech De-Risking Platform.
Features:
- Multi-Theme Engine (🌿 Emerald Light, 🌙 Cyber Forest Dark, ⚙️ Minimal Neutral)
- Embedded Smart Agro-Meteorology Imagery
- 14 Interactive Visualizations (Maps, Area/Line, Bubbles, Treemaps, Waterfalls, Gauges, Donut & Box plots)
- Real-Time Cooperative Advisory & Institutional Bank Underwriting
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.financial_engine import FinancialDecisionEngine

# ---------------------------------------------------------
# 1. PAGE CONFIG & PERSISTENT SESSION STATE
# ---------------------------------------------------------
st.set_page_config(
    page_title="ClimaCrop Intelligence | Kilimo-Smart Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. SIDEBAR CONTROLS & THEME SWITCHER
# ---------------------------------------------------------
st.sidebar.image(
    "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=600&auto=format&fit=crop&q=80",
    caption="Smart Agro-Meteorology & Analytics",
    use_container_width=True
)

st.sidebar.markdown("### 🎨 Interface Theme")
theme_mode = st.sidebar.radio(
    "Select Display Theme",
    ["🌿 Emerald Light", "🌙 Cyber Forest Dark", "⚙️ Minimal Modern"],
    index=0
)

# Define Theme Variables
if theme_mode == "🌙 Cyber Forest Dark":
    is_dark = True
    plotly_theme = "plotly_dark"
    bg_main = "#0b130e"
    card_bg = "#13231a"
    card_border = "#1f3b2d"
    text_main = "#e2fbe8"
    text_muted = "#86efac"
    primary_color = "#10b981"
    kpi_val_color = "#34d399"
    badge_low_bg = "#064e3b"
    badge_low_txt = "#a7f3d0"
    hero_grad = "linear-gradient(135deg, rgba(8, 28, 18, 0.95) 0%, rgba(19, 42, 31, 0.92) 60%, rgba(6, 78, 59, 0.90) 100%)"
elif theme_mode == "⚙️ Minimal Modern":
    is_dark = False
    plotly_theme = "plotly_white"
    bg_main = "#fafaf9"
    card_bg = "#ffffff"
    card_border = "#e7e5e4"
    text_main = "#1c1917"
    text_muted = "#57534e"
    primary_color = "#292524"
    kpi_val_color = "#1c1917"
    badge_low_bg = "#f5f5f4"
    badge_low_txt = "#292524"
    hero_grad = "linear-gradient(135deg, rgba(41, 37, 36, 0.95) 0%, rgba(68, 64, 60, 0.90) 100%)"
else: # Emerald Light (Default)
    is_dark = False
    plotly_theme = "plotly_white"
    bg_main = "#f4fbf7"
    card_bg = "#ffffff"
    card_border = "#d8f3dc"
    text_main = "#133a27"
    text_muted = "#40916c"
    primary_color = "#2d6a4f"
    kpi_val_color = "#1b4332"
    badge_low_bg = "#d8f3dc"
    badge_low_txt = "#1b4332"
    hero_grad = "linear-gradient(135deg, rgba(20, 58, 38, 0.92) 0%, rgba(45, 106, 79, 0.88) 60%, rgba(64, 145, 108, 0.85) 100%)"

# Dynamic CSS Injection
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {bg_main} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {text_main} !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {card_bg} !important;
        border-right: 1px solid {card_border} !important;
    }}
    
    /* Hero Banner */
    .hero-banner {{
        position: relative;
        background: {hero_grad},
                    url('https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=1400&auto=format&fit=crop&q=80') center/cover no-repeat;
        color: #ffffff !important;
        padding: 34px 36px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, {'0.4' if is_dark else '0.12'});
        border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    .hero-tag {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(216, 243, 220, 0.25);
        backdrop-filter: blur(8px);
        color: #d8f3dc;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        border: 1px solid rgba(216, 243, 220, 0.4);
    }}
    .hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        color: #ffffff !important;
    }}
    .hero-subtitle {{
        font-size: 1.02rem;
        color: #d8f3dc !important;
        font-weight: 400;
        max-width: 850px;
        line-height: 1.5;
    }}
    
    /* Metric KPI Cards */
    .kpi-card {{
        background: {card_bg};
        border-radius: 14px;
        padding: 18px 22px;
        border: 1px solid {card_border};
        border-left: 6px solid {primary_color};
        box-shadow: 0 4px 12px rgba(0, 0, 0, {'0.25' if is_dark else '0.04'});
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0, 0, 0, {'0.35' if is_dark else '0.08'});
    }}
    .kpi-label {{
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: {text_muted};
        font-weight: 700;
        margin-bottom: 4px;
    }}
    .kpi-val {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {kpi_val_color};
    }}
    .kpi-sub {{
        font-size: 0.82rem;
        color: {text_muted};
        font-weight: 600;
    }}
    
    /* Crop Recommendation Card */
    .crop-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, {'0.25' if is_dark else '0.04'});
        border-left: 6px solid {primary_color};
    }}
    .badge-pill-low {{
        background-color: {badge_low_bg};
        color: {badge_low_txt};
        padding: 6px 14px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    .badge-pill-mod {{
        background-color: {'#78350f' if is_dark else '#fef3c7'};
        color: {'#fde68a' if is_dark else '#92400e'};
        padding: 6px 14px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    .badge-pill-high {{
        background-color: {'#7f1d1d' if is_dark else '#fee2e2'};
        color: {'#fecaca' if is_dark else '#991b1b'};
        padding: 6px 14px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    
    /* Custom Streamlit Buttons */
    .stButton>button {{
        background-color: {primary_color} !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_engine():
    return FinancialDecisionEngine()


engine = load_engine()

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌾 Region & Planting Calendar")

counties_list = [
    "Nakuru", "Uasin Gishu", "Kiambu", "Nyeri", "Nyandarua", "Machakos", "Makueni", "Kitui",
    "Bungoma", "Kakamega", "Kisumu", "Siaya", "Migori", "Kisii", "Kericho", "Bomet",
    "Narok", "Embu", "Tharaka Nithi", "Kwale", "Kilifi", "Mombasa", "Taita Taveta", "West Pokot", "Turkana", "Laikipia"
]

selected_county = st.sidebar.selectbox("📍 Select County", counties_list, index=0)
selected_season = st.sidebar.selectbox("📅 Planting Season", ["Long Rains (MAM)", "Short Rains (OND)"], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Platform Persona Mode")
platform_view = st.sidebar.radio(
    "Active View",
    [
        "🌱 Agricultural Cooperative View",
        "🏦 Bank & SACCO Credit Risk Portal",
        "🌍 10-Year Climate Trend Intelligence",
        "📊 40-Crop & Market Price Catalog"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background-color: {card_bg}; padding: 14px 16px; border-radius: 12px; border: 1px solid {card_border};">
    <div style="font-size: 0.82rem; color: {text_muted}; font-weight: 700; margin-bottom: 4px;">
        📡 LIVE DATA STACK
    </div>
    <div style="font-size: 0.85rem; color: {text_main}; font-weight: 600;">
        • 116 TAHMO Ground Weather Stations<br>
        • 10-Year Time-Series (2015–2025)<br>
        • 40-Crop KNBS Production Model<br>
        • 5 Wholesale Arbitrage Hubs
    </div>
</div>
""", unsafe_allow_html=True)


# Top Hero Banner with Smart Agriculture Visual
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-tag">
        <span style="color: #4ade80;">●</span> 116 ACTIVE STATIONS • SEASONAL ADVISORY ENGINE
    </div>
    <div class="hero-title">KILIMO-SMART DECISION SUPPORT SYSTEM</div>
    <div class="hero-subtitle">
        Bridging 10 years of localized ground weather patterns with optimal 40-crop selection, member farm profitability, and institutional agricultural credit de-risking.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 1: COOPERATIVE ADVISORY & MARKET ARBITRAGE
# ---------------------------------------------------------
if platform_view == "🌱 Agricultural Cooperative View":
    st.subheader(f"🌱 Cooperative Advisory Hub: {selected_county} County — {selected_season}")
    st.markdown("Translating 10-year local weather station trends into optimal crop selection, farm revenue projections, and regional wholesale market arbitrage.")
    
    col_c1, col_c2, col_c3 = st.columns([1.2, 1.2, 1])
    with col_c1:
        farm_size = st.slider("Member Farm Size (Acres)", min_value=0.5, max_value=30.0, value=3.0, step=0.5)
    with col_c2:
        cat_filter = st.selectbox("Crop Category Filter", ["All", "Cereals", "Pulses", "Roots & Tubers", "Horticulture", "Cash Crops"])
    with col_c3:
        top_k = st.slider("Top Recommendations Count", min_value=3, max_value=10, value=4)

    recs_df, climate_profile = engine.get_cooperative_recommendations(
        county=selected_county,
        season=selected_season,
        farm_size_acres=farm_size,
        category_filter=cat_filter,
        top_n=top_k
    )
    
    # Climate Summary KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Predicted Rainfall</div>
            <div class="kpi-val">{climate_profile['seasonal_rainfall_mm']} mm</div>
            <div class="kpi-sub">{selected_season} Season</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Mean Temperature</div>
            <div class="kpi-val">{climate_profile['temp_mean_c']} °C</div>
            <div class="kpi-sub">Min: {climate_profile['temp_min_c']}°C | Max: {climate_profile['temp_max_c']}°C</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Max Dry Spell Risk</div>
            <div class="kpi-val">{climate_profile['max_dry_spell_days']} Days</div>
            <div class="kpi-sub">Consecutive Rain &lt; 2mm</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Climate Archetype</div>
            <div class="kpi-val" style="font-size:1.2rem;">{climate_profile['cluster_name']}</div>
            <div class="kpi-sub">K-Means Cluster #{climate_profile['cluster_id']}</div>
        </div>
        """, unsafe_allow_html=True)

    if not recs_df.empty:
        st.markdown("### 🏆 Top Recommended Crops for This Season")
        
        # Display Cards
        for idx, row in recs_df.iterrows():
            badge_class = "badge-pill-low" if row["risk_level"] == "Low" else ("badge-pill-mod" if row["risk_level"] == "Moderate" else "badge-pill-high")
            
            with st.container():
                st.markdown(f"""
                <div class="crop-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 1.35rem; font-weight: 800; color: {primary_color};">#{idx+1} {row['crop']}</span>
                            <span style="color: {text_muted}; margin-left: 10px; font-weight: 600;">({row['category']} • {row['growth_days']} days cycle)</span>
                        </div>
                        <div>
                            <span class="{badge_class}">Suitability: {row['suitability_score']}% ({row['risk_level']} Risk)</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Total Expected Yield", f"{row['total_farm_yield_kg']:,} kg", f"{row['expected_yield_kg_per_acre']:,} kg/acre")
                c2.metric("Total Production CapEx", f"KES {row['total_production_cost_kes']:,}", f"KES {row['cost_per_acre_kes']:,}/acre")
                c3.metric("Projected Gross Revenue", f"KES {row['total_farm_revenue_kes']:,}", f"KES {row['optimized_net_price_kes_per_kg']}/kg")
                c4.metric("Net Farm Profit", f"KES {row['total_farm_net_profit_kes']:,}", f"BCR: {row['benefit_cost_ratio']}x")
                c5.metric("Best Trading Market", row['best_target_market'], f"+KES {row['arbitrage_added_value_kes']:,} gain")
                
                st.markdown("---")

        # -----------------------------------------------------
        # VISUALIZATION 1: STRATEGIC BUBBLE CHART
        # -----------------------------------------------------
        st.markdown("### 🫧 1. Strategic Decision Frontier: Suitability vs. Profitability vs. Yield")
        st.caption("Bubble size represents expected total yield in kg. Higher & further right indicates optimal commercial choices.")
        
        fig_bubble = px.scatter(
            recs_df,
            x="suitability_score",
            y="total_farm_net_profit_kes",
            size="total_farm_yield_kg",
            color="risk_level",
            hover_name="crop",
            text="crop",
            color_discrete_map={"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"},
            labels={
                "suitability_score": "Crop Suitability Score (%)",
                "total_farm_net_profit_kes": "Net Farm Profit (KES)",
                "total_farm_yield_kg": "Total Yield (kg)",
                "risk_level": "Climate Risk"
            },
            title=f"Crop Suitability vs. Net Profit Frontier ({farm_size} Acres in {selected_county})"
        )
        fig_bubble.update_traces(textposition='top center', marker=dict(opacity=0.88, line=dict(width=1.5, color='#ffffff' if is_dark else '#1b4332')))
        fig_bubble.update_layout(height=450, template=plotly_theme)
        st.plotly_chart(fig_bubble, use_container_width=True)

        # -----------------------------------------------------
        # VISUALIZATION 2: FINANCIAL BREAKDOWN GROUPED BAR
        # -----------------------------------------------------
        col_v1, col_v2 = st.columns([1.1, 0.9])
        
        with col_v1:
            st.markdown("### 📊 2. Production CapEx vs. Gross Revenue vs. Net Profit")
            
            df_fin_melt = recs_df.melt(
                id_vars=["crop"],
                value_vars=["total_production_cost_kes", "total_farm_net_profit_kes", "total_farm_revenue_kes"],
                var_name="Metric",
                value_name="Amount_KES"
            )
            df_fin_melt["Metric"] = df_fin_melt["Metric"].map({
                "total_production_cost_kes": "Production CapEx",
                "total_farm_net_profit_kes": "Net Farm Profit",
                "total_farm_revenue_kes": "Gross Revenue"
            })
            
            fig_bar = px.bar(
                df_fin_melt,
                x="crop",
                y="Amount_KES",
                color="Metric",
                barmode="group",
                color_discrete_map={"Production CapEx": "#ef4444", "Net Farm Profit": "#10b981", "Gross Revenue": "#3b82f6"},
                title=f"Financial Payoff Comparison ({farm_size} Acres)",
                labels={"Amount_KES": "Amount (KES)", "crop": "Crop"}
            )
            fig_bar.update_layout(height=400, template=plotly_theme)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_v2:
            st.markdown("### 🌳 3. Profit Share by Agricultural Category (Treemap)")
            
            fig_tree = px.treemap(
                recs_df,
                path=["category", "crop"],
                values="total_farm_net_profit_kes",
                color="benefit_cost_ratio",
                color_continuous_scale="Greens",
                title="Category Profit Proportions & Benefit-Cost Ratio"
            )
            fig_tree.update_layout(height=400, template=plotly_theme)
            st.plotly_chart(fig_tree, use_container_width=True)

        # -----------------------------------------------------
        # VISUALIZATION 4: REGIONAL MARKET ARBITRAGE
        # -----------------------------------------------------
        st.markdown("### 💰 4. Cross-Market Arbitrage & Transport Net Price Comparison")
        st.caption("Net price after deducting transportation costs from origin county to regional wholesale trading hubs.")
        
        sample_crop_for_market = st.selectbox("Select Crop for Multi-Market Breakdown", recs_df["crop"].tolist(), index=0)
        market_opps = engine.market_engine.get_market_opportunities(sample_crop_for_market, origin_county=selected_county)
        
        if not market_opps.empty:
            fig_mkt = px.bar(
                market_opps,
                x="market",
                y="net_market_price_kes",
                color="arbitrage_margin_vs_base",
                text="net_market_price_kes",
                color_continuous_scale="Greens",
                title=f"Net Price per kg for {sample_crop_for_market} across Regional Markets (KES / kg)",
                labels={"net_market_price_kes": "Net Price (KES/kg)", "market": "Wholesale Market Hub", "arbitrage_margin_vs_base": "Arbitrage Margin (KES)"}
            )
            fig_mkt.update_traces(texttemplate='KES %{text:.1f}', textposition='outside')
            fig_mkt.update_layout(height=380, template=plotly_theme)
            st.plotly_chart(fig_mkt, use_container_width=True)


# ---------------------------------------------------------
# TAB 2: BANK & SACCO CREDIT RISK PORTAL
# ---------------------------------------------------------
elif platform_view == "🏦 Bank & SACCO Credit Risk Portal":
    st.subheader("🏦 Agricultural Credit Underwriting & Risk De-Risking Portal")
    st.markdown("Automating agricultural loan sizing (70% CapEx), calculating risk-weighted interest rates, and stress-testing climate defaults.")

    tab_single, tab_portfolio = st.tabs(["📝 Single Loan Underwriter", "💼 Multi-Borrower Portfolio Stress Test"])
    
    with tab_single:
        st.markdown("#### 🌾 Individual Farm Facility Assessment")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1:
            borrower_name = st.text_input("Borrower / SACCO Group", value="Nakuru Grain Growers Co-op")
        with col_b2:
            underwrite_crop = st.selectbox("Funded Crop", engine.crops_df["crop"].unique() if engine.crops_df is not None else ["Maize", "Sorghum", "Tomatoes"], index=0)
        with col_b3:
            loan_acres = st.number_input("Cultivated Acres", min_value=1.0, max_value=200.0, value=6.0, step=1.0)
        with col_b4:
            underwrite_county = st.selectbox("Farm Location County", counties_list, index=counties_list.index(selected_county))

        loan_res = engine.underwrite_agricultural_loan(
            county=underwrite_county,
            crop_name=underwrite_crop,
            acres=loan_acres,
            season=selected_season,
            borrower_name=borrower_name
        )

        st.markdown("---")
        
        # Credit Metrics Banner
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Credit Rating Grade", loan_res["credit_grade"], f"Risk Index: {loan_res['composite_risk_score']}")
        m2.metric("Eligible Loan Facility (70% CapEx)", f"KES {loan_res['loan_amount_kes']:,}", f"Total Cost: KES {loan_res['total_project_cost_kes']:,}")
        m3.metric("Risk-Adjusted Interest Rate", f"{loan_res['interest_rate_pct']:.2f}%", f"Base 12% + Risk Premium")
        m4.metric("Expected Default Probability", f"{loan_res['expected_default_rate_pct']:.2f}%", f"DSCR Buffer: {loan_res['debt_service_coverage_ratio']}x")

        # -----------------------------------------------------
        # VISUALIZATION 5: GAUGE & DONUT CHARTS
        # -----------------------------------------------------
        col_g1, col_g2 = st.columns([1, 1])
        
        with col_g1:
            st.markdown("#### 🧭 Composite Credit Risk Gauge ($R_{agri}$)")
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = loan_res["composite_risk_score"],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Risk Score: {loan_res['credit_grade']}", 'font': {'size': 18, 'color': text_main}},
                gauge = {
                    'axis': {'range': [0.0, 1.0], 'tickwidth': 1, 'tickcolor': primary_color},
                    'bar': {'color': "#10b981" if loan_res["composite_risk_score"] < 0.38 else ("#f59e0b" if loan_res["composite_risk_score"] < 0.58 else "#ef4444")},
                    'bgcolor': card_bg,
                    'borderwidth': 2,
                    'bordercolor': card_border,
                    'steps': [
                        {'range': [0.0, 0.25], 'color': '#064e3b' if is_dark else '#d8f3dc'},
                        {'range': [0.25, 0.40], 'color': '#065f46' if is_dark else '#b7e4c7'},
                        {'range': [0.40, 0.60], 'color': '#78350f' if is_dark else '#ffe8d6'},
                        {'range': [0.60, 1.0], 'color': '#7f1d1d' if is_dark else '#ffccd5'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.65
                    }
                }
            ))
            fig_gauge.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), template=plotly_theme)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_g2:
            st.markdown("#### 🔬 Risk Factor Decomposition (Donut Chart)")
            
            risk_breakdown = pd.DataFrame({
                "Component": ["Climate Stress (40%)", "Crop Fit Gap (35%)", "Market Price Volatility (25%)"],
                "Score": [loan_res["climate_risk_component"], loan_res["crop_suitability_component"], loan_res["market_volatility_component"]]
            })
            fig_donut = px.pie(
                risk_breakdown,
                values="Score",
                names="Component",
                hole=0.55,
                color_discrete_sequence=["#ef4444", "#10b981", "#3b82f6"],
                title="Underwriting Risk Drivers"
            )
            fig_donut.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), template=plotly_theme)
            st.plotly_chart(fig_donut, use_container_width=True)

        # -----------------------------------------------------
        # VISUALIZATION 6: WATERFALL FINANCING SIZING
        # -----------------------------------------------------
        st.markdown("#### 💧 Facility Sizing & Revenue Coverage Buffer (Waterfall)")
        
        fig_waterfall = go.Figure(go.Waterfall(
            name="Facility Coverage",
            orientation="v",
            measure=["relative", "relative", "total", "relative", "total"],
            x=["Farmer Equity (30%)", "Bank Loan Facility (70%)", "Total Project CapEx", "Net Farm Operating Margin", "Expected Gross Harvest"],
            textposition="outside",
            text=[
                f"KES {loan_res['total_project_cost_kes'] * 0.3:,.0f}",
                f"KES {loan_res['loan_amount_kes']:,}",
                f"KES {loan_res['total_project_cost_kes']:,}",
                f"KES {loan_res['expected_revenue_kes'] - loan_res['total_project_cost_kes']:,}",
                f"KES {loan_res['expected_revenue_kes']:,}"
            ],
            y=[
                loan_res['total_project_cost_kes'] * 0.3,
                loan_res['loan_amount_kes'],
                0,
                loan_res['expected_revenue_kes'] - loan_res['total_project_cost_kes'],
                0
            ],
            connector={"line": {"color": "#10b981" if is_dark else "#40916c"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))
        fig_waterfall.update_layout(height=380, template=plotly_theme, title="Loan Facility Sizing vs. Harvest Revenue Coverage")
        st.plotly_chart(fig_waterfall, use_container_width=True)

        # Covenants & Mitigations
        st.markdown("#### 🛡️ Required Loan Covenants & Climate Mitigations")
        st.success(f"**Underwriting Decision:** {loan_res['recommendation']}")
        for m in loan_res["mitigation_strategies"]:
            st.markdown(f"- 🔒 **{m}**")

    # ---------------------------------------------------------
    # TAB 2.2: PORTFOLIO STRESS TESTING
    # ---------------------------------------------------------
    with tab_portfolio:
        st.markdown("#### 💼 Institutional Loan Portfolio Simulation (10 Sample Borrowers)")
        sample_portfolio = [
            {"borrower": "Molo Farmers Sacco", "county": "Nakuru", "crop": "Irish Potatoes", "acres": 8.0, "season": selected_season},
            {"borrower": "Uasin Gishu Grain Union", "county": "Uasin Gishu", "crop": "Maize", "acres": 20.0, "season": selected_season},
            {"borrower": "Makueni Green Grams Co-op", "county": "Makueni", "crop": "Green Grams (Ndengu)", "acres": 12.0, "season": selected_season},
            {"borrower": "Kitui Sorghum Group", "county": "Kitui", "crop": "Sorghum", "acres": 15.0, "season": selected_season},
            {"borrower": "Kiambu Horti Growers", "county": "Kiambu", "crop": "Tomatoes", "acres": 4.0, "season": selected_season},
            {"borrower": "Bungoma Sugar Farmers", "county": "Bungoma", "crop": "Sugarcane", "acres": 10.0, "season": selected_season},
            {"borrower": "Kwale Coast Cashew Group", "county": "Kwale", "crop": "Cashew Nuts", "acres": 15.0, "season": selected_season},
            {"borrower": "Nyeri Highlands Coffee Sacco", "county": "Nyeri", "crop": "Coffee (Arabica)", "acres": 6.0, "season": selected_season},
            {"borrower": "Kisumu Rice Irrigation Co-op", "county": "Kisumu", "crop": "Rice", "acres": 10.0, "season": selected_season},
            {"borrower": "Nyandarua Vegetable Growers", "county": "Nyandarua", "crop": "Cabbage", "acres": 5.0, "season": selected_season},
        ]
        
        port_summary, port_df = engine.simulate_loan_portfolio(sample_portfolio)
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("Total Portfolio Exposure", f"KES {port_summary['total_disbursed_kes']:,}", f"{port_summary['total_loans_count']} Active Loans")
        col_p2.metric("Weighted Interest Yield", f"{port_summary['weighted_average_interest_rate_pct']:.2f}%", "Risk-Weighted Yield")
        col_p3.metric("Expected Default Losses", f"KES {port_summary['expected_credit_losses_kes']:,}", f"{port_summary['weighted_expected_default_rate_pct']:.2f}% Default Rate")
        col_p4.metric("Net Projected Portfolio ROI", f"{port_summary['net_projected_roi_pct']:.2f}%", "After Expected Credit Loss")

        # -----------------------------------------------------
        # VISUALIZATION 7: PORTFOLIO RISK-RETURN BUBBLE SCATTER
        # -----------------------------------------------------
        st.markdown("### 🫧 7. Portfolio Risk vs. Return Matrix")
        st.caption("Bubble size indicates loan disbursement amount (KES). Color represents credit grade.")
        
        fig_port_scatter = px.scatter(
            port_df,
            x="expected_default_rate_pct",
            y="interest_rate_pct",
            size="loan_amount_kes",
            color="credit_grade",
            hover_name="borrower_name",
            text="crop",
            labels={
                "expected_default_rate_pct": "Expected Default Rate (%)",
                "interest_rate_pct": "Risk-Adjusted Interest Rate (%)",
                "loan_amount_kes": "Loan Amount (KES)",
                "credit_grade": "Credit Grade"
            },
            title="Portfolio Risk-Return Frontier across Counties and Crops",
            color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
        )
        fig_port_scatter.update_traces(textposition='top center')
        fig_port_scatter.update_layout(height=440, template=plotly_theme)
        st.plotly_chart(fig_port_scatter, use_container_width=True)

        st.dataframe(
            port_df[["borrower_name", "county", "crop", "acres", "credit_grade", "loan_amount_kes", "interest_rate_pct", "expected_default_rate_pct", "recommendation"]],
            use_container_width=True
        )


# ---------------------------------------------------------
# TAB 3: 10-YEAR CLIMATE INTELLIGENCE
# ---------------------------------------------------------
elif platform_view == "🌍 10-Year Climate Trend Intelligence":
    st.subheader(f"🌍 10-Year Historical Climate Analysis (2015–2025): {selected_county} County")
    st.markdown("Aggregated from 116 high-resolution TAHMO ground meteorological stations across Kenya.")

    if engine.climate_df is not None and not engine.climate_df.empty:
        county_data = engine.climate_df[engine.climate_df["county"] == selected_county]
        if county_data.empty:
            county_data = engine.climate_df.head(20)
            
        # KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean Seasonal Rainfall", f"{county_data['seasonal_rainfall_mm'].mean():.1f} mm", "10-Yr Historical Mean")
        c2.metric("Mean Temperature", f"{county_data['temp_mean_c'].mean():.1f} °C", "+0.08°C / Year Warming Trend")
        c3.metric("Max Dry Spell Duration", f"{int(county_data['max_dry_spell_days'].mean())} Days", "Consecutive Rain < 2mm")
        c4.metric("Rainfall Volatility (CV)", f"{county_data['seasonal_rainfall_mm'].std() / county_data['seasonal_rainfall_mm'].mean():.2f}", "Coefficient of Variation")

        st.markdown("---")
        
        # -----------------------------------------------------
        # VISUALIZATION 8: COMBINED AREA & DUAL AXIS LINE
        # -----------------------------------------------------
        st.markdown("### 📈 8. Seasonal Rainfall & Temperature Shift (Combined Area & Line)")
        
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Shaded Rainfall Area
        fig_trend.add_trace(
            go.Scatter(
                x=county_data["year"].astype(str) + " " + county_data["season"],
                y=county_data["seasonal_rainfall_mm"],
                name="Seasonal Rainfall (mm)",
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.22)' if is_dark else 'rgba(45, 106, 79, 0.25)',
                line=dict(color='#10b981' if is_dark else '#2d6a4f', width=2.5)
            ),
            secondary_y=False
        )
        
        # Temperature Line Curve
        fig_trend.add_trace(
            go.Scatter(
                x=county_data["year"].astype(str) + " " + county_data["season"],
                y=county_data["temp_mean_c"],
                name="Mean Temperature (°C)",
                line=dict(color='#f87171' if is_dark else '#e76f51', width=3.5, dash='solid')
            ),
            secondary_y=True
        )
        
        fig_trend.update_layout(
            title=f"10-Year Climate Trajectory in {selected_county} (2015–2025)",
            height=450,
            hovermode="x unified",
            template=plotly_theme
        )
        fig_trend.update_yaxes(title_text="Seasonal Rainfall (mm)", secondary_y=False)
        fig_trend.update_yaxes(title_text="Temperature (°C)", secondary_y=True)
        st.plotly_chart(fig_trend, use_container_width=True)

        # -----------------------------------------------------
        # VISUALIZATION 9: DISTRIBUTION BOX PLOTS & HISTOGRAM
        # -----------------------------------------------------
        col_c_v1, col_c_v2 = st.columns([1, 1])
        
        with col_c_v1:
            st.markdown("### 📦 9. Rainfall Distribution by Season (Box Plot)")
            fig_box = px.box(
                engine.climate_df,
                x="season",
                y="seasonal_rainfall_mm",
                color="season",
                points="all",
                color_discrete_sequence=["#10b981", "#3b82f6"],
                title="Rainfall Spread & Outliers across Kenyan Seasons (mm)"
            )
            fig_box.update_layout(height=380, template=plotly_theme, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

        with col_c_v2:
            st.markdown("### 📊 10. Dry Spell Duration Histogram")
            fig_hist = px.histogram(
                engine.climate_df,
                x="max_dry_spell_days",
                color="season",
                nbins=20,
                opacity=0.75,
                color_discrete_sequence=["#10b981", "#f59e0b"],
                title="Frequency of Dry Spell Lengths (Days)"
            )
            fig_hist.update_layout(height=380, template=plotly_theme)
            st.plotly_chart(fig_hist, use_container_width=True)

        # -----------------------------------------------------
        # VISUALIZATION 11: GEOSPATIAL MAP OF 116 STATIONS
        # -----------------------------------------------------
        if os.path.exists("data/stations_with_counties.csv"):
            stations_df = pd.read_csv("data/stations_with_counties.csv")
            st.markdown("### 🗺️ 11. TAHMO Ground Weather Stations Across Kenya (116 Stations)")
            
            fig_map = px.scatter_mapbox(
                stations_df,
                lat="latitude",
                lon="longitude",
                hover_name="name",
                hover_data=["county", "elevation_msl", "installation_date"],
                color="elevation_msl",
                size_max=12,
                zoom=5.5,
                center={"lat": 0.5, "lon": 37.5},
                mapbox_style="carto-darkmatter" if is_dark else "carto-positron",
                title="Geographical Distribution of Ingested Ground Weather Stations",
                color_continuous_scale="Greens"
            )
            fig_map.update_layout(height=480)
            st.plotly_chart(fig_map, use_container_width=True)


# ---------------------------------------------------------
# TAB 4: 40-CROP & MARKET CATALOG
# ---------------------------------------------------------
elif platform_view == "📊 40-Crop & Market Price Catalog":
    st.subheader("📊 Kenyan 40-Crop Agronomic & Market Intelligence Catalog")
    st.markdown("Comprehensive benchmark database across 5 agricultural classes, production economics, and 5 major wholesale trading hubs.")

    if engine.crops_df is not None:
        cat_sel = st.selectbox("Filter Category", ["All"] + list(engine.crops_df["category"].unique()))
        df_display = engine.crops_df if cat_sel == "All" else engine.crops_df[engine.crops_df["category"] == cat_sel]
        
        # -----------------------------------------------------
        # VISUALIZATION 12: 40-CROP HIERARCHICAL TREEMAP
        # -----------------------------------------------------
        st.markdown("### 🌳 12. 40-Crop Catalog Hierarchy & Yield Potential (Treemap)")
        
        fig_crop_tree = px.treemap(
            engine.crops_df,
            path=["category", "crop"],
            values="yield_per_acre_kg",
            color="base_price_kes_per_kg",
            color_continuous_scale="Greens",
            title="Crop Yield Potential (Size) vs. Base Farm-Gate Price (Color)"
        )
        fig_crop_tree.update_layout(height=420, template=plotly_theme)
        st.plotly_chart(fig_crop_tree, use_container_width=True)

        st.dataframe(
            df_display[["crop", "category", "growth_days", "drought_tolerance", "cost_per_acre_kes", "yield_per_acre_kg", "base_price_kes_per_kg"]],
            use_container_width=True
        )

        # -----------------------------------------------------
        # VISUALIZATION 13: MULTI-MARKET REGIONAL PRICE COMPARISON
        # -----------------------------------------------------
        if engine.market_df is not None:
            st.markdown("### 💰 13. Regional Wholesale Prices across Key Trading Hubs")
            sample_crops = st.multiselect("Select Crops to Compare", df_display["crop"].unique(), default=list(df_display["crop"].head(4)))
            if sample_crops:
                m_sub = engine.market_df[engine.market_df["crop"].isin(sample_crops)]
                fig_m = px.bar(
                    m_sub,
                    x="crop",
                    y="market_price",
                    color="market",
                    barmode="group",
                    title="Market Price Variations by Trading Hub (KES / kg)",
                    labels={"market_price": "Market Price (KES/kg)", "crop": "Crop", "market": "Trading Hub"},
                    color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#06b6d4"] if is_dark else ["#1b4332", "#2d6a4f", "#40916c", "#52b788", "#74c69d"]
                )
                fig_m.update_layout(height=420, template=plotly_theme)
                st.plotly_chart(fig_m, use_container_width=True)

            # -----------------------------------------------------
            # VISUALIZATION 14: VOLATILITY BOX PLOTS BY CATEGORY
            # -----------------------------------------------------
            st.markdown("### 📦 14. Market Price Volatility by Agricultural Category")
            fig_vol_box = px.box(
                engine.market_df,
                x="category",
                y="volatility_cv",
                color="category",
                title="Coefficient of Variation (CV) by Crop Category",
                color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#06b6d4"] if is_dark else ["#1b4332", "#2d6a4f", "#40916c", "#52b788", "#74c69d"]
            )
            fig_vol_box.update_layout(height=380, template=plotly_theme, showlegend=False)
            st.plotly_chart(fig_vol_box, use_container_width=True)
