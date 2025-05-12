import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import snowflake.connector
import json
from PIL import Image
import os
from io import BytesIO
import requests
import random
import matplotlib.pyplot as plt
import base64

# Set page config
st.set_page_config(
    page_title="Art, Culture & Tourism in India",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6347;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4682B4;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 5px;
        background-color: #e9ecef;
        color: #495057;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FF6347;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Function to connect to Snowflake
def connect_to_snowflake():
    try:
        # In a real application, store these securely using st.secrets
        conn = snowflake.connector.connect(
            user=st.session_state.get('snowflake_user', 'somdevsheel'),
            password=st.session_state.get('snowflake_password', 'hh'),
            account=st.session_state.get('snowflake_account', 'LO64709'),
            warehouse=st.session_state.get('snowflake_warehouse', 'COMPUTE_WH'),
            database=st.session_state.get('snowflake_database', 'SNOWFLAKE_SAMPLE_DATA'),
            schema=st.session_state.get('snowflake_schema', 'PUBLIC')
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {str(e)}")
        return None

# Function to generate mock data
def generate_mock_data():
    # Indian states and union territories
    states = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
        'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
        'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
        'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir'
    ]
    
    # Define regions for each state
    regions = {
        'North': ['Delhi', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Punjab', 'Rajasthan', 'Uttar Pradesh', 'Uttarakhand'],
        'South': ['Andhra Pradesh', 'Karnataka', 'Kerala', 'Tamil Nadu', 'Telangana'],
        'East': ['Bihar', 'Jharkhand', 'Odisha', 'West Bengal'],
        'West': ['Goa', 'Gujarat', 'Maharashtra'],
        'Central': ['Chhattisgarh', 'Madhya Pradesh'],
        'Northeast': ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura']
    }
    
    # Map states to their regions
    state_to_region = {}
    for region, region_states in regions.items():
        for state in region_states:
            state_to_region[state] = region
    
    # Traditional art forms by state
    art_forms = {
        'Andhra Pradesh': ['Kuchipudi', 'Kalamkari', 'Budithi Brass Craft'],
        'Arunachal Pradesh': ['Monpa Mask', 'Thangka Paintings', 'Wancho Wood Carving'],
        'Assam': ['Bihu Dance', 'Sattriya Dance', 'Assam Silk Weaving'],
        'Bihar': ['Madhubani Painting', 'Manjusha Art', 'Sujni Embroidery'],
        'Chhattisgarh': ['Panthi Dance', 'Godna Art', 'Bell Metal Craft'],
        'Goa': ['Dekni Dance', 'Fugdi Dance', 'Goan Lacework'],
        'Gujarat': ['Garba', 'Patola Weaving', 'Rogan Art'],
        'Haryana': ['Phag Dance', 'Embroidery Craft', 'Charpai Weaving'],
        'Himachal Pradesh': ['Kullu Shawl Weaving', 'Chamba Rumal', 'Kangra Painting'],
        'Jharkhand': ['Sohrai Painting', 'Chhau Dance', 'Dokra Metal Craft'],
        'Karnataka': ['Yakshagana', 'Bidri Ware', 'Mysore Painting'],
        'Kerala': ['Kathakali', 'Mohiniyattam', 'Aranmula Kannadi'],
        'Madhya Pradesh': ['Gond Art', 'Bagh Print', 'Chanderi Weaving'],
        'Maharashtra': ['Lavani Dance', 'Warli Painting', 'Paithani Sarees'],
        'Manipur': ['Manipuri Dance', 'Longpi Pottery', 'Phanek Weaving'],
        'Meghalaya': ['Nongkrem Dance', 'Bamboo Craft', 'Garo Wangala Dance'],
        'Mizoram': ['Cheraw Dance', 'Mizo Bamboo Dance', 'Puanchei Textiles'],
        'Nagaland': ['Hornbill Festival Dances', 'Naga Shawl Weaving', 'Wood Carving'],
        'Odisha': ['Odissi Dance', 'Pattachitra', 'Applique Work'],
        'Punjab': ['Bhangra', 'Phulkari Embroidery', 'Jutti Making'],
        'Rajasthan': ['Ghoomar Dance', 'Blue Pottery', 'Miniature Painting'],
        'Sikkim': ['Mask Dance', 'Thangka Painting', 'Carpet Weaving'],
        'Tamil Nadu': ['Bharatanatyam', 'Tanjore Painting', 'Stone Carving'],
        'Telangana': ['Perini Shivatandavam', 'Nirmal Paintings', 'Bidri Craft'],
        'Tripura': ['Hojagiri Dance', 'Bamboo Craft', 'Risa Textile Weaving'],
        'Uttar Pradesh': ['Kathak Dance', 'Chikankari', 'Lucknow Zardozi'],
        'Uttarakhand': ['Choliya Dance', 'Aipan Art', 'Ringal Craft'],
        'West Bengal': ['Durga Puja Art', 'Kantha Stitch', 'Patachitra'],
        'Delhi': ['Kathak Dance', 'Zardozi Work', 'Meenakari Craft'],
        'Jammu and Kashmir': ['Rauf Dance', 'Pashmina Weaving', 'Walnut Wood Carving']
    }
    
    # Latitude and longitude for each state (approximate centers)
    state_coordinates = {
        'Andhra Pradesh': (15.9129, 79.7400),
        'Arunachal Pradesh': (28.2180, 94.7278),
        'Assam': (26.2006, 92.9376),
        'Bihar': (25.0961, 85.3131),
        'Chhattisgarh': (21.2787, 81.8661),
        'Goa': (15.2993, 74.1240),
        'Gujarat': (22.2587, 71.1924),
        'Haryana': (29.0588, 76.0856),
        'Himachal Pradesh': (31.1048, 77.1734),
        'Jharkhand': (23.6102, 85.2799),
        'Karnataka': (15.3173, 75.7139),
        'Kerala': (10.8505, 76.2711),
        'Madhya Pradesh': (23.4733, 77.9470),
        'Maharashtra': (19.7515, 75.7139),
        'Manipur': (24.6637, 93.9063),
        'Meghalaya': (25.4670, 91.3662),
        'Mizoram': (23.1645, 92.9376),
        'Nagaland': (26.1584, 94.5624),
        'Odisha': (20.9517, 85.0985),
        'Punjab': (31.1471, 75.3412),
        'Rajasthan': (27.0238, 74.2179),
        'Sikkim': (27.5330, 88.5122),
        'Tamil Nadu': (11.1271, 78.6569),
        'Telangana': (18.1124, 79.0193),
        'Tripura': (23.9408, 91.9882),
        'Uttar Pradesh': (26.8467, 80.9462),
        'Uttarakhand': (30.0668, 79.0193),
        'West Bengal': (22.9868, 87.8550),
        'Delhi': (28.7041, 77.1025),
        'Jammu and Kashmir': (33.7782, 76.5762)
    }
    
    # Create empty list to store data
    data = []
    
    # Generate data for the last 5 years (2020-2024) and for each month
    years = range(2020, 2025)
    months = range(1, 13)
    
    # Seasonal trends - higher tourism in different regions based on season
    # Higher tourism in North and Central during winter (Nov-Feb)
    # Higher tourism in Himalayan regions during summer (Apr-Jul)
    # Higher tourism in South and East during monsoon (Jul-Oct)
    seasonal_multipliers = {
        'North': [0.8, 0.7, 0.9, 1.0, 1.1, 1.2, 0.7, 0.6, 0.8, 1.0, 1.5, 1.7],
        'South': [1.3, 1.2, 1.0, 0.8, 0.7, 0.6, 0.8, 1.0, 1.2, 1.4, 1.3, 1.5],
        'East': [1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.9, 1.1, 1.3, 1.4, 1.2, 1.3],
        'West': [1.1, 1.0, 0.9, 0.7, 0.6, 0.5, 0.8, 1.2, 1.4, 1.3, 1.2, 1.3],
        'Central': [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.5],
        'Northeast': [0.6, 0.7, 0.9, 1.1, 1.3, 1.4, 0.9, 0.7, 0.8, 1.0, 0.8, 0.7]
    }
    
    # Year-on-year growth trend (tourism recovery after COVID)
    yearly_growth = {
        2020: 0.4,  # COVID impact
        2021: 0.6,  # Partial recovery
        2022: 0.8,  # Further recovery
        2023: 0.9,  # Almost back to normal
        2024: 1.1   # Beyond pre-COVID levels
    }
    
    # Base popularity factors for states (larger states/popular tourist destinations have higher base visitors)
    popularity_factor = {
        'Rajasthan': 1.8, 'Kerala': 1.7, 'Goa': 1.6, 'Tamil Nadu': 1.7, 'Uttar Pradesh': 1.7,
        'Maharashtra': 1.6, 'Delhi': 1.6, 'Gujarat': 1.4, 'Karnataka': 1.5, 'Himachal Pradesh': 1.4,
        'Uttarakhand': 1.4, 'Jammu and Kashmir': 1.3, 'West Bengal': 1.4, 'Madhya Pradesh': 1.3,
        'Odisha': 1.2, 'Andhra Pradesh': 1.2, 'Telangana': 1.2, 'Assam': 1.1, 'Punjab': 1.1,
        'Bihar': 0.9, 'Chhattisgarh': 0.9, 'Jharkhand': 0.8, 'Manipur': 0.8, 'Meghalaya': 0.9,
        'Tripura': 0.8, 'Nagaland': 0.8, 'Mizoram': 0.7, 'Sikkim': 1.0, 'Arunachal Pradesh': 0.9,
        'Haryana': 0.9
    }
    
    for year in years:
        for month in months:
            for state in states:
                region = state_to_region.get(state, 'Other')
                state_pop_factor = popularity_factor.get(state, 1.0)
                seasonal_factor = seasonal_multipliers.get(region, [1.0] * 12)[month - 1]
                year_factor = yearly_growth.get(year, 1.0)
                
                # Generate tourist visits with some randomness and factors
                base_visits = np.random.gamma(shape=10, scale=state_pop_factor * 10000)
                tourist_visits = int(base_visits * seasonal_factor * year_factor * (1 + np.random.normal(0, 0.1)))
                
                # Random art form selection for this record
                if state in art_forms:
                    art_form = random.choice(art_forms[state])
                else:
                    art_form = "Traditional Dance"
                
                # Generate funding received with correlation to tourist visits but with variability
                funding_base = tourist_visits * random.uniform(0.5, 2.0)
                funding_received = int(funding_base * (1 + np.random.normal(0, 0.2)))
                
                # Get coordinates
                lat, lon = state_coordinates.get(state, (0, 0))
                
                # Append data
                data.append({
                    'state': state,
                    'art_form': art_form,
                    'tourist_visits': tourist_visits,
                    'month': month,
                    'year': year,
                    'region': region,
                    'funding_received': funding_received,
                    'latitude': lat,
                    'longitude': lon
                })
    
    return pd.DataFrame(data)

# Function to query data from Snowflake
def query_snowflake_data():
    try:
        conn = connect_to_snowflake()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state, art_form, tourist_visits, month, year, region, funding_received 
                FROM tourism_data
            """)
            
            # Fetch result into a pandas dataframe
            result = cursor.fetch_pandas_all()
            
            # Close connection
            cursor.close()
            conn.close()
            
            return result
        else:
            # If connection fails, use mock data
            return generate_mock_data()
    except Exception as e:
        st.warning(f"Using mock data (Error: {str(e)})")
        return generate_mock_data()

# Sidebar Configuration
st.sidebar.markdown("<h2 style='text-align: center;'>Settings</h2>", unsafe_allow_html=True)

# Data source selection
data_source = st.sidebar.radio("Select Data Source", ["Mock Data", "Snowflake Connection"])

if data_source == "Mock Data":
    df = generate_mock_data()
else:
    # Snowflake connection credentials
    st.sidebar.subheader("Snowflake Credentials")
    if 'snowflake_user' not in st.session_state:
        st.session_state.snowflake_user = ""
    if 'snowflake_password' not in st.session_state:
        st.session_state.snowflake_password = ""
    if 'snowflake_account' not in st.session_state:
        st.session_state.snowflake_account = ""
    if 'snowflake_warehouse' not in st.session_state:
        st.session_state.snowflake_warehouse = ""
    if 'snowflake_database' not in st.session_state:
        st.session_state.snowflake_database = ""
    if 'snowflake_schema' not in st.session_state:
        st.session_state.snowflake_schema = ""
    
    st.session_state.snowflake_user = st.sidebar.text_input("Username", st.session_state.snowflake_user)
    st.session_state.snowflake_password = st.sidebar.text_input("Password", st.session_state.snowflake_password, type="password")
    st.session_state.snowflake_account = st.sidebar.text_input("Account", st.session_state.snowflake_account)
    st.session_state.snowflake_warehouse = st.sidebar.text_input("Warehouse", st.session_state.snowflake_warehouse)
    st.session_state.snowflake_database = st.sidebar.text_input("Database", st.session_state.snowflake_database)
    st.session_state.snowflake_schema = st.sidebar.text_input("Schema", st.session_state.snowflake_schema)
    
    if st.sidebar.button("Connect to Snowflake"):
        with st.spinner("Connecting to Snowflake..."):
            df = query_snowflake_data()
    else:
        df = generate_mock_data()

# Filter controls
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

# Year selection
years = sorted(df['year'].unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)  # Default to most recent year

# Filter by region
regions = sorted(df['region'].unique())
selected_region = st.sidebar.multiselect("Filter by Region", regions, default=regions)

# Month selection for seasonal analysis
months = list(range(1, 13))
month_names = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
month_dict = {i+1: month for i, month in enumerate(month_names)}
selected_months = st.sidebar.multiselect("Select Months", options=months, 
                                       default=months, format_func=lambda x: month_dict[x])

# Apply filters
filtered_df = df[(df['year'] == selected_year) & 
                (df['region'].isin(selected_region)) &
                (df['month'].isin(selected_months))]

# Aggregate data by state
state_agg = filtered_df.groupby('state').agg({
    'tourist_visits': 'sum',
    'funding_received': 'sum'
}).reset_index()

# Get top 10 states by tourist visits
top_states = state_agg.sort_values('tourist_visits', ascending=False).head(10)

# Main Area
st.markdown("<h1 class='main-header'>🏛️ Art, Culture & Tourism in India</h1>", unsafe_allow_html=True)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:,}</div>
        <div class="metric-label">Total Tourist Visits</div>
    </div>
    """.format(int(filtered_df['tourist_visits'].sum())), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{}</div>
        <div class="metric-label">States & UTs</div>
    </div>
    """.format(len(filtered_df['state'].unique())), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{}</div>
        <div class="metric-label">Art Forms</div>
    </div>
    """.format(len(filtered_df['art_form'].unique())), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">₹{:,.0f} Cr</div>
        <div class="metric-label">Total Funding</div>
    </div>
    """.format(filtered_df['funding_received'].sum() / 10000000), unsafe_allow_html=True)

st.markdown("---")

# Interactive Map and Top States
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<h2 class='sub-header'>🗺️ Tourism Map of India</h2>", unsafe_allow_html=True)
    
    # Prepare data for the map
    map_data = filtered_df.groupby(['state', 'latitude', 'longitude']).agg({
        'tourist_visits': 'sum'
    }).reset_index()
    
    # Scale the size of circles based on tourist visits
    max_visits = map_data['tourist_visits'].max()
    map_data['size'] = map_data['tourist_visits'] / max_visits * 30
    
    # Create the map
    fig = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        size="size",
        color="tourist_visits",
        hover_name="state",
        hover_data={"tourist_visits": True, "latitude": False, "longitude": False, "size": False},
        color_continuous_scale=px.colors.sequential.Plasma,
        zoom=4,
        center={"lat": 23.5937, "lon": 78.9629},
        opacity=0.7,
        height=500,
        title="Tourist Visits by State",
        labels={"tourist_visits": "Tourist Visits"}
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Tourist Visits"),
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("<h2 class='sub-header'>🏆 Top 10 Tourist States</h2>", unsafe_allow_html=True)
    
    # Create a bar chart for top states
    fig = px.bar(
        top_states,
        x='tourist_visits',
        y='state',
        orientation='h',
        color='tourist_visits',
        color_continuous_scale=px.colors.sequential.Viridis,
        labels={'tourist_visits': 'Number of Visitors', 'state': 'State'},
        height=500
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="Tourist Visits",
        yaxis_title=None,
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# State-wise Analysis
st.markdown("<h2 class='sub-header'>🏞️ State-wise Cultural Tourism Analysis</h2>", unsafe_allow_html=True)

# Select state for detailed analysis
all_states = sorted(df['state'].unique())
selected_state_analysis = st.selectbox("Select a state to explore its art forms and funding", all_states)

# Filter data for selected state
state_data = filtered_df[filtered_df['state'] == selected_state_analysis]

if not state_data.empty:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Aggregate art form data
        art_form_data = state_data.groupby('art_form').agg({
            'tourist_visits': 'sum',
            'funding_received': 'sum'
        }).reset_index()
        
        # Create pie chart for art forms
        fig = px.pie(
            art_form_data,
            values='tourist_visits',
            names='art_form',
            title=f"Popular Art Forms in {selected_state_analysis}",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Create funding bar chart
        fig = px.bar(
            art_form_data,
            x='art_form',
            y='funding_received',
            title=f"Government Funding by Art Form in {selected_state_analysis}",
            color='funding_received',
            color_continuous_scale=px.colors.sequential.Blugrn,
            labels={'funding_received': 'Funding (₹)', 'art_form': 'Art Form'}
        )
        
        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Funding (₹)",
            margin=dict(t=40, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Monthly trends for selected state
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader(f"Monthly Tourism Trends in {selected_state_analysis} ({selected_year})")
    
    # Get monthly data for the selected state and year
    monthly_data = df[(df['state'] == selected_state_analysis) & (df['year'] == selected_year)]
    monthly_agg = monthly_data.groupby('month').agg({
        'tourist_visits': 'sum'
    }).reset_index()
    
    # Sort by month
    monthly_agg = monthly_agg.sort_values('month')
    monthly_agg['month_name'] = monthly_agg['month'].map(month_dict)
    
    # Create line chart
    fig = px.line(
        monthly_agg,
        x='month_name',
        y='tourist_visits',
        markers=True,
        labels={'tourist_visits': 'Tourist Visits', 'month_name': 'Month'},
        height=400
    )
    
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': list(month_dict.values())},
        margin=dict(l=0, r=0, t=10, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Regional comparison
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    region_of_state = df[df['state'] == selected_state_analysis]['region'].iloc[0]
    st.subheader(f"Comparing {selected_state_analysis} with Other States in {region_of_state} Region")
    
    # Get states in the same region
    states_in_region = df[df['region'] == region_of_state]['state'].unique()
    
    # Aggregate data for regional comparison
    region_comp = filtered_df[filtered_df['state'].isin(states_in_region)].groupby('state').agg({
        'tourist_visits': 'sum',
        'funding_received': 'sum'
    }).reset_index()
    
    # Calculate funding per visitor
    region_comp['funding_per_visitor'] = region_comp['funding_received'] / region_comp['tourist_visits']
    
    # Create scatter plot
    fig = px.scatter(
        region_comp,
        x='tourist_visits',
        y='funding_received',
        size='funding_per_visitor',
        color='state',
        hover_name='state',
        labels={
            'tourist_visits': 'Total Tourist Visits',
            'funding_received': 'Total Funding (₹)',
            'funding_per_visitor': 'Funding per Visitor (₹)'
        },
        height=500
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error(f"No data available for {selected_state_analysis} with the current filters")

# Add Year-over-Year Comparison
st.markdown("---")
st.markdown("<h2 class='sub-header'>📈 Year-over-Year Tourism Growth</h2>", unsafe_allow_html=True)

# Year-over-year analysis
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Calculate year-by-year totals
    yearly_data = df.groupby(['year', 'region']).agg({
        'tourist_visits': 'sum'
    }).reset_index()
    
    # Create line chart
    fig = px.line(
        yearly_data,
        x='year',
        y='tourist_visits',
        color='region',
        markers=True,
        labels={'tourist_visits': 'Tourist Visits', 'year': 'Year', 'region': 'Region'},
        title="Tourism Growth by Region (2020-2024)",
        height=400
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Calculate growth percentage
    yearly_totals = df.groupby('year').agg({
        'tourist_visits': 'sum'
    }).reset_index()
    
    yearly_totals['growth'] = yearly_totals['tourist_visits'].pct_change() * 100
    yearly_totals['growth'] = yearly_totals['growth'].fillna(0)
    
    # Create the chart
    fig = px.bar(
        yearly_totals,
        x='year',
        y='growth',
        text=yearly_totals['growth'].apply(lambda x: f"{x:.1f}%"),
        title="Annual Growth Rate (%)",
        color='growth',
        color_continuous_scale=px.colors.diverging.RdYlGn,
        height=400
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis_title="Growth (%)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Art and Culture Showcase
st.markdown("---")
st.markdown("<h2 class='sub-header'>🎭 Art and Culture Showcase</h2>", unsafe_allow_html=True)

# Top art forms across India
art_form_agg = filtered_df.groupby('art_form').agg({
    'tourist_visits': 'sum',
    'funding_received': 'sum'
}).reset_index()

top_art_forms = art_form_agg.sort_values('tourist_visits', ascending=False).head(10)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Most Popular Art Forms in India")
    
    fig = px.bar(
        top_art_forms,
        x='tourist_visits',
        y='art_form',
        orientation='h',
        color='tourist_visits',
        color_continuous_scale=px.colors.sequential.Oranges,
        labels={'tourist_visits': 'Associated Tourist Visits', 'art_form': 'Art Form'},
        height=500
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="Tourist Visits",
        yaxis_title=None
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Funding Distribution by Art Form")
    
    # Funding distribution
    funding_df = top_art_forms.copy()
    funding_df['funding_per_visitor'] = funding_df['funding_received'] / funding_df['tourist_visits']
    
    fig = px.scatter(
        funding_df,
        x='tourist_visits',
        y='funding_received',
        size='funding_per_visitor',
        color='art_form',
        hover_name='art_form',
        log_x=True,
        log_y=True,
        size_max=30,
        labels={
            'tourist_visits': 'Tourist Visits (log scale)',
            'funding_received': 'Funding Received (log scale)',
            'funding_per_visitor': 'Funding per Visitor (₹)'
        },
        height=500
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Seasonal Analysis
st.markdown("---")
st.markdown("<h2 class='sub-header'>🌦️ Seasonal Tourism Patterns</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Monthly Tourism Across Regions")
    
    # Get monthly trends by region
    monthly_region = df[df['year'] == selected_year].groupby(['month', 'region']).agg({
        'tourist_visits': 'sum'
    }).reset_index()
    
    # Add month names
    monthly_region['month_name'] = monthly_region['month'].map(month_dict)
    
    # Create the chart
    fig = px.line(
        monthly_region,
        x='month_name',
        y='tourist_visits',
        color='region',
        markers=True,
        labels={'tourist_visits': 'Tourist Visits', 'month_name': 'Month', 'region': 'Region'},
        height=400
    )
    
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': list(month_dict.values())},
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Peak Tourism Months by Region")
    
    # Calculate the month with maximum tourists for each region
    peak_months = monthly_region.loc[monthly_region.groupby('region')['tourist_visits'].idxmax()]
    
    # Create the chart
    fig = px.bar(
        peak_months,
        x='region',
        y='tourist_visits',
        color='month_name',
        labels={'tourist_visits': 'Peak Monthly Visits', 'region': 'Region', 'month_name': 'Month'},
        height=400
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title=None,
        yaxis_title="Tourist Visits",
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Download the data
st.markdown("---")
st.markdown("<h2 class='sub-header'>📊 Data Export</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Convert dataframe to CSV for download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        label="Download Current View as CSV",
        data=csv,
        file_name=f"india_tourism_data_{selected_year}.csv",
        mime="text/csv",
    )

with col2:
    # Generate Excel report with selected charts
    if st.button("Generate Detailed Excel Report"):
        with st.spinner("Generating report..."):
            st.success("Report generated! Click the download button below.")
            # Note: In a real application, you would create an Excel file with charts here
            st.download_button(
                label="Download Excel Report",
                data=csv,  # Placeholder - should be Excel data in real app
                file_name=f"india_tourism_report_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# Advanced Analytics
st.markdown("---")
st.markdown("<h2 class='sub-header'>🔍 Advanced Analytics</h2>", unsafe_allow_html=True)

# Create tabs for different analyses
tab1, tab2, tab3 = st.tabs(["Correlation Analysis", "Funding Impact", "Tourism Forecasting"])

with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Correlation Between Tourism and Cultural Funding")
    
    # Calculate correlation metrics
    state_corr = filtered_df.groupby('state').agg({
        'tourist_visits': 'sum',
        'funding_received': 'sum'
    }).reset_index()
    
    correlation = state_corr['tourist_visits'].corr(state_corr['funding_received'])
    
    # Create a scatter plot
    fig = px.scatter(
        state_corr,
        x='tourist_visits',
        y='funding_received',
        hover_name='state',
        trendline="ols",
        labels={
            'tourist_visits': 'Total Tourist Visits',
            'funding_received': 'Total Cultural Funding (₹)'
        },
        height=500
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        annotations=[
            dict(
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                text=f"Correlation Coefficient: {correlation:.2f}",
                showarrow=False,
                font=dict(size=14)
            )
        ]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    st.markdown(f"""
    The correlation coefficient of {correlation:.2f} suggests a {'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.4 else 'weak'} 
    {'positive' if correlation > 0 else 'negative'} relationship between tourism visits and cultural funding. 
    
    This indicates that {'states with higher tourism numbers tend to receive more cultural funding' if correlation > 0 else 'there is no clear pattern between tourism and funding allocation'}.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Funding Impact on Tourism Growth")
    
    # Calculate metrics for previous year
    prev_year = selected_year - 1
    
    # Get data for both years
    current_year_data = df[df['year'] == selected_year].groupby('state').agg({
        'tourist_visits': 'sum',
        'funding_received': 'sum'
    }).reset_index()
    
    prev_year_data = df[df['year'] == prev_year].groupby('state').agg({
        'tourist_visits': 'sum',
        'funding_received': 'sum'
    }).reset_index()
    
    # Merge data
    if not prev_year_data.empty and not current_year_data.empty:
        growth_data = pd.merge(current_year_data, prev_year_data, on='state', suffixes=('_current', '_prev'))
        
        # Calculate growth metrics
        growth_data['visit_growth_pct'] = ((growth_data['tourist_visits_current'] - growth_data['tourist_visits_prev']) / 
                                          growth_data['tourist_visits_prev'] * 100)
        growth_data['funding_prev_per_visitor'] = growth_data['funding_received_prev'] / growth_data['tourist_visits_prev']
        
        # Create scatter plot
        fig = px.scatter(
            growth_data,
            x='funding_prev_per_visitor',
            y='visit_growth_pct',
            hover_name='state',
            size='tourist_visits_prev',
            color='tourist_visits_current',
            color_continuous_scale='Viridis',
            labels={
                'funding_prev_per_visitor': f'Funding per Visitor in {prev_year} (₹)',
                'visit_growth_pct': f'Tourist Growth Rate {prev_year} to {selected_year} (%)',
                'tourist_visits_prev': f'Tourist Visits in {prev_year}',
                'tourist_visits_current': f'Tourist Visits in {selected_year}'
            },
            height=500
        )
        
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insights
        funding_growth_corr = growth_data['funding_prev_per_visitor'].corr(growth_data['visit_growth_pct'])
        
        st.markdown(f"""
        This analysis examines whether states that received more cultural funding per visitor in {prev_year} 
        experienced higher tourism growth in {selected_year}.
        
        The correlation coefficient is {funding_growth_corr:.2f}, suggesting a 
        {'strong' if abs(funding_growth_corr) > 0.7 else 'moderate' if abs(funding_growth_corr) > 0.4 else 'weak'} 
        {'positive' if funding_growth_corr > 0 else 'negative'} relationship between funding and subsequent tourism growth.
        """)
    else:
        st.info(f"Insufficient data to compare {prev_year} and {selected_year}")
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Tourism Growth Forecast")
    
    # Simple forecast using historical trends
    yearly_total = df.groupby('year').agg({
        'tourist_visits': 'sum'
    }).reset_index()
    
    # Add forecast years
    forecast_years = list(range(max(yearly_total['year']) + 1, max(yearly_total['year']) + 4))
    forecast_data = pd.DataFrame({'year': forecast_years})
    
    # Use simple linear regression for forecasting
    from sklearn.linear_model import LinearRegression
    
    X = yearly_total[['year']]
    y = yearly_total['tourist_visits']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict for future years
    forecast_data['tourist_visits'] = model.predict(forecast_data[['year']])
    
    # Combine actual and forecast data
    combined_data = pd.concat([yearly_total, forecast_data])
    combined_data['type'] = combined_data['year'].apply(lambda x: 'Actual' if x <= max(yearly_total['year']) else 'Forecast')
    
    # Create the chart
    fig = px.line(
        combined_data,
        x='year',
        y='tourist_visits',
        color='type',
        markers=True,
        labels={'tourist_visits': 'Total Tourist Visits', 'year': 'Year', 'type': ''},
        height=400
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add forecast metrics
    last_actual = yearly_total['tourist_visits'].iloc[-1]
    first_forecast = forecast_data['tourist_visits'].iloc[0]
    growth_rate = (first_forecast - last_actual) / last_actual * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"Estimated {forecast_years[0]} Visitors",
            value=f"{int(first_forecast):,}",
            delta=f"{growth_rate:.1f}%"
        )
    
    with col2:
        st.metric(
            label=f"Estimated {forecast_years[1]} Visitors",
            value=f"{int(forecast_data['tourist_visits'].iloc[1]):,}",
            delta=f"{((forecast_data['tourist_visits'].iloc[1] - last_actual) / last_actual * 100):.1f}%"
        )
    
    with col3:
        st.metric(
            label=f"Estimated {forecast_years[2]} Visitors",
            value=f"{int(forecast_data['tourist_visits'].iloc[2]):,}",
            delta=f"{((forecast_data['tourist_visits'].iloc[2] - last_actual) / last_actual * 100):.1f}%"
        )
    
    st.markdown("""
    **Note:** This forecast is based on a simple linear regression model using historical data. 
    Actual tourism numbers may vary based on economic conditions, policy changes, and global events.
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 10px;'>
    <p>Created for the Art, Culture, and Tourism in India Hackathon Challenge.</p>
    <p>Data is simulated for demonstration purposes.</p>
</div>
""", unsafe_allow_html=True)
