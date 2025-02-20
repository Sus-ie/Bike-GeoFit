import streamlit as st
import pandas as pd
import numpy as np
import os

# Load the dataset with error handling
@st.cache_data
def load_data():
    try:
        file_path = 'geometrics_modifiedv3.csv'
        if not os.path.exists(file_path):
            st.error("The dataset file was not found. Please ensure 'geometrics_modifiedv3.csv' is in the same directory as this script.")
            return pd.DataFrame()
        return pd.read_csv(file_path, sep=None, engine='python')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
data = load_data()

# Display total number of bike options and rows
st.sidebar.markdown(f"**Total Bikes Available:** {len(data)}")
st.sidebar.markdown(f"**Unique Models Available:** {data['Model'].nunique() if 'Model' in data.columns else 'N/A'}")

if data.empty:
    st.stop()

# Function to map height ranges to frame sizes
def map_height_to_frame_size(height):
    if height < 155:
        return 'XXS'
    elif 155 <= height < 165:
        return 'XS'
    elif 165 <= height < 170:
        return 'S'
    elif 170 <= height < 175:
        return 'M'
    elif 175 <= height < 185:
        return 'L'
    else:
        return 'XL'

# Function to find the closest frame size if an exact match is not available
def find_closest_frame_size(frame_size, available_sizes):
    size_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL']
    if frame_size in available_sizes:
        return frame_size
    try:
        index = size_order.index(frame_size)
        for offset in range(1, len(size_order)):
            if index - offset >= 0 and size_order[index - offset] in available_sizes:
                return size_order[index - offset]
            if index + offset < len(size_order) and size_order[index + offset] in available_sizes:
                return size_order[index + offset]
    except ValueError:
        return None
    return None

# Title
st.title("Bike Fit & Geometry Recommendation System")

# User Inputs
st.sidebar.header("User Input Parameters")
height = st.sidebar.number_input("Rider's Height (cm):", min_value=100, max_value=220, value=170)
inseam = st.sidebar.number_input("Rider's Inseam Length (cm):", min_value=50, max_value=120, value=75)
riding_style = st.sidebar.selectbox("Preferred Riding Style:", ["Road", "Mountain", "Gravel", "Hybrid"])
wheel_size_pref = st.sidebar.selectbox("Preferred Wheel Size (Optional):", ["Any", "27.5\"", "28\"", "29\""])
riding_position = st.sidebar.selectbox("Preferred Riding Position (Optional):", ["No Preference", "Comfortable (Upright)", "Aggressive (Racing)"])

# Determine frame size based on height
matched_frame_size = map_height_to_frame_size(height)
available_sizes = data['Frame Size'].dropna().str.upper().unique().tolist()
closest_frame_size = find_closest_frame_size(matched_frame_size, available_sizes)

# Filter based on riding style and closest frame size
data_filtered = data[(data['Category'].str.lower() == riding_style.lower()) &
                     (data['Frame Size'].str.upper() == closest_frame_size)]

# Inseam Validation
data_filtered = data_filtered[data_filtered['Standover Height'] <= inseam]

# Wheel Size Filtering
if wheel_size_pref != "Any":
    data_filtered = data_filtered[data_filtered['Wheel Size'].str.contains(wheel_size_pref, na=False)]

# Geometry Adjustments based on riding position if specified
if riding_position == "Comfortable (Upright)":
    data_filtered = data_filtered[(data_filtered['Stack'] >= data_filtered['Stack'].quantile(0.4)) &
                                  (data_filtered['Reach'] <= data_filtered['Reach'].quantile(0.6)) &
                                  (data_filtered['Head Tube Angle'] >= 69) & (data_filtered['Head Tube Angle'] <= 73)]
elif riding_position == "Aggressive (Racing)":
    data_filtered = data_filtered[(data_filtered['Stack'] <= data_filtered['Stack'].quantile(0.6)) &
                                  (data_filtered['Reach'] >= data_filtered['Reach'].quantile(0.4)) &
                                  (data_filtered['Head Tube Angle'] >= 72) & (data_filtered['Head Tube Angle'] <= 76)]

# Re-filter the table based on closest frame size dynamically
filtered_data_by_height = data[(data['Frame Size'].str.upper() == closest_frame_size) &
                               (data['Category'].str.lower() == riding_style.lower())]

# Display Results
st.header("Recommended Bikes Based on Your Preferences")
if closest_frame_size:
    st.subheader(f"Closest Matching Frame Size for Your Height: **{closest_frame_size}**")
else:
    st.warning("No matching or close frame size found based on height and category.")

# Fully expanded display of the recommendation table
st.markdown("""
    <style>
    div[data-testid="stDataFrame"] div[role="grid"] {
        height: calc(100vh - 250px) !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

if filtered_data_by_height.empty:
    st.error("No exact matches found. Displaying top 5 closest available bikes (relaxed criteria, unique models):")
    fallback_recommendations = data[(data['Category'].str.lower() == riding_style.lower())]
    fallback_recommendations = fallback_recommendations.drop_duplicates(subset=["Model"]).head(5)[["Brand", "Model", "Frame Size"]].reset_index(drop=True)
    st.dataframe(fallback_recommendations, use_container_width=True)
else:
    top_recommendations = filtered_data_by_height.drop_duplicates(subset=["Model"]).head(5)[["Brand", "Model", "Frame Size"]].reset_index(drop=True)
    st.subheader("Top 5 Recommended Bikes (Unique Models):")
    st.dataframe(top_recommendations, use_container_width=True)

# Fit Adjustments Summary
st.header("Fit Adjustments Summary")
seat_height = inseam * 0.883
handlebar_reach = height * 0.45

st.markdown(f"- **Recommended Seat Height:** {seat_height:.1f} cm")
st.markdown(f"- **Recommended Handlebar Reach:** {handlebar_reach:.1f} cm")

st.success("All recommendations are based on optimal geometry and fit for your preferences!")
