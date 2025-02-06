import streamlit as st
import pandas as pd

# Load dataset
df = pd.read_csv("geometrics.mtb-news.de.csv")

# Streamlit App Title
st.title("Bike Fit Calculator")

# User Inputs
st.header("Rider Information")
rider_height = st.number_input("Enter your height (cm):", min_value=100, max_value=220, value=170)

inseam_length = st.number_input("Enter your inseam length (cm):", min_value=50, max_value=120, value=80)

bike_type = st.selectbox("Select your riding style:", df['Category'].unique())

wheel_size_pref = st.selectbox("Preferred Wheel Size (optional):", ["Any"] + list(df['Wheel Size'].unique()))

# Frame Size Calculation
if bike_type == "Road":
    frame_size = rider_height * 0.665
elif bike_type == "Mountain":
    frame_size = rider_height * 0.225
elif bike_type == "Gravel" or bike_type == "Hybrid":
    frame_size = rider_height * 0.685
else:
    frame_size = rider_height * 0.6  # Default multiplier if unknown category

# Closest frame size match
df_filtered = df[df['Category'] == bike_type]
df_filtered['Frame Size Difference'] = abs(df_filtered['Frame Size'] - frame_size)
best_frame = df_filtered.sort_values('Frame Size Difference').iloc[0]

# Standover Height Validation
df_filtered = df_filtered[df_filtered['Standover Height'] <= (inseam_length - 2)]

# Stack-to-Reach Ratio Calculation
df_filtered['STR Ratio'] = df_filtered['Stack'] / df_filtered['Reach']
df_filtered = df_filtered[(df_filtered['STR Ratio'] >= 1.4) & (df_filtered['STR Ratio'] <= 1.6)]

# Wheel Size Filtering (if specified)
if wheel_size_pref != "Any":
    df_filtered = df_filtered[df_filtered['Wheel Size'] == wheel_size_pref]

# Display Recommendations
st.header("Recommended Bikes")
if not df_filtered.empty:
    st.dataframe(df_filtered[['Frame Size', 'Category', 'Wheel Size', 'Standover Height', 'Reach', 'Stack', 'Head Tube Angle', 'Seat Tube Angle Effective', 'Top Tube Length', 'Chainstay Length', 'Wheelbase', 'Bottom Bracket Height', 'Fork Offset', 'Fork Trail', 'Suspension Travel (front)', 'Suspension Travel (rear)']])
else:
    st.write("No suitable bikes found based on the given criteria. Try adjusting your preferences.")
