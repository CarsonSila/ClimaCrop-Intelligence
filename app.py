"""
ClimaCrop Intelligence — Kilimo-Smart Climate Decision Support & Agri-Fintech De-Risking Platform
Version 3.0 | Enhanced UX & Data Visualisation Edition
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.financial_engine import FinancialDecisionEngine
from src.humanize import humanize_crop_recommendation, humanize_loan_decision
from src.ai_agent import GEMINI_AVAILABLE, get_api_key, init_chat_session, ask_kiilimobot, generate_offline_response

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClimaCrop Intelligence | Kilimo-Smart Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "**ClimaCrop Intelligence** — Kenya's first end-to-end Climate-Agri Decision Platform combining 10 years of TAHMO ground weather data, NASA satellite reanalysis, FAOSTAT baselines and machine learning to help cooperatives, banks and farmers grow smarter."
    }
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — SETTINGS ONLY (theme, county, season, engine)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=600&auto=format&fit=crop&q=80",
        use_container_width=True
    )
    st.markdown(
        "<div style='text-align:center;font-weight:700;font-size:1.05rem;letter-spacing:-0.3px;margin-top:8px;margin-bottom:2px;'>🌿 ClimaCrop Intelligence</div>"
        "<div style='text-align:center;font-size:0.76rem;color:#6b7280;margin-bottom:14px;'>Kilimo-Smart Decision Platform</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Theme
    st.markdown("#### 🎨 Display Theme")
    theme_mode = st.radio(
        "Theme",
        ["🌿 Emerald Light", "🌙 Dark Forest", "⚙️ Minimal Slate"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Region & Calendar
    st.markdown("#### 📍 Location & Season")
    counties_list = [
        "Nakuru", "Uasin Gishu", "Kiambu", "Nyeri", "Nyandarua", "Machakos", "Makueni", "Kitui",
        "Bungoma", "Kakamega", "Kisumu", "Siaya", "Migori", "Kisii", "Kericho", "Bomet",
        "Narok", "Embu", "Tharaka Nithi", "Kwale", "Kilifi", "Mombasa", "Taita Taveta",
        "West Pokot", "Turkana", "Laikipia"
    ]
    selected_county = st.selectbox("📍 County", counties_list, index=0)
    selected_season = st.selectbox("📅 Season", ["Long Rains (MAM)", "Short Rains (OND)"], index=0)

    st.markdown("---")

    # Engine mode
    st.markdown("#### 🧠 Advisory Engine")
    st.caption("Choose how crop suitability scores are calculated.")
    engine_mode = st.radio(
        "Engine",
        ["📐 Agro-Ecological Rules (AEZ)", "🤖 Machine Learning (Random Forest)"],
        index=0,
        label_visibility="collapsed"
    )
    use_rule_based = engine_mode.startswith("📐")
    st.info(
        "📐 **Rules (AEZ):** Transparent, explainable scores based on Kenya's Agro-Ecological Zone rainfall & temperature bands."
        if use_rule_based else
        "🤖 **ML Model:** Probabilistic Random Forest recommendations — great for comparing against rule-based outputs."
    )

    st.markdown("---")

    # Live Data Stack info card
    st.markdown("""
<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:12px 14px;">
<div style="font-size:0.72rem;font-weight:800;letter-spacing:0.6px;color:#059669;margin-bottom:6px;">📡 DATA SOURCES</div>
<div style="font-size:0.8rem;line-height:1.6;">
🌡️ 116 TAHMO Ground Stations<br>
🛰️ NASA POWER Satellite Reanalysis<br>
📋 FAOSTAT & KNBS 40-Crop Matrix<br>
🏪 5 Regional Wholesale Hubs
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Navigation is at the top of the main page. Scroll up to switch views.")

# ─────────────────────────────────────────────────────────────────────────────
# THEME VARIABLES
# ─────────────────────────────────────────────────────────────────────────────
if theme_mode == "🌙 Dark Forest":
    is_dark = True
    plotly_theme = "plotly_dark"
    bg_main = "#090f0c"
    card_bg = "#111a14"
    card_border = "#1e3326"
    text_main = "#e2fbe8"
    text_muted = "#6ee7b7"
    primary_color = "#10b981"
    primary_light = "#064e3b"
    kpi_val_color = "#34d399"
    badge_low_bg = "#064e3b"; badge_low_txt = "#a7f3d0"
    badge_mod_bg = "#78350f"; badge_mod_txt = "#fde68a"
    badge_high_bg = "#7f1d1d"; badge_high_txt = "#fecaca"
    accent_blue = "#60a5fa"
    hero_bg = "linear-gradient(135deg,rgba(6,24,14,0.97) 0%,rgba(16,60,38,0.95) 60%,rgba(6,78,59,0.93) 100%)"
    advisory_bg = "rgba(16,185,129,0.08)"
    briefing_bg = "rgba(59,130,246,0.12)"
    section_bg = "rgba(255,255,255,0.02)"
elif theme_mode == "⚙️ Minimal Slate":
    is_dark = False
    plotly_theme = "plotly_white"
    bg_main = "#f8fafc"
    card_bg = "#ffffff"
    card_border = "#e2e8f0"
    text_main = "#0f172a"
    text_muted = "#64748b"
    primary_color = "#334155"
    primary_light = "#f1f5f9"
    kpi_val_color = "#0f172a"
    badge_low_bg = "#f0fdf4"; badge_low_txt = "#166534"
    badge_mod_bg = "#fffbeb"; badge_mod_txt = "#92400e"
    badge_high_bg = "#fff1f2"; badge_high_txt = "#9f1239"
    accent_blue = "#3b82f6"
    hero_bg = "linear-gradient(135deg,rgba(15,23,42,0.95) 0%,rgba(51,65,85,0.92) 100%)"
    advisory_bg = "#f0fdf4"
    briefing_bg = "#eff6ff"
    section_bg = "#f8fafc"
else:  # Emerald Light (default)
    is_dark = False
    plotly_theme = "plotly_white"
    bg_main = "#f0faf5"
    card_bg = "#ffffff"
    card_border = "#bbf7d0"
    text_main = "#0f2d1e"
    text_muted = "#2d7a56"
    primary_color = "#166534"
    primary_light = "#dcfce7"
    kpi_val_color = "#14532d"
    badge_low_bg = "#dcfce7"; badge_low_txt = "#14532d"
    badge_mod_bg = "#fef9c3"; badge_mod_txt = "#713f12"
    badge_high_bg = "#ffe4e6"; badge_high_txt = "#9f1239"
    accent_blue = "#2563eb"
    hero_bg = "linear-gradient(135deg,rgba(15,45,30,0.94) 0%,rgba(22,101,52,0.91) 60%,rgba(5,150,105,0.88) 100%)"
    advisory_bg = "#f0fdf4"
    briefing_bg = "#eff6ff"
    section_bg = "#f7fef9"

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background-color: {bg_main} !important;
    font-family: 'Inter', sans-serif !important;
    color: {text_main} !important;
}}
[data-testid="stSidebar"] {{
    background-color: {card_bg} !important;
    border-right: 1px solid {card_border} !important;
}}

/* ── Hero ── */
.hero {{
    background: {hero_bg},
        url('https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1600&auto=format&fit=crop&q=85') center/cover no-repeat;
    color:#fff; padding:34px 36px 28px; border-radius:20px; margin-bottom:22px;
    box-shadow:0 16px 40px rgba(0,0,0,{'0.45' if is_dark else '0.14'});
    border:1px solid rgba(255,255,255,0.12);
}}
.hero-pill {{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(74,222,128,0.2);backdrop-filter:blur(10px);
    color:#86efac;padding:5px 14px;border-radius:20px;
    font-size:0.75rem;font-weight:700;letter-spacing:0.7px;
    border:1px solid rgba(74,222,128,0.3);margin-bottom:12px;
}}
.hero-title {{ font-size:2.0rem;font-weight:800;letter-spacing:-0.6px;line-height:1.15;margin-bottom:8px;color:#fff; }}
.hero-subtitle {{ font-size:0.95rem;color:rgba(255,255,255,0.82);line-height:1.55;max-width:780px;font-weight:400; }}
.hero-stats {{ display:flex;flex-wrap:wrap;gap:16px;margin-top:18px; }}
.hero-stat {{
    background:rgba(255,255,255,0.1);backdrop-filter:blur(8px);
    padding:8px 18px;border-radius:10px;border:1px solid rgba(255,255,255,0.15);
}}
.hero-stat-val {{ font-size:1.3rem;font-weight:800;color:#4ade80; }}
.hero-stat-lbl {{ font-size:0.68rem;color:rgba(255,255,255,0.7);font-weight:600;letter-spacing:0.5px; }}

/* ── Section Header ── */
.sec-header {{
    display:flex;align-items:flex-start;gap:12px;
    margin:26px 0 12px;padding-bottom:12px;border-bottom:2px solid {card_border};
}}
.sec-icon {{ font-size:1.4rem;flex-shrink:0;padding-top:1px; }}
.sec-title {{ font-size:1.1rem;font-weight:800;color:{text_main}; }}
.sec-desc {{ font-size:0.82rem;color:{text_muted};font-weight:500;margin-top:2px;line-height:1.45; }}

/* ── KPI Cards ── */
.kpi-grid {{ display:flex;flex-wrap:wrap;gap:12px;margin-bottom:20px; }}
.kpi-card {{
    background:{card_bg};border-radius:14px;padding:16px 20px;
    border:1px solid {card_border};border-top:4px solid {primary_color};
    flex:1;min-width:150px;
    box-shadow:0 2px 10px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
    transition:transform 0.18s ease,box-shadow 0.18s ease;
}}
.kpi-card:hover {{ transform:translateY(-3px);box-shadow:0 8px 20px rgba(0,0,0,{'0.3' if is_dark else '0.09'}); }}
.kpi-icon {{ font-size:1.5rem;margin-bottom:6px; }}
.kpi-label {{ font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:{text_muted};font-weight:700;margin-bottom:5px; }}
.kpi-val {{ font-size:1.6rem;font-weight:800;color:{kpi_val_color};line-height:1.1; }}
.kpi-sub {{ font-size:0.75rem;color:{text_muted};font-weight:500;margin-top:4px; }}

/* ── Crop Cards ── */
.crop-card {{
    background:{card_bg};border:1px solid {card_border};border-radius:16px;
    padding:20px 22px 14px;margin-bottom:16px;border-left:5px solid {primary_color};
    box-shadow:0 4px 16px rgba(0,0,0,{'0.2' if is_dark else '0.05'});
    transition:box-shadow 0.18s ease;
}}
.crop-card:hover {{ box-shadow:0 8px 28px rgba(0,0,0,{'0.3' if is_dark else '0.1'}); }}
.crop-rank {{
    display:inline-flex;align-items:center;justify-content:center;
    width:28px;height:28px;border-radius:50%;
    background:{primary_color};color:#fff;font-size:0.82rem;font-weight:800;margin-right:8px;flex-shrink:0;
}}
.crop-name {{ font-size:1.18rem;font-weight:800;color:{primary_color}; }}
.crop-meta {{ font-size:0.82rem;color:{text_muted};font-weight:500; }}
.advisory-box {{
    background:{advisory_bg};border-left:3px solid {primary_color};
    border-radius:0 8px 8px 0;padding:10px 14px;margin:12px 0;
    font-size:0.88rem;line-height:1.55;color:{text_main};
}}

/* ── Badges ── */
.badge {{ display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem; }}
.badge-low {{ background:{badge_low_bg};color:{badge_low_txt}; }}
.badge-mod {{ background:{badge_mod_bg};color:{badge_mod_txt}; }}
.badge-high {{ background:{badge_high_bg};color:{badge_high_txt}; }}

/* ── Info boxes ── */
.briefing-box {{
    background:{briefing_bg};border-left:4px solid {accent_blue};
    border-radius:0 10px 10px 0;padding:14px 18px;
    font-size:0.9rem;line-height:1.6;color:{text_main};margin:14px 0;
}}
.info-box {{
    background:{section_bg};border:1px solid {card_border};
    border-radius:12px;padding:14px 18px;margin:12px 0;
    font-size:0.86rem;color:{text_muted};line-height:1.55;
}}

/* ── Metrics ── */
[data-testid="stMetricValue"] {{ font-size:1.2rem !important;font-weight:800 !important;color:{kpi_val_color} !important; }}
[data-testid="stMetricLabel"] {{ font-size:0.74rem !important;font-weight:700 !important;color:{text_muted} !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap:5px;background:{'rgba(255,255,255,0.04)' if is_dark else '#f3f4f6'};border-radius:12px;padding:4px;
}}
.stTabs [data-baseweb="tab"] {{ border-radius:8px;font-weight:600;font-size:0.86rem;padding:8px 18px;color:{text_muted}; }}
.stTabs [aria-selected="true"] {{ background:{card_bg} !important;color:{primary_color} !important;box-shadow:0 2px 8px rgba(0,0,0,0.1); }}

/* ── Buttons ── */
.stButton>button {{
    background-color:{primary_color} !important;color:#fff !important;
    border-radius:10px !important;border:none !important;
    font-weight:700 !important;padding:9px 20px !important;font-size:0.88rem !important;
}}

/* ── Chart caption ── */
.chart-caption {{
    font-size:0.8rem;color:{text_muted};margin-bottom:6px;
    padding:6px 12px;background:{section_bg};border-radius:6px;
    border-left:2px solid {primary_color};line-height:1.45;
}}

/* ── Footer ── */
.footer {{
    margin-top:48px;margin-bottom:24px;padding:22px 28px;background:{card_bg};border-radius:16px;
    border:1px solid {card_border};text-align:center;line-height:1.6;
    box-shadow:0 4px 16px rgba(0,0,0,{'0.25' if is_dark else '0.04'});
}}

/* ── Mobile ── */
@media(max-width:768px) {{
    .hero {{ padding:20px 18px 18px;border-radius:14px; }}
    .hero-title {{ font-size:1.45rem; }}
    .hero-subtitle {{ font-size:0.84rem; }}
    .hero-stats {{ gap:10px; }}
    .hero-stat {{ padding:6px 12px; }}
    .hero-stat-val {{ font-size:1.1rem; }}
    .kpi-card {{ padding:12px 14px;min-width:130px; }}
    .kpi-val {{ font-size:1.25rem; }}
    .crop-card {{ padding:14px 14px 10px; }}
    .crop-name {{ font-size:1.0rem; }}
    .block-container {{ padding-top:1rem !important;padding-left:0.5rem !important;padding-right:0.5rem !important; }}
    .sec-title {{ font-size:1rem; }}
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD ENGINE
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🌱 Loading ClimaCrop intelligence engines...")
def load_engine():
    return FinancialDecisionEngine()

engine = load_engine()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def section(icon, title, desc=""):
    st.markdown(f"""
<div class="sec-header">
    <span class="sec-icon">{icon}</span>
    <div>
        <div class="sec-title">{title}</div>
        {f'<div class="sec-desc">{desc}</div>' if desc else ''}
    </div>
</div>""", unsafe_allow_html=True)


def chart_caption(text):
    st.markdown(f'<div class="chart-caption">ℹ️ {text}</div>', unsafe_allow_html=True)


def apply_chart_style(fig, height=400):
    fig.update_layout(
        height=height,
        margin=dict(l=14, r=14, t=42, b=14),
        template=plotly_theme,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color=text_main),
        title_font=dict(size=13, color=text_main),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=card_border, borderwidth=1, font=dict(size=11)),
    )
    return fig


def kpi(icon, label, value, sub):
    return f"""<div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-val">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
engine_badge = "📐 Agro-Ecological Rules (AEZ)" if use_rule_based else "🤖 Random Forest ML"
st.markdown(f"""
<div class="hero">
    <div class="hero-pill">
        <span style="color:#4ade80;font-size:0.55rem;">●</span>
        LIVE — {selected_county.upper()} · {selected_season.upper()} · {engine_badge.upper()}
    </div>
    <div class="hero-title">ClimaCrop Intelligence</div>
    <div class="hero-subtitle">
        Kenya's climate-smart agri-decision platform — translating 10 years of localized rainfall,
        temperature and market data into optimal crop choices, farm profit projections,
        and institutional credit de-risking for cooperatives and banks.
    </div>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-val">116</div><div class="hero-stat-lbl">TAHMO STATIONS</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-val">40</div><div class="hero-stat-lbl">KENYAN CROPS</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-val">10 YRS</div><div class="hero-stat-lbl">CLIMATE HISTORY</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-val">26</div><div class="hero-stat-lbl">COUNTIES COVERED</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TOP-TAB NAVIGATION — 5 tabs displayed in main content area
# ─────────────────────────────────────────────────────────────────────────────
tab_coop, tab_bank, tab_climate, tab_catalog, tab_ai = st.tabs([
    "🌱 Cooperative Advisory",
    "🏦 Bank & Credit Risk",
    "🌍 Climate Trends",
    "📊 Crop & Market Catalog",
    "🤖 KilimoBot AI Assistant"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — COOPERATIVE ADVISORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_coop:
    platform_view = "🌱 Cooperative Advisory"  # local alias for section calls

    section("🌱", f"Cooperative Advisory — {selected_county} County",
            f"Evaluating 40 Kenyan crops using {engine_badge} for the {selected_season} season")

    col_c1, col_c2, col_c3 = st.columns([1.2, 1.2, 0.8])
    with col_c1:
        farm_size = st.slider("🌾 Farm Size (Acres)", 0.5, 30.0, 3.0, 0.5,
                              help="Total cultivated acreage for your cooperative members")
    with col_c2:
        cat_filter = st.selectbox("🌿 Crop Category",
                                  ["All", "Cereals", "Pulses", "Roots & Tubers", "Horticulture", "Cash Crops"],
                                  help="Filter crop recommendations by agricultural class")
    with col_c3:
        top_k = st.slider("🏆 Show Top N", 3, 10, 4, help="Number of top-ranked crops to display")

    with st.spinner("Calculating recommendations for your county & season..."):
        recs_df, climate_profile, provenance = engine.get_cooperative_recommendations(
            county=selected_county, season=selected_season,
            farm_size_acres=farm_size, category_filter=cat_filter,
            top_n=top_k, use_rule_based=use_rule_based
        )

    # ── Climate KPIs ──
    section("🌡️", "Local Climate Snapshot",
            f"10-year meteorological averages for {selected_county} · {selected_season}")
    st.markdown(
        '<div class="kpi-grid">'
        + kpi("🌧️", "Seasonal Rainfall", f"{climate_profile['seasonal_rainfall_mm']} mm", f"{selected_season} mean")
        + kpi("🌡️", "Mean Temperature", f"{climate_profile['temp_mean_c']} °C",
              f"Min {climate_profile['temp_min_c']}°C · Max {climate_profile['temp_max_c']}°C")
        + kpi("☀️", "Dry Spell Risk", f"{climate_profile['max_dry_spell_days']} days",
              "Consecutive days with rain < 2 mm")
        + kpi("🗺️", "Climate Zone", climate_profile['cluster_name'],
              f"AEZ cluster #{climate_profile['cluster_id']}")
        + '</div>', unsafe_allow_html=True)

    # ── Data Quality Expander ──
    with st.expander("🔍 Data Quality & Source Confidence Report", expanded=False):
        conf = provenance.get("overall_confidence", 0.75)
        conf_pct = conf * 100
        conf_color = "#10b981" if conf >= 0.8 else ("#f59e0b" if conf >= 0.6 else "#ef4444")
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;padding:10px 0 4px;">
    <div style="flex:1;background:{'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'};
                border-radius:8px;height:12px;overflow:hidden;">
        <div style="width:{conf_pct:.0f}%;height:100%;background:{conf_color};border-radius:8px;"></div>
    </div>
    <div style="font-size:1.05rem;font-weight:800;color:{conf_color};white-space:nowrap;">
        {conf_pct:.0f}% data confidence
    </div>
</div>
<div style="font-size:0.84rem;color:{text_muted};margin-bottom:10px;">{provenance.get('summary','')}</div>
""", unsafe_allow_html=True)
        cols_prov = st.columns(2)
        prov_colors = {"MEASURED": "#10b981", "OFFICIAL": "#3b82f6", "ESTIMATED": "#f59e0b",
                       "MODELED": "#8b5cf6", "ASSUMED": "#6b7280"}
        for i, (f_name, f_data) in enumerate(provenance.get("fields", {}).items()):
            lbl = f_data.get("provenance_label", "")
            note = f_data.get("note", "")
            c = prov_colors.get(lbl, "#6b7280")
            cols_prov[i % 2].markdown(f"""
<div style="background:{card_bg};border:1px solid {card_border};border-left:3px solid {c};
            border-radius:8px;padding:8px 12px;margin-bottom:6px;font-size:0.81rem;">
    <strong style="color:{c};">{lbl}</strong> · <code>{f_name}</code><br>
    <span style="color:{text_muted};">{note}</span>
</div>""", unsafe_allow_html=True)

    # ── Crop Recommendation Cards ──
    if not recs_df.empty:
        section("🏆", "Top Recommended Crops",
                "Ranked by combined climate suitability, yield potential, and market profitability")

        for idx, row in recs_df.iterrows():
            risk = row.get("risk_level", "Low")
            suit = row.get("suitability_score", 0)
            advice = humanize_crop_recommendation(row.to_dict())
            badge_cls = {"Low": "badge-low", "Moderate": "badge-mod", "High": "badge-high"}.get(risk, "badge-low")
            bar_clr = {"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"}.get(risk, "#10b981")

            st.markdown(f"""
<div class="crop-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
            <span class="crop-rank">{idx+1}</span>
            <span class="crop-name">{row['crop']}</span>
            <span class="crop-meta">· {row['category']} · {row['growth_days']}-day cycle</span>
        </div>
        <span class="badge {badge_cls}">{risk} Risk &nbsp;·&nbsp; {suit}% Suitability</span>
    </div>
    <div style="margin-bottom:10px;">
        <div style="font-size:0.68rem;font-weight:700;color:{text_muted};letter-spacing:0.6px;margin-bottom:3px;">
            CLIMATE FIT SCORE
        </div>
        <div style="background:{'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'};border-radius:6px;height:10px;overflow:hidden;">
            <div style="width:{suit}%;height:100%;background:{bar_clr};border-radius:6px;"></div>
        </div>
    </div>
    <div class="advisory-box">🌾 <strong>Farmer Advisory:</strong> {advice}</div>
</div>
""", unsafe_allow_html=True)

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Expected Yield", f"{row['total_farm_yield_kg']:,} kg",
                      f"{row['expected_yield_kg_per_acre']:,} kg/acre")
            m2.metric("Production Cost", f"KES {row['total_production_cost_kes']:,}",
                      f"KES {row['cost_per_acre_kes']:,}/acre")
            m3.metric("Gross Revenue", f"KES {row['total_farm_revenue_kes']:,}",
                      f"KES {row['optimized_net_price_kes_per_kg']}/kg")
            m4.metric("Net Profit", f"KES {row['total_farm_net_profit_kes']:,}",
                      f"BCR {row['benefit_cost_ratio']}×")
            m5.metric("Best Market", row['best_target_market'],
                      f"+KES {row['arbitrage_added_value_kes']:,}")
            st.markdown(f'<hr style="margin:10px 0 18px;border:none;border-top:1px solid {card_border};">', unsafe_allow_html=True)

        # ── VIZ 1: Strategic Bubble Chart ──
        section("🫧", "Strategic Decision Frontier",
                "Bubble size = expected yield · Move right and up for the best crops")
        fig1 = px.scatter(recs_df,
            x="suitability_score", y="total_farm_net_profit_kes",
            size="total_farm_yield_kg", color="risk_level", hover_name="crop", text="crop",
            color_discrete_map={"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"},
            labels={"suitability_score": "Climate Suitability (%)",
                    "total_farm_net_profit_kes": "Estimated Net Profit (KES)",
                    "total_farm_yield_kg": "Total Yield (kg)", "risk_level": "Risk Level"}
        )
        fig1.update_traces(textposition="top center",
                           marker=dict(opacity=0.86, line=dict(width=1.5, color="#fff" if is_dark else "#14532d")))
        fig1.update_layout(xaxis=dict(ticksuffix="%", gridcolor=card_border),
                           yaxis=dict(tickprefix="KES ", gridcolor=card_border))
        chart_caption("Each bubble = one crop. Rightmost = best climate fit. Highest = most profitable. Larger bubble = more yield volume.")
        st.plotly_chart(apply_chart_style(fig1, 430), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 2 + 3: Financial Bar & Treemap ──
        col_v2, col_v3 = st.columns([1.1, 0.9])
        with col_v2:
            section("📊", "Financial Breakdown per Crop",
                    "Red = production cost · Blue = gross revenue · Green = net profit")
            df_melt = recs_df.melt(id_vars=["crop"],
                value_vars=["total_production_cost_kes", "total_farm_revenue_kes", "total_farm_net_profit_kes"],
                var_name="Metric", value_name="KES")
            df_melt["Metric"] = df_melt["Metric"].map({
                "total_production_cost_kes": "📦 Cost",
                "total_farm_revenue_kes": "💰 Revenue",
                "total_farm_net_profit_kes": "✅ Profit"
            })
            fig2 = px.bar(df_melt, x="crop", y="KES", color="Metric", barmode="group",
                color_discrete_map={"📦 Cost": "#f87171", "💰 Revenue": "#60a5fa", "✅ Profit": "#34d399"},
                labels={"KES": "Amount (KES)", "crop": "Crop", "Metric": ""})
            fig2.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            chart_caption(f"Compare cost, revenue and profit side-by-side for your {farm_size}-acre farm. The green profit bar should always exceed the red cost bar.")
            st.plotly_chart(apply_chart_style(fig2, 380), use_container_width=True, config={"displayModeBar": False})

        with col_v3:
            section("🌳", "Profit Share by Category", "Area = profit share · Color = Benefit-Cost Ratio (BCR)")
            fig3 = px.treemap(recs_df, path=["category", "crop"],
                values="total_farm_net_profit_kes", color="benefit_cost_ratio",
                color_continuous_scale=["#bbf7d0", "#16a34a", "#052e16"] if not is_dark else ["#064e3b", "#10b981", "#d1fae5"])
            fig3.update_traces(textinfo="label+percent parent", textfont_size=12)
            chart_caption("Bigger box = more profit. Darker green = higher return per shilling invested (BCR). Click a box to zoom in.")
            st.plotly_chart(apply_chart_style(fig3, 380), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 4: Radar Chart ──
        if len(recs_df) >= 2:
            section("📡", "Multi-Criteria Crop Comparison Radar",
                    "5 key dimensions visualised at once — bigger coverage = better overall crop choice")
            dims = ["suitability_score", "benefit_cost_ratio", "drought_tolerance_score",
                    "expected_yield_kg_per_acre", "optimized_net_price_kes_per_kg"]
            dim_labels = ["Suitability\n(%)", "BCR\n(Return)", "Drought\nTolerance",
                          "Yield / Acre\n(kg)", "Price / kg\n(KES)"]
            maxvals = [100, 5, 100, 5000, 200]
            radar_colors = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#f43f5e"]
            radar_fig = go.Figure()
            for i, (_, row) in enumerate(recs_df.iterrows()):
                raw = [row.get(d, 0) for d in dims]
                norm = [min(v / m * 100, 100) for v, m in zip(raw, maxvals)]
                norm.append(norm[0])
                lbl = dim_labels + [dim_labels[0]]
                radar_fig.add_trace(go.Scatterpolar(
                    r=norm, theta=lbl, name=row["crop"], fill="toself",
                    line=dict(color=radar_colors[i % len(radar_colors)], width=2.2),
                    opacity=0.72
                ))
            radar_fig.update_layout(
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor=card_border, tickfont=dict(size=8)),
                    angularaxis=dict(gridcolor=card_border)),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25)
            )
            chart_caption("Larger filled area = stronger crop across all 5 criteria. Look for crops that dominate in the dimensions most important to your cooperative.")
            st.plotly_chart(apply_chart_style(radar_fig, 430), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 5: Market Arbitrage ──
        section("💰", "Cross-Market Arbitrage Analysis",
                "Net price (after transport cost) from your county to each regional wholesale hub")
        sel_crop = st.selectbox("Select a crop to analyse its market breakdown", recs_df["crop"].tolist())
        mkt_opps = engine.market_engine.get_market_opportunities(sel_crop, origin_county=selected_county)
        if not mkt_opps.empty:
            fig5 = px.bar(
                mkt_opps.sort_values("net_market_price_kes", ascending=False),
                x="market", y="net_market_price_kes",
                color="arbitrage_margin_vs_base", text="net_market_price_kes",
                color_continuous_scale=["#86efac", "#16a34a", "#052e16"] if not is_dark else ["#064e3b", "#10b981", "#4ade80"],
                labels={"net_market_price_kes": "Net Price (KES/kg)", "market": "Trading Hub",
                        "arbitrage_margin_vs_base": "Extra Gain vs Base (KES)"}
            )
            fig5.update_traces(texttemplate="KES %{text:.0f}", textposition="outside",
                               marker_line_color=card_border, marker_line_width=0.5)
            fig5.update_layout(xaxis_tickangle=-25)
            chart_caption(f"Tallest bar = best market to sell {sel_crop} from {selected_county}. Darker bar = highest extra profit vs local market price.")
            st.plotly_chart(apply_chart_style(fig5, 380), use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BANK & CREDIT RISK
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bank:

    section("🏦", "Agricultural Credit Underwriting Portal",
            "Automated loan sizing (70% CapEx rule), climate-adjusted interest rates, and portfolio stress testing")

    tab_single, tab_port = st.tabs(["📝 Single Loan Assessment", "💼 Portfolio Stress Test"])

    with tab_single:
        st.markdown('<div class="info-box">ℹ️ <strong>How it works:</strong> Enter the borrower details below. The system calculates the recommended loan amount as 70% of total production CapEx, adjusts the interest rate upward for higher climate and crop risk, and shows the Debt Service Coverage Ratio (DSCR). A DSCR ≥ 1.2× means the farm revenue can comfortably cover loan repayments.</div>', unsafe_allow_html=True)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            borrower_name = st.text_input("🏢 Borrower / SACCO Name", "Nakuru Grain Growers Co-op")
            underwrite_crop = st.selectbox("🌾 Crop to Finance",
                engine.crops_df["crop"].unique() if engine.crops_df is not None else ["Maize"], index=0)
        with col_b2:
            loan_acres = st.number_input("🌱 Farm Size (Acres)", 1.0, 200.0, 6.0, 1.0)
            underwrite_county = st.selectbox("📍 Farm County", counties_list,
                                             index=counties_list.index(selected_county))

        with st.spinner("Running credit underwriting..."):
            loan_res = engine.underwrite_agricultural_loan(
                county=underwrite_county, crop_name=underwrite_crop,
                acres=loan_acres, season=selected_season, borrower_name=borrower_name
            )

        st.markdown(f'<hr style="margin:14px 0;border:none;border-top:1px solid {card_border};">', unsafe_allow_html=True)

        grade = loan_res.get("credit_grade", "C")
        grade_color = {"A+": "#10b981", "A": "#10b981", "B+": "#34d399", "B": "#6ee7b7",
                       "C+": "#f59e0b", "C": "#f59e0b", "D": "#ef4444", "E": "#dc2626"}.get(grade, "#6b7280")

        st.markdown(f"""
<div style="display:flex;align-items:center;gap:16px;padding:14px 20px;background:{card_bg};
            border-radius:14px;border:1px solid {card_border};margin-bottom:16px;flex-wrap:wrap;gap:12px;">
    <div style="width:56px;height:56px;border-radius:50%;background:{grade_color};
                display:flex;align-items:center;justify-content:center;
                font-size:1.45rem;font-weight:900;color:#fff;flex-shrink:0;">{grade}</div>
    <div>
        <div style="font-size:1.05rem;font-weight:800;color:{text_main};">{borrower_name}</div>
        <div style="font-size:0.83rem;color:{text_muted};">
            {underwrite_crop} · {loan_acres:.0f} acres · {underwrite_county} · {selected_season}
        </div>
        <div style="font-size:0.83rem;margin-top:4px;">
            <span style="color:{grade_color};font-weight:700;">Grade {grade}</span>
            &nbsp;·&nbsp; Risk Score: <strong>{loan_res.get('composite_risk_score', 'N/A')}</strong>
            &nbsp;·&nbsp; <strong style="color:{grade_color};">{loan_res.get('recommendation','')}</strong>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💳 Eligible Loan", f"KES {loan_res['loan_amount_kes']:,}",
                  f"70% of KES {loan_res['total_project_cost_kes']:,}")
        m2.metric("📈 Interest Rate", f"{loan_res['interest_rate_pct']:.2f}%",
                  "Base 12% + Risk premium")
        m3.metric("⚠️ Default Risk", f"{loan_res['expected_default_rate_pct']:.2f}%",
                  "Climate-adjusted probability")
        m4.metric("📊 DSCR", f"{loan_res['debt_service_coverage_ratio']}×",
                  "≥1.2× = adequate coverage")

        st.markdown(f'<div class="briefing-box">📋 <strong>Credit Officer Briefing:</strong> {humanize_loan_decision(loan_res)}</div>',
                    unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            section("🧭", "Composite Risk Gauge", "Overall agricultural credit risk score (0 = safest, 1 = riskiest)")
            risk_val = loan_res["composite_risk_score"]
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_val,
                number={"font": {"size": 30, "color": text_main}},
                gauge={
                    "axis": {"range": [0, 1], "tickwidth": 1, "tickcolor": text_muted, "nticks": 6},
                    "bar": {"color": "#10b981" if risk_val < 0.35 else ("#f59e0b" if risk_val < 0.6 else "#ef4444"),
                            "thickness": 0.28},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0.00, 0.25], "color": "#064e3b" if is_dark else "#d1fae5"},
                        {"range": [0.25, 0.40], "color": "#065f46" if is_dark else "#a7f3d0"},
                        {"range": [0.40, 0.60], "color": "#78350f" if is_dark else "#fde68a"},
                        {"range": [0.60, 1.00], "color": "#7f1d1d" if is_dark else "#fecaca"},
                    ],
                    "threshold": {"line": {"color": "#ef4444", "width": 3}, "thickness": 0.7, "value": 0.65}
                }
            ))
            fig_gauge.update_layout(height=270, margin=dict(l=20, r=20, t=30, b=10),
                                    template=plotly_theme, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
            chart_caption("Green (< 0.40) = low risk. Amber (0.40–0.60) = monitor closely. Red (> 0.60) = high risk — require additional collateral.")

        with col_g2:
            section("🔬", "Risk Factor Decomposition", "What is driving the credit risk score?")
            risk_breakdown = pd.DataFrame({
                "Factor": ["🌧️ Climate Stress (40%)", "🌾 Crop Suitability Gap (35%)", "📉 Market Volatility (25%)"],
                "Score": [loan_res["climate_risk_component"], loan_res["crop_suitability_component"],
                          loan_res["market_volatility_component"]]
            })
            fig_donut = px.pie(risk_breakdown, values="Score", names="Factor", hole=0.58,
                color_discrete_sequence=["#ef4444", "#10b981", "#3b82f6"])
            fig_donut.update_traces(textinfo="percent+label", textfont_size=11, pull=[0.04, 0, 0])
            fig_donut.update_layout(height=270, margin=dict(l=10, r=10, t=30, b=10),
                                    template=plotly_theme, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            chart_caption("The largest slice is the primary risk driver. Mitigation efforts should focus there first to reduce the composite risk score.")

        section("💧", "Facility Sizing & Revenue Coverage",
                "How the loan fits within the overall farm financial structure")
        fig_wf = go.Figure(go.Waterfall(
            orientation="v", measure=["relative", "relative", "total", "relative", "total"],
            x=["👨‍🌾 Farmer Equity\n(30%)", "🏦 Bank Loan\n(70%)", "Total CapEx", "📈 Operating\nMargin", "🌾 Gross\nRevenue"],
            text=[f"KES {loan_res['total_project_cost_kes']*0.3:,.0f}",
                  f"KES {loan_res['loan_amount_kes']:,}",
                  f"KES {loan_res['total_project_cost_kes']:,}",
                  f"KES {loan_res['expected_revenue_kes'] - loan_res['total_project_cost_kes']:,}",
                  f"KES {loan_res['expected_revenue_kes']:,}"],
            y=[loan_res['total_project_cost_kes']*0.3, loan_res['loan_amount_kes'], 0,
               loan_res['expected_revenue_kes'] - loan_res['total_project_cost_kes'], 0],
            textposition="outside",
            connector={"line": {"color": "#10b981", "width": 1.5}},
            increasing={"marker": {"color": "#10b981"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))
        chart_caption("Blue bars = totals. Green = positive flow. The final 'Gross Revenue' bar should be taller than 'Total CapEx' — confirming the farm is commercially viable.")
        st.plotly_chart(apply_chart_style(fig_wf, 380), use_container_width=True, config={"displayModeBar": False})

        section("🛡️", "Required Loan Covenants & Mitigations",
                "Conditions and risk management steps attached to this credit facility")
        rec_txt = loan_res.get("recommendation", "")
        rec_color = "#10b981" if "Recommend" in rec_txt else "#ef4444"
        st.markdown(f'<div style="background:{rec_color};color:#fff;padding:10px 18px;border-radius:10px;font-weight:700;font-size:0.9rem;margin-bottom:14px;">Underwriting Decision: {rec_txt}</div>', unsafe_allow_html=True)
        cols_m = st.columns(2)
        for i, m in enumerate(loan_res.get("mitigation_strategies", [])):
            cols_m[i % 2].markdown(f"🔒 {m}")

    with tab_port:
        st.markdown('<div class="info-box">ℹ️ <strong>Portfolio simulation:</strong> Runs 10 sample agricultural loans across different crops, counties and farm sizes to provide a portfolio-level view of credit exposure, expected losses, weighted interest rates and net return.</div>', unsafe_allow_html=True)

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
        with st.spinner("Stress-testing loan portfolio..."):
            port_summary, port_df = engine.simulate_loan_portfolio(sample_portfolio)

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("💰 Total Exposure", f"KES {port_summary['total_disbursed_kes']:,}", f"{port_summary['total_loans_count']} loans")
        p2.metric("📈 Weighted Interest", f"{port_summary['weighted_average_interest_rate_pct']:.2f}%", "Portfolio average")
        p3.metric("⚠️ Expected Losses", f"KES {port_summary['expected_credit_losses_kes']:,}", f"{port_summary['weighted_expected_default_rate_pct']:.2f}% default rate")
        p4.metric("📊 Net Portfolio ROI", f"{port_summary['net_projected_roi_pct']:.2f}%", "After credit loss provision")

        section("🫧", "Portfolio Risk vs. Return Matrix",
                "Each bubble = one borrower · Bubble size = loan amount · Top-left = best risk-return position")
        fig_port = px.scatter(port_df,
            x="expected_default_rate_pct", y="interest_rate_pct",
            size="loan_amount_kes", color="credit_grade", hover_name="borrower_name", text="crop",
            labels={"expected_default_rate_pct": "Default Risk (%)", "interest_rate_pct": "Interest Rate (%)",
                    "loan_amount_kes": "Loan (KES)", "credit_grade": "Credit Grade"},
            color_discrete_sequence=["#10b981", "#34d399", "#60a5fa", "#f59e0b", "#ef4444"]
        )
        fig_port.update_traces(textposition="top center",
                               marker=dict(opacity=0.85, line=dict(width=1, color=card_border)))
        chart_caption("Ideal loans are top-left (high interest rate, low default risk). Loans in the bottom-right quadrant carry the most credit risk and should have enhanced collateral.")
        st.plotly_chart(apply_chart_style(fig_port, 430), use_container_width=True, config={"displayModeBar": False})

        section("📋", "Full Portfolio Loan Breakdown", "Complete detail for all 10 simulated facilities")
        st.dataframe(
            port_df[["borrower_name", "county", "crop", "acres", "credit_grade", "loan_amount_kes",
                     "interest_rate_pct", "expected_default_rate_pct", "recommendation"]]
            .rename(columns={"borrower_name": "Borrower", "county": "County", "crop": "Crop",
                             "acres": "Acres", "credit_grade": "Grade", "loan_amount_kes": "Loan (KES)",
                             "interest_rate_pct": "Rate (%)", "expected_default_rate_pct": "Default (%)",
                             "recommendation": "Decision"}),
            use_container_width=True, height=360
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CLIMATE TREND ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_climate:

    section("🌍", f"10-Year Climate Intelligence — {selected_county} County",
            "Aggregated from 116 TAHMO ground stations and NASA POWER satellite reanalysis (2015–2025)")

    if engine.climate_df is not None and not engine.climate_df.empty:
        county_data = engine.climate_df[engine.climate_df["county"] == selected_county]
        if county_data.empty:
            st.info(f"💡 No specific data for {selected_county}. Showing national trend as a reference.")
            county_data = engine.climate_df.head(24)

        st.markdown(
            '<div class="kpi-grid">'
            + kpi("🌧️", "Avg Seasonal Rainfall", f"{county_data['seasonal_rainfall_mm'].mean():.0f} mm", "10-year average")
            + kpi("🌡️", "Mean Temperature", f"{county_data['temp_mean_c'].mean():.1f} °C", "+0.08 °C/year trend")
            + kpi("☀️", "Avg Dry Spell", f"{county_data['max_dry_spell_days'].mean():.0f} days", "Consecutive days < 2 mm rain")
            + kpi("📉", "Rainfall Variability", f"{county_data['seasonal_rainfall_mm'].std()/county_data['seasonal_rainfall_mm'].mean():.2f} CV", "Higher = more unpredictable")
            + '</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-box">💡 <strong>How to read these charts:</strong> The green area shows seasonal rainfall. The red temperature line reveals long-term warming trends. The dry spell histogram shows how frequently long rainless periods occur — a critical indicator of crop stress and drought risk in your county.</div>', unsafe_allow_html=True)

        # ── VIZ 8: Combined Area + Dual-Axis Line ──
        section("📈", "Seasonal Rainfall & Temperature Trend (2015–2025)",
                "Green area = rainfall · Red line = temperature · Hover for exact values")
        label_x = county_data["year"].astype(str) + " " + county_data["season"].str.extract(r'\((\w+)\)', expand=False).fillna("")
        fig8 = make_subplots(specs=[[{"secondary_y": True}]])
        fig8.add_trace(go.Scatter(
            x=label_x, y=county_data["seasonal_rainfall_mm"], name="🌧️ Rainfall (mm)",
            fill="tozeroy",
            fillcolor="rgba(16,185,129,0.18)" if is_dark else "rgba(22,163,74,0.15)",
            line=dict(color="#10b981" if is_dark else "#16a34a", width=2.5)
        ), secondary_y=False)
        fig8.add_trace(go.Scatter(
            x=label_x, y=county_data["temp_mean_c"], name="🌡️ Temperature (°C)",
            line=dict(color="#f87171", width=2.8, dash="solid"),
            mode="lines+markers", marker=dict(size=5)
        ), secondary_y=True)
        fig8.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, gridcolor=card_border)
        fig8.update_yaxes(title_text="Temperature (°C)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
        fig8.update_layout(hovermode="x unified",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        chart_caption("Look for years where the green area drops sharply — these are drought years that strongly affect crop yield. The rising red line indicates regional warming over time.")
        st.plotly_chart(apply_chart_style(fig8, 430), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 9 + 10: Box + Histogram ──
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            section("📦", "Rainfall Distribution by Season",
                    "Spread, median and outliers of seasonal rainfall values")
            fig9 = px.box(engine.climate_df, x="season", y="seasonal_rainfall_mm", color="season",
                points="all", color_discrete_sequence=["#10b981", "#3b82f6"],
                labels={"seasonal_rainfall_mm": "Rainfall (mm)", "season": "Season"})
            fig9.update_traces(boxmean="sd")
            fig9.update_layout(showlegend=False)
            chart_caption("The box shows the middle 50% of seasons. Line inside = median. Individual dots = each season recorded. Whiskers show extreme values.")
            st.plotly_chart(apply_chart_style(fig9, 370), use_container_width=True, config={"displayModeBar": False})

        with col_c2:
            section("📊", "Dry Spell Frequency",
                    "How often different dry spell lengths occur across all recorded seasons")
            fig10 = px.histogram(engine.climate_df, x="max_dry_spell_days", color="season",
                nbins=18, opacity=0.80, barmode="overlay",
                color_discrete_sequence=["#10b981", "#f59e0b"],
                labels={"max_dry_spell_days": "Max Dry Spell Duration (Days)", "season": "Season"})
            chart_caption("Taller bars = this dry spell length is more common. Dry spells exceeding 20 consecutive days create severe water stress for most Kenyan crops.")
            st.plotly_chart(apply_chart_style(fig10, 370), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 11: Station Map ──
        if os.path.exists("data/stations_with_counties.csv"):
            stations_df = pd.read_csv("data/stations_with_counties.csv")
            section("🗺️", "TAHMO Ground Weather Station Network",
                    "116 active automatic weather stations across Kenya — hover for station details")
            map_style = "carto-darkmatter" if is_dark else "carto-positron"
            if hasattr(px, "scatter_map"):
                fig11 = px.scatter_map(stations_df, lat="latitude", lon="longitude",
                    hover_name="name", hover_data=["county", "elevation_msl"],
                    color="elevation_msl", size_max=14, zoom=5.3,
                    center={"lat": 0.5, "lon": 37.5}, map_style=map_style,
                    color_continuous_scale="Greens")
            elif hasattr(px, "scatter_mapbox"):
                fig11 = px.scatter_mapbox(stations_df, lat="latitude", lon="longitude",
                    hover_name="name", hover_data=["county", "elevation_msl"],
                    color="elevation_msl", size_max=14, zoom=5.3,
                    center={"lat": 0.5, "lon": 37.5}, mapbox_style=map_style,
                    color_continuous_scale="Greens")
            else:
                fig11 = px.scatter_geo(stations_df, lat="latitude", lon="longitude",
                    hover_name="name", color="elevation_msl",
                    scope="africa", color_continuous_scale="Greens")
            fig11.update_layout(height=470, margin=dict(l=0, r=0, t=30, b=0))
            chart_caption("Each dot = one weather station. Darker green = higher elevation station. Hover to see station name and county. Climate data from all 116 stations is aggregated into county-level averages.")
            st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar": False})

    else:
        st.info("⚠️ Climate dataset not loaded. Ensure `data/county_climate_historical.csv` is present.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CROP & MARKET CATALOG
# ═══════════════════════════════════════════════════════════════════════════════
with tab_catalog:

    section("📊", "40-Crop Agronomic & Market Intelligence Catalog",
            "Complete crop database across 5 classes with production economics and 5 regional wholesale market prices")

    if engine.crops_df is not None:
        st.markdown('<div class="info-box">💡 <strong>How to use this page:</strong> Filter by crop category, explore the treemap to understand yield vs price relationships, use the scatter chart to find the highest-efficiency crops (high yield at low cost), and compare prices across trading hubs to plan your sales strategy.</div>', unsafe_allow_html=True)

        cat_sel = st.selectbox("🌿 Filter by Crop Category",
                               ["All"] + list(engine.crops_df["category"].unique()))
        df_display = engine.crops_df if cat_sel == "All" else engine.crops_df[engine.crops_df["category"] == cat_sel]

        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("🌾 Crops Shown", len(df_display), f"of 40 total")
        col_s2.metric("📦 Avg Cost / Acre", f"KES {df_display['cost_per_acre_kes'].mean():,.0f}", "KNBS benchmark")
        col_s3.metric("🌱 Avg Yield / Acre", f"{df_display['yield_per_acre_kg'].mean():,.0f} kg", "Season average")

        # ── VIZ 12: Treemap ──
        section("🌳", "Crop Catalog Overview",
                "Size = yield potential per acre · Color = base market price (KES/kg)")
        fig12 = px.treemap(engine.crops_df, path=["category", "crop"],
            values="yield_per_acre_kg", color="base_price_kes_per_kg",
            color_continuous_scale=["#bbf7d0", "#16a34a", "#052e16"] if not is_dark else ["#064e3b", "#10b981", "#d1fae5"],
            labels={"yield_per_acre_kg": "Yield (kg/acre)", "base_price_kes_per_kg": "Price (KES/kg)"})
        fig12.update_traces(textinfo="label+percent parent", textfont_size=12)
        chart_caption("Larger boxes = higher yield potential. Darker green = higher market price. Click any category to zoom in, then click the header to zoom back out.")
        st.plotly_chart(apply_chart_style(fig12, 430), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 13: Yield vs Cost Efficiency ──
        section("🔍", "Yield vs. Cost Efficiency",
                "Find the best-value crops — high yield at low cost per acre")
        fig13 = px.scatter(df_display, x="cost_per_acre_kes", y="yield_per_acre_kg",
            color="category", hover_name="crop", size="base_price_kes_per_kg", text="crop",
            labels={"cost_per_acre_kes": "Production Cost (KES/acre)", "yield_per_acre_kg": "Yield (kg/acre)",
                    "base_price_kes_per_kg": "Price (KES/kg)", "category": "Category"})
        fig13.update_traces(textposition="top center",
                            marker=dict(opacity=0.82, line=dict(width=1, color=card_border)))
        chart_caption("Top-left zone = HIGH yield at LOW cost — the sweet spot. Bubble size = market price per kg. Crops with big bubbles in the top-left are the most commercially attractive.")
        st.plotly_chart(apply_chart_style(fig13, 430), use_container_width=True, config={"displayModeBar": False})

        # ── Data Table ──
        section("📋", "Full Crop Reference Database", "Sortable table — click column headers to sort")
        st.dataframe(
            df_display[["crop", "category", "growth_days", "drought_tolerance",
                        "cost_per_acre_kes", "yield_per_acre_kg", "base_price_kes_per_kg"]]
            .rename(columns={"crop": "Crop", "category": "Category", "growth_days": "Growth Days",
                             "drought_tolerance": "Drought Tolerance", "cost_per_acre_kes": "Cost/Acre (KES)",
                             "yield_per_acre_kg": "Yield/Acre (kg)", "base_price_kes_per_kg": "Base Price (KES/kg)"})
            .sort_values("Yield/Acre (kg)", ascending=False),
            use_container_width=True, height=380
        )

        # ── VIZ 14 + 15: Market Price Comparison & Volatility ──
        if engine.market_df is not None:
            section("💰", "Regional Wholesale Price Comparison",
                    "Select crops to compare their prices across Kenya's 5 major trading hubs")
            sel_crops_cat = st.multiselect("Select crops to compare",
                df_display["crop"].unique().tolist(),
                default=list(df_display["crop"].head(4)))

            if sel_crops_cat:
                m_sub = engine.market_df[engine.market_df["crop"].isin(sel_crops_cat)]
                fig14 = px.bar(m_sub, x="crop", y="market_price", color="market", barmode="group",
                    labels={"market_price": "Price (KES/kg)", "crop": "Crop", "market": "Trading Hub"},
                    color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#06b6d4"]
                    if is_dark else ["#14532d", "#1e40af", "#4c1d95", "#78350f", "#0e7490"])
                fig14.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
                chart_caption("Taller bar = higher price at that market hub. Always sell where your crop's bar is tallest to maximise revenue. Shorter bars still may make sense if transport costs are lower.")
                st.plotly_chart(apply_chart_style(fig14, 400), use_container_width=True, config={"displayModeBar": False})

            section("📦", "Price Volatility by Agricultural Category",
                    "How stable are market prices across each crop class?")
            fig15 = px.box(engine.market_df, x="category", y="volatility_cv",
                color="category",
                labels={"volatility_cv": "Price Volatility (CV)", "category": "Crop Category"})
            fig15.update_layout(showlegend=False, xaxis_tickangle=-20)
            chart_caption("Higher box position = more unpredictable prices. Cash crops (e.g., coffee, tea) often have higher volatility. Lower volatility = more predictable income — better for loan repayment planning.")
            st.plotly_chart(apply_chart_style(fig15, 370), use_container_width=True, config={"displayModeBar": False})

    else:
        st.info("⚠️ Crop database not loaded. Ensure `data/crops_database.csv` is available.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — KILIMOBOT AI ADVISORY AGENT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ai:
    section("🤖", "KilimoBot AI Advisory Agent",
            f"Ask real-time questions about agriculture, climate risks in {selected_county}, credit underwriting, and market arbitrage")

    # API key and engine status banner
    api_key = get_api_key()
    has_gemini = bool(api_key and GEMINI_AVAILABLE)

    col_ai_stat, col_ai_cfg = st.columns([1.8, 1.2])
    with col_ai_stat:
        if has_gemini:
            st.markdown(f"""
            <div style="background:{'rgba(16,185,129,0.12)' if is_dark else '#f0fdf4'};
                        border:1px solid {'#059669' if is_dark else '#86efac'};border-radius:10px;padding:10px 14px;margin-bottom:12px;">
                <span style="color:#10b981;font-weight:800;">● LIVE AI CONNECTED</span> &nbsp;·&nbsp;
                <span style="font-size:0.85rem;color:{text_main};">Powered by <strong>Google Gemini 1.5 Flash</strong> with real-time agronomic reasoning</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:{'rgba(59,130,246,0.12)' if is_dark else '#eff6ff'};
                        border:1px solid {'#2563eb' if is_dark else '#bfdbfe'};border-radius:10px;padding:10px 14px;margin-bottom:12px;">
                <span style="color:#3b82f6;font-weight:800;">💡 PLATFORM KNOWLEDGE ENGINE ACTIVE</span> &nbsp;·&nbsp;
                <span style="font-size:0.85rem;color:{text_main};">Instant offline answers from 116 TAHMO stations & 40-crop database</span>
            </div>
            """, unsafe_allow_html=True)

    with col_ai_cfg:
        with st.expander("⚙️ AI Configuration & API Key", expanded=False):
            st.caption("Enter a Google Gemini API Key for multi-turn generative AI, or use the built-in Knowledge Engine without a key.")
            user_key_input = st.text_input(
                "Gemini API Key",
                value=st.session_state.get("user_gemini_api_key", ""),
                type="password",
                help="Get a free key from Google AI Studio: https://aistudio.google.com/"
            )
            if user_key_input != st.session_state.get("user_gemini_api_key", ""):
                st.session_state.user_gemini_api_key = user_key_input
                if "gemini_chat" in st.session_state:
                    del st.session_state["gemini_chat"]
                st.rerun()

    # Quick question suggestions
    st.markdown("##### 💡 Suggested Questions")
    q_col1, q_col2, q_col3 = st.columns(3)
    quick_prompt = None
    with q_col1:
        if st.button(f"🌾 Best crops for {selected_county}?", use_container_width=True):
            quick_prompt = f"What are the best crops to plant in {selected_county} County for the {selected_season} season?"
        if st.button("🏦 How does the bank calculate my loan?", use_container_width=True):
            quick_prompt = "How does the platform calculate eligible loan amount, DSCR, and interest rate?"
    with q_col2:
        if st.button(f"🌧️ Climate risk in {selected_county}?", use_container_width=True):
            quick_prompt = f"What is the rainfall, temperature, and dry spell risk for {selected_county} in {selected_season}?"
        if st.button("🧠 Rules (AEZ) vs Machine Learning?", use_container_width=True):
            quick_prompt = "What is the difference between Agro-Ecological Rules (AEZ) and Machine Learning models?"
    with q_col3:
        if st.button("💰 Best market for high profit?", use_container_width=True):
            quick_prompt = f"Which regional market hub gives the highest arbitrage price for crops from {selected_county}?"
        if st.button("🗑️ Reset Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            if "gemini_chat" in st.session_state:
                del st.session_state["gemini_chat"]
            st.rerun()

    st.markdown("---")

    # Initialise chat message history in session state
    if "chat_messages" not in st.session_state or not st.session_state.chat_messages:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    f"👋 Hello! I'm **KilimoBot**, your ClimaCrop Intelligence AI assistant.\n\n"
                    f"I'm currently loaded with data for **{selected_county} County** ({selected_season}) using the **{engine_mode}**.\n\n"
                    f"Ask me anything about:\n"
                    f"- 🌾 **Crop recommendations** & agronomic cycle\n"
                    f"- 🌧️ **Rainfall, temperature & dry spell risks** from 116 TAHMO stations\n"
                    f"- 💰 **Wholesale market price arbitrage** across Nairobi, Mombasa, Kisumu, Nakuru & Eldoret\n"
                    f"- 🏦 **Agricultural credit sizing, DSCR, and interest rate calculation**\n\n"
                    f"Type your question below or click any of the suggested question buttons above! 🌿"
                )
            }
        ]

    # Display all messages in history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="🌿" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    # Handle user input from chat_input or quick buttons
    user_input = st.chat_input(f"Ask KilimoBot about agriculture, {selected_county} climate, loans, or markets...")
    prompt_to_run = quick_prompt or user_input

    if prompt_to_run:
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Generate assistant response
        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("KilimoBot is analyzing climate data & crop parameters..."):
                response_text = ""
                # If Gemini API key is available, use Gemini chat
                if has_gemini:
                    chat_sess = init_chat_session(selected_county, selected_season, engine_mode, api_key)
                    if chat_sess:
                        response_text = ask_kiilimobot(chat_sess, prompt_to_run)
                    else:
                        response_text = generate_offline_response(prompt_to_run, selected_county, selected_season, engine, engine_mode)
                else:
                    # Instant built-in Knowledge Engine response
                    response_text = generate_offline_response(prompt_to_run, selected_county, selected_season, engine, engine_mode)

                st.markdown(response_text)
                st.session_state.chat_messages.append({"role": "assistant", "content": response_text})



# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <div style="font-size: 0.96rem; font-weight: 800; color: {primary_color}; margin-bottom: 6px; letter-spacing: -0.2px;">
        🌿 ClimaCrop Intelligence &nbsp;·&nbsp; Kilimo-Smart Decision Platform &nbsp;·&nbsp; Kenya 🇰🇪
    </div>
    <div style="font-size: 0.82rem; color: {text_main}; margin-bottom: 4px; font-weight: 500;">
        Data: TAHMO 116 Ground Stations · NASA POWER Satellite Reanalysis · FAOSTAT · Kenya National Bureau of Statistics
    </div>
    <div style="font-size: 0.78rem; color: {text_muted}; font-weight: 500;">
        Built for agricultural cooperatives, rural SACCOs, development finance institutions and agri-tech researchers.
    </div>
</div>
""", unsafe_allow_html=True)
