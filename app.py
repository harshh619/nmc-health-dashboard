import streamlit as st
import pandas as pd
import json
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import datetime
import plotly.express as px
import requests

# Set page config with initial_sidebar_state="expanded" so it loads open by default
st.set_page_config(page_title="NMC Health Dashboard", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

# --- ENTERPRISE-GRADE PROFESSIONAL CSS STYLING ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="st-"], .stApp { 
            font-family: 'Inter', sans-serif !important; 
        }
        .material-symbols-rounded, .material-icons, [data-testid="stIconMaterial"], [class*="Icon"] {
            font-family: 'Material Symbols Rounded', 'Material Icons' !important;
            font-weight: normal !important;
        }

        /* 1. Eliminate Top Padding to stick banner to the top */
        .block-container {
            padding-top: 0.1rem !important; 
            padding-bottom: 1rem !important;
        }
        
        [data-testid="stSidebarHeader"] button, 
        [data-testid="collapsedControl"] {
            opacity: 0 !important;
            transition: opacity 0.3s ease-in-out, transform 0.2s ease !important;
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            color: #1e3a8a !important;
            z-index: 99999 !important;
        }
        
        [data-testid="collapsedControl"] {
            margin-top: 10px;
            margin-left: 10px;
        }
        
        .stApp:hover [data-testid="stSidebarHeader"] button,
        .stApp:hover [data-testid="collapsedControl"] {
            opacity: 1 !important;
        }
        
        [data-testid="stSidebarHeader"] button:hover,
        [data-testid="collapsedControl"]:hover {
            background-color: #1e3a8a !important;
            color: #ffffff !important;
            transform: scale(1.08) !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0px !important;
        }

        header[data-testid="stHeader"] .stAppToolbar {
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        header[data-testid="stHeader"]:hover .stAppToolbar {
            opacity: 1;
        }

        .main {
            background-color: #ffffff !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #f8fafc !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        section[data-testid="stSidebar"] div.block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            gap: 0.2rem !important;
        }
        section[data-testid="stSidebar"] label {
            font-size: 13px !important;
            margin-bottom: -5px !important;
            font-weight: 500 !important;
            color: #334155 !important;
        }
        
        /* Compact & Sleek Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 8px 12px !important;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-color: #cbd5e1;
            background-color: #ffffff;
        }
        div[data-testid="stMetric"] label {
            font-size: 12px !important;
            color: #475569 !important;
            margin-bottom: 2px !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #0f172a !important;
        }

        h3 {
            color: #0f172a;
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: -0.025em;
            margin-top: 0.75rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .header-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 10px 18px;
            border-radius: 8px;
            color: white;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.2);
            margin-bottom: 12px;
            margin-top: 0px;
        }
        .header-banner h2 {
            color: white !important;
            margin: 0;
            font-weight: 700;
            font-size: 22px;
            letter-spacing: -0.02em;
        }
        .header-banner-subtitle {
            font-size: 13px;
            opacity: 0.9;
            font-weight: 500;
            margin-top: 2px;
        }
        @keyframes pulse-alert {
            0% { background-color: #fef2f2; border-color: #fecaca; }
            50% { background-color: #fee2e2; border-color: #fca5a5; }
            100% { background-color: #fef2f2; border-color: #fecaca; }
        }
        .pulsing-alert {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #fecaca;
            color: #991b1b;
            font-weight: 600;
            font-size: 13.5px;
            animation: pulse-alert 2s infinite ease-in-out;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .vertical-divider {
            border-left: 2px solid #e2e8f0;
            height: 320px;
            margin: auto;
        }
        .footer-container {
            margin-top: 30px;
            padding: 15px;
            border-top: 1px solid #e2e8f0;
            background-color: #ffffff;
            border-radius: 8px;
            text-align: center;
            color: #475569;
            font-size: 13px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        .footer-container b {
            color: #1e3a8a;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. PASSWORD PROTECTION FIX ---
def check_password():
    def password_entered():
        if st.session_state["login_password"] == "nagpurhealth": 
            st.session_state["password_correct"] = True
            del st.session_state["login_password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

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
    except:
        pass

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
    @st.cache_data(ttl=600)
    def get_nagpur_weather():
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=21.1458&longitude=79.0882&current=temperature_2m,relative_humidity_2m,precipitation"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                curr = data.get('current', {})
                return curr.get('temperature_2m', 32), curr.get('relative_humidity_2m', 65), curr.get('precipitation', 0.0)
        except:
            pass
        return 32.5, 68.0, 0.0

    temp, humidity, rainfall = get_nagpur_weather()
    
    w_col1, w_col2, w_col3 = st.columns(3)
    with w_col1:
        st.metric("🌡️ Nagpur Temperature", f"{temp} °C", delta="Live Weather")
    with w_col2:
        st.metric("💧 Relative Humidity", f"{humidity} %", delta="Vector-Borne Risk Factor")
    with w_col3:
        st.metric("🌧️ Precipitation / Rainfall", f"{rainfall} mm", delta="Waterlogging Index")

    # --- 2. DATA LOAD & MERGE ---
    @st.cache_data(ttl=30)
    def load_all_data():
        try:
            mapping_df = pd.read_excel('Table.xlsx')
            mapping_df.rename(columns={'name': 'Ward_Name', 'description': 'Zone'}, inplace=True)
        except Exception as e:
            st.error("Table.xlsx file nahi mili ya format galat hai.")
            return None, None, None

        google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_77OEOeI0MVDxYCbcTlq_Ld7Oq5CFSTC6LyYyAwQGyiHHSJhBvniVns4djzswkQSGNGT2_09r0LUA/pub?gid=0&single=true&output=csv" 
        
        try:
            patient_df = pd.read_csv(google_sheet_url)
            
            if 'Date' in patient_df.columns:
                patient_df['Date'] = pd.to_datetime(patient_df['Date'], format='mixed', dayfirst=True, errors='coerce')
                
            patient_df = pd.merge(patient_df, mapping_df, on='Ward_Name', how='left')
        except:
            st.warning("Google Sheet link update nahi hua hai. Dummy data load ho raha hai.")
            patient_df = pd.DataFrame(columns=['Date', 'Patient_ID', 'Patient_Name', 'Disease', 'Ward_Name', 'Zone', 'Lat', 'Long', 'Status'])

        try:
            with open('wards.geojson', encoding='utf-8') as f:
                geo_data = json.load(f)
        except:
            st.error("wards.geojson file load nahi ho payi.")
            geo_data = None
            
        return patient_df, mapping_df, geo_data

    patient_df, mapping_df, geo_data = load_all_data()

    if patient_df is not None:
        
        def clean_zone_name(val):
            if pd.isna(val): return "Unknown"
            val = str(val)
            for prefix in ["Zone No. ", "Zone No ", "Zone No."]:
                if val.startswith(prefix):
                    val = val[len(prefix):]
            return val.strip()

        if 'Zone' in mapping_df.columns:
            mapping_df['Zone'] = mapping_df['Zone'].apply(clean_zone_name)
        if 'Zone' in patient_df.columns:
            patient_df['Zone'] = patient_df['Zone'].apply(clean_zone_name)

        min_date, max_date = None, None
        if 'Date' in patient_df.columns and not patient_df['Date'].dropna().empty:
            min_date = patient_df['Date'].min().date()
            max_date = patient_df['Date'].max().date()

        def clear_filters():
            st.session_state['disease_filter'] = "All"
            st.session_state['zone_filter'] = "All"
            st.session_state['ward_filter'] = "All"
            st.session_state['status_filter'] = "All"
            if min_date and max_date:
                st.session_state['start_date'] = min_date
                st.session_state['end_date'] = max_date

        # --- 3. SIDEBAR SMART FILTERS ---
        col_header, col_reset = st.sidebar.columns([5, 3])
        with col_header:
            st.markdown("<h3 style='margin-top:0px;'>Filters 🔍</h3>", unsafe_allow_html=True)
        with col_reset:
            st.button("Reset", on_click=clear_filters, help="Clear all filters", use_container_width=True)
        
        filtered_df = patient_df.copy()
        
        if min_date and max_date:
            st.sidebar.markdown("<div style='font-size: 13px; font-weight: 600; margin-bottom: 2px; color: #334155;'>Date Window</div>", unsafe_allow_html=True)
            
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date, format="DD/MM/YYYY", key="start_date")
                
            with col2:
                end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date, format="DD/MM/YYYY", key="end_date")
            
            if start_date > end_date:
                st.sidebar.error("Error: 'To' date 'From' date se aage ki honi chahiye.")
            else:
                filtered_df = filtered_df[(filtered_df['Date'].dt.date >= start_date) & (filtered_df['Date'].dt.date <= end_date)]
        else:
            st.sidebar.warning("Data me valid 'Date' column nahi hai.")

        if 'Disease' in filtered_df.columns:
            raw_diseases = filtered_df['Disease'].dropna().unique()
            disease_options = ["All"] + sorted([str(x) for x in raw_diseases])
        else:
            disease_options = ["All"]
            
        selected_disease = st.sidebar.selectbox("Select Disease", disease_options, key="disease_filter")
        
        if selected_disease != "All":
            filtered_df = filtered_df[filtered_df['Disease'] == selected_disease]

        raw_zones = mapping_df['Zone'].dropna().unique()
        zones_list = ["All"] + sorted([str(x) for x in raw_zones], key=lambda x: int(''.join(filter(str.isdigit, str(x))) or 0))
        
        selected_zone = st.sidebar.selectbox("Select Zone", zones_list, key="zone_filter")

        if selected_zone != "All":
            filtered_df = filtered_df[filtered_df['Zone'] == selected_zone]
            raw_wards = mapping_df[mapping_df['Zone'] == selected_zone]['Ward_Name'].dropna().unique()
        else:
            raw_wards = mapping_df['Ward_Name'].dropna().unique()
            
        wards_list = ["All"] + sorted([str(x) for x in raw_wards])

        selected_ward = st.sidebar.selectbox("Select Ward", wards_list, key="ward_filter")
        
        if selected_ward != "All":
            filtered_df = filtered_df[filtered_df['Ward_Name'] == selected_ward]

        # --- PATIENT STATUS FILTER ---
        if 'Status' in filtered_df.columns:
            raw_statuses = filtered_df['Status'].dropna().unique()
            status_options = ["All"] + sorted([str(x) for x in raw_statuses])
        else:
            status_options = ["All"]
            
        selected_status = st.sidebar.selectbox("Select Patient Status", status_options, key="status_filter")
        
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]

        # --- ZONE-WISE SUMMARY TABLE ---
        st.sidebar.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
        st.sidebar.markdown("<h3 style='margin-top:0px; margin-bottom: 5px; font-size: 15px;'>📊 Zone-wise Cases</h3>", unsafe_allow_html=True)
        
        if not filtered_df.empty and 'Zone' in filtered_df.columns:
            zone_summary = filtered_df['Zone'].value_counts().reset_index()
            zone_summary.columns = ['Zone', 'Cases']
            
            st.sidebar.dataframe(
                zone_summary, 
                hide_index=True, 
                use_container_width=True,
                height=450
            )
        else:
            st.sidebar.info("No data available for summary.")

        # --- 4. DASHBOARD METRICS ---
        st.markdown(f"**Active View:** `{selected_zone} Zone` ➔ `{selected_ward}`")
        
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            total_cases = len(filtered_df)
            st.metric("Total Cases in Selected Window", total_cases, delta="Live Data")
            
        with col_m2:
            if not filtered_df.empty and 'Ward_Name' in filtered_df.columns:
                top_ward = filtered_df['Ward_Name'].value_counts().idxmax()
                top_ward_cases = filtered_df['Ward_Name'].value_counts().max()
                
                st.markdown(f"""
                    <div class="pulsing-alert">
                        <span>🚨</span>
                        <div><b>High-Risk Hotspot Alert:</b> {top_ward} is currently the most affected area with <b>{top_ward_cases} cases</b>!</div>
                    </div>
                """, unsafe_allow_html=True)

        if 'Status' in filtered_df.columns and not filtered_df['Status'].dropna().empty:
            st.markdown("### 🏥 Patient Status Breakdown")
            status_counts = filtered_df['Status'].value_counts()
            status_cols = st.columns(len(status_counts) if len(status_counts) > 0 else 1)
            
            for idx, (status_name, count_val) in enumerate(status_counts.items()):
                with status_cols[idx % len(status_cols)]:
                    st.metric(label=f"● Status: {status_name}", value=count_val)

        # --- 4.1 ANALYTICAL CHARTS ---
        col_chart1, col_divider, col_chart2 = st.columns([3.9, 0.2, 5.9])
        
        with col_chart1:
            st.markdown("### 🦠 Disease Distribution")
            if 'Disease' in filtered_df.columns and not filtered_df['Disease'].dropna().empty:
                disease_df = filtered_df['Disease'].value_counts().reset_index()
                disease_df.columns = ['Disease', 'Count']
                
                fig_pie = px.pie(
                    disease_df, 
                    names='Disease', 
                    values='Count', 
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_pie.update_traces(
                    textinfo='percent', 
                    textfont_size=12, 
                    textfont_color='white',
                    marker=dict(line=dict(color='#ffffff', width=2))
                )
                fig_pie.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10), 
                    height=280,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=0.82
                    )
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Disease data available nahi hai.")

        with col_divider:
            st.markdown("<div class='vertical-divider'></div>", unsafe_allow_html=True)
                
        with col_chart2:
            st.markdown("### 🏢 Top Affected Wards")
            if 'Ward_Name' in filtered_df.columns and not filtered_df['Ward_Name'].dropna().empty:
                ward_df = filtered_df['Ward_Name'].value_counts().head(8).reset_index()
                ward_df.columns = ['Ward', 'Cases']
                
                fig_bar = px.bar(
                    ward_df,
                    x='Ward',
                    y='Cases',
                    text='Cases',
                    color='Cases',
                    color_continuous_scale=['#fca5a5', '#dc2626', '#991b1b']
                )
                fig_bar.update_traces(
                    textposition='outside',
                    marker_cornerradius=6
                )
                fig_bar.update_layout(
                    margin=dict(t=25, b=10, l=10, r=10),
                    height=280,
                    coloraxis_showscale=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Ward data available nahi hai.")

        # --- TIMELINE AREA CHART ---
        st.markdown("### 📈 Date Trend / Timeline Analysis")
        if 'Date' in filtered_df.columns and not filtered_df['Date'].dropna().empty:
            timeline_df = filtered_df.dropna(subset=['Date']).copy()
            timeline_df['DateOnly'] = timeline_df['Date'].dt.date
            timeline_counts = timeline_df['DateOnly'].value_counts().sort_index().reset_index()
            timeline_counts.columns = ['Date', 'Cases']
            
            fig_timeline = px.area(
                timeline_counts,
                x='Date',
                y='Cases',
                markers=True,
                color_discrete_sequence=['#1e3a8a']
            )
            fig_timeline.update_traces(
                line=dict(width=3, color='#1e3a8a'),
                marker=dict(size=6, color='#1e3a8a', line=dict(width=2, color='white')),
                fill='tozeroy',
                fillcolor='rgba(30, 58, 138, 0.12)'
            )
            fig_timeline.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=260,
                xaxis=dict(title='', showgrid=False),
                yaxis=dict(title='Daily Cases', showgrid=True, gridcolor='#f1f5f9'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Timeline ke liye valid Date data available nahi hai.")
        
        # --- 5. MAP VIEW SWITCHER (RADIO BUTTON + MAP LAYERS) ---
        st.markdown("### 📍 Patients Map View")
        
        map_mode = st.radio(
            "Select Map View Mode",
            ["Patient Cluster View", "Ward-wise Exact Count View", "All Cases Points View"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if geo_data:
            # Added attribution_control=False to completely disable the Leaflet/OSM attribution footer
            m = folium.Map(location=[21.1458, 79.0882], zoom_start=11.5, tiles=None, attribution_control=False)
            
            folium.TileLayer(
                'CartoDB Positron', 
                name='Clean B&W Map',
                control=True
            ).add_to(m)

            folium.TileLayer(
                'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
                attr='&copy; OpenStreetMap & CARTO',
                name='Clean No-Labels Map',
                control=True
            ).add_to(m)

            folium.TileLayer(
                'OpenStreetMap', 
                name='Default Map',
                control=True
            ).add_to(m)
            
            def clean_ward_str(val):
                if pd.isna(val): return "Unknown"
                val = str(val)
                if val.endswith('.0'): val = val[:-2]
                for remove_word in ["Prabhag No. ", "Prabhag No.", "Prabhag No "]:
                    val = val.replace(remove_word, "")
                return val.strip()

            zone_dict = {clean_ward_str(w): str(z) for w, z in zip(mapping_df['Ward_Name'], mapping_df['Zone'])}
            
            clean_ward_counts = {}
            if not filtered_df.empty:
                for w, count in filtered_df['Ward_Name'].value_counts().items():
                    clean_w = clean_ward_str(w)
                    clean_ward_counts[clean_w] = clean_ward_counts.get(clean_w, 0) + count
                    
            clean_zone_counts = {}
            if not filtered_df.empty:
                for z, count in filtered_df['Zone'].value_counts().items():
                    clean_z = str(z)
                    clean_zone_counts[clean_z] = clean_zone_counts.get(clean_z, 0) + count

            max_ward_cases = max(clean_ward_counts.values()) if clean_ward_counts else 1

            def get_density_color(cases):
                if cases == 0: return "#ebedef"  
                elif cases < max_ward_cases * 0.2: return "#ffeda0"  
                elif cases < max_ward_cases * 0.4: return "#feb24c"  
                elif cases < max_ward_cases * 0.7: return "#fc4e2a"  
                else: return "#bd0026"

            for feature in geo_data['features']:
                raw_ward = feature['properties'].get('name', 'Unknown')
                clean_ward = clean_ward_str(raw_ward)
                zone_name = zone_dict.get(clean_ward, 'Unknown Zone')
                
                ward_cases = clean_ward_counts.get(clean_ward, 0)
                zone_cases = clean_zone_counts.get(zone_name, 0)
                
                feature['properties']['Clean_Ward'] = clean_ward 
                feature['properties']['Clean_Zone'] = zone_name
                feature['properties']['Ward_Cases'] = ward_cases
                feature['properties']['Zone_Cases'] = zone_cases
                feature['properties']['fill_color'] = get_density_color(ward_cases)

            # Custom CSS injected into map to enforce 'Inter' font across ALL popups uniformly
            popup_font_injection = """
            <style>
                .leaflet-popup-content, .leaflet-popup-content-wrapper {
                    font-family: 'Inter', sans-serif !important;
                    font-size: 13px !important;
                }
            </style>
            """
            m.get_root().html.add_child(folium.Element(popup_font_injection))

            # Background Boundary Layer with Unified Inter Font Popup
            folium.GeoJson(
                geo_data,
                style_function=lambda feature: {
                    'color': '#444444',
                    'weight': 1,
                    'fillColor': feature['properties']['fill_color'],
                    'fillOpacity': 0.60
                },
                highlight_function=lambda feature: {
                    'color': '#000000',
                    'weight': 2.5,
                    'fillColor': feature['properties']['fill_color'],
                    'fillOpacity': 0.80
                },
                popup=folium.GeoJsonPopup(
                    fields=['Clean_Ward', 'Ward_Cases', 'Clean_Zone', 'Zone_Cases'],
                    aliases=['Ward No :', 'Total Cases :', 'Zone No :', 'Total Cases :'],
                    labels=True,
                    style="font-family: 'Inter', sans-serif; font-size: 13px;"
                )
            ).add_to(m)

            if map_mode == "Patient Cluster View":
                marker_cluster = MarkerCluster().add_to(m)
                if not filtered_df.empty:
                    for idx, row in filtered_df.iterrows():
                        date_str = "N/A"
                        if pd.notna(row.get('Date')):
                            date_str = row['Date'].strftime('%d/%m/%Y') 

                        popup_text = f"""
                        <div style="font-family: 'Inter', sans-serif; font-size: 13px; min-width: 160px;">
                            <b style="color: #1e3a8a; font-size: 14px;">Patient ID: {row.get('Patient_ID', 'N/A')}</b><br>
                            <hr style="margin: 4px 0;">
                            <b>Date:</b> {date_str}<br>
                            <b>Disease:</b> {row.get('Disease', 'N/A')}<br>
                            <b>Ward No:</b> {clean_ward_str(row.get('Ward_Name', 'N/A'))}<br>
                            <b>Status:</b> {row.get('Status', 'N/A')}
                        </div>
                        """
                        if pd.notna(row['Lat']) and pd.notna(row['Long']):
                            folium.CircleMarker(
                                location=[row['Lat'], row['Long']],
                                radius=7,
                                color='white',
                                weight=1,
                                fill=True,
                                fill_color='#2563eb',
                                fill_opacity=0.9,
                                popup=folium.Popup(popup_text, max_width=250)
                            ).add_to(marker_cluster)

            elif map_mode == "Ward-wise Exact Count View":
                for feature in geo_data['features']:
                    ward_cases = feature['properties']['Ward_Cases']
                    zone_cases = feature['properties']['Zone_Cases']
                    
                    if ward_cases > 0:
                        geom = feature.get('geometry')
                        if geom:
                            try:
                                coords = geom.get('coordinates')
                                ring = coords[0] if geom['type'] == 'Polygon' else coords[0][0]
                                lons = [p[0] for p in ring]
                                lats = [p[1] for p in ring]
                                center_lat = sum(lats) / len(lats)
                                center_lon = sum(lons) / len(lons)
                                
                                badge_html = f"""
                                <div style="
                                    background-color: #e53e3e; 
                                    border: 2px solid #ffffff; 
                                    color: #ffffff; 
                                    font-weight: bold; 
                                    font-size: 11px; 
                                    width: 24px; 
                                    height: 24px; 
                                    line-height: 20px; 
                                    border-radius: 50%; 
                                    text-align: center; 
                                    box-shadow: 0 2px 5px rgba(0,0,0,0.4);
                                    transform: translate(-50%, -50%);">
                                    {ward_cases}
                                </div>
                                """
                                popup_html = f"""
                                <div style="font-family: 'Inter', sans-serif; font-size: 13px;">
                                    <b>Ward No :</b> {feature['properties']['Clean_Ward']}<br>
                                    <b>Total Cases :</b> {ward_cases}<br>
                                    <b>Zone No :</b> {feature['properties']['Clean_Zone']}<br>
                                    <b>Total Cases :</b> {zone_cases}
                                </div>
                                """
                                folium.Marker(
                                    location=[center_lat, center_lon],
                                    icon=folium.DivIcon(html=badge_html),
                                    popup=folium.Popup(popup_html, max_width=200)
                                ).add_to(m)
                            except Exception:
                                pass

            elif map_mode == "All Cases Points View":
                if not filtered_df.empty:
                    for idx, row in filtered_df.iterrows():
                        popup_text = f"""
                        <div style="font-family: 'Inter', sans-serif; font-size: 13px; min-width: 160px;">
                            <b style="color: #dc2626; font-size: 14px;">Disease: {row.get('Disease', 'N/A')}</b><br>
                            <hr style="margin: 4px 0;">
                            <b>Patient Name:</b> {row.get('Patient_Name', 'N/A')}<br>
                            <b>Ward No:</b> {clean_ward_str(row.get('Ward_Name', 'N/A'))}<br>
                            <b>Status:</b> {row.get('Status', 'N/A')}
                        </div>
                        """
                        if pd.notna(row['Lat']) and pd.notna(row['Long']):
                            folium.CircleMarker(
                                location=[row['Lat'], row['Long']],
                                radius=5,
                                popup=folium.Popup(popup_text, max_width=250),
                                color='#ffffff',
                                weight=1,
                                fill=True,
                                fill_color='#e53e3e',
                                fill_opacity=0.9
                            ).add_to(m)
                
            folium.LayerControl().add_to(m)
            st_folium(m, height=700, use_container_width=True, returned_objects=[])
        else:
            st.info("Geojson data available nahi hai.")

        # --- 6. DATA TABLE WITH EXPORT BUTTON ---
        col_t1, col_t2 = st.columns([8, 2], vertical_alignment="bottom")
        with col_t1:
            st.markdown("### 📋 Patient Details")
        with col_t2:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name="NMC_Health_Report.csv",
                mime="text/csv",
                use_container_width=True
            )

        display_df = filtered_df.copy()
        if 'Date' in display_df.columns:
            display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y') 
            
        st.dataframe(display_df, use_container_width=True)

        # --- PROFESSIONAL FOOTER ---
        st.markdown("""
            <div class="footer-container">
                <div><b>Nagpur Municipal Corporation (NMC)</b> - Public Health Intelligence & Disease Surveillance Portal</div>
                <div style="margin-top: 4px; color: #64748b;">Designed & Developed by <b>Harsh Wardhan Chandel</b> (Technical Officer I.T., MSU Nagpur)</div>
            </div>
        """, unsafe_allow_html=True)
