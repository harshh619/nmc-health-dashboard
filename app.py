import streamlit as st
import pandas as pd
import json
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import datetime

st.set_page_config(page_title="NMC Health Dashboard", layout="wide")

# --- 1. PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "nagpurhealth": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("NMC Dashboard ka Password enter karein", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("NMC Dashboard ka Password enter karein", type="password", on_change=password_entered, key="password")
        st.error("❌ Galat Password")
        return False
    return True

if check_password():
    st.title("🏥 Nagpur Municipal Corporation - Health Dashboard")

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
        
        min_date, max_date = None, None
        if 'Date' in patient_df.columns and not patient_df['Date'].dropna().empty:
            min_date = patient_df['Date'].min().date()
            max_date = patient_df['Date'].max().date()

        def clear_filters():
            st.session_state['disease_filter'] = "All"
            st.session_state['zone_filter'] = "All"
            st.session_state['ward_filter'] = "All"
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
        zones_list = ["All"] + sorted([str(x) for x in raw_zones])
        
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

        # --- 4. DASHBOARD METRICS ---
        st.subheader(f"Current Filter: {selected_zone} Zone -> {selected_ward}")
        total_cases = len(filtered_df)
        st.metric("Total Cases in Selected Window", total_cases)
        
        # --- 5. MAP GENERATION (CHOROPLETH DENSITY STYLE) ---
        st.markdown("### 📍 Patients Map (Density Heatmap & Clustering)")
        
        if not filtered_df.empty and 'Lat' in filtered_df.columns and 'Long' in filtered_df.columns and geo_data:
            m = folium.Map(location=[21.1458, 79.0882], zoom_start=11.5)
            
            def clean_ward_str(val):
                if pd.isna(val): return "Unknown"
                val = str(val)
                if val.endswith('.0'): val = val[:-2]
                for remove_word in ["Prabhag No. ", "Prabhag No.", "Prabhag No "]:
                    val = val.replace(remove_word, "")
                return val.strip()

            zone_dict = {clean_ward_str(w): str(z) for w, z in zip(mapping_df['Ward_Name'], mapping_df['Zone'])}
            
            clean_ward_counts = {}
            for w, count in filtered_df['Ward_Name'].value_counts().items():
                clean_w = clean_ward_str(w)
                clean_ward_counts[clean_w] = clean_ward_counts.get(clean_w, 0) + count
                
            clean_zone_counts = {}
            for z, count in filtered_df['Zone'].value_counts().items():
                clean_z = str(z)
                clean_zone_counts[clean_z] = clean_zone_counts.get(clean_z, 0) + count

            # Case count ke aadhar par color shade nikalne ka logic (Yellow -> Orange -> Red)
            max_ward_cases = max(clean_ward_counts.values()) if clean_ward_counts else 1

            def get_density_color(cases):
                if cases == 0:
                    return "#ebedef"  # Bohot kam/0 cases ke liye grey/light
                elif cases < max_ward_cases * 0.2:
                    return "#ffeda0"  # Light Yellow
                elif cases < max_ward_cases * 0.4:
                    return "#feb24c"  # Orange-Yellow
                elif cases < max_ward_cases * 0.7:
                    return "#fc4e2a"  # Orange-Red
                else:
                    # Sabse zyada cases wale wards ke liye dark red
                    return "#bd0026"

            for feature in geo_data['features']:
                raw_ward = feature['properties'].get('name', 'Unknown')
                
                clean_ward = clean_ward_str(raw_ward)
                zone_name = zone_dict.get(clean_ward, 'Unknown Zone')
                
                formatted_zone = zone_name.replace("Zone No. ", "").replace("Zone No ", "")
                formatted_ward = clean_ward
                
                ward_cases = clean_ward_counts.get(clean_ward, 0)
                
                feature['properties']['Clean_Ward'] = formatted_ward 
                feature['properties']['Clean_Zone'] = formatted_zone
                feature['properties']['Ward_Cases'] = ward_cases
                feature['properties']['Zone_Cases'] = clean_zone_counts.get(zone_name, 0)
                
                # Density color assign karna
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
                    padding: 5px 8px !important;
                    vertical-align: middle !important;
                    white-space: nowrap !important;
                }
            </style>
            """
            m.get_root().html.add_child(folium.Element(popup_styling))

            # Choropleth Styled GeoJson layer
            folium.GeoJson(
                geo_data,
                style_function=lambda feature: {
                    'color': '#444444',
                    'weight': 1,
                    'fillColor': feature['properties']['fill_color'],
                    'fillOpacity': 0.65
                },
                highlight_function=lambda feature: {
                    'color': '#000000',
                    'weight': 2.5,
                    'fillColor': feature['properties']['fill_color'],
                    'fillOpacity': 0.85
                },
                popup=folium.features.GeoJsonPopup(
                    fields=['Clean_Zone', 'Clean_Ward', 'Ward_Cases', 'Zone_Cases'],
                    aliases=['📍 Zone:', '🏢 Prabhag:', '📈 Prabhag Cases:', '📊 Zone Cases:'],
                    labels=True,
                    style="font-family: Arial; font-size: 13px; font-weight: bold;"
                )
            ).add_to(m)

            marker_cluster = MarkerCluster().add_to(m)

            for idx, row in filtered_df.iterrows():
                date_str = "N/A"
                if pd.notna(row.get('Date')):
                    date_str = row['Date'].strftime('%d/%m/%Y') 

                popup_text = f"""
                <b>Date:</b> {date_str}<br>
                <b>Patient ID:</b> {row.get('Patient_ID', 'N/A')}<br>
                <b>Name:</b> {row.get('Patient_Name', 'N/A')}<br>
                <b>Disease:</b> {row.get('Disease', 'N/A')}<br>
                <b>Ward:</b> {row.get('Ward_Name', 'N/A')}
                """
                
                if pd.notna(row['Lat']) and pd.notna(row['Long']):
                    folium.Marker(
                        location=[row['Lat'], row['Long']],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(marker_cluster)
                
            st_folium(m, height=750, use_container_width=True, returned_objects=[])
            
        else:
            st.info("Is filter ke liye data ya Lat/Long points nahi hain.")

        # --- 6. DATA TABLE ---
        st.markdown("### 📋 Patient Details")
        display_df = filtered_df.copy()
        if 'Date' in display_df.columns:
            display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y') 
            
        st.dataframe(display_df)
