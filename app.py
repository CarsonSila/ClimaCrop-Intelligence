"""
Kilimo-Smart: Climate-Smart Agricultural Advisory and De-Risking Platform.
Dual-View Decision Support for Cooperatives & Credit Underwriting for Financial Institutions.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.financial_engine import FinancialDecisionEngine

# ---------------------------------------------------------
# PAGE CONFIG & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kilimo-Smart | Agricultural Intelligence & De-Risking",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished fintech/agtech UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #40916c;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 18px;
        border-left: 5px solid #2d6a4f;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6c757d;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .card-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1b4332;
    }
    .badge-low {
        background-color: #d8f3dc;
        color: #1b4332;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-mod {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-high {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .crop-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_engine():
    return FinancialDecisionEngine()


engine = load_engine()

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=400&q=80", use_container_width=True)
st.sidebar.title("⚙️ Regional Controls")

# County list
counties_list = [
    "Nakuru", "Uasin Gishu", "Kiambu", "Nyeri", "Nyandarua", "Machakos", "Makueni", "Kitui",
    "Bungoma", "Kakamega", "Kisumu", "Siaya", "Migori", "Kisii", "Kericho", "Bomet",
    "Narok", "Embu", "Tharaka Nithi", "Kwale", "Kilifi", "Mombasa", "Taita Taveta", "West Pokot", "Turkana", "Laikipia"
]

selected_county = st.sidebar.selectbox("📍 Select County", counties_list, index=0)
selected_season = st.sidebar.selectbox("📅 Planting Season", ["Long Rains (MAM)", "Short Rains (OND)"], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Platform Mode")
platform_view = st.sidebar.radio("Active Persona", ["🌱 Agricultural Cooperative", "🏦 Bank & SACCO Financier", "🌍 Climate Trend Intelligence", "📊 40-Crop Market Catalog"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **10-Year Weather Ingestion:** Powered by 116 TAHMO ground weather stations across Kenya (2015–2025) & KNBS Agricultural Economics.")

# Top Header
st.markdown('<div class="main-header">🌾 KILIMO-SMART INTELLIGENCE & DE-RISKING PLATFORM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Climate-Smart Agricultural Decision Support for Cooperatives & Credit Underwriting for Financial Institutions</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 1: AGRICULTURAL COOPERATIVE VIEW
# ---------------------------------------------------------
if platform_view == "🌱 Agricultural Cooperative":
    st.subheader(f"🌱 Cooperative Advisory Hub: {selected_county} County — {selected_season}")
    st.markdown("Translating 10-year local climate patterns into optimal crop selection, farm gate yield projections, and regional market arbitrage.")
    
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c1:
        farm_size = st.slider("Typical Member Farm Size (Acres)", min_value=0.5, max_value=25.0, value=2.5, step=0.5)
    with col_c2:
        cat_filter = st.selectbox("Crop Category Filter", ["All", "Cereals", "Pulses", "Roots & Tubers", "Horticulture", "Cash Crops"])
    with col_c3:
        top_k = st.slider("Number of Recommendations", min_value=3, max_value=10, value=4)

    # Fetch recommendations
    recs_df, climate_profile = engine.get_cooperative_recommendations(
        county=selected_county,
        season=selected_season,
        farm_size_acres=farm_size,
        category_filter=cat_filter,
        top_n=top_k
    )
    
    # Climate banner summary
    st.markdown(f"""
    > **🌍 Climate Context for {selected_county} ({selected_season})**:
    > Predicted Rainfall: **{climate_profile['seasonal_rainfall_mm']} mm** | Mean Temp: **{climate_profile['temp_mean_c']}°C** | Dry Spell Max: **{climate_profile['max_dry_spell_days']} days** | Archetype: **{climate_profile['cluster_name']}**
    """)

    if not recs_df.empty:
        st.markdown("### 🏆 Top Recommended Crops for Season")
        
        # Display Cards
        for idx, row in recs_df.iterrows():
            badge_class = "badge-low" if row["risk_level"] == "Low" else ("badge-mod" if row["risk_level"] == "Moderate" else "badge-high")
            
            with st.container():
                st.markdown(f"""
                <div class="crop-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 1.35rem; font-weight: 700; color: #1b4332;">#{idx+1} {row['crop']}</span>
                            <span style="color: #6c757d; margin-left: 10px; font-size: 0.95rem;">({row['category']})</span>
                        </div>
                        <div>
                            <span class="{badge_class}">Suitability: {row['suitability_score']}% ({row['risk_level']} Risk)</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Expected Total Yield", f"{row['total_farm_yield_kg']:,} kg", f"{row['expected_yield_kg_per_acre']:,} kg/acre")
                c2.metric("Total Production CapEx", f"KES {row['total_production_cost_kes']:,}", f"KES {row['cost_per_acre_kes']:,}/acre")
                c3.metric("Projected Gross Revenue", f"KES {row['total_farm_revenue_kes']:,}", f"KES {row['optimized_net_price_kes_per_kg']}/kg")
                c4.metric("Net Farm Profit", f"KES {row['total_farm_net_profit_kes']:,}", f"BCR: {row['benefit_cost_ratio']}x")
                c5.metric("Best Trading Market", row['best_target_market'], f"+KES {row['arbitrage_added_value_kes']:,} gain")
                
                st.markdown("---")

        # Interactive Chart Comparison
        st.markdown("### 📊 Farm Net Profit & Benefit-Cost Ratio Comparison")
        fig = px.bar(
            recs_df,
            x="crop",
            y="total_farm_net_profit_kes",
            color="suitability_score",
            text="total_farm_net_profit_kes",
            color_continuous_scale="Greens",
            title=f"Projected Net Profit for {farm_size} Acres in {selected_county} (KES)",
            labels={"total_farm_net_profit_kes": "Net Profit (KES)", "crop": "Crop", "suitability_score": "Suitability (%)"}
        )
        fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# TAB 2: BANK & SACCO CREDIT RISK UNDERWRITING
# ---------------------------------------------------------
elif platform_view == "🏦 Bank & SACCO Financier":
    st.subheader(f"🏦 Agricultural Credit Underwriting & De-Risking Portal")
    st.markdown("Evaluating agricultural loan portfolios, assigning risk-weighted interest rates, and stress-testing climate defaults.")

    tab_single, tab_portfolio = st.tabs(["📝 Single Loan Underwriter", "💼 Multi-Borrower Portfolio Stress Test"])
    
    with tab_single:
        st.markdown("#### 🌾 Individual Farm Facility Assessment")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1:
            borrower_name = st.text_input("Borrower / SACCO Group", value="Nakuru Grain Growers Co-op")
        with col_b2:
            underwrite_crop = st.selectbox("Funded Crop", engine.crops_df["crop"].unique() if engine.crops_df is not None else ["Maize", "Sorghum", "Tomatoes"], index=0)
        with col_b3:
            loan_acres = st.number_input("Cultivated Acres", min_value=1.0, max_value=200.0, value=5.0, step=1.0)
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
        # Credit Decision Ribbon
        st.markdown("### 📋 Credit Assessment & Pricing Summary")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Credit Rating Grade", loan_res["credit_grade"], f"Risk Score: {loan_res['composite_risk_score']}")
        m2.metric("Eligible Loan Facility (70% CapEx)", f"KES {loan_res['loan_amount_kes']:,}", f"Total Cost: KES {loan_res['total_project_cost_kes']:,}")
        m3.metric("Risk-Adjusted Interest Rate", f"{loan_res['interest_rate_pct']:.2f}%", f"Base 12% + Risk Premium")
        m4.metric("Expected Default Probability", f"{loan_res['expected_default_rate_pct']:.2f}%", f"DSCR: {loan_res['debt_service_coverage_ratio']}x")

        # Risk Decomposition Chart & Mitigations
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.markdown("#### 🔬 Risk Decomposition")
            risk_breakdown = pd.DataFrame({
                "Risk Component": ["Climate Stress (40%)", "Crop Suitability Gap (35%)", "Market Price Volatility (25%)"],
                "Weight Score": [loan_res["climate_risk_component"], loan_res["crop_suitability_component"], loan_res["market_volatility_component"]]
            })
            fig_pie = px.pie(
                risk_breakdown,
                values="Weight Score",
                names="Risk Component",
                color_discrete_sequence=["#e76f51", "#f4a261", "#2a9d8f"],
                title="Underwriting Risk Drivers"
            )
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_r2:
            st.markdown("#### 🛡️ Required Loan Covenants & Climate Mitigations")
            st.success(f"**Underwriting Verdict:** {loan_res['recommendation']}")
            for m in loan_res["mitigation_strategies"]:
                st.markdown(f"- 🔒 **{m}**")

    with tab_portfolio:
        st.markdown("#### 💼 Agri-Lending Portfolio Simulation (10 Sample Borrowers)")
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
        col_p1.metric("Total Portfolio Exposure", f"KES {port_summary['total_disbursed_kes']:,}", f"{port_summary['total_loans_count']} Loans")
        col_p2.metric("Weighted Interest Yield", f"{port_summary['weighted_average_interest_rate_pct']:.2f}%", "Risk-Weighted")
        col_p3.metric("Expected Default Losses", f"KES {port_summary['expected_credit_losses_kes']:,}", f"{port_summary['weighted_expected_default_rate_pct']:.2f}% Default Rate")
        col_p4.metric("Net Projected Portfolio ROI", f"{port_summary['net_projected_roi_pct']:.2f}%", "After Credit Losses")

        st.dataframe(
            port_df[["borrower_name", "county", "crop", "acres", "credit_grade", "loan_amount_kes", "interest_rate_pct", "expected_default_rate_pct", "recommendation"]],
            use_container_width=True
        )


# ---------------------------------------------------------
# TAB 3: 10-YEAR CLIMATE INTELLIGENCE (2015-2025)
# ---------------------------------------------------------
elif platform_view == "🌍 Climate Trend Intelligence":
    st.subheader(f"🌍 10-Year Historical Climate Analysis (2015–2025): {selected_county} County")
    st.markdown("Aggregated from 116 high-resolution TAHMO ground meteorological stations across Kenya.")

    if engine.climate_df is not None and not engine.climate_df.empty:
        county_data = engine.climate_df[engine.climate_df["county"] == selected_county]
        if county_data.empty:
            county_data = engine.climate_df.head(20)
            
        # Top KPI Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean Seasonal Rainfall", f"{county_data['seasonal_rainfall_mm'].mean():.1f} mm", "10-Yr Historical")
        c2.metric("Mean Temperature", f"{county_data['temp_mean_c'].mean():.1f} °C", "+0.08°C / Year Trend")
        c3.metric("Max Dry Spell Duration", f"{int(county_data['max_dry_spell_days'].mean())} Days", "Moisture Stress Risk")
        c4.metric("Rainfall Variability (CV)", f"{county_data['seasonal_rainfall_mm'].std() / county_data['seasonal_rainfall_mm'].mean():.2f}", "Climate Volatility")

        st.markdown("---")
        # Time-Series Chart
        st.markdown("### 📈 Seasonal Rainfall & Temperature Shift (2015–2025)")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=county_data["year"].astype(str) + " " + county_data["season"],
            y=county_data["seasonal_rainfall_mm"],
            name="Seasonal Rainfall (mm)",
            marker_color="#2d6a4f"
        ))
        fig_trend.add_trace(go.Scatter(
            x=county_data["year"].astype(str) + " " + county_data["season"],
            y=county_data["temp_mean_c"],
            name="Mean Temp (°C)",
            yaxis="y2",
            line=dict(color="#e76f51", width=3)
        ))
        fig_trend.update_layout(
            title=f"Rainfall & Temperature Shift in {selected_county}",
            yaxis=dict(title="Seasonal Rainfall (mm)"),
            yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right"),
            height=450,
            hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Weather Station Distribution Map
        if os.path.exists("data/stations_with_counties.csv"):
            stations_df = pd.read_csv("data/stations_with_counties.csv")
            st.markdown("### 🗺️ TAHMO Ground Weather Stations Across Kenya (116 Stations)")
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
                mapbox_style="carto-positron",
                title="Ground Meteorological Stations Map",
                color_continuous_scale="Viridis"
            )
            fig_map.update_layout(height=450)
            st.plotly_chart(fig_map, use_container_width=True)


# ---------------------------------------------------------
# TAB 4: 40-CROP & MARKET CATALOG
# ---------------------------------------------------------
elif platform_view == "📊 40-Crop Market Catalog":
    st.subheader("📊 Kenyan 40-Crop Agronomic & Market Intelligence Database")
    st.markdown("Comprehensive benchmark database across 5 agricultural classes, production economics, and 5 major wholesale trading hubs.")

    if engine.crops_df is not None:
        cat_sel = st.selectbox("Filter Category", ["All"] + list(engine.crops_df["category"].unique()))
        df_display = engine.crops_df if cat_sel == "All" else engine.crops_df[engine.crops_df["category"] == cat_sel]
        
        st.dataframe(
            df_display[["crop", "category", "growth_days", "drought_tolerance", "cost_per_acre_kes", "yield_per_acre_kg", "base_price_kes_per_kg"]],
            use_container_width=True
        )

        if engine.market_df is not None:
            st.markdown("### 💰 Regional Market Wholesale Prices (Nairobi, Nakuru, Eldoret, Kisumu, Mombasa)")
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
                    labels={"market_price": "Market Price (KES/kg)", "crop": "Crop", "market": "Trading Hub"}
                )
                fig_m.update_layout(height=420)
                st.plotly_chart(fig_m, use_container_width=True)

