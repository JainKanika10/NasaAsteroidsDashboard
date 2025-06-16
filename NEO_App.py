import streamlit as st
import pandas as pd
import mysql.connector

# --- Custom CSS for background and layout ---
st.markdown(
    """
    <style>
    /* Main background */
    .main {
        background-color: #f4f9ff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #e6f0ff;
    }

    /* Title and headers */
    h1, h2, h3 {
        color: #003366;
    }

    /* Dataframe table font */
    .dataframe th, .dataframe td {
        font-size: 14px;
    }

    /* Radio and selectbox labels */
    label, .css-1cpxqw2 {
        color: #1a1a1a !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- DB CONNECTION ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="11Sanskriti11",
    database="nasa_asteroids"
)
cursor = conn.cursor()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Asteroid Approaches")
page = st.sidebar.radio("Select Page", ["Home", "Filter Criteria", "Query Explorer"])

# --- PAGE 0: HOME PAGE ---
if page == "Home":
    st.title("🌌 Welcome to NASA Asteroid Tracker")
    st.markdown("""
    Welcome to the **NASA NEO (Near-Earth Object) Tracking and Insights Dashboard**.  
    This tool provides:
    - 🌠 Filter-based asteroid tracking between selected dates.
    - 📊 Query explorer for deep space insights.


    ---
    **Use the sidebar to navigate between pages.**

    Created by: *Kanika Jain*  
    Powered by: Streamlit + MySQL + NASA NEO Data  
    """)

# --- PAGE 1: FILTER CRITERIA ---
elif page == "Filter Criteria":
    st.title("🚀 NASA Asteroid Tracker")

    col1, col_spacer1, col2, col_spacer2, col3 = st.columns([1, 0.2, 1, 0.2, 1])
    with col1:
        min_mag = st.slider("Min Magnitude", 10.41, 32.38, 10.41)
        min_dia = st.slider("Min Estimated Diameter (km)", 0.0, 22.00, 0.0)
        max_dia = st.slider("Max Estimated Diameter (km)", 0.0, 49.21, 49.21)

    with col2:
        rel_vel = st.slider("Relative Velocity (kmph)", 1054.26, 186136.00, (1054.26, 186136.00))
        astronomical = st.slider("Astronomical Unit", 0.0, 0.5, 0.5)
        hazardous_only = st.selectbox("Only Show Potentially Hazardous", ["0", "1"])

    with col3:
        Distance_Lunar = st.slider("Distance_Lunar", 0.26, 194.46, (0.26, 194.46))
        start_date = st.date_input("Start Date", pd.to_datetime("2025-05-01"))
        end_date = st.date_input("End Date", pd.to_datetime("2027-07-29"))

    if st.button("Apply Filter"):
        filter_query = f"""
            SELECT a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km,
                   a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid,
                   c.close_approach_date, c.relative_velocity_kmph, c.astronomical
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE close_approach_date BETWEEN '{start_date}' AND '{end_date}'
              AND a.absolute_magnitude_h >= {min_mag}
              AND a.estimated_diameter_min_km >= {min_dia}
              AND a.estimated_diameter_max_km <= {max_dia}
              AND c.relative_velocity_kmph BETWEEN {rel_vel[0]} AND {rel_vel[1]}
              AND c.astronomical <= {astronomical}
              AND c.miss_distance_lunar BETWEEN {Distance_Lunar[0]} AND {Distance_Lunar[1]}
              {"AND a.is_potentially_hazardous_asteroid = 1" if hazardous_only == "1" else ""}
        """
        cursor.execute(filter_query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[
            "Name", "Magnitude", "Min Diameter (km)", "Max Diameter (km)", "Hazardous",
            "Date", "Velocity (km/h)", "Astronomical Unit"
        ])
        df["Hazardous"] = df["Hazardous"].map({0: "No", 1: "Yes"})
        if df.empty:
            st.warning("No asteroids found matching the criteria.")
        else:
            st.subheader("Filtered Asteroids")
            st.dataframe(df)

# --- PAGE 2: QUERY EXPLORER ---
elif page == "Query Explorer":
    st.title("📊 Asteroid Query Explorer")

    query_list = [
        "Approach Count", "Average Velocity", "Top 10 Fastest", "Hazardous >3 Times",
        "Busiest Month", "Fastest Ever", "Max Diameter", "Getting Closer",
        "Closest Approach", "Velocity > 50,000", "Monthly Approach Count",
        "Highest Brightness", "Hazardous vs Non-Hazardous", "Closer than Moon", "Within 0.05 AU",
        "Slowest 10 Asteroid", "Year-wise Asteroid Count", "Asteroids Seen Only Once",
        "Average Diameter of Hazardous vs Non-Hazardous", "Top 5 Closest Hazardous Asteroids"
    ]

    selected_tab = st.selectbox("Select a Query", query_list)

    def run_query(query, columns):
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        st.subheader(selected_tab)
        st.dataframe(df)

    # Queries (unchanged - same as your original ones)
    if selected_tab == "Approach Count":
        run_query("""
            SELECT a.name, COUNT(*) AS approach_count
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name ORDER BY approach_count DESC
        """, ["Asteroid Name", "Approach Count"])

    elif selected_tab == "Average Velocity":
        run_query("""
            SELECT a.name, ROUND(AVG(c.relative_velocity_kmph), 2) AS avg_velocity
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name 
            ORDER BY avg_velocity DESC
        """, ["Asteroid Name", "Avg Velocity (km/h)"])

    elif selected_tab == "Top 10 Fastest":
        run_query("""
            SELECT a.name, MAX(c.relative_velocity_kmph) AS max_velocity
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name 
            ORDER BY max_velocity DESC 
            LIMIT 10
        """, ["Asteroid Name", "Max Velocity (km/h)"])

    elif selected_tab == "Hazardous >3 Times":
        run_query("""
            SELECT a.name, COUNT(*) AS approach_count
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = 1
            GROUP BY a.name 
            HAVING COUNT(*) > 3 
            ORDER BY approach_count DESC
        """, ["Asteroid Name", "Approach Count"])

    elif selected_tab == "Busiest Month":
        run_query("""
            SELECT MONTHNAME(close_approach_date) AS month, COUNT(*) AS approach_count
            FROM close_approach 
            GROUP BY MONTH
            ORDER BY approach_count DESC 
            LIMIT 1
        """, ["Month", "Approach Count"])

    elif selected_tab == "Fastest Ever":
        run_query("""
            SELECT a.name, c.relative_velocity_kmph, c.close_approach_date
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            ORDER BY c.relative_velocity_kmph DESC 
            LIMIT 1
        """, ["Asteroid Name", "Velocity (km/h)", "Date"])

    elif selected_tab == "Max Diameter":
        run_query("""
            SELECT name, estimated_diameter_max_km
            FROM asteroids ORDER BY estimated_diameter_max_km DESC 
            LIMIT 1
        """, ["Asteroid Name", "Max Diameter (km)"])

    elif selected_tab == "Getting Closer":
        run_query("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            ORDER BY a.name, c.close_approach_date
        """, ["Asteroid Name", "Date", "Miss Distance (km)"])

    elif selected_tab == "Closest Approach":
        run_query("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE (a.id, c.miss_distance_km) IN (
                SELECT neo_reference_id, MIN(miss_distance_km)
                FROM close_approach GROUP BY neo_reference_id
            )
            ORDER BY c.miss_distance_km ASC
        """, ["Asteroid Name", "Date", "Closest Distance (km)"])

    elif selected_tab == "Velocity > 50,000":
        run_query("""
            SELECT DISTINCT a.name, c.relative_velocity_kmph
            FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.relative_velocity_kmph > 50000 
            ORDER BY c.relative_velocity_kmph DESC
        """, ["Asteroid Name", "Velocity (km/h)"])

    elif selected_tab == "Monthly Approach Count":
        run_query("""
          SELECT MONTHNAME(close_approach_date) AS month_name, COUNT(*) AS approach_count
          FROM close_approach
          GROUP BY Month_name , Month(close_approach_date)
          ORDER BY Month(close_approach_date)
        """, ["Month", "Approach Count"])

    elif selected_tab == "Highest Brightness":
        run_query("""
          SELECT name, absolute_magnitude_h
          FROM asteroids ORDER BY absolute_magnitude_h ASC 
          LIMIT 1
        """, ["Asteroid Name", "Brightness (mag)"])

    elif selected_tab == "Hazardous vs Non-Hazardous":
        run_query("""
          SELECT is_potentially_hazardous_asteroid AS Hazardous, COUNT(*) AS count
          FROM asteroids 
          GROUP BY is_potentially_hazardous_asteroid
        """, ["Hazardous", "Count"])

    elif selected_tab == "Closer than Moon":
        run_query("""
          SELECT a.name, c.close_approach_date, c.miss_distance_lunar
          FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
          WHERE c.miss_distance_lunar < 1 
          ORDER BY c.miss_distance_lunar
        """, ["Asteroid Name", "Date", "Distance (LD)"])

    elif selected_tab == "Within 0.05 AU":
        run_query("""
          SELECT a.name, c.close_approach_date, c.astronomical
          FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
          WHERE c.astronomical < 0.05 
          ORDER BY c.astronomical
        """, ["Asteroid Name", "Date", "Distance (AU)"])

    elif selected_tab == "Slowest 10 Asteroid":
        run_query("""
          SELECT a.name, MIN(c.relative_velocity_kmph) AS min_velocity
          FROM asteroids a JOIN close_approach c ON a.id = c.neo_reference_id
          GROUP BY a.name ORDER BY min_velocity ASC 
          LIMIT 10
        """, ["Asteroid Name", "min_velocity"])

    elif selected_tab == "Year-wise Asteroid Count":
        run_query("""
          SELECT YEAR(close_approach_date) AS year, COUNT(*) AS approach_count
          FROM close_approach GROUP BY year ORDER BY year
        """, ["Year", "Asteroid Count"])

    elif selected_tab == "Average Diameter of Hazardous vs Non-Hazardous":
        run_query("""
          SELECT is_potentially_hazardous_asteroid, 
          ROUND(AVG(estimated_diameter_max_km), 2) AS avg_diameter
          FROM asteroids 
          GROUP BY is_potentially_hazardous_asteroid
        """, ["Average Diameter of Hazardous/Non-Hazardous Asteroid", "Avg_Diameter_Km"])

    elif selected_tab == "Asteroids Seen Only Once":
        run_query("""
          SELECT a.name , count(*)
          FROM asteroids a
          JOIN close_approach c ON a.id = c.neo_reference_id
          GROUP BY a.name 
          HAVING COUNT(*) = 1
        """, ["Asteroid Name", "Asteroid_Count"])

    elif selected_tab == "Top 5 Closest Hazardous Asteroids":
        run_query("""
          SELECT a.name, c.close_approach_date, c.miss_distance_km
          FROM asteroids a
          JOIN close_approach c ON a.id = c.neo_reference_id
          WHERE a.is_potentially_hazardous_asteroid = 1
          ORDER BY c.miss_distance_km ASC LIMIT 5
        """, ["Asteroid Name", "Approach Date", "Distance(Km)"])

# --- CLOSE DB CONNECTION ---
cursor.close()
conn.close()
