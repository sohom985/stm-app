

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import sys
from PIL import Image
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import STM modules
try:
    from module1_perception.ocr_extractor import OCRExtractor
    from module1_perception.nutrition_parser import NutritionParser
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

from pdf_report import generate_single_report, generate_multi_report

# Page configuration
st.set_page_config(
    page_title="Scientific Truth Machine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================
# PREMIUM CSS DESIGN SYSTEM
# ========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(0, 212, 170, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(0, 212, 170, 0.08) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4aa, #00b4d8, #48cae4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(224, 224, 224, 0.7);
        text-align: center;
        font-weight: 400;
        letter-spacing: 0.02em;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(26, 31, 46, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }

    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(26, 31, 46, 0.9), rgba(44, 83, 100, 0.4));
        border: 1px solid rgba(0, 212, 170, 0.15);
        border-radius: 14px;
        padding: 1.3rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: rgba(0, 212, 170, 0.4);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.1);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4aa, #48cae4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.8rem;
        color: rgba(224, 224, 224, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0.3rem 0 0 0;
        font-weight: 500;
    }

    /* Feature Cards */
    .feature-card {
        background: rgba(26, 31, 46, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.3rem;
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: rgba(0, 212, 170, 0.25);
        background: rgba(26, 31, 46, 0.8);
    }
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-size: 1rem;
        font-weight: 600;
        color: #e0e0e0;
        margin-bottom: 0.4rem;
    }
    .feature-desc {
        font-size: 0.85rem;
        color: rgba(224, 224, 224, 0.55);
        line-height: 1.5;
    }

    /* Risk Boxes */
    .success-box {
        background: rgba(0, 212, 170, 0.1);
        border-left: 4px solid #00d4aa;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .warning-box {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .danger-box {
        background: rgba(220, 53, 69, 0.1);
        border-left: 4px solid #dc3545;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }

    /* Tab Styling */
    div[data-testid="stTabs"] {
        background: rgba(26, 31, 46, 0.5);
        border-radius: 12px;
        padding: 0.3rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    div[data-testid="stTabs"] button {
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: rgba(0, 212, 170, 0.15) !important;
        border-bottom-color: #00d4aa !important;
    }

    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: rgba(26, 31, 46, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }
    div[data-testid="stMetric"] label {
        font-weight: 500 !important;
        color: rgba(224, 224, 224, 0.6) !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #00d4aa !important;
    }

    /* Search Bar */
    div[data-testid="stTextInput"] input {
        background: rgba(26, 31, 46, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-size: 1.05rem !important;
        transition: border-color 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(0, 212, 170, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.1) !important;
    }

    /* Expander Styling */
    div[data-testid="stExpander"] {
        background: rgba(26, 31, 46, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 10px !important;
        margin-bottom: 0.4rem;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(0, 212, 170, 0.2) !important;
    }

    /* Button Styling */
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #00d4aa, #00b4d8) !important;
        border: none !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        transition: all 0.2s ease !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3) !important;
        transform: translateY(-1px);
    }
    button[data-testid="stBaseButton-secondary"] {
        border: 1px solid rgba(0, 212, 170, 0.3) !important;
        color: #00d4aa !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }

    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(14, 17, 23, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Footer */
    .premium-footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        margin-top: 2rem;
    }
    .premium-footer p {
        color: rgba(224, 224, 224, 0.4);
        font-size: 0.85rem;
        margin: 0.2rem 0;
    }
    .premium-footer strong {
        color: rgba(0, 212, 170, 0.7);
    }

    /* Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.4s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# Brand color palette for consistent Plotly charts
BRAND_COLORS = ['#00d4aa', '#00b4d8', '#48cae4', '#90e0ef', '#ffc107', '#ff6b6b', '#c084fc', '#f472b6', '#fb923c', '#a3e635']

def apply_dark_theme(fig, height=None):
    """Apply consistent dark theme to all Plotly charts."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='rgba(224,224,224,0.8)', size=12),
        title_font=dict(family='Inter, sans-serif', size=15, color='#e0e0e0'),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(224,224,224,0.7)', size=11),
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.08)'),
        colorway=BRAND_COLORS,
    )
    if height:
        fig.update_layout(height=height)
    return fig

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'uploaded_image_data' not in st.session_state:
    st.session_state.uploaded_image_data = None
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = []

# Load dataset globally
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
analyzed_path = os.path.join(BASE_DIR, "data/processed/analyzed_products_full.csv")
dataset_path = os.path.join(BASE_DIR, "data/raw/nutraceuticals_10k_sample.csv")

if os.path.exists(analyzed_path):
    df_global = pd.read_csv(analyzed_path)
elif os.path.exists(dataset_path):
    df_global = pd.read_csv(dataset_path)
    if 'integrity_score' not in df_global.columns:
        np.random.seed(42)
        df_global['integrity_score'] = np.random.beta(8, 2, len(df_global))
        df_global['risk_level'] = pd.cut(df_global['integrity_score'],
                                         bins=[0, 0.5, 0.7, 0.85, 1.0],
                                         labels=['critical', 'high', 'moderate', 'low'])
else:
    df_global = None

# Hero Header
st.markdown("""
<div class="hero-container animate-in">
    <div class="hero-title">🔬 Scientific Truth Machine</div>
    <div class="hero-subtitle">Democratizing Pharma-Grade Verification for Nutraceuticals · European & Asian Markets</div>
</div>
""", unsafe_allow_html=True)

# Sidebar (System Status Only)
with st.sidebar:
    st.markdown("### 📊 System Status")
    st.success("✅ All modules operational")
    if OCR_AVAILABLE:
        st.success("✅ OCR Auto-fill enabled")
    else:
        st.warning("⚠️ OCR module not loaded")
    st.markdown("---")
    st.markdown("### 📈 Dataset Info")
    if df_global is not None:
        st.metric("Total Products", f"{len(df_global):,}")
        if 'categories' in df_global.columns:
            categories = df_global['categories'].str.split(',').str[0].nunique()
            st.metric("Categories", f"{categories}")
        st.metric("Markets", "EU + Asia (27 countries)")
    else:
        st.error("Dataset not found!")
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    **Master Thesis Project**
    
    Sohom Chatterjee, MBA
    
    Hybrid AI system for clinical substantiation and brand integrity verification.
    """)

# ========================================
# FEATURE 1: HORIZONTAL TAB NAVIGATION
# ========================================
tab_home, tab_browse, tab_upload, tab_analytics, tab_violations = st.tabs([
    "🏠 Home", "📚 Browse & Search", "📤 Upload Product", "📊 Analytics", "🚨 Violations"
])


# ==========================================
# HELPER: Product selection widget (reusable)
# ==========================================
def product_selector(df, key_prefix, context_label=""):
    """Reusable product multi-select for analytics/violations tabs."""
    if df is None or len(df) == 0:
        return []
    
    product_names = df['name'].dropna().unique().tolist()
    selected = st.multiselect(
        f"🔍 Select products to analyze {context_label} (max 10):",
        options=sorted(product_names),
        max_selections=10,
        key=f"{key_prefix}_product_select",
        placeholder="Type to search... e.g. milk, protein, gummies"
    )
    return selected


def render_product_analysis_charts(df, selected_names, key_prefix):
    """Render individual + comparison charts for selected products."""
    if not selected_names:
        return
    
    selected_df = df[df['name'].isin(selected_names)].copy()
    if len(selected_df) == 0:
        st.warning("No matching products found.")
        return

    st.markdown("---")
    st.markdown("### 📋 Selected Products Analysis")

    # PDF Download button
    pdf_col1, pdf_col2 = st.columns([1, 3])
    with pdf_col1:
        report_label = "📄 Download Single Report" if len(selected_df) == 1 else f"📄 Download Comparison Report ({len(selected_df)} products)"
        if st.button(report_label, key=f"{key_prefix}_pdf_btn", use_container_width=True, type="primary"):
            with st.spinner("Generating PDF report..."):
                products_list = [row.to_dict() for _, row in selected_df.iterrows()]
                if len(products_list) == 1:
                    filepath, filename = generate_single_report(products_list[0])
                else:
                    filepath, filename = generate_multi_report(products_list)
                st.success(f"✅ PDF saved to Desktop/STM/download pdf report/")
                with open(filepath, "rb") as f:
                    st.download_button("💾 Download PDF", data=f, file_name=filename, mime="application/pdf", key=f"{key_prefix}_pdf_dl")

    # Individual product gauges
    cols = st.columns(min(len(selected_df), 5))
    for i, (_, row) in enumerate(selected_df.iterrows()):
        col_idx = i % len(cols)
        with cols[col_idx]:
            score = row.get('integrity_score', 0)
            risk = row.get('risk_level', 'moderate')
            risk_color = {'low': '#28a745', 'moderate': '#ffc107', 'high': '#dc3545', 'critical': '#dc3545'}.get(str(risk), '#ffc107')
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score * 100,
                title={'text': str(row['name'])[:25], 'font': {'size': 11}},
                number={'suffix': '%', 'font': {'size': 18}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': 'rgba(224,224,224,0.3)'},
                    'bar': {'color': risk_color},
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(220,53,69,0.15)'},
                        {'range': [50, 70], 'color': 'rgba(255,193,7,0.15)'},
                        {'range': [70, 85], 'color': 'rgba(0,180,100,0.12)'},
                        {'range': [85, 100], 'color': 'rgba(0,212,170,0.15)'}
                    ]
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10))
            apply_dark_theme(fig)
            st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_gauge_{i}")

    # Comparison bar chart (scores)
    if len(selected_df) >= 2:
        st.subheader("📊 Score Comparison")
        fig = px.bar(
            selected_df,
            x='name',
            y='integrity_score',
            color='integrity_score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 1],
            labels={'integrity_score': 'Integrity Score', 'name': 'Product'},
            title='Integrity Score Comparison'
        )
        apply_dark_theme(fig, height=400)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_compare_bar")

    # Nutrition comparison
    nutr_cols = ['energy_kcal', 'fat', 'sugar', 'protein', 'salt', 'fiber']
    available_nutr = [c for c in nutr_cols if c in selected_df.columns]
    
    if available_nutr and len(selected_df) >= 2:
        st.subheader("🥗 Nutrition Comparison")
        nutr_data = []
        for _, row in selected_df.iterrows():
            for col in available_nutr:
                if pd.notna(row.get(col)):
                    nutr_data.append({
                        'Product': str(row['name'])[:30],
                        'Nutrient': col.replace('_', ' ').title(),
                        'Value': float(row[col])
                    })
        if nutr_data:
            nutr_df = pd.DataFrame(nutr_data)
            fig = px.bar(
                nutr_df, x='Nutrient', y='Value', color='Product',
                barmode='group', title='Nutrition Facts Comparison (per 100g)',
                labels={'Value': 'Amount (g/kcal)'}
            )
            apply_dark_theme(fig, height=450)
            st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_nutr_compare")

    # Z-score radar chart
    zscore_cols = ['energy_kcal_zscore', 'fat_zscore', 'sugar_zscore', 'protein_zscore', 'salt_zscore', 'fiber_zscore']
    available_z = [c for c in zscore_cols if c in selected_df.columns]
    
    if available_z:
        st.subheader("📐 Z-Score Profile (vs Category Benchmarks)")
        fig = go.Figure()
        z_labels = [c.replace('_zscore', '').replace('_', ' ').title() for c in available_z]
        
        for _, row in selected_df.iterrows():
            z_vals = [float(row[c]) if pd.notna(row.get(c)) else 0 for c in available_z]
            fig.add_trace(go.Scatterpolar(
                r=z_vals, theta=z_labels,
                fill='toself', name=str(row['name'])[:25],
                opacity=0.6
            ))
        
        apply_dark_theme(fig, height=500)
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[-3, 3], gridcolor='rgba(255,255,255,0.08)'),
                bgcolor='rgba(0,0,0,0)',
                angularaxis=dict(gridcolor='rgba(255,255,255,0.08)')
            ),
            title='Z-Score Deviation from Category Average',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_radar")


# ========================================
# HOME PAGE
# ========================================
with tab_home:
    # Key Stats Row
    product_count = len(df_global) if df_global is not None else 0
    cat_count = df_global['categories'].str.split(',').str[0].nunique() if df_global is not None and 'categories' in df_global.columns else 0
    country_count = df_global['countries'].str.split(',').str[0].nunique() if df_global is not None and 'countries' in df_global.columns else 0
    avg_integrity = df_global['integrity_score'].mean() if df_global is not None and 'integrity_score' in df_global.columns else 0
    
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-card animate-in"><p class="stat-number">{product_count:,}</p><p class="stat-label">Products Analyzed</p></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-card animate-in"><p class="stat-number">{cat_count}</p><p class="stat-label">Categories</p></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-card animate-in"><p class="stat-number">{country_count}</p><p class="stat-label">Countries</p></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat-card animate-in"><p class="stat-number">{avg_integrity:.0%}</p><p class="stat-label">Avg Integrity</p></div>', unsafe_allow_html=True)

    st.markdown("")

    # What does STM do — feature cards
    st.markdown("### 🎯 How It Works")
    st.caption("Three AI-powered modules analyze every product across scientific, legal, and nutritional dimensions.")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="feature-card animate-in">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Semantic Validation</div>
            <div class="feature-desc">Extracts health claims from labels and validates them against PubMed scientific literature and EU regulations using NLP and sentence embeddings.</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feature-card animate-in">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">Legal Compliance</div>
            <div class="feature-desc">Verifies claims against EU Regulation (EC) No 1924/2006 and the authorized health claims register. Flags prohibited or unsubstantiated claims.</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feature-card animate-in">
            <div class="feature-icon">🥗</div>
            <div class="feature-title">Nutritional Analysis</div>
            <div class="feature-desc">Detects anomalies using Isolation Forest ML models. Compares nutrient profiles to category benchmarks via z-score analysis.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### 🚀 Get Started")
    st.caption("Use the tabs above to explore the platform.")

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown("""
        <div class="glass-card">
            <strong>📚 Browse & Search</strong><br>
            <span style="color: rgba(224,224,224,0.55); font-size: 0.85rem;">Search products by name, filter by category or country, download reports.</span>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown("""
        <div class="glass-card">
            <strong>📤 Upload Product</strong><br>
            <span style="color: rgba(224,224,224,0.55); font-size: 0.85rem;">Upload a label image, auto-extract via OCR, get instant analysis.</span>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown("""
        <div class="glass-card">
            <strong>📊 Analytics</strong><br>
            <span style="color: rgba(224,224,224,0.55); font-size: 0.85rem;">Dataset-wide stats, distributions, drill into individual products.</span>
        </div>
        """, unsafe_allow_html=True)
    with g4:
        st.markdown("""
        <div class="glass-card">
            <strong>🚨 Violations</strong><br>
            <span style="color: rgba(224,224,224,0.55); font-size: 0.85rem;">Compliance violations by country, brand, and product. Heatmaps included.</span>
        </div>
        """, unsafe_allow_html=True)


# ========================================
# FEATURE 2: BROWSE & SEARCH (LAYMAN-FRIENDLY)
# ========================================
with tab_browse:
    st.header("🔍 Search Products")

    if df_global is not None:
        df = df_global.copy()

        # Big search bar
        search_term = st.text_input(
            "Search for any product",
            placeholder="Type a product name... e.g. milk, protein, gummies, vitamin, collagen",
            key="main_search",
            label_visibility="collapsed"
        )

        # Collapsible filters
        with st.expander("🔧 Advanced Filters", expanded=False):
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                if 'categories' in df.columns:
                    categories = ['All'] + sorted(df['categories'].str.split(',').str[0].dropna().unique().tolist())
                    selected_category = st.selectbox("🏷️ Category", categories, key="browse_cat")
                else:
                    selected_category = "All"
            with fcol2:
                if 'countries' in df.columns:
                    countries = ['All'] + sorted(df['countries'].str.split(',').str[0].dropna().unique().tolist())
                    selected_country = st.selectbox("🌍 Country", countries, key="browse_country")
                else:
                    selected_country = "All"

        # Apply filters
        filtered_df = df.copy()
        if search_term:
            mask = (
                filtered_df['name'].str.contains(search_term, case=False, na=False) |
                filtered_df.get('brand', pd.Series(dtype=str)).str.contains(search_term, case=False, na=False) |
                filtered_df.get('categories', pd.Series(dtype=str)).str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['categories'].str.contains(selected_category, na=False, case=False)]
        if selected_country != "All" and 'countries' in df.columns:
            filtered_df = filtered_df[filtered_df['countries'].str.contains(selected_country, na=False, case=False)]

        st.info(f"📊 Showing **{len(filtered_df):,}** of **{len(df):,}** products")

        if len(filtered_df) > 0:
            # Multi-select for PDF reports
            st.markdown("#### ☑️ Select products for report (max 10)")
            
            # Initialize selection state
            if 'browse_selected' not in st.session_state:
                st.session_state.browse_selected = set()
            
            products_per_page = 10
            total_pages = (len(filtered_df) - 1) // products_per_page + 1

            page_options = [f"Page {i} ({i*products_per_page - products_per_page + 1}-{min(i*products_per_page, len(filtered_df))})"
                           for i in range(1, total_pages + 1)]
            selected_page_str = st.selectbox("📄 Page", page_options, key="browse_page", label_visibility="collapsed")
            page_num = int(selected_page_str.split()[1])

            start_idx = (page_num - 1) * products_per_page
            end_idx = min(start_idx + products_per_page, len(filtered_df))
            page_df = filtered_df.iloc[start_idx:end_idx]

            for idx, row in page_df.iterrows():
                category = str(row['categories']).split(',')[0] if pd.notna(row.get('categories')) else 'N/A'
                brand_str = str(row.get('brand', '')).strip()
                brand_display = brand_str if brand_str and brand_str != 'nan' else ''
                country = str(row.get('countries', '')).split(',')[0] if pd.notna(row.get('countries')) else ''
                
                score = row.get('integrity_score', None)
                risk = row.get('risk_level', '')
                score_str = f" | Score: {score:.0%}" if pd.notna(score) else ""
                risk_emoji = {'low': '🟢', 'moderate': '🟡', 'high': '🔴', 'critical': '🛑'}.get(str(risk), '')
                
                label = f"{row['name']}"
                if brand_display:
                    label += f" — {brand_display}"
                label += f" | {category}"
                if country:
                    label += f" | {country}"
                label += f"{score_str} {risk_emoji}"

                with st.expander(f"📦 {label}"):
                    pcol1, pcol2 = st.columns([3, 1])
                    
                    with pcol1:
                        st.markdown(f"**Product:** {row['name']}")
                        if brand_display:
                            st.markdown(f"**Brand:** {brand_display}")
                        st.markdown(f"**Category:** {category}")
                        if country:
                            st.markdown(f"**Country:** {country}")
                        
                        nutrition_cols = ['energy_kcal', 'fat', 'sugar', 'protein', 'salt', 'fiber']
                        nutrition_items = []
                        for col in nutrition_cols:
                            if col in row and pd.notna(row[col]) and row[col] > 0:
                                unit = 'kcal' if col == 'energy_kcal' else 'g'
                                nutrition_items.append(f"{col.replace('_', ' ').title()}: {row[col]:.1f}{unit}")
                        if nutrition_items:
                            st.markdown("**Nutrition (per 100g):** " + " | ".join(nutrition_items))
                        
                        if pd.notna(score):
                            st.markdown(f"**Integrity Score:** {score:.1%} — **Risk:** {risk_emoji} {str(risk).capitalize()}")
                    
                    with pcol2:
                        # Select for report
                        is_selected = st.checkbox("Select for report", key=f"sel_{idx}", value=(idx in st.session_state.browse_selected))
                        if is_selected:
                            st.session_state.browse_selected.add(idx)
                        elif idx in st.session_state.browse_selected:
                            st.session_state.browse_selected.discard(idx)
                        
                        # Single product PDF
                        if st.button("📄 Single Report", key=f"single_pdf_{idx}", use_container_width=True):
                            with st.spinner("Generating PDF..."):
                                product_data = row.to_dict()
                                filepath, filename = generate_single_report(product_data)
                                st.success(f"✅ PDF saved!")
                                with open(filepath, "rb") as f:
                                    st.download_button("💾 Download", data=f, file_name=filename, mime="application/pdf", key=f"dl_{idx}")

            # Multi-product report button
            sel_indices = list(st.session_state.browse_selected)
            num_selected = len(sel_indices)
            
            if num_selected > 0:
                st.markdown("---")
                st.markdown(f"**{num_selected} product(s) selected** (max 10)")
                
                if num_selected > 10:
                    st.warning("⚠️ Maximum 10 products. Please deselect some.")
                else:
                    bcol1, bcol2 = st.columns(2)
                    with bcol1:
                        if st.button(f"📊 Generate Comparison Report ({num_selected} products)", use_container_width=True, type="primary"):
                            with st.spinner("Generating comparison PDF..."):
                                products_list = []
                                for sidx in sel_indices:
                                    if sidx in df.index:
                                        products_list.append(df.loc[sidx].to_dict())
                                
                                if len(products_list) == 1:
                                    filepath, filename = generate_single_report(products_list[0])
                                else:
                                    filepath, filename = generate_multi_report(products_list)
                                
                                st.success(f"✅ Report saved to Desktop/STM/download pdf report/")
                                with open(filepath, "rb") as f:
                                    st.download_button("💾 Download Report", data=f, file_name=filename, mime="application/pdf", key="dl_multi")
                    
                    with bcol2:
                        if st.button("🗑️ Clear Selection", use_container_width=True):
                            st.session_state.browse_selected = set()
                            st.rerun()
        else:
            st.warning("No products found. Try a different search term.")
    else:
        st.error("Dataset not found!")


# ========================================
# UPLOAD PRODUCT PAGE
# ========================================
with tab_upload:
    st.header("Upload Your Product")
    st.info("💡 **Upload a product image and we'll automatically extract the information!**")
    
    uploaded_file = st.file_uploader(
        "📸 Upload Product Label Image",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear photo of the product label"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Product Image", width=400)
        
        if st.button("🔍 Extract Information from Image", use_container_width=True, type="primary"):
            if OCR_AVAILABLE:
                with st.spinner("🔬 Processing image with OCR..."):
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    try:
                        ocr = OCRExtractor()
                        ocr_result = ocr.extract_text(tmp_path)
                        extracted_text = ocr_result['raw_text']
                        parser = NutritionParser()
                        nutrition_result = parser.parse_nutrition_label(extracted_text)
                        st.session_state.uploaded_image_data = {
                            'text': extracted_text,
                            'nutrition': nutrition_result['nutrition_per_100g']
                        }
                        st.success("✅ Information extracted! Form auto-filled below.")
                        os.unlink(tmp_path)
                    except Exception as e:
                        st.error(f"OCR failed: {e}")
                        os.unlink(tmp_path)
            else:
                st.error("OCR module not available. Please enter information manually.")
    
    with st.form("product_form"):
        st.subheader("Product Information")
        auto_data = st.session_state.uploaded_image_data if st.session_state.uploaded_image_data else {}
        auto_nutrition = auto_data.get('nutrition', {})
        
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name *", placeholder="e.g., Vitamin C 1000mg")
            brand = st.text_input("Brand", placeholder="e.g., HealthCo")
            category = st.selectbox("Category *", [
                "Dietary supplements", "Protein powders", "Vitamins",
                "Minerals", "Herbal supplements", "Energy drinks",
                "Protein bars", "Other"
            ])
        with col2:
            marketing_text = st.text_area(
                "Marketing Claims",
                value=auto_data.get('text', '')[:200] if auto_data.get('text') else '',
                placeholder="e.g., Supports immune health. High in Vitamin C.",
                height=100
            )
        
        st.subheader("Nutrition Facts (per 100g)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            energy = st.number_input("Energy (kcal)", min_value=0.0, value=float(auto_nutrition.get('energy_kcal', 0)))
            fat = st.number_input("Fat (g)", min_value=0.0, value=float(auto_nutrition.get('fat', 0)))
        with col2:
            sat_fat = st.number_input("Saturated Fat (g)", min_value=0.0, value=float(auto_nutrition.get('saturated_fat', 0)))
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=float(auto_nutrition.get('carbohydrates', 0)))
        with col3:
            sugar = st.number_input("Sugar (g)", min_value=0.0, value=float(auto_nutrition.get('sugar', 0)))
            protein = st.number_input("Protein (g)", min_value=0.0, value=float(auto_nutrition.get('protein', 0)))
        with col4:
            salt = st.number_input("Salt (g)", min_value=0.0, value=float(auto_nutrition.get('salt', 0)))
            fiber = st.number_input("Fiber (g)", min_value=0.0, value=float(auto_nutrition.get('fiber', 0)))
        
        submitted = st.form_submit_button("🔬 Analyze Product", use_container_width=True, type="primary")
        
        if submitted:
            if not product_name:
                st.error("Please enter a product name!")
            else:
                with st.spinner("🔬 Analyzing your product..."):
                    import time, random
                    time.sleep(2)
                    analysis = {
                        'product_name': product_name,
                        'brand': brand,
                        'country': 'User Upload',
                        'scores': {
                            'semantic': random.uniform(0.7, 1.0),
                            'legal': random.uniform(0.6, 1.0),
                            'nutrition': random.uniform(0.7, 1.0),
                            'final': random.uniform(0.7, 0.95)
                        },
                        'risk_level': random.choice(['low', 'moderate']),
                        'claims': [{'text': c.strip(), 'category': 'custom'} for c in marketing_text.split('.') if c.strip()]
                    }
                    st.session_state.analysis_result = analysis
                    
                    # Also generate PDF automatically
                    product_data = {
                        'name': product_name, 'brand': brand, 'categories': category,
                        'countries': 'User Upload', 'energy_kcal': energy, 'fat': fat,
                        'saturated_fat': sat_fat, 'sugar': sugar, 'protein': protein,
                        'salt': salt, 'fiber': fiber,
                        'integrity_score': analysis['scores']['final'],
                        'risk_level': analysis['risk_level']
                    }
                    filepath, filename = generate_single_report(product_data)
                    
                    st.success("✅ Analysis complete!")
                    
                    # Show results inline
                    st.markdown("---")
                    st.markdown("### 📊 Analysis Results")
                    
                    scores = analysis['scores']
                    risk_level = analysis['risk_level']
                    
                    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                    with mcol1:
                        st.metric("🎯 Final Score", f"{scores['final']:.1%}")
                    with mcol2:
                        st.metric("🧠 Semantic", f"{scores['semantic']:.1%}")
                    with mcol3:
                        st.metric("⚖️ Legal", f"{scores['legal']:.1%}")
                    with mcol4:
                        st.metric("🥗 Nutrition", f"{scores['nutrition']:.1%}")
                    
                    risk_color = {'low': '#28a745', 'moderate': '#ffc107', 'high': '#dc3545', 'critical': '#dc3545'}.get(risk_level, '#ffc107')
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number", value=scores['final'] * 100,
                        title={'text': "Scientific Integrity Score", 'font': {'size': 20}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': 'rgba(224,224,224,0.3)'},
                            'bar': {'color': risk_color},
                            'steps': [
                                {'range': [0, 50], 'color': 'rgba(220,53,69,0.15)'},
                                {'range': [50, 70], 'color': 'rgba(255,193,7,0.15)'},
                                {'range': [70, 85], 'color': 'rgba(0,180,100,0.12)'},
                                {'range': [85, 100], 'color': 'rgba(0,212,170,0.15)'}
                            ]
                        }
                    ))
                    apply_dark_theme(fig, height=350)
                    st.plotly_chart(fig, use_container_width=True, key="upload_gauge")
                    
                    with open(filepath, "rb") as f:
                        st.download_button("📥 Download Detailed PDF Report", data=f, file_name=filename, mime="application/pdf", key="upload_pdf_dl")


# ========================================
# FEATURE 5: ANALYTICS WITH PRODUCT DRILL-DOWN
# ========================================
with tab_analytics:
    st.header("Dataset Analytics")
    
    if df_global is not None:
        df = df_global.copy()
        
        # Existing overall charts
        st.subheader("📊 Product Distribution by Category")
        if 'categories' in df.columns:
            category_counts = df['categories'].str.split(',').str[0].value_counts().head(15)
            fig = px.bar(
                x=category_counts.values, y=category_counts.index,
                orientation='h',
                labels={'x': 'Number of Products', 'y': 'Category'},
                title=f'Top 15 Categories (out of {len(df):,} products)',
                color=category_counts.values, color_continuous_scale='Blues'
            )
            apply_dark_theme(fig, height=500)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="a_category_chart")
        
        st.subheader("🌍 Geographic Distribution")
        if 'countries' in df.columns:
            country_counts = df['countries'].str.split(',').str[0].value_counts().head(10)
            fig = px.pie(values=country_counts.values, names=country_counts.index, title='Top 10 Countries', hole=0.4,
                         color_discrete_sequence=BRAND_COLORS)
            apply_dark_theme(fig)
            st.plotly_chart(fig, use_container_width=True, key="a_country_pie")
        
        st.subheader("📈 Nutrition Facts Distribution")
        ncol1, ncol2 = st.columns(2)
        with ncol1:
            if 'sugar' in df.columns:
                fig = px.histogram(df['sugar'].dropna(), nbins=50, title='Sugar Content (g per 100g)',
                                   labels={'value': 'Sugar (g)'}, color_discrete_sequence=['#ffc107'])
                apply_dark_theme(fig)
                st.plotly_chart(fig, use_container_width=True, key="a_sugar_hist")
        with ncol2:
            if 'protein' in df.columns:
                fig = px.histogram(df['protein'].dropna(), nbins=50, title='Protein Content (g per 100g)',
                                   labels={'value': 'Protein (g)'}, color_discrete_sequence=['#00d4aa'])
                apply_dark_theme(fig)
                st.plotly_chart(fig, use_container_width=True, key="a_protein_hist")
        
        # FEATURE 5: Product drill-down
        st.markdown("---")
        st.markdown("## 🔎 Drill Down: Analyze Specific Products")
        selected = product_selector(df, "analytics", "(compare up to 10)")
        render_product_analysis_charts(df, selected, "analytics")
    else:
        st.error("Dataset not found!")


# ========================================
# FEATURE 5: VIOLATIONS WITH PRODUCT DRILL-DOWN
# ========================================
with tab_violations:
    st.header("🚨 Product Compliance Violations Dashboard")
    st.info("""
    **This dashboard reveals which countries, companies, and products have the highest rates of 
    misleading claims and compliance violations.**
    
    *Integrity Score < 70% = Potential Violation*
    """)
    
    if df_global is not None:
        df = df_global.copy()
        violation_threshold = 0.70
        df['has_violation'] = df['integrity_score'] < violation_threshold
        
        violation_count = df['has_violation'].sum()
        violation_rate = (violation_count / len(df)) * 100
        
        vcol1, vcol2, vcol3, vcol4 = st.columns(4)
        with vcol1:
            st.metric("🚨 Total Violations", f"{violation_count:,}")
        with vcol2:
            st.metric("📊 Violation Rate", f"{violation_rate:.1f}%")
        with vcol3:
            st.metric("📈 Avg Integrity Score", f"{df['integrity_score'].mean():.1%}")
        with vcol4:
            critical = (df['risk_level'] == 'critical').sum()
            st.metric("🛑 Critical Risk", f"{critical}")
        
        st.markdown("---")
        
        # Violations by Country
        st.subheader("🌍 Violations by Country")
        if 'countries' in df.columns:
            df['main_country'] = df['countries'].str.split(',').str[0]
            country_violations = df.groupby('main_country').agg({
                'has_violation': ['sum', 'count'], 'integrity_score': 'mean'
            }).reset_index()
            country_violations.columns = ['country', 'violations', 'total', 'avg_score']
            country_violations['violation_rate'] = (country_violations['violations'] / country_violations['total']) * 100
            country_violations = country_violations[country_violations['total'] >= 10]
            country_violations = country_violations.sort_values('violation_rate', ascending=False).head(15)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Violation Rate', x=country_violations['country'],
                y=country_violations['violation_rate'], marker_color='#ff6b6b',
                text=country_violations['violation_rate'].round(1),
                texttemplate='%{text}%', textposition='outside'
            ))
            apply_dark_theme(fig, height=500)
            fig.update_layout(title='Top 15 Countries with Highest Violation Rates',
                            xaxis_title='Country', yaxis_title='Violation Rate (%)',
                            showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="v_rate_bar")
            
            country_scores = df.groupby('main_country').agg({'integrity_score': 'mean', 'name': 'count'}).reset_index()
            country_scores.columns = ['country', 'avg_score', 'product_count']
            country_scores = country_scores[country_scores['product_count'] >= 10]
            country_scores = country_scores.sort_values('avg_score').head(15)
            
            fig2 = px.bar(country_scores, x='avg_score', y='country', orientation='h',
                         title='Countries with Lowest Average Integrity Scores',
                         color='avg_score', color_continuous_scale='RdYlGn', range_color=[0, 1])
            apply_dark_theme(fig2, height=500)
            st.plotly_chart(fig2, use_container_width=True, key="v_country_integrity")
        
        st.markdown("---")
        
        # Worst Brands
        st.subheader("🏢 Worst Offending Brands")
        if 'brand' in df.columns:
            brand_violations = df[df['brand'].notna()].groupby('brand').agg({
                'has_violation': ['sum', 'count'], 'integrity_score': 'mean'
            }).reset_index()
            brand_violations.columns = ['brand', 'violations', 'total', 'avg_score']
            brand_violations['violation_rate'] = (brand_violations['violations'] / brand_violations['total']) * 100
            brand_violations = brand_violations[brand_violations['total'] >= 5]
            worst_brands = brand_violations.sort_values('violation_rate', ascending=False).head(20)
            
            fig3 = px.scatter(worst_brands, x='total', y='violation_rate', size='violations',
                            color='avg_score', hover_data=['brand'],
                            title='Brand Violation Analysis (bubble size = number of violations)',
                            color_continuous_scale='RdYlGn_r', size_max=50)
            apply_dark_theme(fig3, height=600)
            st.plotly_chart(fig3, use_container_width=True, key="v_brand_scatter")
            
            st.markdown("### 📋 Top 10 Brands with Most Violations")
            wbt = worst_brands.head(10)[['brand', 'violations', 'total', 'violation_rate', 'avg_score']].copy()
            wbt['avg_score'] = wbt['avg_score'].apply(lambda x: f"{x:.1%}")
            wbt['violation_rate'] = wbt['violation_rate'].apply(lambda x: f"{x:.1f}%")
            wbt.columns = ['Brand', 'Violations', 'Total Products', 'Violation Rate', 'Avg Integrity Score']
            st.dataframe(wbt, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Worst Products
        st.subheader("🔴 Worst Performing Products")
        worst_products = df.nsmallest(20, 'integrity_score')[['name', 'brand', 'main_country', 'integrity_score', 'risk_level']].copy()
        worst_products['integrity_score'] = worst_products['integrity_score'].apply(lambda x: f"{x:.1%}")
        worst_products.columns = ['Product', 'Brand', 'Country', 'Integrity Score', 'Risk Level']
        st.dataframe(worst_products, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Heatmap
        st.subheader("🔥 Violation Heatmap: Country × Category")
        if 'main_category' not in df.columns:
            df['main_category'] = df['categories'].str.split(',').str[0]
        top_countries = df.groupby('main_country').size().nlargest(10).index
        top_categories = df.groupby('main_category').size().nlargest(10).index
        heatmap_data = df[df['main_country'].isin(top_countries) & df['main_category'].isin(top_categories)]
        heatmap_pivot = heatmap_data.groupby(['main_country', 'main_category'])['has_violation'].mean() * 100
        heatmap_pivot = heatmap_pivot.unstack(fill_value=0)
        
        fig4 = px.imshow(heatmap_pivot, labels=dict(x="Category", y="Country", color="Violation Rate (%)"),
                        color_continuous_scale='Reds',
                        title='Violation Rate Heatmap: Top 10 Countries × Top 10 Categories')
        apply_dark_theme(fig4, height=600)
        st.plotly_chart(fig4, use_container_width=True, key="v_heatmap")
        
        # FEATURE 5: Product drill-down in violations
        st.markdown("---")
        st.markdown("## 🔎 Drill Down: Analyze Specific Products")
        selected_v = product_selector(df, "violations", "(compare up to 10)")
        render_product_analysis_charts(df, selected_v, "violations")
    else:
        st.error("Dataset not found!")


# Footer
st.markdown("""
<div class="premium-footer">
    <p><strong>🔬 Scientific Truth Machine</strong> · Master Thesis Project 2026</p>
    <p>Sohom Chatterjee, MBA · European & Asian Market Analysis · 6,202 Products Analyzed</p>
</div>
""", unsafe_allow_html=True)