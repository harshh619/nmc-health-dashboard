import streamlit as st
import pandas as pd
import json
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import datetime
import plotly.express as px

st.set_page_config(page_title="NMC Health Dashboard", layout="wide", page_icon="🏥")

# --- ENTERPRISE-GRADE PROFESSIONAL CSS STYLING (SIDEBAR GLITCH FIXED) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .main {
            background-color: #f8fafc;
        }
        
        /* Sidebar Styling & Clean Glitch-Free Padding */
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9;
            border-right: 1px solid #e2e8f0;
        }
        section[data-testid="stSidebar"] div.block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Modern Metric Cards with Soft Shadows */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 16px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
        }
        
        /* Section Headings with Accent Bar */
        h3 {
            color: #0f172a;
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: -0.025em;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Professional Municipal Header Banner */
        .header-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 20px 24px;
            border-radius: 12px;
            color: white;
            display: flex;
            align-items: center;
            gap: 18px;
            box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.2);
            margin-bottom: 24px;
        }
        .header-banner h2 {
            color: white !important;
            margin: 0;
            font-weight: 700;
            font-size: 28px;
            letter-spacing: -0.03em;
        }
        
        /* Pulsating Animation for High-Risk Alert Box */
        @keyframes pulse-alert {
            0% { background-color: #fef2f2; border-color: #fecaca; }
            50% { background-color: #fee2e2; border-color: #fca5a5; }
            100% { background-color: #fef2f2; border-color: #fecaca; }
        }
        .pulsing-alert {
            padding: 18px 22px;
            border-radius: 10px;
            border: 1px solid #fecaca;
            color: #991b1b;
            font-weight: 600;
            font-size: 15px;
            animation: pulse-alert 2s infinite ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* Vertical Divider Line between Charts */
        .vertical-divider {
            border-left: 2px solid #e2e8f0;
            height: 320px;
            margin: auto;
        }

        /* Professional Footer Styling */
        .footer-container {
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #e2e8f0;
            background-color: #ffffff;
            border-radius: 8px;
            text-align: center;
            color: #475569;
            font-size: 13.5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        .footer-container b {
            color: #1e3a8a;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "nagpurhealth": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Nagpur Municipal Corporation - Health Portal")
            st.text_input("Enter Dashboard Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Nagpur Municipal Corporation - Health Portal")
            st.text_input("Enter Dashboard Password", type="password", on_change=password_entered, key="password")
            st.error("❌ Incorrect Password")
        return False
    return True

if check_password():
    # --- PROFESSIONAL HEADER BANNER WITH LOGO ---
    logo_html = ""
    try:
        import base64
        with open("logo.png", "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{encoded_string}" width="52" style="background: white; border-radius: 50%; padding: 3px;" />'
    except:
        logo_html = '<div style="background: white; border-radius: 50%; padding: 8px; display: flex; align-items: center; justify-content: center; width: 48px; height: 48px;"><span style="font-size: 26px;">🏥</span></div>'

    st.markdown(f"""
        <div class="header-banner">
            {logo_html}
            <div>
                <h2>Nagpur Municipal Corporation - Health Dashboard</h2>
                <div style="font-size: 13.5px; opacity: 0.9; font-weight: 500; margin-top: 3px;">Public Health Intelligence & Disease Surveillance Portal</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. DATA LOAD & MERGE ---
    @st.cache_data(ttl=600)
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
            st.markdown("### Filters 🔍")
        with col_reset:
            st.button("Reset", on_click=clear_filters, help="Clear all filters", use_container_width=True)
        
        filtered_df = patient_df.copy()
        
        if min_date and max_date:
            st.sidebar.markdown("**Date Window (DD/MM/YYYY)**")
            
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
            st.sidebar.warning("Sheet me 'Disease' column add nahi hua hai.")
            
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
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Zone-wise Cases")
        
        if not filtered_df.empty and 'Zone' in filtered_df.columns:
            zone_summary = filtered_df['Zone'].value_counts().reset_index()
            zone_summary.columns = ['Zone', 'Cases']
            
            st.sidebar.dataframe(
                zone_summary, 
                hide_index=True, 
                use_container_width=True,
                height=395
            )
        else:
            st.sidebar.info("No data available for summary.")

        # --- 4. DASHBOARD METRICS & PULSATING HIGH-RISK HOTSPOT ALERT ---
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
            else:
                st.info("Hotspot data ke liye sufficient records nahi hain.")

        # --- PATIENT STATUS TRACKING SUMMARY METRICS WITH INDICATOR DOTS ---
        if 'Status' in filtered_df.columns and not filtered_df['Status'].dropna().empty:
            st.markdown("### 🏥 Patient Status Breakdown")
            status_counts = filtered_df['Status'].value_counts()
            status_cols = st.columns(len(status_counts) if len(status_counts) > 0 else 1)
            
            for idx, (status_name, count_val) in enumerate(status_counts.items()):
                with status_cols[idx % len(status_cols)]:
                    st.metric(
                        label=f"● Status: {status_name}", 
                        value=count_val
                    )

        # --- 4.1 ANALYTICAL CHARTS (BEAUTIFIED PIE, DIVIDER & DARK BOLD BAR CHART) ---
        col_chart1, col_divider, col_chart2 = st.columns([3.9, 0.2, 5.9])
        
        with col_chart1:
            st.markdown("### 🦠 Disease Distribution (Pie Chart)")
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
                    textfont_size=13, 
                    textfont_color='white',
                    marker=dict(line=dict(color='#ffffff', width=2))
                )
                fig_pie.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10), 
                    height=300,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=0.82,
                        font=dict(size=12, color="#111827", family="Inter")
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
                max_cases_val = ward_df['Cases'].max() if not ward_df.empty else 10
                
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
                    textfont=dict(size=12, color='#111827', family="Inter"),
                    marker_cornerradius=6
                )
                fig_bar.update_layout(
                    margin=dict(t=25, b=10, l=10, r=10),
                    height=300,
                    xaxis=dict(title='', tickangle=-25, tickfont=dict(size=11, color='#111827', family="Inter")),
                    yaxis=dict(title='Cases Count', showgrid=True, gridcolor='#f1f5f9', range=[0, max_cases_val * 1.2], tickfont=dict(size=11, color='#111827', family="Inter")),
                    coloraxis_showscale=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Ward data available nahi hai.")

        # --- ADVANCED BEAUTIFIED DATE TREND / TIMELINE AREA CHART ---
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
                height=280,
                xaxis=dict(title='', showgrid=False, tickfont=dict(size=11, color='#111827', family="Inter")),
                yaxis=dict(title='Daily Cases', showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=11, color='#111827', family="Inter")),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Timeline ke liye valid Date data available nahi hai.")
        
        # --- 5. MAP VIEW SWITCHER (3 MODES WITH ALL MAP LAYERS) ---
        st.markdown("### 📍 Patients Map View")
        
        map_mode = st.radio(
            "Select Map View Mode",
            ["Patient Cluster View", "Ward-wise Exact Count View", "All Cases Points View"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if geo_data:
            m = folium.Map(location=[21.1458, 79.0882], zoom_start=11.5, tiles=None)
            
            folium.TileLayer(
                'CartoDB Positron', 
                name='Clean B&W Map',
                control=True
            ).add_to(m)

            folium.TileLayer(
                'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
                attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
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
                if cases == 0:
                    return "#ebedef"  
                elif cases < max_ward_cases * 0.2:
                    return "#ffeda0"  
                elif cases < max_ward_cases * 0.4:
                    return "#feb24c"  
                elif cases < max_ward_cases * 0.7:
                    return "#fc4e2a"  
                else:
                    return "#bd0026"

            for feature in geo_data['features']:
                raw_ward = feature['properties'].get('name', 'Unknown')
                clean_ward = clean_ward_str(raw_ward)
                zone_name = zone_dict.get(clean_ward, 'Unknown Zone')
                
                ward_cases = clean_ward_counts.get(clean_ward, 0)
                
                feature['properties']['Clean_Ward'] = clean_ward 
                feature['properties']['Clean_Zone'] = zone_name
                feature['properties']['Ward_Cases'] = ward_cases
                feature['properties']['Zone_Cases'] = clean_zone_counts.get(zone_name, 0)
                feature['properties']['fill_color'] = get_density_color(ward_cases)

            popup_styling = """
            <style>
                .leaflet-popup-content table {
                    width: 100%;
                }
                .leaflet-popup-content tr {
                    line-height: 1.3;
                }
                .leaflet-popup-content td, .leaflet-popup-content th {
                    padding: 6px 10px !important;
                    vertical-align: middle !important;
                    white-space: nowrap !important;
                }
            </style>
            """
            m.get_root().html.add_child(folium.Element(popup_styling))

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
                popup=folium.features.GeoJsonPopup(
                    fields=['Clean_Zone', 'Clean_Ward', 'Ward_Cases', 'Zone_Cases'],
                    aliases=['📍 Zone:', '🏢 Prabhag:', '📈 Prabhag Cases:', '📊 Zone Cases:'],
                    labels=True,
                    style="font-family: Inter; font-size: 13px; font-weight: bold;"
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
                        <b>Date:</b> {date_str}<br>
                        <b>Patient ID:</b> {row.get('Patient_ID', 'N/A')}<br>
                        <b>Name:</b> {row.get('Patient_Name', 'N/A')}<br>
                        <b>Disease:</b> {row.get('Disease', 'N/A')}<br>
                        <b>Status:</b> {row.get('Status', 'N/A')}<br>
                        <b>Ward:</b> {row.get('Ward_Name', 'N/A')}
                        """
                        
                        if pd.notna(row['Lat']) and pd.notna(row['Long']):
                            folium.Marker(
                                location=[row['Lat'], row['Long']],
                                popup=folium.Popup(popup_text, max_width=300),
                                icon=folium.Icon(color="red", icon="info-sign")
                            ).add_to(marker_cluster)

            elif map_mode == "Ward-wise Exact Count View":
                for feature in geo_data['features']:
                    ward_cases = feature['properties']['Ward_Cases']
                    
                    if ward_cases > 0:
                        geom = feature.get('geometry')
                        if geom:
                            try:
                                coords = geom.get('coordinates')
                                if geom['type'] == 'Polygon':
                                    ring = coords[0]
                                elif geom['type'] == 'MultiPolygon':
                                    ring = coords[0][0]
                                else:
                                    ring = None
                                
                                if ring:
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
                                    folium.Marker(
                                        location=[center_lat, center_lon],
                                        icon=folium.DivIcon(html=badge_html)
                                    ).add_to(m)
                            except Exception:
                                pass

            elif map_mode == "All Cases Points View":
                if not filtered_df.empty:
                    for idx, row in filtered_df.iterrows():
                        date_str = "N/A"
                        if pd.notna(row.get('Date')):
                            date_str = row['Date'].strftime('%d/%m/%Y') 

                        popup_text = f"""
                        <b>Date:</b> {date_str}<br>
                        <b>Patient ID:</b> {row.get('Patient_ID', 'N/A')}<br>
                        <b>Name:</b> {row.get('Patient_Name', 'N/A')}<br>
                        <b>Disease:</b> {row.get('Disease', 'N/A')}<br>
                        <b>Status:</b> {row.get('Status', 'N/A')}<br>
                        <b>Ward:</b> {row.get('Ward_Name', 'N/A')}
                        """
                        
                        if pd.notna(row['Lat']) and pd.notna(row['Long']):
                            folium.CircleMarker(
                                location=[row['Lat'], row['Long']],
                                radius=5,
                                popup=folium.Popup(popup_text, max_width=300),
                                color='#ffffff',
                                weight=1,
                                fill=True,
                                fill_color='#e53e3e',
                                fill_opacity=0.9
                            ).add_to(m)
                
            folium.LayerControl().add_to(m)
            st_folium(m, height=750, use_container_width=True, returned_objects=[])
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
