import streamlit as st
import pandas as pd
import json
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import datetime # NAYI LIBRARY DATE KE LIYE ADD KI HAI

st.set_page_config(page_title="NMC Health Dashboard", layout="wide")

# --- 1. PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        # Temporary password testing ke liye "nagpurhealth" rakha hai
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
        # A) Table.xlsx ko load karke Wards aur Zones ko map karna
        try:
            mapping_df = pd.read_excel('Table.xlsx')
            # Columns ke naam standardise kar rahe hain
            mapping_df.rename(columns={'name': 'Ward_Name', 'description': 'Zone'}, inplace=True)
        except Exception as e:
            st.error("Table.xlsx file nahi mili ya format galat hai.")
            return None, None, None

        # B) Google Sheet CSV link yahan daalein
        google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_77OEOeI0MVDxYCbcTlq_Ld7Oq5CFSTC6LyYyAwQGyiHHSJhBvniVns4djzswkQSGNGT2_09r0LUA/pub?gid=0&single=true&output=csv" 
        
        try:
            patient_df = pd.read_csv(google_sheet_url)
            
            # NAYA ADDITION: Date column ko proper datetime format me convert karna
            if 'Date' in patient_df.columns:
                patient_df['Date'] = pd.to_datetime(patient_df['Date'], errors='coerce')
                
            # Patient data ko Zone se auto-link kar rahe hain (Ward_Name ke zariye)
            patient_df = pd.merge(patient_df, mapping_df, on='Ward_Name', how='left')
        except:
            st.warning("Google Sheet link update nahi hua hai. Dummy data load ho raha hai.")
            # Naye columns dummy data me bhi add kar diye hain backup ke liye
            patient_df = pd.DataFrame(columns=['Date', 'Patient_ID', 'Patient_Name', 'Disease', 'Ward_Name', 'Zone', 'Lat', 'Long', 'Status'])

        # C) GeoJSON Load karna Map Boundaries ke liye
        try:
            with open('wards.geojson', encoding='utf-8') as f:
                geo_data = json.load(f)
        except:
            st.error("wards.geojson file load nahi ho payi.")
            geo_data = None
            
        return patient_df, mapping_df, geo_data

    patient_df, mapping_df, geo_data = load_all_data()

    if patient_df is not None:
        # --- 3. SIDEBAR SMART FILTERS ---
        st.sidebar.header("Filters 🔍")
        
        # Ek copy banayenge jisme step-by-step filters apply honge
        filtered_df = patient_df.copy()
        
        # 0. SABSE UPAR: Date Range Filter
        if 'Date' in filtered_df.columns and not filtered_df['Date'].dropna().empty:
            min_date = filtered_df['Date'].min().date()
            max_date = filtered_df['Date'].max().date()
            
            selected_date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Date filter logic apply karna
            if len(selected_date_range) == 2:
                start_date, end_date = selected_date_range
                filtered_df = filtered_df[(filtered_df['Date'].dt.date >= start_date) & (filtered_df['Date'].dt.date <= end_date)]
            elif len(selected_date_range) == 1:
                start_date = selected_date_range[0]
                filtered_df = filtered_df[filtered_df['Date'].dt.date == start_date]
        else:
            st.sidebar.warning("Data me valid 'Date' column nahi hai.")

        # 1. Disease Filter
        if 'Disease' in filtered_df.columns:
            # Dropdown me wahi diseases dikhenge jo date filter ke baad bache hain
            disease_options = ["All"] + list(filtered_df['Disease'].dropna().unique())
        else:
            disease_options = ["All"]
            st.sidebar.warning("Sheet me 'Disease' column add nahi hua hai.")
            
        selected_disease = st.sidebar.selectbox("Select Disease", disease_options)
        
        if selected_disease != "All":
            filtered_df = filtered_df[filtered_df['Disease'] == selected_disease]

        # 2. Zone Filter
        zones_list = ["All"] + list(mapping_df['Zone'].dropna().unique())
        selected_zone = st.sidebar.selectbox("Select Zone", zones_list)

        if selected_zone != "All":
            filtered_df = filtered_df[filtered_df['Zone'] == selected_zone]
            # Ward list selected zone ke hisab se update hogi
            wards_list = ["All"] + list(mapping_df[mapping_df['Zone'] == selected_zone]['Ward_Name'].dropna().unique())
        else:
            wards_list = ["All"] + list(mapping_df['Ward_Name'].dropna().unique())

        # 3. Ward Filter 
        selected_ward = st.sidebar.selectbox("Select Ward", wards_list)
        
        if selected_ward != "All":
            filtered_df = filtered_df[filtered_df['Ward_Name'] == selected_ward]

        # --- 4. DASHBOARD METRICS ---
        st.subheader(f"Current Filter: {selected_zone} Zone -> {selected_ward}")
        total_cases = len(filtered_df)
        st.metric("Total Cases in Selected Range", total_cases)
        
        # --- 5. MAP GENERATION (Clustering + Boundaries + Popups) ---
        st.markdown("### 📍 Patients Map (Click on Boundaries & Zoom for Clustering)")
        
        if not filtered_df.empty and 'Lat' in filtered_df.columns and 'Long' in filtered_df.columns and geo_data:
            # Map ka center point set karna (Nagpur)
            m = folium.Map(location=[21.1458, 79.0882], zoom_start=11.5)
            
            # 1. GeoJSON properties me Zone aur Ward_Name add karna taaki Popup me dikh sake
            zone_dict = dict(zip(mapping_df['Ward_Name'], mapping_df['Zone']))
            for feature in geo_data['features']:
                # GeoJSON aur Excel se original naam nikalna
                raw_ward = feature['properties'].get('name', 'Unknown')
                raw_zone = zone_dict.get(raw_ward, 'Unknown Zone')
                
                # Har tarah ke spacing errors ko cover kiya gaya hai
                clean_zone = str(raw_zone).replace("Zone No. ", "").replace("Zone No.", "").replace("Zone No ", "").strip()
                clean_ward = str(raw_ward).replace("Prabhag No. ", "").replace("Prabhag No.", "").replace("Prabhag No ", "").strip()
                
                # In clean naamo ko naye variables me save karna
                feature['properties']['Clean_Ward'] = clean_ward
                feature['properties']['Clean_Zone'] = clean_zone

            # 2. Ward boundaries draw karna Clickable Popups ke sath
            folium.GeoJson(
                geo_data,
                style_function=lambda x: {
                    'color': 'black', 
                    'weight': 1.5, 
                    'fillOpacity': 0.1, 
                    'fillColor': '#3388ff'
                },
                popup=folium.features.GeoJsonPopup(
                    fields=['Clean_Zone', 'Clean_Ward'],
                    aliases=['📍 Zone:', '🏢 Prabhag:'],
                    labels=True,
                    style="font-family: Arial; font-size: 14px; font-weight: bold;"
                )
            ).add_to(m)

            # Marker Cluster add karna (yeh zoom in/out par cases ko scatter karega)
            marker_cluster = MarkerCluster().add_to(m)

            # Har ek patient ka data map par daalna
            for idx, row in filtered_df.iterrows():
                # Format date neatly for popup if it exists and is not NaT
                date_str = "N/A"
                if pd.notna(row.get('Date')):
                    date_str = row['Date'].strftime('%d-%m-%Y')

                # Pop-up ban banana jisme patient ki details hongi (handling blank/NaN safely)
                popup_text = f"""
                <b>Date:</b> {date_str}<br>
                <b>Patient ID:</b> {row.get('Patient_ID', 'N/A')}<br>
                <b>Name:</b> {row.get('Patient_Name', 'N/A')}<br>
                <b>Disease:</b> {row.get('Disease', 'N/A')}<br>
                <b>Ward:</b> {row.get('Ward_Name', 'N/A')}
                """
                
                # Check for valid lat/long before placing marker
                if pd.notna(row['Lat']) and pd.notna(row['Long']):
                    folium.Marker(
                        location=[row['Lat'], row['Long']],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(marker_cluster)
                
            # Streamlit mein map render karna (Bade size ke sath)
            st_folium(m, height=750, use_container_width=True, returned_objects=[])
            
        else:
            st.info("Is filter ke liye data ya Lat/Long points nahi hain.")

        # --- 6. DATA TABLE ---
        st.markdown("### 📋 Patient Details")
        # Displaying the date cleanly in the dataframe if Date column exists
        display_df = filtered_df.copy()
        if 'Date' in display_df.columns:
            display_df['Date'] = display_df['Date'].dt.strftime('%d-%m-%Y')
            
        st.dataframe(display_df)
