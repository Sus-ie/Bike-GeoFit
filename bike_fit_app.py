import streamlit as st
import pandas as pd
import numpy as np

# Load the dataset
@st.cache_data
def load_data():
    file_path = '/Users/susanakohlhaas/Documents/IronHack/Final Project/geometrics_modifiedv3.csv'
    return pd.read_csv(file_path, sep=None, engine='python')

data = load_data()

# Helper function to match the closest frame size
def closest_frame_size(frame_size, available_sizes):
    size_mapping = {'XXS': 1, 'XS': 2, 'S': 3, 'M': 4, 'L': 5, 'XL': 6}
    available_numeric = [size_mapping.get(size, np.nan) for size in available_sizes if size in size_mapping]
    if np.isnan(frame_size) or not available_numeric:
        return None
    closest_index = np.abs(np.array(available_numeric) - frame_size).argmin()
    return available_sizes[closest_index]

# Title
st.title("🚴‍♂️ Bike Fit & Geometry Recommendation System")

# User Inputs
st.sidebar.header("User Input Parameters")
height = st.sidebar.number_input("Rider's Height (cm):", min_value=100, max_value=220, value=170)
inseam = st.sidebar.number_input("Rider's Inseam Length (cm):", min_value=50, max_value=120, value=75)
riding_style = st.sidebar.selectbox("Preferred Riding Style:", ["Road", "Mountain", "Gravel", "Hybrid"])
wheel_size_pref = st.sidebar.selectbox("Preferred Wheel Size (Optional):", ["Any", "27.5\"", "28\"", "29\""])

# Frame Size Calculation
if riding_style == "Road":
    calc_frame_size = height * 0.665
elif riding_style == "Mountain":
    calc_frame_size = height * 0.225
else:
    calc_frame_size = height * 0.685

# Filter based on riding style
data_filtered = data[data['Category'].str.lower() == riding_style.lower()]

# Match closest frame size
available_sizes = data_filtered['Frame Size'].dropna().unique().tolist()
matched_frame_size = closest_frame_size(calc_frame_size / 10, available_sizes)  # Adjust for dataset scaling

# Inseam Validation
data_filtered = data_filtered[data_filtered['Standover Height'] <= (inseam - 2)]

# Wheel Size Filtering
if wheel_size_pref != "Any":
    data_filtered = data_filtered[data_filtered['Wheel Size'].str.contains(wheel_size_pref, na=False)]

# Stack-to-Reach Ratio Calculation
data_filtered['STR Ratio'] = data_filtered.apply(lambda x: x['Stack'] / x['Reach'] if x['Reach'] > 0 else np.nan, axis=1)
data_filtered = data_filtered[(data_filtered['STR Ratio'] >= 1.4) & (data_filtered['STR Ratio'] <= 1.6)]

# Geometry Adjustments
riding_position = st.sidebar.selectbox("Preferred Riding Position:", ["Comfortable (Upright)", "Aggressive (Racing)"])

if riding_position == "Comfortable (Upright)":
    data_filtered = data_filtered[(data_filtered['Stack'] >= data_filtered['Stack'].median()) &
                                  (data_filtered['Reach'] <= data_filtered['Reach'].median()) &
                                  (data_filtered['Head Tube Angle'] >= 70) & (data_filtered['Head Tube Angle'] <= 72)]
else:
    data_filtered = data_filtered[(data_filtered['Stack'] <= data_filtered['Stack'].median()) &
                                  (data_filtered['Reach'] >= data_filtered['Reach'].median()) &
                                  (data_filtered['Head Tube Angle'] >= 73) & (data_filtered['Head Tube Angle'] <= 75)]

# Display Results
st.header("📋 Recommended Bikes Based on Your Preferences")
if matched_frame_size:
    st.subheader(f"✅ Best Frame Size for Your Height: **{matched_frame_size}**")
else:
    st.warning("⚠️ No matching frame size found based on height and category.")

if data_filtered.empty:
    st.error("🚫 No suitable bikes found based on your selected parameters.")
else:
    st.dataframe(data_filtered[["Brand", "Model", "Frame Size", "Category", "Wheel Size", "Reach", "Stack", "Head Tube Angle", "Standover Height", "Wheelbase"]].reset_index(drop=True))

# Fit Adjustments Summary
st.header("🔧 Fit Adjustments Summary")
seat_height = inseam * 0.883
handlebar_reach = height * 0.45

st.markdown(f"- **Recommended Seat Height:** {seat_height:.1f} cm")
st.markdown(f"- **Recommended Handlebar Reach:** {handlebar_reach:.1f} cm")

st.success("🎉 All recommendations are based on optimal geometry and fit for your preferences!")
