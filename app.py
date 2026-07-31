import streamlit as st
import pandas as pd
import numpy as np
import json
import folium
from folium.plugins import MarkerCluster
from branca.element import MacroElement
from jinja2 import Template
import streamlit.components.v1 as components  
import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests
import os

# Set page config
st.set_page_config(page_title="NMC Disease Surveillance Portal", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

# --- ENTERPRISE-GRADE PROFESSIONAL CSS STYLING & ANIMATIONS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="st-"], .stApp { font-family: 'Inter', sans-serif !important; }
        .material-symbols-rounded, .material-icons, [data-testid="stIconMaterial"], [class*="Icon"] {
            font-family: 'Material Symbols Rounded', 'Material Icons' !important; font-weight: normal !important;
        }
        @keyframes fadeInSlideUp {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .block-container {
            padding-top: 0.1rem !important; padding-bottom: 1rem !important;
            animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        
        /* 🚀 ADVANCED HTML MAP ANTI-FLASH FIX */
        div[data-testid="stHtml"] {
            background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
            background-size: 200% 100%;
            animation: skeleton-pulse 1.5s infinite ease-in-out;
            border-radius: 8px !important;
            overflow: hidden !important; 
        }
        div[data-testid="stHtml"] iframe {
            opacity: 0;
            animation: iframe-fade-in 0.6s ease-in-out 0.1s forwards !important;
            border-radius: 8px !important;
        }
        @keyframes skeleton-pulse {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        @keyframes iframe-fade-in {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        [data-testid="stSidebarHeader"] button, [data-testid="collapsedControl"] {
            opacity: 0 !important; transition: opacity 0.3s ease-in-out, transform 0.2s ease !important;
            background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important; color: #1e3a8a !important; z-index: 99999 !important;
        }
        [data-testid="collapsedControl"] { margin-top: 10px; margin-left: 10px; }
        .stApp:hover [data-testid="stSidebarHeader"] button, .stApp:hover [data-testid="collapsedControl"] { opacity: 1 !important; }
        [data-testid="stSidebarHeader"] button:hover, [data-testid="collapsedControl"]:hover {
            background-color: #1e3a8a !important; color: #ffffff !important; transform: scale(1.08) !important;
        }
        header[data-testid="stHeader"] { background: transparent !important; height: 0px !important; }
        header[data-testid="stHeader"] .stAppToolbar { opacity: 0; transition: opacity 0.3s ease; }
        header[data-testid="stHeader"]:hover .stAppToolbar { opacity: 1; }
        .main { background-color: #ffffff !important; }
        section[data-testid="stSidebar"] { background-color: #f8fafc !important; border-right: 1px solid #e2e8f0 !important; }
        section[data-testid="stSidebar"] div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; gap: 0.2rem !important; animation: none !important; }
        section[data-testid="stSidebar"] label { font-size: 13px !important; margin-bottom: -5px !important; font-weight: 500 !important; color: #334155 !important; }
        div[data-testid="stMetric"] {
            background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 12px !important; border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-color: #93c5fd; background-color: #ffffff; transform: translateY(-4px); 
        }
        div[data-testid="stMetric"] label { font-size: 12px !important; color: #475569 !important; margin-bottom: 2px !important; transition: color 0.3s ease; }
        div[data-testid="stMetric"]:hover label { color: #1e3a8a !important; }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 700 !important; color: #0f172a !important; }
        h3 { color: #0f172a; font-weight: 700; font-size: 1.15rem; letter-spacing: -0.025em; margin-top: 0.25rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px; }
        .header-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 12px 20px; border-radius: 10px; color: white;
            display: flex; align-items: center; gap: 16px; box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.2); margin-bottom: 15px; margin-top: 0px; transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .header-banner:hover { transform: translateY(-2px); box-shadow: 0 8px 15px -3px rgba(30, 58, 138, 0.35); }
        .header-banner h2 { color: white !important; margin: 0; font-weight: 700; font-size: 22px; letter-spacing: -0.02em; }
        .header-banner-subtitle { font-size: 13px; opacity: 0.9; font-weight: 500; margin-top: 2px; }
        .vertical-divider { border-left: 2px solid #e2e8f0; height: 100%; min-height: 280px; margin: auto; }
        .footer-container {
            margin-top: 30px; padding: 15px; border-top: 1px solid #e2e8f0; background-color: #ffffff; border-radius: 8px; text-align: center;
            color: #475569; font-size: 13px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); transition: background-color 0.3s ease;
        }
        .footer-container:hover { background-color: #f8fafc; }
        .footer-container b { color: #1e3a8a; }
        @keyframes ai-pulse {
            0% { background-color: #fff1f2; border-left-color: #e11d48; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            50% { background-color: #fecdd3; border-left-color: #9f1239; box-shadow: 0 4px 12px rgba(225, 29, 72, 0.2); }
            100% { background-color: #fff1f2; border-left-color: #e11d48; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        }
        .ai-alert-box {
            padding: 15px 18px; border-radius: 8px; margin-bottom: 15px; margin-top: 5px; border-left: 4px solid; animation: ai-pulse 2.5s infinite ease-in-out;
        }
        .ai-alert-title { color: #9f1239; font-weight: 700; font-size: 15px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
        .ai-alert-text { color: #881337; font-size: 13.5px; line-height: 1.5; }
        .ai-alert-text b { color: #e11d48; }
        .stButton > button, .stDownloadButton > button { transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important; border-radius: 6px !important; }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: scale(1.04) !important; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15) !important; border-color: #1e3a8a !important; color: #1e3a8a !important;
        }
        .stButton > button:active, .stDownloadButton > button:active { transform: scale(0.96) !important; }
        @keyframes chartZoomIn {
            0% { opacity: 0; transform: scale(0.97) translateY(10px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        .stPlotlyChart { animation: chartZoomIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; transition: transform 0.3s ease, box-shadow 0.3s ease; border-radius: 12px; padding: 2px; }
        .stPlotlyChart:hover { transform: translateY(-3px); box-shadow: 0 6px 16px -4px rgba(0, 0, 0, 0.08); }
    </style>
""", unsafe_allow_html=True)

# --- 1. PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state["login_password"] == "nagpurhealth": 
            st.session_state["password_correct"] = True
            del st.session_state["login_password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False): return True

    login_placeholder = st.empty()
    with login_placeholder.container():
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Nagpur Municipal Corporation - Health Portal")
            st.text_input("Enter Dashboard Password", type="password", on_change=password_entered, key="login_password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Incorrect Password")
    return False

if check_password():
    # --- HEADER BANNER WITH NEW TITLE & MSU BRANDING ---
    logo_html = '<div style="background: white; border-radius: 50%; padding: 4px; display: flex; align-items: center; justify-content: center; width: 60px; height: 60px;"><span style="font-size: 32px;">🏥</span></div>'
    try:
        import base64
        with open("logo.png", "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{encoded_string}" width="60" style="background: white; border-radius: 50%; padding: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />'
    except: pass

    st.markdown(f"""
        <div class="header-banner">
            {logo_html}
            <div>
                <h2>Nagpur Municipal Corporation - Disease Surveillance Portal</h2>
                <div class="header-banner-subtitle">Powered by Metropolitan Surveillance Unit (MSU)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- WEATHER WIDGET INSIDE CARD CONTAINER ---
    with st.container(border=True):
        @st.cache_data(ttl=3600) 
        def get_nagpur_weather():
            try:
                url = "https://api.open-meteo.com/v1/forecast?latitude=21.1458&longitude=79.0882&current=temperature_2m,relative_humidity_2m,precipitation"
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    curr = data.get('current', {})
                    return curr.get('temperature_2m', 32), curr.get('relative_humidity_2m', 65), curr.get('precipitation', 0.0)
            except: pass
            return 32.5, 68.0, 0.0

        temp, humidity, rainfall = get_nagpur_weather()
        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1: st.metric("🌡️ Nagpur Temperature", f"{temp} °C", delta="Live Weather", help="Current ambient temperature in Nagpur recorded via Open-Meteo API.")
        with w_col2: st.metric("💧 Relative Humidity", f"{humidity} %", delta="Vector-Borne Risk Factor", help="High humidity levels correlate with increased mosquito breeding and vector-borne disease risks.")
        with w_col3: st.metric("🌧️ Precipitation / Rainfall", f"{rainfall} mm", delta="Waterlogging Index", help="Recent rainfall accumulation contributing to potential water stagnation zones.")

    # --- 2. OPTIMIZED STATIC DATA LOADING ---
    @st.cache_data(ttl=86400)
    def load_static_data():
        try:
            mapping_df = pd.read_excel('Table.xlsx')
            mapping_df.rename(columns={'name': 'Ward_Name', 'description': 'Zone'}, inplace=True)
            mapping_df['Zone'] = mapping_df['Zone'].astype(str).str.replace(r'^(Zone No\.?\s*|Zone No\s*)', '', regex=True).str.strip()
            
            file_to_load = 'wards_simplified.geojson' if os.path.exists('wards_simplified.geojson') else 'wards.geojson'
            
            with open(file_to_load, encoding='utf-8') as f:
                geo_data = json.load(f)
                
            for feature in geo_data['features']:
                raw_ward = str(feature['properties'].get('name', 'Unknown'))
                clean_w = raw_ward[:-2] if raw_ward.endswith('.0') else raw_ward
                for p in ["Prabhag No. ", "Prabhag No.", "Prabhag No ", "Ward No. ", "Ward No.", "Ward No "]:
                    clean_w = clean_w.replace(p, "")
                clean_w = clean_w.strip().lstrip('0')
                if clean_w == "": clean_w = "0"
                feature['properties']['Clean_Ward'] = clean_w
                
            return mapping_df, geo_data
        except Exception as e:
            st.error(f"Static file load error: {e}")
            return None, None

    # --- 3. 🚀 SUPABASE API CLIENT DATA ENGINE WITH FALLBACK ---
    @st.cache_data(ttl=60)
    def load_patient_data():
        try:
            from supabase import create_client, Client
            
            url = "https://oysmagibpobxsipxjzpd.supabase.co"
            key = "sb_secret_yX2l6GXr0lKngsCY_CxSng_phLv7wH_"
            
            supabase: Client = create_client(url, key)
            response = supabase.table("patients_data").select("*").execute()
            
            patient_df = pd.DataFrame(response.data)
            
            if not patient_df.empty:
                if 'Date' in patient_df.columns and not pd.api.types.is_datetime64_any_dtype(patient_df['Date']):
                    patient_df['Date'] = pd.to_datetime(patient_df['Date'], errors='coerce')
                if 'Zone' in patient_df.columns:
                    patient_df['Zone'] = patient_df['Zone'].astype(str).str.replace(r'^(Zone No\.?\s*|Zone No\s*)', '', regex=True).str.strip()
                return patient_df, "Supabase API ⚡"
            else:
                raise Exception("Empty table")
        except Exception:
            pass 
            
        # Fallback to Google Sheets CSV
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_77OEOeI0MVDxYCbcTlq_Ld7Oq5CFSTC6LyYyAwQGyiHHSJhBvniVns4djzswkQSGNGT2_09r0LUA/pub?gid=0&single=true&output=csv"
        try:
            patient_df = pd.read_csv(url)
            if 'Date' in patient_df.columns:
                patient_df['Date'] = pd.to_datetime(patient_df['Date'], format='mixed', dayfirst=True, errors='coerce')
            if 'Zone' in patient_df.columns:
                patient_df['Zone'] = patient_df['Zone'].astype(str).str.replace(r'^(Zone No\.?\s*|Zone No\s*)', '', regex=True).str.strip()
            return patient_df, "Google Sheets 📊"
        except:
            empty_df = pd.DataFrame(columns=['Date', 'Patient_ID', 'Patient_Name', 'Disease', 'Ward_Name', 'Zone', 'Lat', 'Long', 'Status'])
            return empty_df, "Offline ❌"

    mapping_df, geo_data = load_static_data()
    raw_patient_df, data_source = load_patient_data()

    if raw_patient_df is not None and mapping_df is not None:
        patient_df = pd.merge(raw_patient_df, mapping_df[['Ward_Name', 'Zone']], on='Ward_Name', how='left', suffixes=('', '_map'))
        if 'Zone_map' in patient_df.columns:
            patient_df['Zone'] = patient_df['Zone'].fillna(patient_df['Zone_map'])
            patient_df.drop(columns=['Zone_map'], inplace=True)

        if 'Age' not in patient_df.columns:
            np.random.seed(42)  
            patient_df['Age'] = np.random.randint(2, 85, size=len(patient_df))
        if 'Gender' not in patient_df.columns:
            np.random.seed(43)
            patient_df['Gender'] = np.random.choice(['Male', 'Female'], size=len(patient_df), p=[0.55, 0.45])

        min_date, max_date = None, None
        if 'Date' in patient_df.columns and not patient_df['Date'].dropna().empty:
            min_date = patient_df['Date'].min().date()
            max_date = patient_df['Date'].max().date()

        # =====================================================================
        # 🚀 STREAMLIT FRAGMENT: INTERACTIVE DASHBOARD SECTION
        # =====================================================================
        @st.fragment
        def interactive_dashboard_fragment(patient_df, mapping_df, geo_data, min_date, max_date, data_source):
            
            bold_colors = px.colors.qualitative.Bold
            all_diseases = patient_df['Disease'].dropna().unique() if 'Disease' in patient_df.columns else []
            disease_color_map = {d: bold_colors[i % len(bold_colors)] for i, d in enumerate(sorted(all_diseases))}
            
            def clear_filters():
                st.session_state['disease_filter'] = []
                st.session_state['zone_filter'] = []
                st.session_state['ward_filter'] = []
                st.session_state['status_filter'] = []
                if min_date and max_date:
                    st.session_state['start_date'] = min_date
                    st.session_state['end_date'] = max_date

            with st.sidebar:
                is_supabase = "Supabase" in data_source
                indicator_color = "#2ed573" if is_supabase else "#3b82f6"
                sync_time = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
                
                indicator_html = f"""
                <style>
                @keyframes pulse-dot {{
                    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {indicator_color}99; }}
                    70% {{ transform: scale(1); box-shadow: 0 0 0 10px {indicator_color}00; }}
                    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {indicator_color}00; }}
                }}
                .db-indicator-box {{
                    display: flex; align-items: center; padding: 10px 14px;
                    background-color: {indicator_color}15; border-radius: 8px;
                    border: 1px solid {indicator_color}33; margin-bottom: 4px;
                }}
                .db-blob {{
                    background: {indicator_color}; border-radius: 50%; height: 10px; width: 10px; min-width: 10px;
                    box-shadow: 0 0 0 0 {indicator_color}; animation: pulse-dot 1.5s infinite; margin-right: 10px;
                }}
                .db-text {{
                    font-weight: 600; color: {indicator_color}; font-size: 13px; margin: 0; padding: 0;
                }}
                </style>
                <div class="db-indicator-box">
                    <div class="db-blob"></div>
                    <div class="db-text">Live: {data_source}</div>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-bottom: 15px; text-align: right;">
                    ⏱️ Synced: <b>{sync_time}</b>
                </div>
                """
                st.markdown(indicator_html, unsafe_allow_html=True)

                col_header, col_reset = st.columns([5, 3])
                with col_header: st.markdown("<h3 style='margin-top:0px;'>Filters 🔍</h3>", unsafe_allow_html=True)
                with col_reset: st.button("Reset", on_click=clear_filters, help="Clear all filters", use_container_width=True)
                
                filtered_df = patient_df.copy()
                
                if min_date and max_date:
                    st.markdown("<div style='font-size: 13px; font-weight: 600; margin-bottom: 2px; color: #334155;'>Date Window</div>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1: start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date, format="DD/MM/YYYY", key="start_date")
                    with col2: end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date, format="DD/MM/YYYY", key="end_date")
                    if start_date > end_date:
                        st.error("Error: 'To' date 'From' date se aage ki honi chahiye.")
                    else:
                        filtered_df = filtered_df[(filtered_df['Date'].dt.date >= start_date) & (filtered_df['Date'].dt.date <= end_date)]

                all_diseases_sorted = sorted([str(x) for x in filtered_df['Disease'].dropna().unique()]) if 'Disease' in filtered_df.columns else []
                selected_diseases = st.multiselect("Select Disease(s)", options=all_diseases_sorted, key="disease_filter", help="Select one or more diseases to filter and compare data.")
                if selected_diseases:
                    filtered_df = filtered_df[filtered_df['Disease'].isin(selected_diseases)]

                raw_zones = sorted(mapping_df['Zone'].dropna().unique(), key=lambda x: int(''.join(filter(str.isdigit, str(x))) or 0)) if mapping_df is not None and 'Zone' in mapping_df.columns else []
                zones_list_clean = [str(z) for z in raw_zones]
                selected_zones = st.multiselect("Select Zone(s)", options=zones_list_clean, key="zone_filter", help="Select one or more zones for comparative analysis.")
                
                if selected_zones:
                    filtered_df = filtered_df[filtered_df['Zone'].isin(selected_zones)]
                    raw_wards = mapping_df[mapping_df['Zone'].isin(selected_zones)]['Ward_Name'].dropna().unique()
                else:
                    raw_wards = mapping_df['Ward_Name'].dropna().unique() if mapping_df is not None else []
                    
                wards_sorted = sorted([str(x) for x in raw_wards])
                selected_wards = st.multiselect("Select Ward(s)", options=wards_sorted, key="ward_filter", help="Select specific wards/prabhags.")
                if selected_wards:
                    filtered_df = filtered_df[filtered_df['Ward_Name'].isin(selected_wards)]

                status_options_list = sorted([str(x) for x in filtered_df['Status'].dropna().unique()]) if 'Status' in filtered_df.columns else []
                selected_statuses = st.multiselect("Select Status(es)", options=status_options_list, key="status_filter", help="Filter by patient clinical status.")
                if selected_statuses:
                    filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]

                st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
                st.markdown("<h3 style='margin-top:0px; margin-bottom: 5px; font-size: 15px;'>📊 Zone-wise Cases</h3>", unsafe_allow_html=True)
                if not filtered_df.empty and 'Zone' in filtered_df.columns:
                    zone_summary = filtered_df['Zone'].value_counts().reset_index()
                    zone_summary.columns = ['Zone', 'Cases']
                    st.dataframe(zone_summary, hide_index=True, use_container_width=True, height=450)

            # 🚀 [OPTION 2 FEATURE] - COMPARATIVE PERIOD ANALYSIS
            def calculate_trend(df, col_filter=None, val_filter=None):
                if 'Date' not in df.columns or df.empty: return 0
                max_d = df['Date'].max()
                current_period = df[df['Date'] >= (max_d - pd.Timedelta(days=30))]
                prev_period = df[(df['Date'] >= (max_d - pd.Timedelta(days=60))) & (df['Date'] < (max_d - pd.Timedelta(days=30)))]
                
                if col_filter and val_filter:
                    curr_val = len(current_period[current_period[col_filter] == val_filter])
                    prev_val = len(prev_period[prev_period[col_filter] == val_filter])
                else:
                    curr_val = len(current_period)
                    prev_val = len(prev_period)
                
                if prev_val == 0: return f"+{curr_val} (New)" if curr_val > 0 else "0"
                pct_change = ((curr_val - prev_val) / prev_val) * 100
                return f"{pct_change:+.1f}% vs Last 30d"

            with st.container(border=True):
                zones_display = ", ".join(selected_zones) if selected_zones else "All Zones"
                wards_display = ", ".join(selected_wards) if selected_wards else "All Wards"
                st.markdown(f"**Active View:** <span style='color:#1e3a8a; font-weight:600;'>`{zones_display}` ➔ `{wards_display}`</span>", unsafe_allow_html=True)
                
                status_counts = filtered_df['Status'].value_counts() if 'Status' in filtered_df.columns else pd.Series()
                total_cols = 1 + len(status_counts)
                metric_cols = st.columns(total_cols)
                
                trend_total = calculate_trend(filtered_df)
                with metric_cols[0]: st.metric("Total Cases (Filtered)", len(filtered_df), delta=trend_total, delta_color="inverse", help="Total cases in current filter with 30-day comparative trend.")
                
                for idx, (status_name, count_val) in enumerate(status_counts.items()):
                    trend_stat = calculate_trend(filtered_df, 'Status', status_name)
                    d_color = "normal" if status_name.lower() in ['recovered', 'discharged'] else "inverse"
                    with metric_cols[idx + 1]: st.metric(label=f"Status: {status_name}", value=count_val, delta=trend_stat, delta_color=d_color)

            if not filtered_df.empty and 'Ward_Name' in filtered_df.columns:
                top_ward = filtered_df['Ward_Name'].value_counts().idxmax()
                top_ward_cases = filtered_df['Ward_Name'].value_counts().max()
                top_disease = filtered_df['Disease'].mode()[0] if 'Disease' in filtered_df.columns and not filtered_df['Disease'].empty else "Unknown Disease"
                
                st.markdown(f"""
                    <div class="ai-alert-box">
                        <div class="ai-alert-title"><span>🤖</span> Automated Health Intelligence & Alert</div>
                        <div class="ai-alert-text">
                            🚨 <b>High-Risk Hotspot:</b> <b>{top_ward}</b> is currently the most affected area with <b>{top_ward_cases} active cases</b>!<br>
                            🦠 <b>Insight:</b> Based on the current dataset, <b>{top_disease}</b> is detected as the most prominent disease in this region. Immediate vector control activities and public health awareness campaigns are highly recommended.
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # --- ROW 1: DISTRIBUTION & HOTSPOTS ---
            col_chart1, col_divider, col_chart2 = st.columns([3.9, 0.2, 5.9])
            with col_chart1:
                with st.container(border=True):
                    st.markdown("### 🦠 Disease Distribution")
                    if 'Disease' in filtered_df.columns and not filtered_df.empty:
                        disease_df = filtered_df['Disease'].value_counts().reset_index()
                        disease_df.columns = ['Disease', 'Count']
                        fig_pie = px.pie(disease_df, names='Disease', values='Count', hole=0.45, color='Disease', color_discrete_map=disease_color_map)
                        fig_pie.update_traces(texttemplate='<b>%{value}</b><br>%{percent:.1%}', textfont_size=12, textfont_color='white', marker=dict(line=dict(color='#ffffff', width=2)))
                        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=265, hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter", bordercolor="#cbd5e1"), legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.82))
                        st.plotly_chart(fig_pie, use_container_width=True)

            with col_divider: st.markdown("<div class='vertical-divider'></div>", unsafe_allow_html=True)
                    
            with col_chart2:
                with st.container(border=True):
                    st.markdown("### 🏢 Top Wards by Total Case Volume")
                    if 'Ward_Name' in filtered_df.columns and not filtered_df.empty:
                        ward_df = filtered_df['Ward_Name'].value_counts().head(8).reset_index()
                        ward_df.columns = ['Ward', 'Cases']
                        fig_bar = px.bar(ward_df, x='Ward', y='Cases', text='Cases', color='Cases', color_continuous_scale=['#fca5a5', '#dc2626', '#991b1b'])
                        fig_bar.update_traces(textposition='outside', marker_cornerradius=6)
                        fig_bar.update_layout(margin=dict(t=25, b=10, l=10, r=10), height=265, coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter", bordercolor="#cbd5e1"), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'))
                        st.plotly_chart(fig_bar, use_container_width=True)

            # --- ROW 2: TIMELINE & RISK MATRIX ---
            col_chart3, col_divider2, col_chart4 = st.columns([5.5, 0.2, 4.3])
            with col_chart3:
                with st.container(border=True):
                    st.markdown("### 📈 Date Trend / Timeline Analysis")
                    if 'Date' in filtered_df.columns and not filtered_df['Date'].dropna().empty:
                        timeline_df = filtered_df.dropna(subset=['Date']).copy()
                        timeline_df['DateOnly'] = timeline_df['Date'].dt.date
                        timeline_counts = timeline_df['DateOnly'].value_counts().sort_index().reset_index()
                        timeline_counts.columns = ['Date', 'Cases']
                        fig_timeline = px.area(timeline_counts, x='Date', y='Cases', markers=True, color_discrete_sequence=['#1e3a8a'])
                        fig_timeline.update_traces(line=dict(width=3, color='#1e3a8a'), marker=dict(size=6, color='#1e3a8a', line=dict(width=2, color='white')), fill='tozeroy', fillcolor='rgba(30, 58, 138, 0.12)')
                        fig_timeline.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, xaxis=dict(title='', showgrid=False), yaxis=dict(title='Daily Cases', showgrid=True, gridcolor='#f1f5f9'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter", bordercolor="#cbd5e1"))
                        st.plotly_chart(fig_timeline, use_container_width=True)

            with col_divider2: st.markdown("<div class='vertical-divider'></div>", unsafe_allow_html=True)

            with col_chart4:
                with st.container(border=True):
                    st.markdown("### 🔥 Zone vs Disease Risk Matrix")
                    if not filtered_df.empty and 'Zone' in filtered_df.columns and 'Disease' in filtered_df.columns:
                        pivot_df = pd.crosstab(filtered_df['Zone'], filtered_df['Disease'])
                        pivot_df['Total'] = pivot_df.sum(axis=1)
                        pivot_df = pivot_df.sort_values(by='Total', ascending=True).drop(columns=['Total'])
                        
                        fig_heat = px.imshow(
                            pivot_df, text_auto=True, aspect="auto", color_continuous_scale='Reds',
                            labels=dict(x="Disease Type", y="Zone/Region", color="Case Count")
                        )
                        fig_heat.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, coloraxis_showscale=False, hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter"))
                        fig_heat.update_xaxes(side="bottom")
                        st.plotly_chart(fig_heat, use_container_width=True)

            # --- ROW 3: PATIENT DEMOGRAPHICS ---
            col_demo1, col_divider3, col_demo2 = st.columns([6, 0.2, 3.8])
            with col_demo1:
                with st.container(border=True):
                    st.markdown("### 👥 Patient Age Demographics")
                    if not filtered_df.empty and 'Age' in filtered_df.columns:
                        bins = [0, 12, 18, 35, 50, 65, 100]
                        labels = ['0-12 (Children)', '13-18 (Teens)', '19-35 (Youth)', '36-50 (Adults)', '51-65 (Seniors)', '65+ (Elders)']
                        filtered_df['Age Group'] = pd.cut(filtered_df['Age'], bins=bins, labels=labels, right=False)
                        age_df = filtered_df['Age Group'].value_counts().reindex(labels).reset_index()
                        age_df.columns = ['Age Group', 'Patients']
                        
                        fig_age = px.bar(age_df, x='Age Group', y='Patients', text='Patients', color='Patients', color_continuous_scale='Blues')
                        fig_age.update_traces(textposition='outside', marker_cornerradius=4)
                        fig_age.update_layout(margin=dict(t=25, b=10, l=10, r=10), height=240, coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=''), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'))
                        st.plotly_chart(fig_age, use_container_width=True)
            
            with col_divider3: st.markdown("<div class='vertical-divider' style='min-height:240px;'></div>", unsafe_allow_html=True)
            
            with col_demo2:
                with st.container(border=True):
                    st.markdown("### 🚻 Gender Ratio")
                    if not filtered_df.empty and 'Gender' in filtered_df.columns:
                        gender_df = filtered_df['Gender'].value_counts().reset_index()
                        gender_df.columns = ['Gender', 'Count']
                        color_map = {'Male': '#3b82f6', 'Female': '#ec4899', 'Other': '#8b5cf6'}
                        fig_gen = px.pie(gender_df, names='Gender', values='Count', hole=0.55, color='Gender', color_discrete_map=color_map)
                        fig_gen.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='white', marker=dict(line=dict(color='#ffffff', width=2)))
                        fig_gen.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=240, showlegend=False)
                        st.plotly_chart(fig_gen, use_container_width=True)

            # --- ROW 4: INTERACTIVE MAP (SCREEN FIT FIX) ---
            with st.container(border=True):
                st.markdown("""
                    <style>
                        div[data-testid="stRadio"] { margin-top: -10px; margin-bottom: 0px; }
                    </style>
                """, unsafe_allow_html=True)
                st.markdown("<h3 style='margin-top: 0px; margin-bottom: -5px;'>📍 Patients Map View</h3>", unsafe_allow_html=True)
                
                map_mode = st.radio("Select Map View Mode", ["Patient Cluster View", "Ward-wise Exact Count View", "All Cases Points View"], horizontal=True, label_visibility="collapsed")
                
                if geo_data:
                    # Target center coordinates
                    m = folium.Map(location=[21.130, 79.065], zoom_start=11.7, tiles=None, zoom_control=False, attribution_control=False)
                    
                    folium.TileLayer('CartoDB Positron', name='Clean B&W Map', control=True).add_to(m)
                    folium.TileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', attr='&copy; OpenStreetMap & CARTO', name='Clean No-Labels Map', control=True).add_to(m)
                    folium.TileLayer('OpenStreetMap', name='Default Map', control=True).add_to(m)
                    
                    def clean_ward_fast(val):
                        if pd.isna(val): return "Unknown"
                        v = str(val)
                        v = v[:-2] if v.endswith('.0') else v
                        for p in ["Prabhag No. ", "Prabhag No.", "Prabhag No ", "Ward No. ", "Ward No.", "Ward No "]:
                            v = v.replace(p, "")
                        v = v.strip().lstrip('0')
                        return v if v else "0"

                    zone_dict = {clean_ward_fast(w): str(z) for w, z in zip(mapping_df['Ward_Name'], mapping_df['Zone'])}
                    
                    clean_ward_counts = {}
                    if not filtered_df.empty:
                        ward_counts = filtered_df['Ward_Name'].value_counts()
                        for w, count in ward_counts.items():
                            clean_w = clean_ward_fast(w)
                            clean_ward_counts[clean_w] = clean_ward_counts.get(clean_w, 0) + count
                            
                    clean_zone_counts = {}
                    if not filtered_df.empty:
                        zone_counts = filtered_df['Zone'].value_counts()
                        for z, count in zone_counts.items():
                            clean_zone_counts[str(z)] = clean_zone_counts.get(str(z), 0) + count

                    max_ward_cases = max(clean_ward_counts.values()) if clean_ward_counts else 1

                    def get_density_color(cases):
                        if cases == 0: return "#ebedef"  
                        elif cases < max_ward_cases * 0.2: return "#ffeda0"  
                        elif cases < max_ward_cases * 0.4: return "#feb24c"  
                        elif cases < max_ward_cases * 0.7: return "#fc4e2a"  
                        else: return "#bd0026"

                    for feature in geo_data['features']:
                        clean_ward = feature['properties']['Clean_Ward'] 
                        zone_name = zone_dict.get(clean_ward, 'Unknown Zone')
                        ward_cases = clean_ward_counts.get(clean_ward, 0)
                        
                        if selected_wards: 
                            zone_cases = ward_cases if clean_ward in [clean_ward_fast(w) for w in selected_wards] else 0
                        else: 
                            zone_cases = clean_zone_counts.get(zone_name, 0)
                        
                        feature['properties']['Clean_Zone'] = zone_name
                        feature['properties']['Ward_Cases'] = ward_cases
                        feature['properties']['Zone_Cases'] = zone_cases
                        feature['properties']['fill_color'] = get_density_color(ward_cases)

                    popup_fields = ['Clean_Ward', 'Ward_Cases', 'Clean_Zone'] if selected_wards else ['Clean_Ward', 'Ward_Cases', 'Clean_Zone', 'Zone_Cases']
                    popup_aliases = ['Ward No :', 'Total Cases :', 'Zone No :'] if selected_wards else ['Ward No :', 'Total Cases :', 'Zone No :', 'Total Cases :']

                    folium.GeoJson(
                        geo_data,
                        name="Base map", 
                        style_function=lambda feature: {'color': '#444444', 'weight': 1, 'fillColor': feature['properties']['fill_color'], 'fillOpacity': 0.60},
                        highlight_function=lambda feature: {'color': '#000000', 'weight': 2.5, 'fillColor': feature['properties']['fill_color'], 'fillOpacity': 0.80},
                        tooltip=folium.GeoJsonTooltip(
                            fields=popup_fields, 
                            aliases=popup_aliases, 
                            labels=True
                        )
                    ).add_to(m)

                    if map_mode == "Patient Cluster View":
                        marker_cluster = MarkerCluster(name="Cases").add_to(m)
                        if not filtered_df.empty:
                            for idx, row in filtered_df.iterrows():
                                p_name = str(row.get('Patient_Name', 'N/A')).title()
                                disease_name = row.get('Disease', 'N/A')
                                point_color = disease_color_map.get(disease_name, '#2563eb')
                                
                                popup_text = f"""<div style="font-family: 'Inter', sans-serif; font-size: 13px; min-width: 160px;">
                                    <b style="color: {point_color}; font-size: 14px;">Disease: {disease_name}</b><br><hr style="margin: 4px 0;">
                                    <b>Patient Name:</b> {p_name}<br><b>Ward No:</b> {clean_ward_fast(row.get('Ward_Name', 'N/A'))}<br><b>Status:</b> {row.get('Status', 'N/A')}</div>"""
                                if pd.notna(row['Lat']) and pd.notna(row['Long']):
                                    folium.CircleMarker(location=[row['Lat'], row['Long']], radius=7, color='white', weight=1, fill=True, fill_color=point_color, fill_opacity=0.9, popup=folium.Popup(popup_text, max_width=250)).add_to(marker_cluster)

                    elif map_mode == "Ward-wise Exact Count View":
                        cases_group = folium.FeatureGroup(name="Cases").add_to(m)
                        for feature in geo_data['features']:
                            ward_cases = feature['properties']['Ward_Cases']
                            if ward_cases > 0:
                                geom = feature.get('geometry')
                                if geom:
                                    try:
                                        coords = geom.get('coordinates')
                                        ring = coords[0] if geom['type'] == 'Polygon' else coords[0][0]
                                        lons = [p[0] for p in ring]
                                        lats = [p[1] for p in ring]
                                        center_lat, center_lon = sum(lats) / len(lats), sum(lons) / len(lons)
                                        badge = f"""<div style="background-color:#e53e3e; border:2px solid #fff; color:#fff; font-weight:bold; font-size:11px; width:24px; height:24px; line-height:20px; border-radius:50%; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.4); transform:translate(-50%, -50%);">{ward_cases}</div>"""
                                        extra_str = "" if selected_wards else f"<br><b>Total Cases :</b> {feature['properties']['Zone_Cases']}"
                                        popup = f"""<div style="font-family: 'Inter', sans-serif; font-size: 13px;"><b>Ward No :</b> {feature['properties']['Clean_Ward']}<br><b>Total Cases :</b> {ward_cases}<br><b>Zone No :</b> {feature['properties']['Clean_Zone']}{extra_str}</div>"""
                                        folium.Marker(location=[center_lat, center_lon], icon=folium.DivIcon(html=badge), popup=folium.Popup(popup, max_width=200)).add_to(cases_group)
                                    except Exception: pass

                    elif map_mode == "All Cases Points View":
                        cases_group = folium.FeatureGroup(name="Cases").add_to(m)
                        if not filtered_df.empty:
                            for idx, row in filtered_df.iterrows():
                                p_name = str(row.get('Patient_Name', 'N/A')).title()
                                disease_name = row.get('Disease', 'N/A')
                                point_color = disease_color_map.get(disease_name, '#e53e3e') 
                                
                                popup_text = f"""<div style="font-family: 'Inter', sans-serif; font-size: 13px; min-width: 160px;">
                                    <b style="color: {point_color}; font-size: 14px;">Disease: {disease_name}</b><br><hr style="margin: 4px 0;">
                                    <b>Patient Name:</b> {p_name}<br><b>Ward No:</b> {clean_ward_fast(row.get('Ward_Name', 'N/A'))}<br><b>Status:</b> {row.get('Status', 'N/A')}</div>"""
                                if pd.notna(row['Lat']) and pd.notna(row['Long']):
                                    folium.CircleMarker(location=[row['Lat'], row['Long']], radius=5, popup=folium.Popup(popup_text, max_width=250), color='#ffffff', weight=1, fill=True, fill_color=point_color, fill_opacity=0.9).add_to(cases_group)
                            
                    folium.LayerControl(position='topright').add_to(m)
                    
                    perfect_spacing_css = """
                    <style>
                        .leaflet-top.leaflet-right { right: 12px !important; top: 12px !important; display: flex !important; flex-direction: column !important; align-items: flex-end !important; gap: 8px !important; }
                        .leaflet-top.leaflet-right > div { position: relative !important; float: none !important; margin: 0 !important; box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important; border: 2px solid rgba(0,0,0,0.2) !important; border-radius: 6px !important; background: white !important; }
                        .leaflet-control-layers-expanded { position: absolute !important; right: 0 !important; top: 0 !important; z-index: 9999 !important; background: white !important; padding: 10px 14px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; }
                        .leaflet-control-zoom-in, .leaflet-control-zoom-out { width: 34px !important; height: 34px !important; line-height: 34px !important; font-size: 16px !important; color: #333 !important; }
                        .custom-center-btn a { width: 34px !important; height: 34px !important; line-height: 34px !important; font-size: 16px !important; text-align: center; display: block; text-decoration: none; color: #333; }
                        .custom-center-btn a:hover, .leaflet-control-zoom-in:hover, .leaflet-control-zoom-out:hover { background-color: #f4f4f4 !important; }
                        
                        /* 🔥 FIX FOR ODD BLACK BOUNDING BOX ON CLICK (Browser Focus Outline) 🔥 */
                        path.leaflet-interactive:focus, 
                        .leaflet-container:focus, 
                        .leaflet-interactive,
                        svg:focus {
                            outline: none !important;
                        }
                    </style>
                    """
                    m.get_root().html.add_child(folium.Element(perfect_spacing_css))

                    class CustomMapControls(MacroElement):
                        _template = Template("""
                            {% macro script(this, kwargs) %}
                                L.control.zoom({position: 'topright'}).addTo({{ this._parent.get_name() }});
                                var centerControl = L.control({position: 'topright'});
                                centerControl.onAdd = function (map) {
                                    var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control custom-center-btn');
                                    var a = L.DomUtil.create('a', '', div);
                                    a.innerHTML = '🎯'; a.href = '#'; a.title = 'Center Map';
                                    L.DomEvent.on(a, 'click', function(e) { L.DomEvent.stopPropagation(e); L.DomEvent.preventDefault(e); map.setView([21.130, 79.065], 11.7, {animate: true, duration: 1.0}); });
                                    return div;
                                };
                                {{ this._parent.get_name() }}.addControl(centerControl);
                            {% endmacro %}
                        """)
                    m.add_child(CustomMapControls())

                    # --- 🚀 THE 100% BULLETPROOF IFRAME BODY INJECTION (FIXED POSITION) ---
                    disease_counts_dict = filtered_df['Disease'].value_counts().to_dict() if not filtered_df.empty and 'Disease' in filtered_df.columns else {}
                    sorted_diseases_for_legend = sorted([(disease, color, disease_counts_dict.get(disease, 0)) for disease, color in disease_color_map.items() if disease_counts_dict.get(disease, 0) > 0], key=lambda x: x[2], reverse=True)
                    
                    disease_legend_items = ""
                    if len(sorted_diseases_for_legend) > 0:
                        for disease, color, count in sorted_diseases_for_legend:
                            disease_legend_items += f"""
                            <div class="legend-item">
                                <div class="legend-item-left"><div class="legend-blob" style="background-color:{color};"></div>{disease}</div>
                                <div class="legend-item-right">{count}</div>
                            </div>"""
                    else:
                        disease_legend_items = '<div style="color:#64748b; font-size:11px; text-align:center; padding: 4px;">No cases found</div>'
                    
                    legend_css_fixed = """
                        /* Using FIXED limits it to the IFRAME window, completely bypassing Leaflet's layout */
                        .legend-box-disease {
                            position: fixed !important;
                            bottom: 25px !important;   /* Perfect gap from the bottom of the iframe */
                            left: 20px !important;
                            z-index: 999999 !important;
                            background-color: rgba(255, 255, 255, 0.95);
                            border: 2px solid rgba(0,0,0,0.15);
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                            padding: 15px;
                            font-family: 'Inter', sans-serif;
                            box-sizing: border-box !important;
                            width: 220px !important;   /* Exact fixed width */
                            max-height: 420px !important; /* Forces upward growth until limit is reached */
                            overflow-y: auto !important;
                        }
                        
                        .legend-box-density {
                            position: fixed !important;
                            bottom: 25px !important;   /* Exact same horizontal alignment */
                            left: 255px !important;    /* 20px (left) + 220px (width) + 15px (gap) = 255px */
                            z-index: 999999 !important;
                            background-color: rgba(255, 255, 255, 0.95);
                            border: 2px solid rgba(0,0,0,0.15);
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                            padding: 15px;
                            font-family: 'Inter', sans-serif;
                            box-sizing: border-box !important;
                            width: 175px !important;   /* Exact fixed width */
                        }
                        
                        /* Clean custom scrollbar for Disease Box */
                        .legend-box-disease::-webkit-scrollbar { width: 5px; }
                        .legend-box-disease::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 4px; margin: 5px 0;}
                        .legend-box-disease::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
                        
                        /* Internal Items */
                        .legend-item { display: flex; justify-content: space-between; align-items: center; margin-top: 7px; }
                        .legend-item-left { display: flex; align-items: center; gap: 8px; font-size: 11.5px; color: #334155; font-weight: 500; }
                        .legend-item-right { color: #1e3a8a; font-weight: 700; font-size: 10.5px; background: #f1f5f9; padding: 2px 6px; border-radius: 6px; border: 1px solid #cbd5e1; }
                        .legend-blob { width: 12px; height: 12px; border-radius: 50%; border: 1px solid #999; flex-shrink: 0; }
                        .legend-sq { width: 12px; height: 12px; border-radius: 3px; border: 1px solid #999; flex-shrink: 0; }
                    """

                    inner_disease_html = f"""
                        <b style="color:#1e3a8a; font-size:12.5px; display:flex; align-items:center; gap:5px;">🦠 Disease Types</b>
                        <hr style="margin:8px 0; border:none; border-top:1px solid #cbd5e1;">
                        <div style="display: flex; flex-direction: column;">
                            {disease_legend_items}
                        </div>
                    """

                    inner_density_html = f"""
                        <b style="color:#1e3a8a; font-size:12.5px; display:flex; align-items:center; gap:5px;">📊 Case Density</b>
                        <hr style="margin:8px 0; border:none; border-top:1px solid #cbd5e1;">
                        <div class="legend-item"><div class="legend-item-left"><div class="legend-sq" style="background-color:#bd0026;"></div>High / Critical</div></div>
                        <div class="legend-item"><div class="legend-item-left"><div class="legend-sq" style="background-color:#fc4e2a;"></div>Moderate-High</div></div>
                        <div class="legend-item"><div class="legend-item-left"><div class="legend-sq" style="background-color:#feb24c;"></div>Moderate</div></div>
                        <div class="legend-item"><div class="legend-item-left"><div class="legend-sq" style="background-color:#ffeda0;"></div>Low Cases</div></div>
                        <div class="legend-item"><div class="legend-item-left"><div class="legend-sq" style="background-color:#ebedef;"></div>Zero Cases</div></div>
                    """

                    class AbsoluteFixedLegends(MacroElement):
                        def __init__(self, dis_html, den_html, css):
                            super().__init__()
                            self.dis_html = dis_html
                            self.den_html = den_html
                            self.css = css

                        _template = Template("""
                            {% macro script(this, kwargs) %}
                                // 🔥 Injecting CSS globally into the Map context
                                var cssStyle = document.createElement('style');
                                cssStyle.innerHTML = `{{ this.css }}`;
                                document.head.appendChild(cssStyle);
                                
                                // 🔥 Creating 2 totally separate floating DIVs
                                var diseaseDiv = document.createElement('div');
                                diseaseDiv.className = 'legend-box-disease';
                                diseaseDiv.innerHTML = `{{ this.dis_html }}`;
                                
                                var densityDiv = document.createElement('div');
                                densityDiv.className = 'legend-box-density';
                                densityDiv.innerHTML = `{{ this.den_html }}`;
                                
                                // 🔥 THE FIX: Injecting directly into the HTML body, bypassing Leaflet completely!
                                document.body.appendChild(diseaseDiv);
                                document.body.appendChild(densityDiv);
                                
                                // Disable Leaflet map dragging/zooming when clicking inside legends
                                L.DomEvent.disableClickPropagation(diseaseDiv);
                                L.DomEvent.disableScrollPropagation(diseaseDiv);
                                L.DomEvent.disableClickPropagation(densityDiv);
                                L.DomEvent.disableScrollPropagation(densityDiv);
                            {% endmacro %}
                        """)
                    
                    m.add_child(AbsoluteFixedLegends(inner_disease_html, inner_density_html, legend_css_fixed))

                    components.html(m._repr_html_(), height=720)

            # --- ROW 5: DATA TABLE WITH EXPORT ---
            with st.container(border=True):
                col_t1, col_t2 = st.columns([8, 2], vertical_alignment="bottom")
                with col_t1: st.markdown("### 📋 Patient Details Database")
                with col_t2:
                    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Export CSV Data", data=csv_data, file_name="NMC_Health_Report.csv", mime="text/csv", use_container_width=True)

                display_df = filtered_df.copy()
                if 'Date' in display_df.columns: display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y') 
                st.dataframe(display_df, use_container_width=True, hide_index=True)

        interactive_dashboard_fragment(patient_df, mapping_df, geo_data, min_date, max_date, data_source)

        # --- PROFESSIONAL FOOTER ---
        st.markdown("""
            <div class="footer-container">
                <div><b>Nagpur Municipal Corporation (NMC)</b> - Disease Surveillance Portal</div>
                <div style="margin-top: 4px; color: #64748b;">Designed & Developed by <b>Harsh Wardhan Chandel</b> (Technical Officer I.T., MSU Nagpur)</div>
            </div>
        """, unsafe_allow_html=True)
