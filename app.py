"""
ClimaCrop Intelligence — Kilimo-Smart Climate Decision Support & Agri-Fintech De-Risking Platform
Version 4.0 | Multi-Persona Role-Based Authentication Edition
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
from src.auth import authenticate_user, register_user, get_demo_account, ROLES, DEFAULT_USERS

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & SESSION INITIALIZATION
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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "active_role" not in st.session_state:
    st.session_state.active_role = None
if "entered_platform" not in st.session_state:
    st.session_state.entered_platform = False

# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY THEME SELECTION & THEME VARIABLES
# The sidebar is reserved for the authenticated workspace only — on the
# overview and login screens it's hidden and the theme switch lives in a
# small control at the top of the page instead (see THEME_OPTIONS below).
# ─────────────────────────────────────────────────────────────────────────────
THEME_OPTIONS = ["🌿 Emerald Light", "🌙 Dark Forest", "⚙️ Minimal Slate"]
if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = THEME_OPTIONS[0]

def render_theme_toggle():
    """Compact horizontal theme switch used on the overview & login pages
    (the sidebar theme switch is reserved for the authenticated workspace)."""
    st.radio(
        "Theme", THEME_OPTIONS,
        index=THEME_OPTIONS.index(st.session_state.theme_choice),
        label_visibility="collapsed", horizontal=True, key="theme_choice"
    )

if st.session_state.authenticated:
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

        # Display Theme
        st.markdown("#### 🎨 Display Theme")
        theme_mode = st.radio(
            "Theme",
            THEME_OPTIONS,
            index=THEME_OPTIONS.index(st.session_state.theme_choice),
            label_visibility="collapsed",
            key="theme_choice"
        )
else:
    # Pre-login: no sidebar. Just hide it — the actual theme control is
    # rendered inline on the overview/login pages themselves, further down,
    # so it sits naturally in each page's own compact top row.
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none !important;}"
        "[data-testid='collapsedControl']{display:none !important;}"
        "section.main .block-container{padding-top:0.8rem !important;padding-bottom:1rem !important;max-width:1200px;}</style>",
        unsafe_allow_html=True
    )
    theme_mode = st.session_state.theme_choice

theme_mode = st.session_state.theme_choice

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
/* Reserve space at the bottom of every page so the fixed footer never covers content */
.block-container {{ padding-bottom: 76px !important; }}
[data-testid="stSidebar"] {{
    background-color: {card_bg} !important;
    border-right: 1px solid {card_border} !important;
}}
[data-testid="stSidebar"] img {{ border-radius:14px;transition:transform 0.3s ease,box-shadow 0.3s ease; }}
[data-testid="stSidebar"] img:hover {{ transform:scale(1.02);box-shadow:0 6px 18px rgba(0,0,0,0.2); }}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"] {{
    transition:border-color 0.2s ease,box-shadow 0.2s ease;border-radius:10px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {{
    border-color:{primary_color} !important;box-shadow:0 0 0 3px {'rgba(16,185,129,0.15)' if not is_dark else 'rgba(16,185,129,0.25)'};
}}
[data-testid="stSidebar"] label {{ transition:color 0.15s ease; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ color:{primary_color} !important; }}

/* ── Hero ── */
@keyframes heroGradientShift {{
    0%   {{ background-position:0% 50%; }}
    50%  {{ background-position:100% 50%; }}
    100% {{ background-position:0% 50%; }}
}}
.hero {{
    background: {hero_bg},
        url('https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1600&auto=format&fit=crop&q=85') center/cover no-repeat;
    background-size:200% 200%, cover;
    animation:slideInDown 0.6s ease, heroGradientShift 14s ease-in-out infinite;
    color:#fff; padding:32px 34px 26px; border-radius:20px; margin-bottom:20px;
    box-shadow:0 16px 40px rgba(0,0,0,{'0.45' if is_dark else '0.14'});
    border:1px solid rgba(255,255,255,0.12);
    transition:box-shadow 0.25s ease;
}}
.hero:hover {{ box-shadow:0 20px 52px rgba(16,185,129,{'0.35' if is_dark else '0.22'}); }}
.hero-pill {{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(74,222,128,0.2);backdrop-filter:blur(10px);
    color:#86efac;padding:5px 14px;border-radius:20px;
    font-size:0.75rem;font-weight:700;letter-spacing:0.7px;
    border:1px solid rgba(74,222,128,0.3);margin-bottom:12px;
}}
.hero-title {{ font-size:1.95rem;font-weight:800;letter-spacing:-0.6px;line-height:1.15;margin-bottom:8px;color:#fff; }}
.hero-subtitle {{ font-size:0.94rem;color:rgba(255,255,255,0.85);line-height:1.55;max-width:820px;font-weight:400; }}
.hero-stats {{ display:flex;flex-wrap:wrap;gap:14px;margin-top:16px; }}
.hero-stat {{
    background:rgba(255,255,255,0.1);backdrop-filter:blur(8px);
    padding:8px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.15);
    transition:transform 0.2s ease,background 0.2s ease;
}}
.hero-stat:hover {{ transform:translateY(-3px) scale(1.04);background:rgba(255,255,255,0.18); }}
.hero-stat-val {{ font-size:1.25rem;font-weight:800;color:#4ade80; }}
.hero-stat-lbl {{ font-size:0.68rem;color:rgba(255,255,255,0.7);font-weight:600;letter-spacing:0.5px; }}

/* ── Section Header ── */
.sec-header {{
    display:flex;align-items:flex-start;gap:12px;
    margin:24px 0 12px;padding-bottom:12px;border-bottom:2px solid {card_border};
    animation:slideInUp 0.5s ease forwards;
}}
.sec-icon {{ font-size:1.4rem;flex-shrink:0;padding-top:1px;display:inline-block;transition:transform 0.25s ease; }}
.sec-header:hover .sec-icon {{ transform:scale(1.25) rotate(-6deg); }}
.sec-title {{ font-size:1.1rem;font-weight:800;color:{text_main}; }}
.sec-desc {{ font-size:0.82rem;color:{text_muted};font-weight:500;margin-top:2px;line-height:1.45; }}

/* ── KPI Cards ── */
.kpi-grid {{ display:flex;flex-wrap:wrap;gap:12px;margin-bottom:20px; }}
.kpi-card {{
    background:{card_bg};border-radius:14px;padding:16px 20px;
    border:1px solid {card_border};border-top:4px solid {primary_color};
    flex:1;min-width:150px;
    box-shadow:0 2px 10px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
    transition:transform 0.2s ease,box-shadow 0.2s ease;
    animation:slideInUp 0.5s ease forwards;opacity:0;
}}
.kpi-grid .kpi-card:nth-child(1) {{ animation-delay:0.05s; }}
.kpi-grid .kpi-card:nth-child(2) {{ animation-delay:0.14s; }}
.kpi-grid .kpi-card:nth-child(3) {{ animation-delay:0.23s; }}
.kpi-grid .kpi-card:nth-child(4) {{ animation-delay:0.32s; }}
.kpi-grid .kpi-card:nth-child(5) {{ animation-delay:0.41s; }}
.kpi-card:hover {{
    transform:translateY(-5px) scale(1.015);
    box-shadow:0 12px 28px rgba(16,185,129,{'0.28' if is_dark else '0.16'});
    border-top-width:6px;
}}
.kpi-icon {{ font-size:1.5rem;margin-bottom:6px;display:inline-block;transition:transform 0.25s ease; }}
.kpi-card:hover .kpi-icon {{ transform:scale(1.18); }}
.kpi-label {{ font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:{text_muted};font-weight:700;margin-bottom:5px; }}
.kpi-val {{ font-size:1.6rem;font-weight:800;color:{kpi_val_color};line-height:1.1; }}
.kpi-sub {{ font-size:0.75rem;color:{text_muted};font-weight:500;margin-top:4px; }}

/* ── Crop Cards ── */
.crop-card {{
    background:{card_bg};border:1px solid {card_border};border-radius:16px;
    padding:20px 22px 14px;margin-bottom:16px;border-left:5px solid {primary_color};
    box-shadow:0 4px 16px rgba(0,0,0,{'0.2' if is_dark else '0.05'});
    transition:box-shadow 0.22s ease,transform 0.22s ease,border-left-width 0.22s ease;
    animation:slideInUp 0.5s ease forwards;opacity:0;
}}
.crop-card:nth-of-type(1) {{ animation-delay:0.05s; }}
.crop-card:nth-of-type(2) {{ animation-delay:0.15s; }}
.crop-card:nth-of-type(3) {{ animation-delay:0.25s; }}
.crop-card:nth-of-type(4) {{ animation-delay:0.35s; }}
.crop-card:nth-of-type(5) {{ animation-delay:0.45s; }}
.crop-card:hover {{
    box-shadow:0 12px 32px rgba(16,185,129,{'0.25' if is_dark else '0.14'});
    transform:translateX(4px);
    border-left-width:8px;
}}
.crop-rank {{
    display:inline-flex;align-items:center;justify-content:center;
    width:28px;height:28px;border-radius:50%;
    background:{primary_color};color:#fff;font-size:0.82rem;font-weight:800;margin-right:8px;flex-shrink:0;
    transition:transform 0.25s ease;
}}
.crop-card:hover .crop-rank {{ transform:scale(1.15) rotate(-8deg); }}
.crop-name {{ font-size:1.18rem;font-weight:800;color:{primary_color}; }}
.crop-meta {{ font-size:0.82rem;color:{text_muted};font-weight:500; }}
.advisory-box {{
    background:{advisory_bg};border-left:3px solid {primary_color};
    border-radius:0 8px 8px 0;padding:10px 14px;margin:12px 0;
    font-size:0.88rem;line-height:1.55;color:{text_main};
    animation:slideInUp 0.4s ease forwards;
}}

/* ── Badges ── */
.badge {{ display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;transition:transform 0.18s ease; }}
.badge:hover {{ transform:scale(1.08); }}
.badge-low {{ background:{badge_low_bg};color:{badge_low_txt}; }}
.badge-mod {{ background:{badge_mod_bg};color:{badge_mod_txt}; }}
@keyframes badgePulse {{
    0%,100% {{ box-shadow:0 0 0 0 rgba(239,68,68,0.45); }}
    50%      {{ box-shadow:0 0 0 6px rgba(239,68,68,0); }}
}}
.badge-high {{ background:{badge_high_bg};color:{badge_high_txt};animation:badgePulse 2s infinite; }}

/* ── Info boxes ── */
.briefing-box {{
    background:{briefing_bg};border-left:4px solid {accent_blue};
    border-radius:0 10px 10px 0;padding:14px 18px;
    font-size:0.9rem;line-height:1.6;color:{text_main};margin:14px 0;
    animation:slideInUp 0.45s ease forwards;
}}
.info-box {{
    background:{section_bg};border:1px solid {card_border};
    border-radius:12px;padding:14px 18px;margin:12px 0;
    font-size:0.86rem;color:{text_muted};line-height:1.55;
    animation:slideInUp 0.45s ease forwards;
}}

/* ── Persona Cards (Login Portal) ── */
.persona-card {{
    background:{card_bg};border:1px solid {card_border};
    border-radius:16px;padding:20px;margin-bottom:14px;
    box-shadow:0 4px 16px rgba(0,0,0,{'0.25' if is_dark else '0.05'});
    transition:transform 0.18s ease, box-shadow 0.18s ease;
}}
.persona-card:hover {{
    transform:translateY(-3px);
    box-shadow:0 8px 24px rgba(0,0,0,{'0.35' if is_dark else '0.1'});
}}
.user-profile-box {{
    background:{card_bg};border:1px solid {card_border};border-radius:14px;
    padding:14px 16px;margin-bottom:14px;
    box-shadow:0 2px 8px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
}}

/* ── Metrics ── */
[data-testid="stMetricValue"] {{ font-size:1.2rem !important;font-weight:800 !important;color:{kpi_val_color} !important;transition:transform 0.2s ease; }}
[data-testid="stMetric"]:hover [data-testid="stMetricValue"] {{ transform:scale(1.06); }}
[data-testid="stMetricLabel"] {{ font-size:0.74rem !important;font-weight:700 !important;color:{text_muted} !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap:5px;background:{'rgba(255,255,255,0.04)' if is_dark else '#f3f4f6'};border-radius:12px;padding:4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius:8px;font-weight:600;font-size:0.86rem;padding:8px 18px;color:{text_muted};
    transition:background 0.2s ease,color 0.2s ease,transform 0.15s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background:{'rgba(255,255,255,0.06)' if is_dark else 'rgba(255,255,255,0.7)'};
    color:{primary_color};transform:translateY(-1px);
}}
.stTabs [aria-selected="true"] {{ background:{card_bg} !important;color:{primary_color} !important;box-shadow:0 2px 8px rgba(0,0,0,0.1); }}

/* ── Buttons ── */
.stButton>button {{
    background-color:{primary_color} !important;color:#fff !important;
    border-radius:10px !important;border:none !important;
    font-weight:700 !important;padding:9px 20px !important;font-size:0.88rem !important;
    transition:transform 0.16s ease,box-shadow 0.16s ease,filter 0.16s ease !important;
    box-shadow:0 2px 8px rgba(0,0,0,{'0.25' if is_dark else '0.08'});
}}
.stButton>button:hover {{
    transform:translateY(-2px);filter:brightness(1.08);
    box-shadow:0 8px 20px rgba(16,185,129,0.35) !important;
}}
.stButton>button:active {{ transform:translateY(0);filter:brightness(0.96); }}

/* ── Chart caption ── */
.chart-caption {{
    font-size:0.8rem;color:{text_muted};margin-bottom:6px;
    padding:6px 12px;background:{section_bg};border-radius:6px;
    border-left:2px solid {primary_color};line-height:1.45;
}}

/* ── Chart cards — every Plotly chart sits inside its own elevated card,
   instead of floating bare on the page background ── */
[data-testid="stPlotlyChart"] {{
    background:{card_bg};border:1px solid {card_border};border-radius:16px;
    padding:14px 16px 4px;margin-bottom:10px;
    box-shadow:0 4px 16px rgba(0,0,0,{'0.22' if is_dark else '0.05'});
    transition:box-shadow 0.25s ease,transform 0.25s ease;
    animation:slideInUp 0.55s ease forwards;
}}
[data-testid="stPlotlyChart"]:hover {{
    box-shadow:0 10px 30px rgba(16,185,129,{'0.22' if is_dark else '0.14'});
    transform:translateY(-2px);
}}
/* Plotly's own modebar / hoverlayer should never get clipped by the card radius */
[data-testid="stPlotlyChart"] .plot-container {{ border-radius:12px;overflow:visible; }}

/* ── Footer — fixed to viewport bottom so it stays in one place regardless of page length ── */
.footer {{
    position:fixed;left:0;right:0;bottom:0;z-index:998;
    margin:0;border-radius:0;padding:8px 20px;background:{card_bg};
    border-top:1px solid {card_border};text-align:center;line-height:1.35;
    box-shadow:0 -4px 16px rgba(0,0,0,{'0.30' if is_dark else '0.06'});
    backdrop-filter:blur(6px);
}}
.footer .footer-line {{ font-size:0.74rem;color:{text_muted};font-weight:500; }}
.footer .footer-brand {{ font-size:0.8rem;font-weight:800;color:{primary_color}; }}

/* ── Overview / Landing Page ── */
.landing-hero {{
    position:relative;border-radius:24px;overflow:hidden;margin-bottom:26px;
    padding:64px 40px 54px;text-align:center;color:#fff;
    background:linear-gradient(135deg,rgba(6,30,18,0.90) 0%,rgba(15,70,42,0.85) 55%,rgba(16,120,80,0.80) 100%),
               url('https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1600&auto=format&fit=crop&q=85') center/cover no-repeat;
    box-shadow:0 20px 50px rgba(0,0,0,{'0.5' if is_dark else '0.18'});
}}
.landing-hero-title {{ font-size:2.4rem;font-weight:800;letter-spacing:-0.8px;margin-bottom:10px;line-height:1.15; }}
.landing-hero-sub {{ font-size:1.05rem;color:rgba(255,255,255,0.9);max-width:700px;margin:0 auto 22px;line-height:1.6; }}
.landing-badge {{
    display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.14);
    backdrop-filter:blur(8px);color:#d1fae5;padding:6px 16px;border-radius:20px;
    font-size:0.78rem;font-weight:700;letter-spacing:0.5px;border:1px solid rgba(255,255,255,0.25);
    margin-bottom:16px;
}}
.feature-card {{
    background:{card_bg};border:1px solid {card_border};border-radius:16px;padding:20px 20px 18px;
    height:100%;box-shadow:0 4px 16px rgba(0,0,0,{'0.22' if is_dark else '0.05'});
    transition:transform 0.18s ease,box-shadow 0.18s ease;
}}
.feature-card:hover {{ transform:translateY(-4px);box-shadow:0 10px 26px rgba(0,0,0,{'0.32' if is_dark else '0.1'}); }}
.feature-icon {{
    font-size:1.6rem;width:48px;height:48px;border-radius:12px;display:flex;
    align-items:center;justify-content:center;margin-bottom:10px;
}}
.feature-title {{ font-size:1.02rem;font-weight:800;color:{text_main};margin-bottom:6px; }}
.feature-desc {{ font-size:0.84rem;color:{text_muted};line-height:1.55; }}
.gallery-card {{
    border-radius:16px;overflow:hidden;position:relative;box-shadow:0 6px 20px rgba(0,0,0,{'0.3' if is_dark else '0.08'});
}}
.gallery-caption {{
    position:absolute;left:0;right:0;bottom:0;padding:12px 16px 10px;
    background:linear-gradient(to top,rgba(0,0,0,0.75),rgba(0,0,0,0));
    color:#fff;font-size:0.85rem;font-weight:700;
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
    .block-container {{ padding-top:1rem !important;padding-left:0.5rem !important;padding-right:0.5rem !important;padding-bottom:64px !important; }}
    .sec-title {{ font-size:1rem; }}
    .footer {{ padding:6px 10px; }}
    .footer .footer-line {{ font-size:0.66rem;display:block;white-space:normal; }}
    .footer .footer-brand {{ font-size:0.74rem; }}
    .float-bot {{ bottom:68px;right:14px;width:48px;height:48px;font-size:1.3rem; }}
    .ticker-wrap {{ font-size:0.74rem; }}
    .counter-strip {{ gap:12px; }}
    .counter-card {{ padding:14px 16px; }}
    .counter-val {{ font-size:1.8rem; }}
    .landing-hero-slide {{ min-height:260px; }}
}}

/* ══════════════════════════════════════════════════════
   ANIMATED SLIDESHOW HERO
══════════════════════════════════════════════════════ */
@keyframes slideFade {{
    0%   {{ opacity:1; transform:scale(1.04); }}
    22%  {{ opacity:1; transform:scale(1.04); }}
    28%  {{ opacity:0; transform:scale(1.00); }}
    95%  {{ opacity:0; transform:scale(1.00); }}
    100% {{ opacity:1; transform:scale(1.04); }}
}}
.landing-hero-wrap {{
    position:relative;border-radius:26px;overflow:hidden;
    min-height:340px;margin-bottom:0;
    box-shadow:0 24px 60px rgba(0,0,0,0.28);
}}
.landing-hero-slide {{
    position:absolute;inset:0;background-size:cover;background-position:center;
    opacity:0;animation:slideFade 24s infinite;
    border-radius:26px;
}}
.slide-1 {{ animation-delay:0s;
    background-image:url('https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1600&auto=format&fit=crop&q=85'); }}
.slide-2 {{ animation-delay:6s;
    background-image:url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1600&auto=format&fit=crop&q=85'); }}
.slide-3 {{ animation-delay:12s;
    background-image:url('https://images.unsplash.com/photo-1715198901384-0b7ff9f37a77?w=1600&auto=format&fit=crop&q=85'); }}
.slide-4 {{ animation-delay:18s;
    background-image:url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1600&auto=format&fit=crop&q=80'); }}
.landing-hero-overlay {{
    position:absolute;inset:0;border-radius:26px;
    background:linear-gradient(135deg,rgba(4,20,12,0.88) 0%,rgba(12,55,32,0.82) 55%,rgba(5,95,65,0.76) 100%);
    z-index:1;
}}
.landing-hero-content {{
    position:relative;z-index:2;padding:70px 40px 56px;text-align:center;color:#fff;
}}
.landing-badge-new {{
    display:inline-flex;align-items:center;gap:7px;
    background:rgba(74,222,128,0.18);backdrop-filter:blur(12px);
    color:#86efac;padding:7px 18px;border-radius:22px;
    font-size:0.78rem;font-weight:700;letter-spacing:0.6px;
    border:1px solid rgba(74,222,128,0.35);margin-bottom:18px;
    box-shadow:0 0 20px rgba(74,222,128,0.15);
}}
.landing-title-big {{
    font-size:2.8rem;font-weight:900;letter-spacing:-1px;line-height:1.1;
    margin-bottom:14px;color:#fff;text-shadow:0 2px 20px rgba(0,0,0,0.4);
}}
.landing-sub-big {{
    font-size:1.05rem;color:rgba(255,255,255,0.88);line-height:1.65;
    max-width:720px;margin:0 auto 28px;font-weight:400;
}}
.landing-cta-btn {{
    display:inline-flex;align-items:center;gap:9px;
    background:linear-gradient(135deg,#10b981,#0d9488);
    color:#fff;padding:14px 34px;border-radius:14px;font-size:1rem;
    font-weight:800;letter-spacing:0.2px;text-decoration:none;
    box-shadow:0 8px 28px rgba(16,185,129,0.45);
    border:1px solid rgba(255,255,255,0.2);
    transition:transform 0.2s,box-shadow 0.2s;
}}
.landing-cta-btn:hover {{ transform:translateY(-3px);box-shadow:0 14px 36px rgba(16,185,129,0.55); }}

/* ══════════════════════════════════════════════════════
   SCROLLING STATS TICKER
══════════════════════════════════════════════════════ */
@keyframes ticker-scroll {{
    0%   {{ transform:translateX(0); }}
    100% {{ transform:translateX(-50%); }}
}}
.ticker-wrap {{
    overflow:hidden;background:{'rgba(16,40,26,0.96)' if is_dark else 'rgba(5,46,22,0.92)'};
    border-radius:10px;padding:0;margin:10px 0 20px;
    border:1px solid rgba(74,222,128,0.25);
    box-shadow:0 4px 16px rgba(0,0,0,0.18);
}}
.ticker-inner {{
    display:inline-flex;gap:0;white-space:nowrap;
    animation:ticker-scroll 38s linear infinite;
    padding:10px 0;
}}
.ticker-item {{
    display:inline-flex;align-items:center;gap:6px;
    padding:0 28px;font-size:0.82rem;font-weight:600;color:#a7f3d0;
    border-right:1px solid rgba(74,222,128,0.2);
}}
.ticker-item span {{ color:#4ade80;font-weight:800; }}

/* ══════════════════════════════════════════════════════
   ANIMATED COUNTER STRIP
══════════════════════════════════════════════════════ */
@keyframes countUp {{
    from {{ opacity:0;transform:translateY(20px); }}
    to   {{ opacity:1;transform:translateY(0); }}
}}
.counter-strip {{
    display:flex;flex-wrap:wrap;gap:16px;margin:24px 0;justify-content:center;
}}
.counter-card {{
    flex:1;min-width:160px;max-width:220px;
    background:{'rgba(16,185,129,0.10)' if is_dark else 'rgba(255,255,255,0.92)'};
    border:1px solid {'rgba(74,222,128,0.3)' if is_dark else '#bbf7d0'};
    border-top:4px solid transparent;
    border-image:linear-gradient(90deg,#10b981,#0d9488) 1 0 0 0;
    border-radius:16px;padding:20px 22px;text-align:center;
    backdrop-filter:blur(10px);
    box-shadow:0 4px 20px rgba(0,0,0,{'0.25' if is_dark else '0.05'});
    animation:countUp 0.7s ease forwards;
}}
.counter-card:nth-child(2) {{ animation-delay:0.15s; }}
.counter-card:nth-child(3) {{ animation-delay:0.30s; }}
.counter-card:nth-child(4) {{ animation-delay:0.45s; }}
.counter-val {{
    font-size:2.4rem;font-weight:900;letter-spacing:-1px;line-height:1;
    background:linear-gradient(135deg,#10b981,#0d9488);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;
}}
.counter-lbl {{ font-size:0.76rem;font-weight:700;color:{text_muted};letter-spacing:0.5px;margin-top:5px;text-transform:uppercase; }}
.counter-sub {{ font-size:0.72rem;color:{text_muted};margin-top:3px;font-weight:500; }}

/* ══════════════════════════════════════════════════════
   PULSING LIVE DOT
══════════════════════════════════════════════════════ */
@keyframes pulse-ring {{
    0%   {{ box-shadow:0 0 0 0 rgba(74,222,128,0.7); }}
    70%  {{ box-shadow:0 0 0 8px rgba(74,222,128,0); }}
    100% {{ box-shadow:0 0 0 0 rgba(74,222,128,0); }}
}}
.live-dot {{
    display:inline-block;width:8px;height:8px;border-radius:50%;
    background:#4ade80;animation:pulse-ring 1.8s infinite;
    vertical-align:middle;margin-right:5px;
}}
.live-badge {{
    display:inline-flex;align-items:center;gap:5px;
    background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.3);
    border-radius:20px;padding:4px 12px;
    font-size:0.74rem;font-weight:700;color:#4ade80;letter-spacing:0.4px;
}}

/* ══════════════════════════════════════════════════════
   GLASSMORPHISM FEATURE CARDS
══════════════════════════════════════════════════════ */
.glass-feature-card {{
    border-radius:20px;padding:24px 22px 20px;height:100%;
    background:rgba(255,255,255,{'0.08' if is_dark else '0.82'});
    border:1px solid rgba(255,255,255,{'0.18' if is_dark else '0.60'});
    backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 8px 32px rgba(0,0,0,{'0.28' if is_dark else '0.07'}),
               inset 0 1px 0 rgba(255,255,255,{'0.15' if is_dark else '0.6'});
    transition:transform 0.22s ease,box-shadow 0.22s ease;
    position:relative;overflow:hidden;
}}
.glass-feature-card::before {{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    border-radius:20px 20px 0 0;
}}
.glass-feature-card:hover {{
    transform:translateY(-6px);
    box-shadow:0 18px 42px rgba(0,0,0,{'0.36' if is_dark else '0.12'}),
               inset 0 1px 0 rgba(255,255,255,0.25);
}}
.glass-icon-wrap {{
    width:52px;height:52px;border-radius:14px;display:flex;
    align-items:center;justify-content:center;font-size:1.7rem;
    margin-bottom:13px;box-shadow:0 4px 12px rgba(0,0,0,0.18);
}}
.glass-feature-title {{ font-size:1.05rem;font-weight:800;color:{text_main};margin-bottom:7px; }}
.glass-feature-desc {{ font-size:0.84rem;color:{text_muted};line-height:1.58; }}
.glass-feature-tag {{
    display:inline-block;margin-top:12px;padding:3px 10px;border-radius:20px;
    font-size:0.72rem;font-weight:700;letter-spacing:0.4px;
}}

/* ══════════════════════════════════════════════════════
   TRUST BADGE ROW
══════════════════════════════════════════════════════ */
.trust-row {{
    display:flex;flex-wrap:wrap;gap:10px;justify-content:center;
    align-items:center;margin:20px 0;
}}
.trust-badge {{
    display:inline-flex;align-items:center;gap:7px;
    background:{'rgba(255,255,255,0.06)' if is_dark else 'rgba(255,255,255,0.88)'};
    border:1px solid {'rgba(255,255,255,0.15)' if is_dark else '#d1fae5'};
    border-radius:12px;padding:8px 16px;
    font-size:0.79rem;font-weight:700;
    color:{'#a7f3d0' if is_dark else '#166534'};
    backdrop-filter:blur(8px);
    box-shadow:0 2px 10px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
    transition:transform 0.18s;
}}
.trust-badge:hover {{ transform:translateY(-2px); }}
.trust-badge-icon {{ font-size:1.1rem; }}

/* ══════════════════════════════════════════════════════
   WELCOME BANNER (post-login)
══════════════════════════════════════════════════════ */
@keyframes slideInDown {{
    from {{ opacity:0;transform:translateY(-24px); }}
    to   {{ opacity:1;transform:translateY(0); }}
}}
.welcome-banner {{
    border-radius:16px;padding:18px 24px;margin-bottom:18px;
    background:linear-gradient(135deg,
        {'rgba(4,120,87,0.25)' if is_dark else '#f0fdf4'} 0%,
        {'rgba(5,150,105,0.18)' if is_dark else '#dcfce7'} 100%);
    border:1px solid {'rgba(74,222,128,0.3)' if is_dark else '#bbf7d0'};
    border-left:5px solid #10b981;
    display:flex;align-items:center;gap:16px;
    animation:slideInDown 0.6s ease;
    box-shadow:0 4px 18px rgba(16,185,129,{'0.2' if is_dark else '0.08'});
}}
.welcome-avatar {{
    width:52px;height:52px;border-radius:50%;
    background:linear-gradient(135deg,#10b981,#0d9488);
    display:flex;align-items:center;justify-content:center;
    font-size:1.5rem;flex-shrink:0;
    box-shadow:0 4px 14px rgba(16,185,129,0.35);
}}
.welcome-text-main {{ font-size:1.05rem;font-weight:800;color:{text_main}; }}
.welcome-text-sub {{ font-size:0.84rem;color:{text_muted};font-weight:500;margin-top:3px; }}
.welcome-season-pill {{
    margin-left:auto;flex-shrink:0;
    background:linear-gradient(135deg,#10b981,#0d9488);
    color:#fff;padding:6px 16px;border-radius:20px;
    font-size:0.78rem;font-weight:800;
    box-shadow:0 4px 12px rgba(16,185,129,0.3);
    white-space:nowrap;
}}

/* ══════════════════════════════════════════════════════
   FLOATING KILIMOBOT BUTTON
══════════════════════════════════════════════════════ */
@keyframes float-bob {{
    0%,100% {{ transform:translateY(0) scale(1); }}
    50%      {{ transform:translateY(-7px) scale(1.04); }}
}}
@keyframes glow-ring {{
    0%,100% {{ box-shadow:0 8px 28px rgba(16,185,129,0.45); }}
    50%      {{ box-shadow:0 8px 36px rgba(13,148,136,0.65),0 0 0 8px rgba(16,185,129,0.1); }}
}}
.float-bot {{
    position:fixed;bottom:76px;right:22px;z-index:9999;
    width:58px;height:58px;border-radius:50%;
    background:linear-gradient(135deg,#10b981,#0d9488);
    display:flex;align-items:center;justify-content:center;
    font-size:1.55rem;cursor:pointer;
    animation:float-bob 3s ease-in-out infinite,glow-ring 3s ease-in-out infinite;
    border:2px solid rgba(255,255,255,0.3);
}}
.float-bot-tooltip {{
    position:fixed;bottom:138px;right:18px;z-index:9998;
    background:{'rgba(17,26,20,0.95)' if is_dark else 'rgba(5,46,22,0.93)'};
    color:#a7f3d0;padding:7px 14px;border-radius:10px;
    font-size:0.77rem;font-weight:700;letter-spacing:0.3px;
    white-space:nowrap;backdrop-filter:blur(8px);
    border:1px solid rgba(74,222,128,0.25);
    box-shadow:0 4px 16px rgba(0,0,0,0.3);
    pointer-events:none;
}}
.float-bot-tooltip::after {{
    content:'';position:absolute;top:100%;right:20px;
    border:6px solid transparent;
    border-top-color:rgba(5,46,22,0.93);
}}

/* ══════════════════════════════════════════════════════
   SCROLL REVEAL
══════════════════════════════════════════════════════ */
@keyframes slideInUp {{
    from {{ opacity:0;transform:translateY(32px); }}
    to   {{ opacity:1;transform:translateY(0); }}
}}
.reveal {{ animation:slideInUp 0.65s ease forwards; }}
.reveal-1 {{ animation-delay:0.1s; }}
.reveal-2 {{ animation-delay:0.22s; }}
.reveal-3 {{ animation-delay:0.34s; }}
.reveal-4 {{ animation-delay:0.46s; }}

/* ══════════════════════════════════════════════════════
   SEASON WEATHER MOOD BANNER
══════════════════════════════════════════════════════ */
.season-banner {{
    border-radius:14px;padding:14px 20px;margin-bottom:16px;
    display:flex;align-items:center;gap:14px;
    background:linear-gradient(135deg,
        {'rgba(6,78,59,0.35)' if is_dark else 'rgba(220,252,231,0.9)'} 0%,
        {'rgba(3,105,161,0.20)' if is_dark else 'rgba(219,234,254,0.8)'} 100%);
    border:1px solid {'rgba(74,222,128,0.25)' if is_dark else '#bbf7d0'};
    box-shadow:0 2px 12px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
}}
.season-icon {{ font-size:2rem;flex-shrink:0; }}
.season-title {{ font-size:0.95rem;font-weight:800;color:{primary_color}; }}
.season-desc {{ font-size:0.82rem;color:{text_muted};font-weight:500;margin-top:2px;line-height:1.4; }}


/* ══════════════════════════════════════════════════════
   MULTI-COLOR ACCENTS & COMMAND STRIP
══════════════════════════════════════════════════════ */
.login-wrap {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 18px;
    padding: 20px 24px 16px;
    box-shadow: 0 12px 40px rgba(0,0,0,{'0.30' if is_dark else '0.07'});
    position: relative;
    overflow: hidden;
}}
.login-wrap::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #10b981 0%, #0284c7 33%, #8b5cf6 66%, #f59e0b 100%);
}}

/* Workspace Top Command Strip */
.workspace-command-strip {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 14px;
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
    animation:slideInUp 0.5s ease forwards;
}}
.command-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 700;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
.command-pill:hover {{
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 4px 12px rgba(0,0,0,{'0.25' if is_dark else '0.08'});
}}
.pill-location {{
    background: {'rgba(245,158,11,0.12)' if is_dark else '#fef3c7'};
    color: {'#fbbf24' if is_dark else '#92400e'};
    border: 1px solid {'rgba(245,158,11,0.3)' if is_dark else '#fde68a'};
}}
.pill-season {{
    background: {'rgba(2,132,199,0.12)' if is_dark else '#e0f2fe'};
    color: {'#38bdf8' if is_dark else '#0369a1'};
    border: 1px solid {'rgba(2,132,199,0.3)' if is_dark else '#bae6fd'};
}}
.pill-pipeline {{
    background: {'rgba(16,185,129,0.12)' if is_dark else '#dcfce7'};
    color: {'#4ade80' if is_dark else '#15803d'};
    border: 1px solid {'rgba(16,185,129,0.3)' if is_dark else '#bbf7d0'};
    margin-left: auto;
}}
.pill-engine {{
    background: {'rgba(139,92,246,0.12)' if is_dark else '#ede9fe'};
    color: {'#c084fc' if is_dark else '#6d28d9'};
    border: 1px solid {'rgba(139,92,246,0.3)' if is_dark else '#ddd6fe'};
}}

/* Security footer pill */
.sec-trust-bar {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-top: 18px;
    padding-top: 12px;
    border-top: 1px dashed {card_border};
    font-size: 0.74rem;
    color: {text_muted};
    font-weight: 600;
}}

/* ══════════════════════════════════════════════════════
   NATIVE WIDGET THEMING — bring inputs, selects, sliders,
   tables, expanders & alerts up to the same polish level
   as the custom components above.
══════════════════════════════════════════════════════ */

/* Smooth page entrance so nothing pops in jarringly */
[data-testid="stAppViewContainer"] .main .block-container {{
    animation: pageFadeIn 0.45s ease;
}}
@keyframes pageFadeIn {{
    from {{ opacity:0; transform:translateY(6px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}

/* Custom scrollbar — subtle, on-brand, no jarring default gray */
::-webkit-scrollbar {{ width:10px; height:10px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{
    background: {'rgba(74,222,128,0.35)' if is_dark else 'rgba(22,101,52,0.28)'};
    border-radius:20px; border:2px solid transparent; background-clip:content-box;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {primary_color}; background-clip:content-box;
}}
* {{ scrollbar-width:thin; scrollbar-color:{primary_color} transparent; }}

/* Accessible, on-brand focus ring instead of the default blue browser outline */
a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible,
[tabindex]:focus-visible, [data-baseweb="select"]:focus-within {{
    outline: 2px solid {primary_color} !important;
    outline-offset: 2px !important;
    border-radius: 8px;
}}

/* Text inputs, number inputs, textareas */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {{
    background:{card_bg} !important; color:{text_main} !important;
    border:1.5px solid {card_border} !important; border-radius:10px !important;
    transition:border-color 0.18s ease, box-shadow 0.18s ease !important;
}}
[data-testid="stTextInput"] input:hover,
[data-testid="stNumberInput"] input:hover,
[data-testid="stTextArea"] textarea:hover {{ border-color:{primary_color} !important; }}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color:{primary_color} !important;
    box-shadow:0 0 0 3px {'rgba(16,185,129,0.22)' if is_dark else 'rgba(16,185,129,0.15)'} !important;
}}

/* Select / multiselect (BaseWeb) */
[data-baseweb="select"] > div {{
    background:{card_bg} !important; border:1.5px solid {card_border} !important;
    border-radius:10px !important; transition:border-color 0.18s ease, box-shadow 0.18s ease !important;
}}
[data-baseweb="select"] > div:hover {{ border-color:{primary_color} !important; }}
[data-baseweb="tag"] {{ background:{primary_color} !important; border-radius:6px !important; }}

/* Sliders */
[data-testid="stSlider"] [role="slider"] {{
    background:{primary_color} !important;
    box-shadow:0 2px 8px rgba(16,185,129,0.4) !important;
}}
[data-testid="stSlider"] > div > div > div > div {{ background:{primary_color} !important; }}

/* Checkboxes & radio buttons */
[data-testid="stCheckbox"] label:hover span:first-child,
[data-testid="stRadio"] label:hover span:first-child {{ border-color:{primary_color} !important; }}
[data-testid="stCheckbox"] input:checked + span,
div[role="radiogroup"] label[data-checked="true"] span:first-child {{ background-color:{primary_color} !important; }}

/* Expanders — give them the same card treatment as everything else */
[data-testid="stExpander"] {{
    background:{card_bg} !important; border:1px solid {card_border} !important;
    border-radius:14px !important; overflow:hidden;
    box-shadow:0 3px 12px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
    transition:box-shadow 0.2s ease;
}}
[data-testid="stExpander"]:hover {{ box-shadow:0 8px 22px rgba(16,185,129,{'0.18' if is_dark else '0.1'}); }}
[data-testid="stExpander"] summary {{ font-weight:700 !important; }}

/* DataFrames / tables */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    border:1px solid {card_border} !important; border-radius:14px !important;
    overflow:hidden; box-shadow:0 4px 14px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
}}

/* Alerts — success / info / warning / error */
[data-testid="stAlert"] {{
    border-radius:12px !important; border:1px solid transparent !important;
    box-shadow:0 3px 12px rgba(0,0,0,{'0.2' if is_dark else '0.04'});
    animation:slideInUp 0.4s ease forwards;
}}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {{
    background:{section_bg} !important; border:2px dashed {card_border} !important;
    border-radius:14px !important; transition:border-color 0.2s ease, background 0.2s ease !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color:{primary_color} !important;
    background:{'rgba(16,185,129,0.06)' if is_dark else 'rgba(16,185,129,0.04)'} !important;
}}

/* Progress bar */
[data-testid="stProgress"] > div > div > div {{
    background:linear-gradient(90deg,#10b981,#0d9488) !important;
}}

/* Links inside body text */
[data-testid="stAppViewContainer"] a {{ color:{primary_color} !important; font-weight:600; text-decoration:none; }}
[data-testid="stAppViewContainer"] a:hover {{ text-decoration:underline; }}

/* Code blocks — keep them legible in dark mode */
code {{ border-radius:6px !important; }}

/* Divider — replace the flat default hr with a soft gradient fade */
hr {{
    border:none !important; height:1px !important;
    background:linear-gradient(90deg, transparent, {card_border}, transparent) !important;
    margin:1.2rem 0 !important;
}}

/* Toggle switch */
[data-testid="stToggle"] [role="checkbox"][aria-checked="true"] {{ background-color:{primary_color} !important; }}

/* ══════════════════════════════════════════════════════
   SPLIT-SCREEN LOGIN PANEL
══════════════════════════════════════════════════════ */
.auth-left-panel {{
    position:relative; overflow:hidden; min-height:0;
    border-radius:20px 6px 6px 20px; padding:26px 28px 22px;
    color:#fff; display:flex; flex-direction:column; justify-content:center;
    background:
        linear-gradient(150deg,rgba(4,20,12,0.93) 0%,rgba(11,58,34,0.90) 50%,rgba(6,110,74,0.86) 100%),
        url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&auto=format&fit=crop&q=80') center/cover no-repeat;
    box-shadow:0 20px 50px rgba(0,0,0,{'0.45' if is_dark else '0.16'});
    animation:slideInDown 0.55s ease;
}}
.auth-left-panel::after {{
    content:''; position:absolute; inset:0; z-index:0;
    background:radial-gradient(circle at 85% 15%, rgba(74,222,128,0.22), transparent 55%);
}}
.auth-left-inner {{ position:relative; z-index:1; display:flex; flex-direction:column; height:100%; }}
.auth-brand-row {{ display:flex; align-items:center; gap:9px; margin-bottom:16px; }}
.auth-brand-mark {{
    width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center;
    font-size:1.2rem; background:rgba(255,255,255,0.14); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,0.2);
}}
.auth-brand-name {{ font-weight:800; font-size:0.96rem; letter-spacing:-0.2px; }}
.auth-brand-sub {{ font-size:0.64rem; color:rgba(255,255,255,0.65); font-weight:600; letter-spacing:0.3px; }}
.auth-headline {{
    font-size:1.55rem; font-weight:900; letter-spacing:-0.6px; line-height:1.2;
    margin-bottom:9px; text-shadow:0 2px 18px rgba(0,0,0,0.35);
}}
.auth-headline span {{
    background:linear-gradient(90deg,#4ade80,#86efac);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.auth-sub {{ font-size:0.82rem; color:rgba(255,255,255,0.82); line-height:1.55; max-width:380px; margin-bottom:16px; }}
.auth-feature-list {{ display:flex; flex-direction:column; gap:9px; margin-bottom:16px; }}
.auth-feature-item {{ display:flex; align-items:flex-start; gap:10px; animation:slideInUp 0.5s ease forwards; opacity:0; }}
.auth-feature-list .auth-feature-item:nth-child(1) {{ animation-delay:0.08s; }}
.auth-feature-list .auth-feature-item:nth-child(2) {{ animation-delay:0.18s; }}
.auth-feature-list .auth-feature-item:nth-child(3) {{ animation-delay:0.28s; }}
.auth-feature-check {{
    width:19px; height:19px; border-radius:50%; flex-shrink:0; margin-top:1px;
    background:rgba(74,222,128,0.22); border:1px solid rgba(74,222,128,0.4);
    display:flex; align-items:center; justify-content:center; font-size:0.66rem; color:#86efac;
}}
.auth-feature-txt {{ font-size:0.79rem; color:rgba(255,255,255,0.88); line-height:1.4; }}
.auth-feature-txt strong {{ color:#fff; font-weight:700; }}
.auth-stat-row {{ display:flex; gap:8px; margin-top:4px; flex-wrap:wrap; }}
.auth-stat-chip {{
    background:rgba(255,255,255,0.09); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,0.16); border-radius:11px; padding:7px 12px; flex:1; min-width:80px;
    transition:transform 0.2s ease, background 0.2s ease;
}}
.auth-stat-chip:hover {{ transform:translateY(-3px); background:rgba(255,255,255,0.15); }}
.auth-stat-num {{ font-size:1.02rem; font-weight:800; color:#4ade80; line-height:1.1; }}
.auth-stat-lbl {{ font-size:0.6rem; color:rgba(255,255,255,0.68); font-weight:600; letter-spacing:0.3px; margin-top:2px; }}

.auth-right-panel {{
    background:{card_bg}; border:1px solid {card_border}; border-left:none;
    border-radius:6px 20px 20px 6px; min-height:0;
    padding:24px 30px 20px; box-shadow:0 20px 50px rgba(0,0,0,{'0.30' if is_dark else '0.07'});
    display:flex; flex-direction:column; justify-content:center; animation:slideInUp 0.55s ease;
}}
.auth-right-header {{ text-align:center; margin-bottom:14px; }}
.auth-avatar-ring {{
    width:44px; height:44px; border-radius:50%; margin:0 auto 8px;
    background:linear-gradient(135deg,#10b981,#0d9488); display:flex; align-items:center; justify-content:center;
    font-size:1.35rem; box-shadow:0 8px 22px rgba(16,185,129,0.35);
}}
.auth-right-title {{ font-size:1.12rem; font-weight:800; color:{text_main}; letter-spacing:-0.3px; }}
.auth-right-sub {{ font-size:0.78rem; color:{text_muted}; font-weight:500; margin-top:2px; }}

@media(max-width:900px) {{
    /* On narrow screens, drop the decorative brand panel entirely so the
       actual sign-in form is what people see first — no scrolling past
       marketing copy to reach the fields. */
    .auth-left-panel {{ display:none; }}
    .auth-right-panel {{ border-radius:20px; border-left:1px solid {card_border}; border-top:1px solid {card_border}; min-height:auto; }}
}}

/* ══════════════════════════════════════════════════════
   FLEXIBLE, FLUID TYOGRAPHY — headings scale smoothly with
   viewport width instead of jumping at a single breakpoint.
   (clamp(min, preferred, max) needs no JS and degrades safely.)
══════════════════════════════════════════════════════ */
.hero-title           {{ font-size:clamp(1.35rem, 1.05rem + 1.4vw, 2.1rem)   !important; }}
.landing-title-big    {{ font-size:clamp(1.7rem, 1.1rem + 3vw, 2.9rem)       !important; }}
.landing-hero-title   {{ font-size:clamp(1.6rem, 1.1rem + 2.4vw, 2.5rem)     !important; }}
.auth-headline        {{ font-size:clamp(1.35rem, 1.05rem + 1.4vw, 1.95rem) !important; }}
.counter-val           {{ font-size:clamp(1.7rem, 1.3rem + 1.6vw, 2.5rem)    !important; }}
.sec-title             {{ font-size:clamp(0.98rem, 0.9rem + 0.35vw, 1.14rem) !important; }}

/* ══════════════════════════════════════════════════════
   MOTION PREFERENCE — a calmer, simpler experience for
   anyone whose system asks for reduced motion.
══════════════════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration:0.01ms !important;
        animation-iteration-count:1 !important;
        transition-duration:0.01ms !important;
        scroll-behavior:auto !important;
    }}
}}

/* ══════════════════════════════════════════════════════
   SIDEBAR GROUPING — quiet, consistent cards instead of
   bare "---" dividers, so the control panel reads as one
   organized system rather than a stack of loose widgets.
══════════════════════════════════════════════════════ */
.sidebar-group {{
    background:{section_bg}; border:1px solid {card_border}; border-radius:14px;
    padding:12px 14px 14px; margin-bottom:14px;
}}
.sidebar-group-label {{
    font-size:0.78rem; font-weight:800; color:{primary_color};
    margin-bottom:8px; display:flex; align-items:center; gap:6px;
}}
[data-testid="stSidebar"] hr {{ margin:0.7rem 0 !important; opacity:0.6; }}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW / LANDING PAGE — first thing a visitor sees, before sign in / sign up
# ─────────────────────────────────────────────────────────────────────────────
def render_overview_page():
    # ── Slim utility row: theme switch only (no sidebar on this page) ──
    _ov1, _ov2 = st.columns([4, 1])
    with _ov2:
        render_theme_toggle()

    # ── 1. Animated slideshow hero ──
    st.markdown(f"""
    <div class="landing-hero-wrap">
        <div class="landing-hero-slide slide-1"></div>
        <div class="landing-hero-slide slide-2"></div>
        <div class="landing-hero-slide slide-3"></div>
        <div class="landing-hero-slide slide-4"></div>
        <div class="landing-hero-overlay"></div>
        <div class="landing-hero-content">
            <div class="landing-badge-new">
                <span class="live-dot"></span>
                🌍 Kenya · 26 Counties · 10 Years of Real Climate Data
            </div>
            <div class="landing-title-big">🌾 ClimaCrop Intelligence</div>
            <div class="landing-sub-big">
                Bridging 10-year localized climate patterns, 40-crop agronomic intelligence,
                and institutional credit underwriting — one platform for cooperatives, banks,
                SACCOs and climate researchers across Kenya.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Scrolling ticker bar ──
    ticker_items = [
        ("🌧️", "Avg Long-Rains Rainfall:", "842 mm", "Nakuru County"),
        ("🌡️", "Kenya Mean Temperature:", "22.4 °C", "+0.08 °C per year trend"),
        ("🌾", "Highest-Suitability Crop:", "Irish Potatoes", "Long-rains season"),
        ("💰", "Best Market Hub:", "Nairobi Wholesale", "Highest composite price"),
        ("📡", "Active TAHMO Stations:", "116", "Across 26 counties"),
        ("🏦", "Avg Agricultural Loan Rate:", "14.2%", "Climate-adjusted rate"),
        ("🌿", "Crops in Database:", "40 crops", "5 categories tracked"),
        ("☀️", "Longest Recorded Dry Spell:", "38 days", "Northern counties"),
    ]
    items_html = "".join(
        f'<div class="ticker-item">'
        f'<span>{icon}</span>'
        f'<span style="color:rgba(167,243,208,0.7);font-weight:500;">{label}</span>'
        f'<span>{val}</span>'
        f'<span style="font-size:0.72rem;opacity:0.6;margin-left:2px;">({note})</span>'
        f'</div>'
        for icon, label, val, note in ticker_items
    )
    # Duplicate for seamless loop
    st.markdown(f"""
    <div class="ticker-wrap">
        <div class="ticker-inner">
            {items_html}
            {items_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. Animated counter strip ──
    st.markdown(f"""
    <div class="counter-strip">
        <div class="counter-card reveal reveal-1">
            <div class="counter-val">116</div>
            <div class="counter-lbl">Weather Stations</div>
            <div class="counter-sub">TAHMO Ground Network</div>
        </div>
        <div class="counter-card reveal reveal-2">
            <div class="counter-val">40</div>
            <div class="counter-lbl">Crops Profiled</div>
            <div class="counter-sub">Across 5 agronomic classes</div>
        </div>
        <div class="counter-card reveal reveal-3">
            <div class="counter-val">26</div>
            <div class="counter-lbl">Counties Covered</div>
            <div class="counter-sub">Full county-level data</div>
        </div>
        <div class="counter-card reveal reveal-4">
            <div class="counter-val">10yr</div>
            <div class="counter-lbl">Climate History</div>
            <div class="counter-sub">2015–2025 satellite + ground</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4. What the system does ──
    st.markdown(f"""
    <div style="text-align:center;max-width:780px;margin:0 auto 28px;">
        <div style="font-size:1.08rem;font-weight:800;color:{primary_color};margin-bottom:10px;">
            Beyond "Will It Rain?" — Decision Intelligence for Kenyan Agriculture
        </div>
        <div style="font-size:0.91rem;color:{text_muted};line-height:1.72;">
            For a cooperative, ClimaCrop recommends <strong>what to plant</strong> this season and <strong>where to sell</strong> for
            the highest price. For a bank or SACCO, it prices loans against <strong>real climate and market risk</strong>.
            Everything is powered by 116 TAHMO ground stations, NASA POWER satellite reanalysis, and FAOSTAT economics.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 5. Glassmorphism feature cards ──
    features = [
        ("🌱", "linear-gradient(135deg,#10b981,#059669)", "#dcfce7", "#166534",
         "#f0fdf4", "Cooperative Advisory",
         "Rank 40 Kenyan crops for your county and season by climate fit, yield potential and net farm profit. Know exactly what to grow.",
         "👨‍🌾 Farmers & Cooperatives", "#dcfce7", "#166534"),
        ("🏦", "linear-gradient(135deg,#3b82f6,#1d4ed8)", "#dbeafe", "#1e40af",
         "#eff6ff", "Bank & Credit Risk",
         "Climate-adjusted loan sizing, interest rate pricing, and portfolio-level default stress testing for agricultural finance.",
         "🏦 Banks & SACCOs", "#dbeafe", "#1e40af"),
        ("🌍", "linear-gradient(135deg,#8b5cf6,#6d28d9)", "#ede9fe", "#5b21b6",
         "#f5f3ff", "Climate Intelligence",
         "10-year rainfall, temperature and dry-spell trends visualized county by county from 116 ground weather stations.",
         "🌍 Researchers", "#ede9fe", "#5b21b6"),
        ("📊", "linear-gradient(135deg,#f59e0b,#d97706)", "#fef3c7", "#92400e",
         "#fffbeb", "Crop & Market Catalog",
         "Full agronomic and financial profiles for 40 crops plus live wholesale price comparison across 5 regional trading hubs.",
         "📈 All Users", "#fef3c7", "#92400e"),
    ]
    fcols = st.columns(4)
    for col, (icon, icon_bg, icon_bg_light, icon_fg, card_bg_light, title, desc, tag, tag_bg, tag_fg) in zip(fcols, features):
        with col:
            _card_bg = f"rgba(255,255,255,0.07)" if is_dark else card_bg_light
            st.markdown(f"""
            <div class="glass-feature-card reveal" style="{'border-top:3px solid transparent;background-image:'+icon_bg+',linear-gradient('+_card_bg+','+_card_bg+');background-origin:border-box;background-clip:border-box,padding-box;' if False else ''}">
                <div class="glass-icon-wrap" style="background:{icon_bg};">
                    <span style="filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3));">{icon}</span>
                </div>
                <div class="glass-feature-title">{title}</div>
                <div class="glass-feature-desc">{desc}</div>
                <div class="glass-feature-tag" style="background:{icon_bg_light};color:{icon_fg};">{tag}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    # ── 6. Trust badges ──
    st.markdown(f"""
    <div style="text-align:center;font-size:0.8rem;color:{text_muted};font-weight:700;margin-bottom:12px;letter-spacing:0.5px;text-transform:uppercase;">
        Powered by verified data from
    </div>
    <div class="trust-row">
        <div class="trust-badge"><span class="trust-badge-icon">📡</span> TAHMO · 116 Ground Stations</div>
        <div class="trust-badge"><span class="trust-badge-icon">🛰️</span> NASA POWER · Satellite Reanalysis</div>
        <div class="trust-badge"><span class="trust-badge-icon">🌾</span> FAOSTAT · Crop Economics</div>
        <div class="trust-badge"><span class="trust-badge-icon">📊</span> Kenya National Bureau of Statistics</div>
        <div class="trust-badge"><span class="live-dot"></span> Gemini AI · KilimoBot</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 7. CTA ──
    st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
    _lc, _mc, _rc = st.columns([1, 1.1, 1])
    with _mc:
        if st.button("🚀 Get Started — Sign In / Sign Up", use_container_width=True, key="btn_enter_platform"):
            st.session_state.entered_platform = True
            st.rerun()
    st.markdown(f"""
    <div style="text-align:center;font-size:0.78rem;color:{text_muted};margin-top:10px;">
        Free demo accounts available · No credit card required
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION GATEWAY — If not authenticated, show overview → login / signup
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    if not st.session_state.entered_platform:
        render_overview_page()
        st.stop()

    # Compact Navigation & Header — back link, live status, theme switch, all on one slim row
    top_c1, top_c2, top_c3 = st.columns([1, 2, 1])
    with top_c1:
        if st.button("← Back", key="btn_back_to_overview"):
            st.session_state.entered_platform = False
            st.rerun()
    with top_c2:
        st.markdown(f"""
        <div style="text-align:center;font-size:0.74rem;color:{text_muted};padding-top:9px;">
            <span class="live-dot"></span>
            <strong>TAHMO Live:</strong> 116 Stations · NASA POWER Sync
        </div>
        """, unsafe_allow_html=True)
    with top_c3:
        render_theme_toggle()

    # ── SPLIT-SCREEN LOGIN: brand/showcase panel (left) + auth card (right) ──
    auth_l, auth_r = st.columns([1, 1.15], gap="small")

    with auth_l:
        st.markdown(f"""
        <div class="auth-left-panel">
          <div class="auth-left-inner">
            <div class="auth-brand-row">
                <div class="auth-brand-mark">🌿</div>
                <div>
                    <div class="auth-brand-name">ClimaCrop Intelligence</div>
                    <div class="auth-brand-sub">KILIMO-SMART PLATFORM · KENYA 🇰🇪</div>
                </div>
            </div>
            <div class="auth-headline">Climate-smart decisions,<br><span>backed by real data.</span></div>
            <div class="auth-sub">
                Sign in to plan crops, price agricultural loans and read 10 years of climate
                trends — built on 116 TAHMO ground stations, NASA POWER and FAOSTAT.
            </div>
            <div class="auth-feature-list">
                <div class="auth-feature-item">
                    <div class="auth-feature-check">✓</div>
                    <div class="auth-feature-txt"><strong>Cooperative Advisory</strong> — rank 40 crops by climate fit, yield &amp; profit</div>
                </div>
                <div class="auth-feature-item">
                    <div class="auth-feature-check">✓</div>
                    <div class="auth-feature-txt"><strong>Bank &amp; Credit Risk</strong> — climate-adjusted loan sizing &amp; pricing</div>
                </div>
                <div class="auth-feature-item">
                    <div class="auth-feature-check">✓</div>
                    <div class="auth-feature-txt"><strong>Climate Intelligence</strong> — 10-year rainfall &amp; dry-spell trends by county</div>
                </div>
            </div>
            <div class="auth-stat-row">
                <div class="auth-stat-chip"><div class="auth-stat-num">116</div><div class="auth-stat-lbl">STATIONS</div></div>
                <div class="auth-stat-chip"><div class="auth-stat-num">40</div><div class="auth-stat-lbl">CROPS</div></div>
                <div class="auth-stat-chip"><div class="auth-stat-num">26</div><div class="auth-stat-lbl">COUNTIES</div></div>
                <div class="auth-stat-chip"><div class="auth-stat-num">10yr</div><div class="auth-stat-lbl">HISTORY</div></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with auth_r:
        st.markdown('<div class="auth-right-panel">', unsafe_allow_html=True)
        st.markdown("""
        <div class="auth-right-header">
            <div class="auth-avatar-ring">🌿</div>
            <div class="auth-right-title">Welcome to the Portal</div>
            <div class="auth-right-sub">Sign in to your account or create a new one</div>
        </div>
        """, unsafe_allow_html=True)

        tab_signin, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab_signin:
            with st.form("form_signin_main", clear_on_submit=False):
                in_username = st.text_input("👤 Username", placeholder="e.g. coop_user or your username")
                in_password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
                btn_submit = st.form_submit_button("🚀 Sign In to Portal", use_container_width=True)

                if btn_submit:
                    if not in_username or not in_password:
                        st.error("Please enter both username and password.")
                    else:
                        user_auth = authenticate_user(in_username, in_password)
                        if user_auth:
                            st.session_state.authenticated = True
                            st.session_state.user          = user_auth
                            st.session_state.active_role   = user_auth["role"]
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password. Please try again.")

        with tab_signup:
            with st.form("form_signup_new", clear_on_submit=False):
                su_c1, su_c2 = st.columns(2)
                with su_c1:
                    reg_name  = st.text_input("Full Name", placeholder="e.g. Samuel Kipchumba")
                    reg_user  = st.text_input("Username",  placeholder="e.g. sam_farmer")
                    reg_pass  = st.text_input("Password",  type="password", placeholder="Min 4 chars")
                    reg_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                with su_c2:
                    role_options = {
                        "cooperative":  "👨‍🌾 Cooperative Member / Farmer",
                        "bank_officer": "🏦 Bank & SACCO Credit Officer",
                        "researcher":   "🌍 Climate & Agronomy Researcher",
                    }
                    reg_role_key = st.selectbox(
                        "Your Role",
                        list(role_options.keys()),
                        format_func=lambda x: role_options[x]
                    )
                    reg_org = st.text_input("Organization / SACCO", placeholder="e.g. Molo Agribusiness")
                    reg_county = st.selectbox("Primary County", [
                        "Nakuru", "Uasin Gishu", "Kiambu", "Nyeri", "Nyandarua",
                        "Machakos", "Makueni", "Kitui", "Bungoma", "Kakamega",
                        "Kisumu", "Siaya", "Migori", "Kisii", "Kericho", "Bomet",
                        "Narok", "Embu", "Tharaka Nithi", "Kwale", "Kilifi",
                        "Mombasa", "Taita Taveta", "West Pokot", "Turkana", "Laikipia"
                    ])

                btn_signup = st.form_submit_button("🌿 Register & Sign In", use_container_width=True)
                if btn_signup:
                    if not reg_user or not reg_pass or not reg_name:
                        st.error("Full name, username and password are all required.")
                    elif len(reg_pass) < 4:
                        st.error("Password must be at least 4 characters long.")
                    elif reg_pass != reg_pass2:
                        st.error("⚠️ Passwords do not match. Please re-enter them.")
                    else:
                        ok, msg = register_user(
                            username=reg_user,
                            password=reg_pass,
                            full_name=reg_name,
                            role=reg_role_key,
                            organization=reg_org or "ClimaCrop Partner",
                            county=reg_county
                        )
                        if ok:
                            st.success(f"✅ Account created! Signing you in as {reg_name}…")
                            new_auth = authenticate_user(reg_user, reg_pass)
                            if new_auth:
                                st.session_state.authenticated = True
                                st.session_state.user          = new_auth
                                st.session_state.active_role   = new_auth["role"]
                                st.rerun()
                        else:
                            st.error(f"❌ {msg}")

        # Security Trust strip inside login card
        st.markdown(f"""
        <div class="sec-trust-bar" style="margin-top:10px;padding-top:8px;font-size:0.7rem;">
            <span>🔒 SHA-256 Encrypted</span>
            <span>·</span>
            <span>🛡️ Role-Based Segmentation</span>
            <span>·</span>
            <span>⚡ 116 Active Ground Feeds</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATED USER SESSION & SIDEBAR CONTROLS
# ─────────────────────────────────────────────────────────────────────────────
current_user = st.session_state.user or {}
user_role = st.session_state.active_role or current_user.get("role", "cooperative")
role_meta = ROLES.get(user_role, ROLES["cooperative"])

with st.sidebar:
    st.markdown("---")
    # Multi-color user profile badge card
    _role_aura = {
        "cooperative":  "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "bank_officer": "linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%)",
        "researcher":   "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "admin":        "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
    }.get(user_role, "linear-gradient(135deg, #10b981 0%, #059669 100%)")

    st.markdown(f"""
    <div class="user-profile-box" style="border-left: 4px solid {role_meta['badge_color']};">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width:40px;height:40px;border-radius:50%;background:{_role_aura};display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;color:#fff;">
                {role_meta['icon']}
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:0.92rem;font-weight:800;color:{text_main};line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {current_user.get('full_name', 'Authorized User')}
                </div>
                <div style="font-size:0.75rem;color:{text_muted};font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {current_user.get('organization', 'ClimaCrop Partner')}
                </div>
            </div>
        </div>
        <div style="margin-top: 8px; display: flex; align-items: center; justify-content: space-between;">
            <span style="background: {role_meta['badge_color']}; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.4px;">
                {role_meta['name'].upper()}
            </span>
            <span style="font-size:0.7rem;color:{text_muted};font-weight:600;">
                📍 {current_user.get('county', 'Kenya')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sign Out Button
    if st.button("🚪 Sign Out", key="btn_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.active_role = None
        if "gemini_chat" in st.session_state:
            del st.session_state["gemini_chat"]
        st.rerun()

    # If user is admin, allow switching persona on the fly
    if current_user.get("role") == "admin":
        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🎭 Persona Preview")
        selected_preview_role = st.selectbox(
            "Switch Role View",
            list(ROLES.keys()),
            format_func=lambda r: f"{ROLES[r]['icon']} {ROLES[r]['name']}",
            index=list(ROLES.keys()).index(user_role),
            label_visibility="collapsed"
        )
        if selected_preview_role != user_role:
            st.session_state.active_role = selected_preview_role
            st.rerun()

    st.markdown("---")

    # Region & Calendar Scope Controls
    st.markdown("""
    <div class="sidebar-group-label"><span>🎯</span> Geographic &amp; Seasonal Scope</div>
    """, unsafe_allow_html=True)

    counties_list = [
        "Nakuru", "Uasin Gishu", "Kiambu", "Nyeri", "Nyandarua", "Machakos", "Makueni", "Kitui",
        "Bungoma", "Kakamega", "Kisumu", "Siaya", "Migori", "Kisii", "Kericho", "Bomet",
        "Narok", "Embu", "Tharaka Nithi", "Kwale", "Kilifi", "Mombasa", "Taita Taveta",
        "West Pokot", "Turkana", "Laikipia"
    ]
    default_county_idx = 0
    if current_user.get("county") in counties_list:
        default_county_idx = counties_list.index(current_user["county"])

    selected_county = st.selectbox("📍 Focus County", counties_list, index=default_county_idx)
    selected_season = st.selectbox("📅 Planting Season", ["Long Rains (MAM)", "Short Rains (OND)"], index=0)

    st.markdown("---")

    # Advisory Engine selection (compact in sidebar, full explanation in workspace command strip)
    st.markdown("""
    <div class="sidebar-group-label"><span>🧠</span> Advisory Engine</div>
    """, unsafe_allow_html=True)
    engine_mode = st.radio(
        "Engine",
        ["📐 Agro-Ecological Rules (AEZ)", "🤖 Machine Learning (Random Forest)"],
        index=0,
        label_visibility="collapsed"
    )
    use_rule_based = engine_mode.startswith("📐")

    # Clean bottom telemetry status pill
    st.markdown(f"""
    <div style="margin-top:20px;padding:10px 12px;border-radius:10px;background:{'rgba(16,185,129,0.08)' if is_dark else '#f0fdf4'};border:1px solid {'rgba(16,185,129,0.2)' if is_dark else '#bbf7d0'};font-size:0.75rem;color:{text_muted};">
        <span class="live-dot"></span><strong>Pipeline:</strong> 116 TAHMO Stations Live<br>
        <span style="opacity:0.8;">NASA POWER Satellite &amp; FAOSTAT Sync</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD ENGINES & HELPERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🌱 Loading ClimaCrop intelligence engines...")
def load_engine():
    return FinancialDecisionEngine()

engine = load_engine()


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


# Shared categorical palette so any chart that doesn't set its own explicit
# colors still lands on-brand — greens/blue/amber/rose in a consistent order.
CHART_COLORWAY = (
    ["#34d399", "#60a5fa", "#fbbf24", "#f472b6", "#a78bfa", "#22d3ee", "#f87171", "#4ade80"]
    if is_dark else
    ["#16a34a", "#2563eb", "#d97706", "#db2777", "#7c3aed", "#0891b2", "#dc2626", "#059669"]
)


def apply_chart_style(fig, height=400):
    fig.update_layout(
        height=height,
        margin=dict(l=14, r=14, t=42, b=14),
        template=plotly_theme,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color=text_main),
        title_font=dict(size=13, color=text_main),
        colorway=CHART_COLORWAY,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=card_border, borderwidth=1, font=dict(size=11)),
        hoverlabel=dict(
            bgcolor=card_bg, bordercolor=primary_color,
            font=dict(family="Inter, sans-serif", size=12, color=text_main),
            align="left",
        ),
        xaxis=dict(showgrid=True, gridcolor=card_border, gridwidth=0.6, zeroline=False,
                   linecolor=card_border, showline=True, ticks="outside", tickcolor=card_border,
                   title_font=dict(size=12, color=text_muted)),
        yaxis=dict(showgrid=True, gridcolor=card_border, gridwidth=0.6, zeroline=False,
                   linecolor=card_border, showline=True, ticks="outside", tickcolor=card_border,
                   title_font=dict(size=12, color=text_muted)),
        uniformtext=dict(minsize=9, mode="hide"),
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
# PERSONALIZED HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
engine_badge = "📐 Agro-Ecological Rules (AEZ)" if use_rule_based else "🤖 Random Forest ML"

# Personalized welcome banner
import datetime as _dt
_hour = _dt.datetime.now().hour
_greeting = "Good morning" if _hour < 12 else ("Good afternoon" if _hour < 17 else "Good evening")
_first_name = current_user.get("full_name", "User").split()[0]
_season_emoji = {"Long Rains": "🌧️", "Short Rains": "🌦️", "Dry Season": "☀️", "Cool Season": "🌬️"}.get(
    next((k for k in ["Long Rains","Short Rains","Dry Season","Cool Season"] if k.lower() in selected_season.lower()), "Long Rains"), "🌿")
_role_welcome = {
    "cooperative":  f"Your crop recommendations for {selected_county} are ready for review.",
    "bank_officer": f"Climate risk data for {selected_county} loan portfolio is updated.",
    "researcher":   f"10-year climate dataset for {selected_county} County is loaded.",
    "admin":        "Full platform access · All 5 modules active.",
}.get(user_role, "Welcome to ClimaCrop Intelligence.")

st.markdown(f"""
<div class="welcome-banner">
    <div class="welcome-avatar">{role_meta['icon']}</div>
    <div style="flex:1;">
        <div class="welcome-text-main">{_greeting}, {_first_name}! 👋</div>
        <div class="welcome-text-sub">{_role_welcome}</div>
    </div>
    <div class="welcome-season-pill">{_season_emoji} {selected_season}</div>
</div>
""", unsafe_allow_html=True)

# Floating KilimoBot button
st.markdown("""
<div class="float-bot" title="Ask KilimoBot AI">🤖</div>
<div class="float-bot-tooltip">Ask KilimoBot AI</div>
""", unsafe_allow_html=True)

# Role-specific subtitle
if user_role == "cooperative":
    role_subtitle = f"Welcome **{current_user.get('full_name')}**! You are viewing the **Cooperative Advisory Console** for **{current_user.get('organization', 'your cooperative')}**. Optimize member crop selection, compare farm yield payoffs, and find the highest-paying wholesale market hubs."
elif user_role == "bank_officer":
    role_subtitle = f"Welcome **{current_user.get('full_name')}**! You are viewing the **Institutional Credit Underwriting Portal** for **{current_user.get('organization', 'your financial institution')}**. Automate 70% CapEx facility sizing, test DSCR coverage, and simulate multi-borrower climate risk defaults."
elif user_role == "researcher":
    role_subtitle = f"Welcome **{current_user.get('full_name')}**! You are viewing the **Agro-Meteorology & Climate Research Console** for **{current_user.get('organization', 'your institution')}**. Access 10-year historical climate reanalysis, 116 TAHMO ground stations, and benchmark rule-based vs ML models."
else:
    role_subtitle = f"Welcome **{current_user.get('full_name')}**! You have **Full Administrator Access**. Monitor live engines, evaluate all 4 stakeholder perspectives, and audit data provenance."

st.markdown(f"""
<div class="hero">
    <div class="hero-pill">
        <span class="live-dot" style="width:7px;height:7px;margin-right:4px;"></span>
        {role_meta['icon']} {role_meta['name'].upper()} · {selected_county.upper()} · {selected_season.upper()}
    </div>
    <div class="hero-title">ClimaCrop Intelligence</div>
    <div class="hero-subtitle">
        {role_subtitle}
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
# WORKSPACE COMMAND & SCOPE STRIP
# ─────────────────────────────────────────────────────────────────────────────
_engine_badge_str = "📐 AEZ Agro-Ecological Rules (Explainable Bands)" if use_rule_based else "🤖 Random Forest ML (Probabilistic Multi-Factor)"

st.markdown(f"""
<div class="workspace-command-strip">
    <div class="command-pill pill-location">
        <span style="font-size:1.1rem;">📍</span>
        <span>County: <strong>{selected_county}</strong></span>
    </div>
    <div class="command-pill pill-season">
        <span style="font-size:1.1rem;">📅</span>
        <span>Season: <strong>{selected_season}</strong></span>
    </div>
    <div class="command-pill pill-engine">
        <span style="font-size:1.1rem;">🧠</span>
        <span>Engine: <strong>{_engine_badge_str}</strong></span>
    </div>
    <div class="command-pill pill-pipeline">
        <span class="live-dot"></span>
        <span>116 Ground Stations Live</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TOP-TAB NAVIGATION — Role-specific platform views
# ─────────────────────────────────────────────────────────────────────────────
# Tab definitions per role:
#   cooperative  → Cooperative Advisory | Crop & Market Catalog | KilimoBot AI
#   bank_officer → Bank & Credit Risk   | Crop & Market Catalog | KilimoBot AI
#   researcher   → Climate Trends | Cooperative Advisory (read-only) | Crop & Market Catalog | KilimoBot AI
#   admin        → All 5 tabs

_ALL_TAB_LABELS = {
    "coop":    "🌱 Cooperative Advisory",
    "bank":    "🏦 Bank & Credit Risk",
    "climate": "🌍 Climate Trends",
    "catalog": "📊 Crop & Market Catalog",
    "ai":      "🤖 KilimoBot AI Assistant",
}

# Map role → ordered list of tab keys shown
_ROLE_TABS = {
    "cooperative":  ["coop",    "catalog", "ai"],
    "bank_officer": ["bank",    "catalog", "ai"],
    "researcher":   ["climate", "coop",    "catalog", "ai"],
    "admin":        ["coop",    "bank",    "climate", "catalog", "ai"],
}
_active_keys = _ROLE_TABS.get(user_role, _ROLE_TABS["admin"])
_tab_labels   = [_ALL_TAB_LABELS[k] for k in _active_keys]
_tab_objects  = st.tabs(_tab_labels)
_tab_map      = dict(zip(_active_keys, _tab_objects))

# Provide None-safe handles: only keys in _tab_map are real
tab_coop    = _tab_map.get("coop")
tab_bank    = _tab_map.get("bank")
tab_climate = _tab_map.get("climate")
tab_catalog = _tab_map.get("catalog")
tab_ai      = _tab_map.get("ai")

# Helper: render a tab block only when that tab is part of the current role's view
from contextlib import nullcontext as _nullctx

def _tab(t):
    """Return the tab context or a no-op context if the tab is hidden for this role."""
    return t if t is not None else _nullctx()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — COOPERATIVE ADVISORY
# ═══════════════════════════════════════════════════════════════════════════════
if tab_coop is not None:
    with tab_coop:
        platform_view = "🌱 Cooperative Advisory"

        section("🌱", f"Cooperative Advisory — {selected_county} County",
                f"Evaluating 40 Kenyan crops using {engine_badge} for the {selected_season} season")

        # ── Season weather mood banner ──
        _smood = {
            "Long Rains": ("🌧️", "#3b82f6", "Long Rains Season — Bimodal Wet Phase",
                "Above-average moisture supports maize, beans and high-water crops. Ideal for planting depth-rooted crops."),
            "Short Rains": ("🌦️", "#0d9488", "Short Rains Season — Secondary Wet Phase",
                "Moderate, reliable rainfall. Excellent for fast-maturing legumes, vegetables and horticultural crops."),
            "Dry Season": ("☀️", "#f59e0b", "Dry Season — Irrigation & Drought-Tolerant Crops",
                "Limited rainfall. Focus on drought-tolerant crops (sorghum, millet, cassava) or irrigated horticulture."),
            "Cool Season": ("🌬️", "#8b5cf6", "Cool Dry Season — Highland Crops Optimal",
                "Cool temperatures favour tea, pyrethrum and brassicas. Moisture retention is high in highland counties."),
        }
        _sk = next((k for k in _smood if k.lower() in selected_season.lower()), "Long Rains")
        _sicon, _scolor, _stitle, _sdesc = _smood[_sk]
        st.markdown(f"""
        <div class="season-banner">
            <div class="season-icon">{_sicon}</div>
            <div>
                <div class="season-title" style="color:{_scolor};">{_stitle}</div>
                <div class="season-desc">{_sdesc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
    if recs_df.empty:
        st.markdown(f"""
        <div class="info-box" style="text-align:center;padding:32px 24px;border-style:dashed;">
            <div style="font-size:2rem;margin-bottom:8px;">🌾</div>
            <div style="font-size:1rem;font-weight:800;color:{text_main};margin-bottom:4px;">
                No crops match "{cat_filter}" for {selected_county} in the {selected_season}.
            </div>
            <div style="font-size:0.86rem;color:{text_muted};">
                Try switching <strong>Crop Category</strong> back to "All", or check a different county or season in the sidebar.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
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
            size="total_farm_yield_kg", color="risk_level", hover_name="crop",
            color_discrete_map={"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"},
            labels={"suitability_score": "Climate Suitability (%)",
                    "total_farm_net_profit_kes": "Estimated Net Profit (KES)",
                    "total_farm_yield_kg": "Total Yield (kg)", "risk_level": "Risk Level"}
        )
        fig1.update_traces(marker=dict(opacity=0.86, line=dict(width=1.5, color="#fff" if is_dark else "#14532d")))
        fig1.update_layout(xaxis=dict(ticksuffix="%", gridcolor=card_border),
                           yaxis=dict(tickprefix="KES ", gridcolor=card_border))
        # Annotate only the #1 ranked crop (recs_df is already sorted) instead of labeling every bubble
        _top = recs_df.iloc[0]
        fig1.add_annotation(x=_top["suitability_score"], y=_top["total_farm_net_profit_kes"],
            text=f"⭐ {_top['crop']} — top pick", showarrow=True, arrowhead=2, ax=30, ay=-35,
            font=dict(size=12, color=text_main, family="Inter"),
            bgcolor=card_bg, bordercolor=primary_color, borderwidth=1, borderpad=4)
        chart_caption("Each bubble = one crop. Rightmost = best climate fit. Highest = most profitable. Larger bubble = more yield volume.")
        st.plotly_chart(apply_chart_style(fig1, 430), use_container_width=True, config={"displayModeBar": False})

        # ── VIZ 2 + 3: Financial Bar & Treemap ──
        col_v2, col_v3 = st.columns([1.1, 0.9])
        with col_v2:
            section("📊", "Financial Breakdown per Crop",
                    "Red = production cost · Blue = gross revenue · Green = net profit")
            _crop_order = recs_df.sort_values("total_farm_net_profit_kes", ascending=False)["crop"].tolist()
            df_melt = recs_df.melt(id_vars=["crop"],
                value_vars=["total_production_cost_kes", "total_farm_revenue_kes", "total_farm_net_profit_kes"],
                var_name="Metric", value_name="KES")
            df_melt["Metric"] = df_melt["Metric"].map({
                "total_production_cost_kes": "📦 Cost",
                "total_farm_revenue_kes": "💰 Revenue",
                "total_farm_net_profit_kes": "✅ Profit"
            })
            fig2 = px.bar(df_melt, x="crop", y="KES", color="Metric", barmode="group",
                category_orders={"crop": _crop_order},
                color_discrete_map={"📦 Cost": "#f87171", "💰 Revenue": "#60a5fa", "✅ Profit": "#34d399"},
                labels={"KES": "Amount (KES)", "crop": "Crop", "Metric": ""},
                text_auto=".3s")
            fig2.update_traces(textposition="outside", textfont_size=10)
            fig2.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(tickprefix="KES ", gridcolor=card_border),
                bargap=0.2, bargroupgap=0.06
            )
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
            _all_dims = [
                ("suitability_score", "Suitability\n(%)"),
                ("benefit_cost_ratio", "BCR\n(Return)"),
                ("drought_tolerance", "Drought\nTolerance"),
                ("expected_yield_kg_per_acre", "Yield / Acre\n(kg)"),
                ("optimized_net_price_kes_per_kg", "Price / kg\n(KES)"),
            ]
            # Only use dimensions actually present in this engine's output — protects against
            # column-name drift between the rule-based and ML engines silently crashing the chart.
            dims = [d for d, _ in _all_dims if d in recs_df.columns]
            dim_labels = [lbl for d, lbl in _all_dims if d in recs_df.columns]
            radar_colors = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#f43f5e"]
            if len(dims) < 3:
                st.info("⚠️ Not enough comparable metrics available to draw the radar chart for this engine mode.")
            else:
                # Normalize each dimension against the min/max of the crops actually shown, so the
                # radar reflects *relative* ranking here rather than clipping against a fixed scale
                # that can make every crop look artificially small (or identically maxed-out).
                dim_min = {d: recs_df[d].min() for d in dims}
                dim_max = {d: recs_df[d].max() for d in dims}
                radar_fig = go.Figure()
                for i, (_, row) in enumerate(recs_df.iterrows()):
                    norm = []
                    for d in dims:
                        span = dim_max[d] - dim_min[d]
                        norm.append(50.0 if span == 0 else (row.get(d, 0) - dim_min[d]) / span * 100)
                    norm.append(norm[0])
                    lbl = dim_labels + [dim_labels[0]]
                    raw_vals = [row.get(d, 0) for d in dims] + [row.get(dims[0], 0)]
                    radar_fig.add_trace(go.Scatterpolar(
                        r=norm, theta=lbl, name=row["crop"], fill="toself",
                        line=dict(color=radar_colors[i % len(radar_colors)], width=2.2),
                        opacity=0.72, customdata=raw_vals,
                        hovertemplate="%{theta}: %{customdata:.1f}<extra>%{fullData.name}</extra>"
                    ))
                radar_fig.update_layout(
                    polar=dict(bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0, 100], gridcolor=card_border, tickfont=dict(size=8)),
                        angularaxis=dict(gridcolor=card_border)),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25)
                )
                chart_caption("Each axis is scaled relative to the crops shown here (100% = best among this set, 0% = weakest). Larger filled area = stronger all-round crop. Hover a point for its actual value.")
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
if tab_bank is not None:
    with tab_bank:
        section("🏦", "Agricultural Credit Underwriting Portal",
                "Automated loan sizing (70% CapEx rule), climate-adjusted interest rates, and portfolio stress testing")

        # If Cooperative role is active, add helpful guidance banner
        if user_role == "cooperative":
            st.markdown(f"""
            <div style="background:{'rgba(16,185,129,0.08)' if is_dark else '#f0fdf4'};border-left:4px solid #10b981;padding:12px 16px;border-radius:8px;margin-bottom:14px;font-size:0.86rem;">
                👨‍🌾 <strong>Farmer Loan Pre-Qualification View:</strong> Use this calculator to see what agricultural loan size and interest rate your cooperative would qualify for from our partner banks.
            </div>
            """, unsafe_allow_html=True)

        tab_single, tab_port = st.tabs(["📝 Single Loan Assessment", "💼 Portfolio Stress Test"])

        with tab_single:
            st.markdown('<div class="info-box">ℹ️ <strong>How it works:</strong> Enter the borrower details below. The system calculates the recommended loan amount as 70% of total production CapEx, adjusts the interest rate upward for higher climate and crop risk, and shows the Debt Service Coverage Ratio (DSCR). A DSCR ≥ 1.2× means the farm revenue can comfortably cover loan repayments.</div>', unsafe_allow_html=True)

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                borrower_name = st.text_input("🏢 Borrower / SACCO Name", current_user.get("organization", "Nakuru Grain Growers Co-op"))
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
                                    template=plotly_theme, paper_bgcolor="rgba(0,0,0,0)",
                                    font=dict(family="Inter, sans-serif", color=text_main),
                                    hoverlabel=dict(bgcolor=card_bg, bordercolor=primary_color,
                                                     font=dict(family="Inter, sans-serif", color=text_main)))
            _zone_txt = "LOW RISK" if risk_val < 0.35 else ("MODERATE RISK" if risk_val < 0.6 else "HIGH RISK")
            _zone_clr = "#10b981" if risk_val < 0.35 else ("#f59e0b" if risk_val < 0.6 else "#ef4444")
            fig_gauge.add_annotation(text=_zone_txt, x=0.5, y=0.24, showarrow=False,
                font=dict(size=13, color=_zone_clr, family="Inter"))
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
            fig_donut.update_traces(textinfo="percent+label", textfont_size=11, pull=[0.04, 0, 0],
                                     marker=dict(line=dict(color=card_bg, width=2)))
            fig_donut.update_layout(
                height=290, margin=dict(l=10, r=10, t=30, b=40),
                template=plotly_theme, paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color=text_main),
                hoverlabel=dict(bgcolor=card_bg, bordercolor=primary_color,
                                 font=dict(family="Inter, sans-serif", color=text_main)),
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5,
                            font=dict(size=10))
            )
            # Center annotation names the dominant risk driver at a glance
            _top_factor = risk_breakdown.loc[risk_breakdown["Score"].idxmax(), "Factor"].split(" ", 1)[-1].split(" (")[0]
            fig_donut.add_annotation(text=f"Top driver:<br><b>{_top_factor}</b>", x=0.5, y=0.5,
                                      showarrow=False, font=dict(size=11, color=text_muted, family="Inter"))
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            chart_caption("The largest slice is the primary risk driver. Mitigation efforts should focus there first to reduce the composite risk score.")


        section("💧", "Facility Sizing & Revenue Coverage",
                "How the loan fits within the overall farm financial structure")
        fig_wf = go.Figure(go.Waterfall(
            orientation="v", measure=["relative", "relative", "total", "relative", "total"],
            x=["Farmer Equity\n(30%)", "Bank Loan\n(70%)", "Total CapEx", "Operating\nMargin", "Gross\nRevenue"],
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
            size="loan_amount_kes", color="credit_grade", hover_name="borrower_name",
            labels={"expected_default_rate_pct": "Default Risk (%)", "interest_rate_pct": "Interest Rate (%)",
                    "loan_amount_kes": "Loan (KES)", "credit_grade": "Credit Grade"},
            color_discrete_sequence=["#10b981", "#34d399", "#60a5fa", "#f59e0b", "#ef4444"]
        )
        fig_port.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color=card_border)))
        # Reverse the risk axis so "up and to the right = best" holds everywhere in the dashboard,
        # matching the Strategic Decision Frontier and Yield vs. Cost charts.
        fig_port.update_xaxes(autorange="reversed", title_text="Default Risk (%) — lower is safer, further right")
        chart_caption("Ideal loans sit top-right here (low default risk, healthy interest rate) — same 'up and right is best' rule as the other charts in this app. Bottom-left loans carry the most credit risk and should have enhanced collateral.")
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
if tab_climate is not None:
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
                fillcolor="rgba(16,185,129,0.22)" if is_dark else "rgba(22,163,74,0.18)",
                line=dict(color="#10b981" if is_dark else "#16a34a", width=2.8),
                mode="lines+markers", marker=dict(size=6, symbol="circle")
            ), secondary_y=False)
            fig8.add_trace(go.Scatter(
                x=label_x, y=county_data["temp_mean_c"], name="🌡️ Temperature (°C)",
                line=dict(color="#f87171", width=2.8, dash="solid"),
                mode="lines+markers", marker=dict(size=5)
            ), secondary_y=True)
            fig8.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, gridcolor=card_border)
            fig8.update_yaxes(title_text="Temperature (°C)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
            fig8.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(tickangle=-35, gridcolor=card_border, title="Season / Year")
            )
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
if tab_catalog is not None:
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
            fig12.update_layout(uniformtext=dict(minsize=9, mode="hide"))
            chart_caption("Larger boxes = higher yield potential. Darker green = higher market price. Boxes too small to label are still there — hover or zoom in. Click a category to zoom, click the header to zoom back out.")
            st.plotly_chart(apply_chart_style(fig12, 430), use_container_width=True, config={"displayModeBar": False})

            # ── VIZ 13: Yield vs Cost Efficiency ──
            section("🔍", "Yield vs. Cost Efficiency",
                    "Find the best-value crops — high yield at low cost per acre")
            fig13 = px.scatter(df_display, x="cost_per_acre_kes", y="yield_per_acre_kg",
                color="category", hover_name="crop", size="base_price_kes_per_kg",
                labels={"cost_per_acre_kes": "Production Cost (KES/acre)", "yield_per_acre_kg": "Yield (kg/acre)",
                        "base_price_kes_per_kg": "Price (KES/kg)", "category": "Category"})
            fig13.update_traces(marker=dict(opacity=0.82, line=dict(width=1, color=card_border)))
            # With up to 40 crops on screen, labeling every point makes it unreadable — call out
            # only the single best yield-per-cost-shilling crop instead.
            _best_val = df_display.loc[(df_display["yield_per_acre_kg"] / df_display["cost_per_acre_kes"]).idxmax()]
            fig13.add_annotation(x=_best_val["cost_per_acre_kes"], y=_best_val["yield_per_acre_kg"],
                text=f"⭐ {_best_val['crop']} — best value", showarrow=True, arrowhead=2, ax=30, ay=-30,
                font=dict(size=12, color=text_main, family="Inter"),
                bgcolor=card_bg, bordercolor=primary_color, borderwidth=1, borderpad=4)
            chart_caption("Top-left zone = HIGH yield at LOW cost — the sweet spot. Bubble size = market price per kg. Hover any bubble for its name; the starred crop has the best yield-per-shilling ratio.")
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
                    _crop_price_order = (m_sub.groupby("crop")["market_price"].mean()
                                          .sort_values(ascending=False).index.tolist())
                    fig14 = px.bar(m_sub, x="crop", y="market_price", color="market", barmode="group",
                        category_orders={"crop": _crop_price_order},
                        labels={"market_price": "Price (KES/kg)", "crop": "Crop", "market": "Trading Hub"},
                        color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#06b6d4"]
                        if is_dark else ["#14532d", "#1e40af", "#4c1d95", "#78350f", "#0e7490"],
                        text_auto=".0f")
                    fig14.update_traces(texttemplate="KES %{text}", textposition="outside", textfont_size=10)
                    fig14.update_layout(
                        legend=dict(orientation="h", yanchor="bottom", y=1.02),
                        yaxis=dict(tickprefix="KES ", gridcolor=card_border),
                        bargap=0.18, bargroupgap=0.04
                    )
                    chart_caption("Taller bar = higher price at that market hub. Always sell where your crop's bar is tallest to maximise revenue. Shorter bars still may make sense if transport costs are lower.")
                    st.plotly_chart(apply_chart_style(fig14, 420), use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("👆 Select at least one crop above to see the market price comparison.")

                section("📦", "Price Volatility by Agricultural Category",
                        "How stable are market prices across each crop class? Lower = more predictable income")
                fig15 = px.box(engine.market_df, x="category", y="volatility_cv",
                    color="category",
                    color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#06b6d4"],
                    labels={"volatility_cv": "Price Volatility (CV)", "category": "Crop Category"})
                fig15.update_layout(
                    showlegend=False, xaxis_tickangle=-20,
                    yaxis=dict(gridcolor=card_border),
                    shapes=[dict(
                        type="line", x0=-0.5, x1=len(engine.market_df["category"].unique())-0.5,
                        y0=0.25, y1=0.25, yref="y", xref="x",
                        line=dict(color="#ef4444", dash="dash", width=1.5)
                    )],
                    annotations=[dict(
                        x=len(engine.market_df["category"].unique())-1, y=0.26,
                        text="High Volatility Threshold (CV=0.25)",
                        showarrow=False, font=dict(size=10, color="#ef4444"), xanchor="right"
                    )]
                )
                chart_caption("Higher box = more unpredictable prices. Red dashed line = high-volatility threshold (CV 0.25). Crops below the line offer more stable income — better for loan repayment planning.")
                st.plotly_chart(apply_chart_style(fig15, 380), use_container_width=True, config={"displayModeBar": False})


        else:
            st.info("⚠️ Crop database not loaded. Ensure `data/crops_database.csv` is available.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — KILIMOBOT AI ADVISORY AGENT
# ═══════════════════════════════════════════════════════════════════════════════
if tab_ai is not None:
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
                        f"👋 Hello **{current_user.get('full_name', 'there')}**! I'm **KilimoBot**, your ClimaCrop Intelligence AI assistant.\n\n"
                        f"I'm loaded with data for **{selected_county} County** ({selected_season}) tailored for your role as **{role_meta['name']}**.\n\n"
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
    <span class="footer-brand">🌿 ClimaCrop Intelligence</span>
    <span class="footer-line">&nbsp;·&nbsp; Kilimo-Smart Decision Platform · Kenya 🇰🇪 &nbsp;·&nbsp; TAHMO · NASA POWER · FAOSTAT · KNBS &nbsp;·&nbsp; Built for cooperatives, SACCOs, DFIs & agri-tech researchers</span>
</div>
""", unsafe_allow_html=True)
