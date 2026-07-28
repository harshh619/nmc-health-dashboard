import streamlit as st
import pandas as pd
import json
import pydeck as pdk
import datetime
import plotly.express as px
import requests

# Set page config
st.set_page_config(page_title="NMC Health Dashboard", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

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
        h3 { color: #0f172a; font-weight: 700; font-size: 1.15rem; letter-spacing: -0.025em; margin-top: 0.75rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px; }
        .header-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 10px 18px; border-radius: 8px; color: white;
            display: flex; align-items: center; gap: 16px; box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.2); margin-bottom: 12px; margin-top: 0px; transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .header-banner:hover { transform: translateY(-2px); box-shadow: 0 8px 15px -3px rgba(30, 58, 138, 0.35); }
        .header-banner h2 { color: white !important; margin: 0; font-weight: 700; font-size: 22px; letter-spacing: -0.02em; }
        .header-banner-subtitle { font-size: 13px; opacity: 0.9; font-weight: 500; margin-top: 2px; }
        .vertical-divider { border-left: 2px solid #e2e8f0; height: 320px; margin: auto; }
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
            padding: 15px 18px; border-radius: 8px; margin-bottom: 20px; margin-top: 10px; border-left: 4px solid; animation: ai-pulse 2.5s infinite ease-in-out;
        }
        .ai-alert-title { color: #9f1239; font-weight: 700; font-size: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
        .ai-alert-text { color: #881337; font-size: 14px; line-height: 1.6; }
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
        .stPlotlyChart { animation: chartZoomIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; transition: transform 0.3s ease, box-shadow 0.3s ease; border-radius: 12px; padding: 5px; }
        .stPlotlyChart:hover { transform: translateY(-5px); box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.08); }
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
    # --- HEADER BANNER ---
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
                <h2>Nagpur Municipal Corporation - Health Dashboard</h2>
                <div class="header-banner-subtitle">Public Health Intelligence & Disease Surveillance Portal</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- WEATHER WIDGET ---
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
    with w_col1: st.metric("🌡️ Nagpur Temperature", f"{temp} °C", delta="Live Weather")
    with w_col2: st.metric("💧 Relative Humidity", f"{humidity} %", delta="Vector-Borne Risk Factor")
    with w_col3: st.metric("🌧️ Precipitation / Rainfall", f"{rainfall} mm", delta="Waterlogging Index")

    # --- 2. OPTIMIZED DATA LOADING ---
    @st.cache_data(ttl=86400)
    def load_static_data():
        try:
            mapping_df = pd.read_excel('Table.xlsx')
            mapping_df.rename(columns={'name': 'Ward_Name', 'description': 'Zone'}, inplace=True)
            mapping_df['Zone'] = mapping_df['Zone'].astype(str).str.replace(r'^(Zone No\.?\s*|Zone No\s*)', '', regex=True).str.strip()
            
            with open('wards.geojson', encoding='utf-8') as f:
                geo_data = json.load(f)
                
            for feature in geo_data['features']:
                raw_ward = str(feature['properties'].get('name', 'Unknown'))
                clean_w = raw_ward[:-2] if raw_ward.endswith('.0') else raw_ward
                for p in ["Prabhag No. ", "Prabhag No.", "Prabhag No ", "Ward No. ", "Ward No.", "Ward No "]:
                    clean_w = clean_w.replace(p, "")
                clean_w = clean_w.strip().lstrip('0')
                if clean_w == "": clean_w = "0"
                feature['properties']['Clean_Ward'] = clean_w

                # Calculate Centroid for TextLayer Badge
                centroid_lon, centroid_lat = 79.0882, 21.1458
                geom = feature.get('geometry')
                if geom:
                    try:
                        coords = geom.get('coordinates')
                        ring = coords[0] if geom['type'] == 'Polygon' else coords[0][0]
                        lons = [p[0] for p in ring]
                        lats = [p[1] for p in ring]
                        centroid_lat, centroid_lon = sum(lats) / len(lats), sum(lons) / len(lons)
                    except: pass
                feature['properties']['centroid_lat'] = centroid_lat
                feature['properties']['centroid_lon'] = centroid_lon

            return mapping_df, geo_data
        except Exception as e:
            st.error(f"Static file load error: {e}")
            return None, None

    @st.cache_data(ttl=60)
    def load_patient_data():
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_77OEOeI0MVDxYCbcTlq_Ld7Oq5CFSTC6LyYyAwQGyiHHSJhBvniVns4djzswkQSGNGT2_09r0LUA/pub?gid=0&single=true&output=csv"
        try:
            patient_df = pd.read_csv(url)
            if 'Date' in patient_df.columns:
                patient_df['Date'] = pd.to_datetime(patient_df['Date'], format='mixed', dayfirst=True, errors='coerce')
            if 'Zone' in patient_df.columns:
                patient_df['Zone'] = patient_df['Zone'].astype(str).str.replace(r'^(Zone No\.?\s*|Zone No\s*)', '', regex=True).str.strip()
            return patient_df
        except:
            return pd.DataFrame(columns=['Date', 'Patient_ID', 'Patient_Name', 'Disease', 'Ward_Name', 'Zone', 'Lat', 'Long', 'Status'])

    mapping_df, geo_data = load_static_data()
    raw_patient_df = load_patient_data()

    if raw_patient_df is not None and mapping_df is not None:
        patient_df = pd.merge(raw_patient_df, mapping_df[['Ward_Name', 'Zone']], on='Ward_Name', how='left', suffixes=('', '_map'))
        if 'Zone_map' in patient_df.columns:
            patient_df['Zone'] = patient_df['Zone'].fillna(patient_df['Zone_map'])
            patient_df.drop(columns=['Zone_map'], inplace=True)

        min_date, max_date = None, None
        if 'Date' in patient_df.columns and not patient_df['Date'].dropna().empty:
            min_date = patient_df['Date'].min().date()
            max_date = patient_df['Date'].max().date()

        # =====================================================================
        # 🚀 STREAMLIT FRAGMENT: INTERACTIVE DASHBOARD SECTION
        # =====================================================================
        @st.fragment
        def interactive_dashboard_fragment(patient_df, mapping_df, geo_data, min_date, max_date):
            def clear_filters():
                st.session_state['disease_filter'] = "All"
                st.session_state['zone_filter'] = "All"
                st.session_state['ward_filter'] = "All"
                st.session_state['status_filter'] = "All"
                if min_date and max_date:
                    st.session_state['start_date'] = min_date
                    st.session_state['end_date'] = max_date

            # --- SIDEBAR SMART FILTERS ---
            with st.sidebar:
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

                disease_options = ["All"] + sorted([str(x) for x in filtered_df['Disease'].dropna().unique()]) if 'Disease' in filtered_df.columns else ["All"]
                selected_disease = st.selectbox("Select Disease", disease_options, key="disease_filter")
                if selected_disease != "All": filtered_df = filtered_df[filtered_df['Disease'] == selected_disease]

                raw_zones = mapping_df['Zone'].dropna().unique()
                zones_list = ["All"] + sorted([str(x) for x in raw_zones], key=lambda x: int(''.join(filter(str.isdigit, str(x))) or 0))
                selected_zone = st.selectbox("Select Zone", zones_list, key="zone_filter")

                if selected_zone != "All":
                    filtered_df = filtered_df[filtered_df['Zone'] == selected_zone]
                    raw_wards = mapping_df[mapping_df['Zone'] == selected_zone]['Ward_Name'].dropna().unique()
                else:
                    raw_wards = mapping_df['Ward_Name'].dropna().unique()
                    
                wards_list = ["All"] + sorted([str(x) for x in raw_wards])
                selected_ward = st.selectbox("Select Ward", wards_list, key="ward_filter")
                if selected_ward != "All": filtered_df = filtered_df[filtered_df['Ward_Name'] == selected_ward]

                status_options = ["All"] + sorted([str(x) for x in filtered_df['Status'].dropna().unique()]) if 'Status' in filtered_df.columns else ["All"]
                selected_status = st.selectbox("Select Patient Status", status_options, key="status_filter")
                if selected_status != "All": filtered_df = filtered_df[filtered_df['Status'] == selected_status]

                st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
                st.markdown("<h3 style='margin-top:0px; margin-bottom: 5px; font-size: 15px;'>📊 Zone-wise Cases</h3>", unsafe_allow_html=True)
                if not filtered_df.empty and 'Zone' in filtered_df.columns:
                    zone_summary = filtered_df['Zone'].value_counts().reset_index()
                    zone_summary.columns = ['Zone', 'Cases']
                    st.dataframe(zone_summary, hide_index=True, use_container_width=True, height=450)

            # --- CONSOLIDATED METRICS ---
            st.markdown(f"**Active View:** <span style='color:#1e3a8a; font-weight:600;'>`{selected_zone} Zone` ➔ `{selected_ward}`</span>", unsafe_allow_html=True)
            status_counts = filtered_df['Status'].value_counts() if 'Status' in filtered_df.columns else pd.Series()
            metric_cols = st.columns(1 + len(status_counts))
            with metric_cols[0]: st.metric("Total Cases (Filtered)", len(filtered_df))
            for idx, (status_name, count_val) in enumerate(status_counts.items()):
                with metric_cols[idx + 1]: st.metric(label=f"Status: {status_name}", value=count_val)

            # --- AI INSIGHTS ---
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

            # --- ANALYTICAL CHARTS ---
            col_chart1, col_divider, col_chart2 = st.columns([3.9, 0.2, 5.9])
            with col_chart1:
                st.markdown("### 🦠 Disease Distribution")
                if 'Disease' in filtered_df.columns and not filtered_df.empty:
                    disease_df = filtered_df['Disease'].value_counts().reset_index()
                    disease_df.columns = ['Disease', 'Count']
                    fig_pie = px.pie(disease_df, names='Disease', values='Count', hole=0.45, color_discrete_sequence=px.colors.qualitative.Bold)
                    fig_pie.update_traces(textinfo='percent', textfont_size=12, textfont_color='white', marker=dict(line=dict(color='#ffffff', width=2)))
                    fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter", bordercolor="#cbd5e1"), legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.82))
                    st.plotly_chart(fig_pie, use_container_width=True)

            with col_divider: st.markdown("<div class='vertical-divider'></div>", unsafe_allow_html=True)
                    
            with col_chart2:
                st.markdown("### 🏢 Top Affected Wards")
                if 'Ward_Name' in filtered_df.columns and not filtered_df.empty:
                    ward_df = filtered_df['Ward_Name'].value_counts().head(8).reset_index()
                    ward_df.columns = ['Ward', 'Cases']
                    fig_bar = px.bar(ward_df, x='Ward', y='Cases', text='Cases', color='Cases', color_continuous_scale=['#fca5a5', '#dc2626', '#991b1b'])
                    fig_bar.update_traces(textposition='outside', marker_cornerradius=6)
                    fig_bar.update_layout(margin=dict(t=25, b=10, l=10, r=10), height=280, coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter", bordercolor="#cbd5e1"), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'))
                    st.plotly_chart(fig_bar, use_container_width=True)

            # --- TIMELINE AREA CHART ---
            st.markdown("### 📈 Date Trend / Timeline Analysis")
            if 'Date' in filtered_df.columns and not filtered_df['Date'].dropna().empty:
                timeline_df = filtered_df.dropna(subset=['Date']).copy()
                timeline_df['DateOnly'] = timeline_df['Date'].dt.date
                timeline_counts = timeline_df['DateOnly'].value_counts().sort_index().reset_index()
                timeline_counts.columns = ['Date', 'Cases']
                fig_timeline = px.area(timeline_counts, x='Date', y='Cases', markers=True, color_discrete_sequence=['#1e3a8a'])
                fig_timeline.update_traces(line=dict(width=3, color='#1e3a8a'), marker=dict(size=6, color='#1e3a8a', line=dict(width=2, color='white')), fill='tozeroy', fillcolor='rgba(30, 58, 138, 0.12)')
                fig_timeline.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260, xaxis=dict(title='', showgrid=False), yaxis=dict(title='Daily Cases', showgrid=True, gridcolor='#f1f5f9'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter", bordercolor="#cbd5e1"))
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            # --- 5. ULTRA FAST PYDECK (GPU) MAP RENDERING ---
            st.markdown("### 📍 WebGL Hardware-Accelerated Map View")
            map_mode = st.radio("Select Map View Mode", ["Patient 3D Hexagon View", "Ward-wise Exact Count View", "All Cases Points View"], horizontal=True, label_visibility="collapsed")
            
            if geo_data:
                # 5.1 PREPARE DATA FOR PYDECK
                def clean_ward_fast(val):
                    if pd.isna(val): return "Unknown"
                    v = str(val)
                    v = v[:-2] if v.endswith('.0') else v
                    for p in ["Prabhag No. ", "Prabhag No.", "Prabhag No ", "Ward No. ", "Ward No.", "Ward No "]: v = v.replace(p, "")
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

                # Colors configured for PyDeck (RGBA arrays)
                def get_density_color_rgb(cases):
                    if cases == 0: return [235, 237, 239, 160]         # #ebedef
                    elif cases < max_ward_cases * 0.2: return [255, 237, 160, 170] # #ffeda0
                    elif cases < max_ward_cases * 0.4: return [254, 178, 76, 170]  # #feb24c
                    elif cases < max_ward_cases * 0.7: return [252, 78, 42, 170]   # #fc4e2a
                    else: return [189, 0, 38, 170]                     # #bd0026

                selected_ward_clean = clean_ward_fast(selected_ward) if selected_ward != "All" else "All"
                
                # Update GeoJSON Properties for PyDeck layer
                for feature in geo_data['features']:
                    clean_ward = feature['properties']['Clean_Ward'] 
                    zone_name = zone_dict.get(clean_ward, 'Unknown Zone')
                    ward_cases = clean_ward_counts.get(clean_ward, 0)
                    
                    if selected_ward != "All": zone_cases = ward_cases if clean_ward == selected_ward_clean else 0
                    else: zone_cases = clean_zone_counts.get(zone_name, 0)
                    
                    feature['properties']['Clean_Zone'] = f"Zone No: {zone_name}"
                    feature['properties']['Ward_Cases'] = str(ward_cases)
                    feature['properties']['fill_color'] = get_density_color_rgb(ward_cases)
                    
                    # Unified hover tooltips mapping
                    feature['properties']['Hover_Info_1'] = f"Total Area Cases: {ward_cases}"
                    feature['properties']['Hover_Info_2'] = f"Overall Zone Cases: {zone_cases}"

                # Prepare Point Data for Pydeck
                points_df = filtered_df.dropna(subset=['Lat', 'Long']).copy()
                if not points_df.empty:
                    points_df['Clean_Ward'] = points_df['Ward_Name'].apply(clean_ward_fast)
                    points_df['Clean_Zone'] = "Zone No: " + points_df['Zone'].astype(str)
                    points_df['Disease'] = points_df['Disease'].fillna("Unknown")
                    points_df['Status'] = points_df['Status'].fillna("Unknown")
                    points_df['Patient_Name'] = points_df['Patient_Name'].fillna("Unknown Patient")
                    points_df['Hover_Info_1'] = points_df['Disease'].astype(str) + " (" + points_df['Status'].astype(str) + ")"
                    points_df['Hover_Info_2'] = "Patient: " + points_df['Patient_Name'].astype(str)

                # 5.2 DEFINE PYDECK LAYERS
                layers = []
                
                # Base Polygon Layer (Always ON)
                geojson_layer = pdk.Layer(
                    "GeoJsonLayer",
                    geo_data,
                    pickable=True,
                    stroked=True,
                    filled=True,
                    extruded=False,
                    get_fill_color="properties.fill_color",
                    get_line_color=[100, 100, 100, 200],
                    get_line_width=25,
                    line_width_min_pixels=1,
                )
                layers.append(geojson_layer)

                if map_mode == "Patient 3D Hexagon View" and not points_df.empty:
                    hex_layer = pdk.Layer(
                        "HexagonLayer",
                        data=points_df,
                        get_position="[Long, Lat]",
                        radius=250, # Radius in meters
                        elevation_scale=15,
                        elevation_range=[0, 3000],
                        extruded=True,
                        coverage=0.9,
                        pickable=False,
                        color_range=[[255, 237, 160], [254, 178, 76], [252, 78, 42], [189, 0, 38], [128, 0, 38]]
                    )
                    layers.append(hex_layer)

                elif map_mode == "Ward-wise Exact Count View":
                    text_data = []
                    for feature in geo_data['features']:
                        w_cases = int(feature['properties']['Ward_Cases'])
                        if w_cases > 0:
                            text_data.append({
                                'Clean_Ward': feature['properties']['Clean_Ward'],
                                'Clean_Zone': feature['properties']['Clean_Zone'],
                                'lon': feature['properties']['centroid_lon'],
                                'lat': feature['properties']['centroid_lat'],
                                'cases_text': str(w_cases),
                                'Hover_Info_1': f"Total Cases: {w_cases}",
                                'Hover_Info_2': ""
                            })
                    if text_data:
                        text_layer = pdk.Layer(
                            "TextLayer",
                            data=pd.DataFrame(text_data),
                            get_position="[lon, lat]",
                            get_text="cases_text",
                            get_size=16,
                            get_color=[255, 255, 255, 255], # White text
                            background=True,
                            get_background_color=[220, 38, 38, 255], # Red Badge background
                            background_padding=[6, 4],
                            border_radius=12,
                            pickable=True
                        )
                        layers.append(text_layer)

                elif map_mode == "All Cases Points View" and not points_df.empty:
                    scatter_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=points_df,
                        get_position="[Long, Lat]",
                        get_color=[220, 38, 38, 230], # Red Dots
                        get_radius=80,
                        radius_min_pixels=4,
                        radius_max_pixels=10,
                        pickable=True
                    )
                    layers.append(scatter_layer)

                # Global Tooltip Configuration (Handles both GeoJSON and Points properties)
                deck_tooltip = {
                    "html": """
                        <div style='font-family: "Inter", sans-serif; font-size: 13px; line-height: 1.6;'>
                            <b>Ward No: {Clean_Ward}</b> <br/>
                            <span style='color: #475569;'>{Clean_Zone}</span>
                            <hr style='margin: 6px 0; border: none; border-top: 1px solid #e2e8f0;'/>
                            <span style='color: #dc2626; font-weight: bold;'>{Hover_Info_1}</span><br/>
                            <span style='color: #1e3a8a; font-weight: 500;'>{Hover_Info_2}</span>
                        </div>
                    """,
                    "style": {"backgroundColor": "#ffffff", "border": "1px solid #cbd5e1", "boxShadow": "0 4px 10px rgba(0,0,0,0.1)", "borderRadius": "6px"}
                }

                # Setup View State (Pitch for 3D effect if Hexagon View selected)
                pitch = 45 if map_mode == "Patient 3D Hexagon View" else 0
                view_state = pdk.ViewState(latitude=21.1458, longitude=79.0882, zoom=11.5, pitch=pitch, bearing=0)

                # Render PyDeck Map
                r = pdk.Deck(layers=layers, initial_view_state=view_state, map_provider="carto", map_style="light", tooltip=deck_tooltip)
                st.pydeck_chart(r, use_container_width=True)

                # 5.3 HORIZONTAL LEGEND (Below the map)
                st.markdown("""
                    <div style="display:flex; justify-content:center; flex-wrap:wrap; gap: 15px; background-color:#f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; margin-top: -15px; margin-bottom: 20px;">
                        <b style="color:#1e3a8a; display:flex; align-items:center;">📊 Map Density Indicator:</b>
                        <div style="display:flex; align-items:center;"><div style="width:14px; height:14px; background-color:#bd0026; margin-right:5px; border-radius:3px;"></div>High/Critical</div>
                        <div style="display:flex; align-items:center;"><div style="width:14px; height:14px; background-color:#fc4e2a; margin-right:5px; border-radius:3px;"></div>Moderate-High</div>
                        <div style="display:flex; align-items:center;"><div style="width:14px; height:14px; background-color:#feb24c; margin-right:5px; border-radius:3px;"></div>Moderate</div>
                        <div style="display:flex; align-items:center;"><div style="width:14px; height:14px; background-color:#ffeda0; margin-right:5px; border-radius:3px;"></div>Low Cases</div>
                        <div style="display:flex; align-items:center;"><div style="width:14px; height:14px; background-color:#ebedef; margin-right:5px; border:1px solid #cbd5e1; border-radius:3px;"></div>Zero Cases</div>
                    </div>
                """, unsafe_allow_html=True)

            # --- 6. DATA TABLE WITH EXPORT ---
            col_t1, col_t2 = st.columns([8, 2], vertical_alignment="bottom")
            with col_t1: st.markdown("### 📋 Patient Details")
            with col_t2:
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Export CSV", data=csv_data, file_name="NMC_Health_Report.csv", mime="text/csv", use_container_width=True)

            display_df = filtered_df.copy()
            if 'Date' in display_df.columns: display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y') 
            st.dataframe(display_df, use_container_width=True)

        # Call the Fragment to Render
        interactive_dashboard_fragment(patient_df, mapping_df, geo_data, min_date, max_date)

        # --- PROFESSIONAL FOOTER ---
        st.markdown("""
            <div class="footer-container">
                <div><b>Nagpur Municipal Corporation (NMC)</b> - Public Health Intelligence & Disease Surveillance Portal</div>
                <div style="margin-top: 4px; color: #64748b;">Designed & Developed by <b>Harsh Wardhan Chandel</b> (Technical Officer I.T., MSU Nagpur)</div>
            </div>
        """, unsafe_allow_html=True)
