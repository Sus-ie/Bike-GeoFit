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
data_filtered = data_filtered[data_filtered['Standover Height'] <= (inseam - 2)]

# Wheel Size Filtering
if wheel_size_pref != "Any":
    data_filtered = data_filtered[data_filtered['Wheel Size'].str.contains(wheel_size_pref, na=False)]

# Stack-to-Reach Ratio Calculation
data_filtered['STR Ratio'] = data_filtered.apply(lambda x: x['Stack'] / x['Reach'] if x['Reach'] > 0 else np.nan, axis=1)
data_filtered = data_filtered[(data_filtered['STR Ratio'] >= 1.4) & (data_filtered['STR Ratio'] <= 1.6)]

# Geometry Adjustments based on riding position if specified
if riding_position == "Comfortable (Upright)":
    data_filtered = data_filtered[(data_filtered['Stack'] >= data_filtered['Stack'].median()) &
                                  (data_filtered['Reach'] <= data_filtered['Reach'].median()) &
                                  (data_filtered['Head Tube Angle'] >= 70) & (data_filtered['Head Tube Angle'] <= 72)]
elif riding_position == "Aggressive (Racing)":
    data_filtered = data_filtered[(data_filtered['Stack'] <= data_filtered['Stack'].median()) &
                                  (data_filtered['Reach'] >= data_filtered['Reach'].median()) &
                                  (data_filtered['Head Tube Angle'] >= 73) & (data_filtered['Head Tube Angle'] <= 75)]

# Display Results
st.header("Recommended Bikes Based on Your Preferences")
if closest_frame_size:
    st.subheader(f"Closest Matching Frame Size for Your Height: **{closest_frame_size}**")
else:
    st.warning("No matching or close frame size found based on height and category.")

if data_filtered.empty:
    st.error("No exact matches found. Displaying top 3 closest available bikes:")
    fallback_recommendations = data[(data['Category'].str.lower() == riding_style.lower())].head(3)[["Brand", "Model", "Frame Size"]].reset_index(drop=True)
    st.dataframe(fallback_recommendations)
else:
    top_recommendations = data_filtered[["Brand", "Model", "Frame Size"]].head(3).reset_index(drop=True)
    st.subheader("Top 3 Recommended Bikes:")
    st.dataframe(top_recommendations)

# Fit Adjustments Summary
st.header("Fit Adjustments Summary")
seat_height = inseam * 0.883
handlebar_reach = height * 0.45

st.markdown(f"- **Recommended Seat Height:** {seat_height:.1f} cm")
st.markdown(f"- **Recommended Handlebar Reach:** {handlebar_reach:.1f} cm")

st.success("All recommendations are based on optimal geometry and fit for your preferences!")
