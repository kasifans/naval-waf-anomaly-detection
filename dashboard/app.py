import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import time
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# ======================================================
# MODULE 1: APPLICATION CONFIGURATION
# ======================================================
# Initialize Streamlit app context with wide layout for dashboard visualization
st.set_page_config(
    page_title="WAF Defense Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# MODULE 2: ASSET RESOLUTION & IO
# ======================================================
def get_asset_path(filename):
    """
    Resolves absolute paths for static assets.
    Handles environment discrepancies between local dev and cloud deployment.
    
    Args:
        filename (str): Target asset filename.
    Returns:
        Path object if found, else None (graceful failure).
    """
    possible_paths = [
        Path("dashboard/assets") / filename,  # Dev environment
        Path("assets") / filename,            # Prod environment
        Path(filename)                        # Root fallback
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return None

# ======================================================
# MODULE 3: UI/UX & CSS INJECTION
# ======================================================
def set_background():
    """
    Injects global CSS for background rendering.
    Uses base64 encoding to embed images directly into the DOM.
    """
    bg_path = get_asset_path("bg.png")
    if bg_path:
        try:
            # Base64 encode to prevent path resolution issues in browser
            encoded = base64.b64encode(bg_path.read_bytes()).decode()
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background:
                        linear-gradient(rgba(0, 15, 30, 0.6), rgba(0, 15, 30, 0.8)),
                        url("data:image/png;base64,{encoded}");
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            pass # Suppress IO errors; fallback to default styles
    else:
        # Fallback: CSS Radial Gradient
        st.markdown(
            """<style>.stApp {background: radial-gradient(circle at center, #0b1426 0%, #000000 100%);}</style>""",
            unsafe_allow_html=True
        )

# Initialize UI styles
set_background()

# Inject Global Typography & Component Overrides
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Roboto:wght@500;700&display=swap');

/* Typography Stack */
.stApp { font-family: 'Roboto', sans-serif; }

/* Header Typography - Orbitron for HUD aesthetic */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 2px;
    color: #ffffff !important;
    text-shadow: 0 0 10px rgba(0,255,255,0.5);
    text-transform: uppercase;
}

/* Sidebar Container Styling */
section[data-testid="stSidebar"] {
    background-color: #050a14;
    border-right: 2px solid #00ffff;
}

/* Sidebar Text Color Override (High Contrast) */
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] span, 
section[data-testid="stSidebar"] label, 
section[data-testid="stSidebar"] div {
    color: #e0e0e0 !important;
}

/* Fix for Streamlit Widget Labels in Sidebar */
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
    font-weight: 500;
}

/* Metric Component Styling (Glassmorphism) */
div[data-testid="stMetric"] {
    background: rgba(10, 25, 45, 0.85);
    border-left: 5px solid #00ffff;
    padding: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    border-radius: 5px;
}
div[data-testid="stMetric"] label { color: #00ffff !important; font-family: 'Orbitron'; }
div[data-testid="stMetricValue"] { color: #fff !important; font-size: 2.2rem !important; font-family: 'Orbitron'; }

/* Tab Container Styling */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background-color: rgba(0,0,0,0.5);
    color: #00ffff;
    border: 1px solid #00ffff;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(0,255,255,0.2) !important;
    color: white !important;
}

/* Custom Profile Card CSS */
.operator-card {
    margin-top: 20px;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-left: 3px solid #00ffff;
    font-size: 0.9rem;
    color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# MODULE 4: DATA SIMULATION ENGINE (BACKEND MOCK)
# ======================================================
@st.cache_data(ttl=5) # Cache data for 5s to optimize render performance while allowing updates
def load_live_traffic():
    """
    Generates synthetic telemetry data to simulate high-volume network traffic.
    Includes probabilistic anomaly injection based on 'risk_score'.
    """
    rows = 10000  # High-volume simulation parameter
    now = datetime.now()
    
    # Geo-spatial reference points (Indian Ocean Theater)
    cities = [
        ("Mumbai", 19.07, 72.87), ("Kochi", 9.93, 76.26), 
        ("Chennai", 13.08, 80.27), ("Vizag", 17.68, 83.21),
        ("Port Blair", 11.62, 92.72), ("Colombo", 6.92, 79.86)
    ]
    
    # Vectorized data generation for performance
    city_indices = np.random.choice(len(cities), rows)
    
    data = {
        "timestamp": [now - timedelta(seconds=i*5) for i in range(rows)],
        "ip": [f"10.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}" for _ in range(rows)],
        "req_per_min": np.random.randint(20, 3000, rows),
        "risk_score": np.random.uniform(0.1, 9.9, rows),
        "lat": [cities[i][1] + np.random.uniform(-0.5,0.5) for i in city_indices], # Add jitter
        "lon": [cities[i][2] + np.random.uniform(-0.5,0.5) for i in city_indices], # Add jitter
    }
    
    df = pd.DataFrame(data)
    
    # Anomaly Classification Logic (Threshold > 8.0)
    df["anomaly_label"] = np.where(df["risk_score"] > 8.0, "Anomaly", "Normal") 
    
    # NLP-style Explanation Generation
    df["explanation"] = np.where(
        df["anomaly_label"] == "Anomaly",
        "Traffic pattern deviates >3σ from historical baseline.",
        "Authorized traffic within standard operating parameters."
    )
    
    # Automated Countermeasure Logic
    df["recommended_action"] = np.where(
        df["anomaly_label"] == "Anomaly",
        "BLOCK IP / ALERT WATCH OFFICER",
        "MONITOR"
    )
    
    return df

# Initialize Data Stream
df = load_live_traffic()

# ======================================================
# MODULE 5: SIDEBAR & STATE CONTROLS
# ======================================================
logo_path = get_asset_path("logo.png")
if logo_path:
    st.sidebar.image(str(logo_path), width=200) 
else:
    st.sidebar.markdown("## ⚓ COMMAND DECK")

st.sidebar.markdown("---")

# Manual Cache Invalidation Trigger
if st.sidebar.button("🔄 Refresh System"):
    st.cache_data.clear()
    st.rerun()

# Polling Toggle (Default: False to prevent infinite loop on load)
live_mode = st.sidebar.checkbox("📡 Live Sensor Feed", value=False)

st.sidebar.markdown("---")

# Global Filter Context
scope = st.sidebar.radio("Threat Horizon", ["All Traffic", "Active Threats Only", "Normal Traffic"])

# Render Operator Metadata
st.sidebar.markdown("""
<div class="operator-card">
    <p style="color:white; margin:0;"><b>👤 OPERATOR:</b><br>Mohammad Kasif Ansari</p><br>
    <p style="color:white; margin:0;"><b>🛡️ UNIT:</b><br>WAF-01 Alpha</p><br>
    <p style="color:white; margin:0;"><b>📍 STATION:</b><br>INS-Cyber</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# MODULE 6: MAIN VIEW CONTROLLER
# ======================================================

# Apply DataFrame Filtering based on Sidebar State
view_df = df.copy()
if scope == "Active Threats Only":
    view_df = view_df[view_df["anomaly_label"] == "Anomaly"]
elif scope == "Normal Traffic":
    view_df = view_df[view_df["anomaly_label"] == "Normal"]

# Compute Aggregate Metrics
threat_count = len(df[df["anomaly_label"] == "Anomaly"])
status_color = "#ff4b4b" if threat_count > 0 else "#00ff99"
status_text = f"HIGH ALERT: {threat_count} THREATS DETECTED" if threat_count > 0 else "SYSTEM SECURE"

# Render Dynamic Status Banner
st.markdown(f"""
<div style="background: rgba(0,0,0,0.6); border-left: 8px solid {status_color}; padding: 10px 20px; margin-bottom: 20px;">
    <h3 style="margin:0; color: {status_color} !important;">{status_text}</h3>
</div>
""", unsafe_allow_html=True)

st.title("🛡️ WAF DEFENSE COMMAND CENTER")

# Render KPI Cards
c1, c2, c3 = st.columns(3)
c1.metric("📡 Total Intercepts", f"{len(df):,}")
c2.metric("🚨 Active Threats", f"{threat_count:,}", delta_color="inverse")
c3.metric("✅ Secure Traffic", f"{len(df)-threat_count:,}")

st.markdown("---")

# ======================================================
# MODULE 7: VIEW COMPONENTS (TABS)
# ======================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 TACTICAL OVERVIEW", 
    "🌍 GEO THREAT MAP", 
    "📋 TRAFFIC LOGS", 
    "⚡ RESPONSE"
])

# --- VIEW: TACTICAL ANALYTICS ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Threat Classification")
        counts = view_df["anomaly_label"].value_counts()
        fig_pie = px.pie(
            names=counts.index, values=counts.values, hole=0.6,
            color=counts.index, color_discrete_map={"Normal": "#00cc96", "Anomaly": "#ff4b4b"}
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        st.subheader("Request Velocity")
        fig_hist = px.histogram(
            view_df, x="req_per_min", color="anomaly_label", barmode="overlay",
            color_discrete_map={"Normal": "#00cc96", "Anomaly": "#ff4b4b"}
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", xaxis_title="Requests/Min", yaxis_title="Count"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# --- VIEW: GEOSPATIAL INTELLIGENCE ---
with tab2:
    st.subheader("📍 Indian Ocean Threat Theater")
    threat_map_data = df[df["anomaly_label"] == "Anomaly"]
    
    if not threat_map_data.empty:
        # Downsample for rendering performance (limit to 1000 points)
        display_map_data = threat_map_data.sample(min(len(threat_map_data), 1000))
        
        fig_map = px.scatter_geo(
            display_map_data,
            lat="lat", lon="lon",
            color="risk_score",
            size="risk_score",
            scope="asia",
            projection="natural earth",
            color_continuous_scale="reds",
            hover_name="ip"
        )
        fig_map.update_geos(
            visible=True, resolution=50,
            showcountries=True, countrycolor="#00ffff",
            showland=True, landcolor="#0b1426",
            showocean=True, oceancolor="#000510"
        )
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r":0,"t":0,"l":0,"b":0},
            font_color="white"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No localized threats in this sector.")

# --- VIEW: TELEMETRY LOGS ---
with tab3:
    st.subheader("📋 Intercepted Signal Logs")
    
    # Render Data Grid (Head 1000 for DOM performance)
    st.dataframe(
        view_df[["timestamp", "ip", "req_per_min", "risk_score", "anomaly_label"]].sort_values("timestamp", ascending=False).head(1000),
        use_container_width=True,
        height=400
    )
    st.caption(f"Displaying most recent 1,000 of {len(view_df):,} records. Download full log below.")
    
    # Export Controller
    csv_data = view_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 DOWNLOAD FULL WATCH LOG (CSV)",
        data=csv_data,
        file_name="waf_watch_log.csv",
        mime="text/csv",
        type="primary"
    )

# --- VIEW: INCIDENT RESPONSE ---
with tab4:
    st.subheader("⚡ Active Threat Response")
    
    active_threats = df[df["anomaly_label"] == "Anomaly"]
    
    if active_threats.empty:
        st.success("✅ SECTOR CLEAR. NO ACTIVE TARGETS.")
    else:
        # Target Selection State
        target_list = active_threats["ip"].unique()
        selected_ip = st.selectbox("SELECT HOSTILE VECTOR:", target_list)
        
        # Fetch Record Details
        record = active_threats[active_threats["ip"] == selected_ip].iloc[0]
        
        # Render Warning UI
        st.markdown(f"""
        <div style="padding: 20px; background: rgba(255, 0, 0, 0.15); border: 2px solid #ff4b4b; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2 style="color: #ff4b4b !important; margin: 0; text-shadow: 0 0 10px red;">TARGET LOCKED: {record['ip']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Threat Metadata
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Risk Score", f"{record['risk_score']:.2f}")
        with c2:
            st.metric("Request Velocity", f"{record['req_per_min']}/min")
            
        st.markdown("---")
        
        # Decision Support System
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**🧠 AI DIAGNOSIS:**\n\n{record['explanation']}")
        with col_b:
            st.error(f"**🛡️ RECOMMENDED COUNTERMEASURE:**\n\n{record['recommended_action']}")

# ======================================================
# MODULE 8: FOOTER & COPYRIGHT
# ======================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #555; font-size: 0.8rem;">
    NAVAL INNOVATHON PROTOTYPE | CLASSIFIED | SYSTEM INTEGRITY: 100%
</div>
""", unsafe_allow_html=True)

# ======================================================
# MODULE 9: EVENT LOOP (POLLING MECHANISM)
# ======================================================
if live_mode:
    time.sleep(3) # Execution pause to simulate sensor scan interval
    st.rerun()    # Trigger re-render cycle