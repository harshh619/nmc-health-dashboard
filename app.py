import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import requests

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Nagpur Health Surveillance", page_icon="🏥", layout="wide")

# ==========================================
# 2. AUTHENTICATION (Hardcoded)
# ==========================================
def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center;'>🔒 Nagpur Health Portal Login</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Enter Password", type="password", help="Hint: nagpurhealth")
        if pwd == "nagpurhealth":
            st.session_state["password_correct"] = True
            st.rerun()
        elif pwd != "":
            st.error("Incorrect Password")
        st.stop()  # Do not continue if password is not correct

check_password()

# ==========================================
# 3. CUSTOM CSS & UI STYLING
# ==========================================
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #1E3A8A; font-weight: bold; text-align: center;}
    .insight-box {background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #2563EB;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR - PRO LIVE INDICATOR & NAVIGATION
# ==========================================
live_indicator_html = """
<style>
@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 213, 115, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(46, 213, 115, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 213, 115, 0); }
}
.live-indicator-box {
    display: flex; align-items: center; padding: 10px 15px;
    background-color: rgba(46, 213, 115, 0.1); border-radius: 8px;
    border: 1px solid rgba(46, 213, 115, 0.3); margin-bottom: 20px;
}
.blob {
    background: #2ed573; border-radius: 50%; height: 12px; width: 12px;
    box-shadow: 0 0 0 0 rgba(46, 213, 115, 1); animation: pulse 1.5s infinite; margin-right: 12px;
}
.live-text {
    font-weight: 600; color: #2ed573; font-size: 15px; font-family: sans-serif;
}
</style>
<div class="live-indicator-box">
    <div class="blob"></div>
    <div class="live-text">Live: Supabase Connected</div>
</div>
"""
st.sidebar.markdown(live_indicator_html, unsafe_allow_html=True)

st.sidebar.header("Navigation")
view_mode = st.sidebar.radio("Select View", ["Dashboard", "Map View", "Data Editor"])

# ==========================================
# 5. MULTI-TIERED DATA ENGINE
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    # Placeholder dataframe (Aap isko apne Supabase/Parquet logic se replace karein)
    # Example logic you have built:
    # try: 
    #     df = pd.read_parquet("data.parquet") # Tier 1: Fast Parquet
    # except:
    #     try: 
    #         conn = st.connection("supabase", type="supabase") # Tier 2: Supabase
    #         df = conn.query("*", table="patients_data", ttl=0).execute()
    #     except:
    #         df = pd.read_excel("Table.xlsx") # Tier 3: Fallback 
            
    # Dummy data for demonstration
    data = {
        "Disease": ["Dengue", "Malaria", "COVID-19", "Dengue", "Typhoid", "Malaria"],
        "Zone": ["North", "South", "East", "West", "Central", "North"],
        "Lat": [21.1458, 21.1500, 21.1400, 21.1600, 21.1350, 21.1480],
        "Long": [79.0882, 79.0900, 79.0800, 79.0950, 79.0700, 79.0850]
    }
    return pd.DataFrame(data)

df = load_data()

# ==========================================
# 6. MAIN DASHBOARD CONTENT
# ==========================================
st.markdown("<div class='main-header'>🏥 Nagpur Public Health Surveillance</div>", unsafe_allow_html=True)
st.write("---")

if view_mode == "Dashboard":
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # 6.1 Weather Widget (Placeholder)
    with col1:
        st.subheader("🌦️ Nagpur Weather")
        st.info("**Temp:** 32°C | **Humidity:** 65%\n\n*High humidity indicates mosquito breeding risk.*")
        
    # 6.2 AI Insights
    with col2:
        st.subheader("🧠 AI Health Insights")
        st.markdown("<div class='insight-box'><strong>Alert:</strong> High Dengue cases detected in North Zone. Recommend immediate fogging.</div>", unsafe_allow_html=True)
        
    # 6.3 KPI Metrics
    with col3:
        st.subheader("📊 Quick Stats")
        st.metric(label="Total Cases Today", value=len(df), delta="+2 from yesterday")

    st.write("---")
    
    # 6.4 Disease Distribution - Bold Text Pie Chart
    st.subheader("🦠 Disease Distribution")
    disease_counts = df['Disease'].value_counts().reset_index()
    disease_counts.columns = ['Disease', 'Count']
    
    fig = px.pie(disease_counts, names='Disease', values='Count', hole=0.3)
    # YAHAN TEXT BOLD KIYA GAYA HAI:
    fig.update_traces(
        textinfo='label+value', 
        textfont=dict(size=16, color='black', family='Arial Black', weight='bold')
    )
    st.plotly_chart(fig, use_container_width=True)

elif view_mode == "Map View":
    # 6.5 Multi-view Interactive Mapping (Folium)
    st.subheader("🗺️ Case Heatmap & Ward Map")
    
    # Basic Folium Map Centered on Nagpur
    m = folium.Map(location=[21.1458, 79.0882], zoom_start=12)
    
    # Add Markers from DataFrame
    for idx, row in df.iterrows():
        folium.CircleMarker(
            location=[row['Lat'], row['Long']],
            radius=8,
            popup=f"Disease: {row['Disease']} <br> Zone: {row['Zone']}",
            color="red",
            fill=True,
            fill_color="red"
        ).add_to(m)
        
    # Note: Aap yahan wards_simplified.geojson ko folium.GeoJson ke through add kar sakte hain
    
    st_folium(m, width=900, height=500)

elif view_mode == "Data Editor":
    # 6.6 Backend Data Management (Supabase prep)
    st.subheader("🗄️ Database Management")
    st.write("Edit database directly (Changes will sync to Supabase)")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes to Supabase"):
        st.success("Syncing to Supabase (Backend setup required)...")
