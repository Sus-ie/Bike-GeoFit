import streamlit as st
import pandas as pd

# Field Name: Bike Fit Calculator
# About: A Streamlit app that helps users find the best bike fit based on their height, inseam length, and riding style.
# Author: Susana Kohlhaas
# Date: 17.Feb 2025
# License: MIT
# Description:
# This app loads bicycle geometry data from "geometrics.mtb-news.de.csv" and calculates
# the best frame size recommendation based on user input. It filters bikes based on
# standover height, stack-to-reach ratio, and optional wheel size preference.
# The final list of recommended bikes is displayed in a structured table.

# Load dataset
df = pd.read_csv("geometrics.mtb-news.de.csv")

# Streamlit App Title
st.title("Bike Fit Calculator")

# User Inputs
st.header("Rider Information")

# Input: Rider Height
rider_height = st.number_input("Enter your height (cm):", min_value=100, max_value=220, value=170)

# Input: Inseam Length
inseam_length = st.number_input("Enter your inseam length (cm):", min_value=50, max_value=120, value=80)

# Input: Riding Style
bike_type = st.selectbox("Select your riding style:", df['Category'].unique())

# Input: Preferred Wheel Size (optional)
wheel_size_pref = st.selectbox("Preferred Wheel Size (optional):", ["Any"] + list(df['Wheel Size'].unique()))

# Frame Size Calculation Based on Riding Style
if bike_type == "Road":
    frame_size = rider_height * 0.665  # Road bikes use a higher multiplier for frame size
elif bike_type == "Mountain":
    frame_size = rider_height * 0.225  # Mountain bikes have smaller frames
elif bike_type in ["Gravel", "Hybrid"]:
    frame_size = rider_height * 0.685  # Gravel/Hybrid bikes are slightly larger than road bikes
else:
    frame_size = rider_height * 0.6  # Default multiplier if unknown category

# Filter dataset based on user-selected riding style
df_filtered = df[df['Category'] == bike_type]

# Calculate the difference between the calculated frame size and available frame sizes
df_filtered['Frame Size Difference'] = abs(df_filtered['Frame Size'] - frame_size)

# Find the closest matching frame size
best_frame = df_filtered.sort_values('Frame Size Difference').iloc[0]

# Standover Height Validation - Ensures bike's standover height is within 2cm of inseam length
df_filtered = df_filtered[df_filtered['Standover Height'] <= (inseam_length - 2)]

# Stack-to-Reach Ratio Calculation - Ideal range for comfort and efficiency
df_filtered['STR Ratio'] = df_filtered['Stack'] / df_filtered['Reach']
df_filtered = df_filtered[(df_filtered['STR Ratio'] >= 1.4) & (df_filtered['STR Ratio'] <= 1.6)]

# Apply Wheel Size Filtering (if specified)
if wheel_size_pref != "Any":
    df_filtered = df_filtered[df_filtered['Wheel Size'] == wheel_size_pref]

# Display Recommended Bikes
st.header("Recommended Bikes")

if not df_filtered.empty:
    st.dataframe(df_filtered[['Frame Size', 'Category', 'Wheel Size', 'Standover Height', 'Reach', 'Stack',
                              'Head Tube Angle', 'Seat Tube Angle Effective', 'Top Tube Length',
                              'Chainstay Length', 'Wheelbase', 'Bottom Bracket Height',
                              'Fork Offset', 'Fork Trail', 'Suspension Travel (front)', 'Suspension Travel (rear)']])
else:
    st.write("No suitable bikes found based on the given criteria. Try adjusting your preferences.")
