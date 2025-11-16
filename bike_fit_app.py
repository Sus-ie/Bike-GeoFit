import os

import pandas as pd
import streamlit as st

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

required_columns = [
    "Model",
    "Brand",
    "Category",
    "Frame Size",
    "Standover Height",
    "Wheel Size",
    "Stack",
    "Reach",
    "Head Tube Angle",
]
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    st.error(
        "The dataset is missing required columns: "
        + ", ".join(missing_columns)
        + ". Please update the CSV schema to include them."
    )
    st.stop()

# Normalize frequently used text columns once for consistent filtering
data['Frame Size Norm'] = data['Frame Size'].astype(str).str.upper().str.strip()
data['Category Norm'] = data['Category'].astype(str).str.lower().str.strip()
data['Wheel Size Norm'] = data['Wheel Size'].astype(str).str.replace("\"", "", regex=False)
data['Wheel Size Norm'] = data['Wheel Size Norm'].str.lower().str.strip()


# Show total number of bike options and rows
st.sidebar.markdown(f"**Total Bikes Available:** {len(data)}")
st.sidebar.markdown(f"**Unique Models Available:** {data['Model'].nunique() if 'Model' in data.columns else 'N/A'}")

if data.empty:
    st.stop()

# Map out height ranges to frame sizes
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

# Try to find the closest frame size if there is no exact match
def find_closest_frame_size(frame_size, available_sizes):
    size_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL']
    if frame_size in available_sizes:
        return frame_size
    try:
        target_index = size_order.index(frame_size)
        # Prefer slight downsizing before upsizing when equidistant to respect standover needs
        candidates = sorted(
            (
                (abs(target_index - size_order.index(size)), size_order.index(size), size)
                for size in available_sizes
                if size in size_order
            ),
            key=lambda item: (item[0], item[1]),
        )
        return candidates[0][2] if candidates else None
    except ValueError:
        return None

# App Starts
st.title("Bike Fit & Geometry Recommendation System")

# User input
st.sidebar.header("User Input Parameters")
height = st.sidebar.number_input("Rider's Height (cm):", min_value=100, max_value=220, value=170)
inseam = st.sidebar.number_input("Rider's Inseam Length (cm):", min_value=50, max_value=120, value=75)
riding_style = st.sidebar.selectbox("Preferred Riding Style:", ["Road", "Mountain", "Gravel", "Hybrid"])
wheel_size_pref = st.sidebar.selectbox("Preferred Wheel Size (Optional):", ["Any", "27.5\"", "28\"", "29\""])
riding_position = st.sidebar.selectbox("Preferred Riding Position (Optional):", ["No Preference", "Comfortable (Upright)", "Aggressive (Racing)"])
upright_stack_quantile = st.sidebar.slider(
    "Upright position stack lower quantile",
    min_value=0.2,
    max_value=0.8,
    value=0.4,
    step=0.05,
)
upright_reach_quantile = st.sidebar.slider(
    "Upright position reach upper quantile",
    min_value=0.2,
    max_value=0.8,
    value=0.6,
    step=0.05,
)
aggressive_stack_quantile = st.sidebar.slider(
    "Aggressive position stack upper quantile",
    min_value=0.2,
    max_value=0.8,
    value=0.6,
    step=0.05,
)
aggressive_reach_quantile = st.sidebar.slider(
    "Aggressive position reach lower quantile",
    min_value=0.2,
    max_value=0.8,
    value=0.4,
    step=0.05,
)

st.sidebar.caption(
    "Geometry filters use dataset quantiles; adjust sliders to broaden or tighten upright/" "aggressive fits."
)

#  frame size based on height
matched_frame_size = map_height_to_frame_size(height)
available_sizes = data['Frame Size Norm'].dropna().unique().tolist()
closest_frame_size = find_closest_frame_size(matched_frame_size, available_sizes)

# Filter based on riding style and closest frame size
category_mask = data['Category Norm'].str.contains(riding_style.lower(), na=False)
data_filtered = data[category_mask].copy()

if closest_frame_size:
    data_filtered = data_filtered[data_filtered['Frame Size Norm'] == closest_frame_size]
else:
    st.warning("No matching or close frame size found based on height and category.")

# Standover clearance: require at least 2 cm of clearance when possible
standover_limit = max(inseam - 2, 0)
data_filtered = data_filtered[data_filtered['Standover Height'] <= standover_limit]
if data_filtered.empty:
    st.info(
        "All options were filtered out by standover clearance (inseam minus 2 cm). "
        "Consider a smaller frame size or increasing the allowed clearance."
    )

# Wheel Size
if wheel_size_pref != "Any":
    wheel_norm = wheel_size_pref.replace("\"", "").lower()
    data_filtered = data_filtered[data_filtered['Wheel Size Norm'].str.contains(wheel_norm, na=False)]
    if data_filtered.empty:
        st.info("No bikes matched the selected wheel size. Try choosing 'Any'.")

# Geometry Adjustments based on riding position if specified
if riding_position == "Comfortable (Upright)":
    stack_cut = data['Stack'].quantile(upright_stack_quantile)
    reach_cut = data['Reach'].quantile(upright_reach_quantile)
    data_filtered = data_filtered[(data_filtered['Stack'] >= stack_cut) &
                                  (data_filtered['Reach'] <= reach_cut) &
                                  (69 <= data_filtered['Head Tube Angle']) & (data_filtered['Head Tube Angle'] <= 73)]
    if data_filtered.empty:
        st.info("No upright matches at this strictness. Try lowering the stack quantile or raising the reach quantile.")
elif riding_position == "Aggressive (Racing)":
    stack_cut = data['Stack'].quantile(aggressive_stack_quantile)
    reach_cut = data['Reach'].quantile(aggressive_reach_quantile)
    data_filtered = data_filtered[(data_filtered['Stack'] <= stack_cut) &
                                  (data_filtered['Reach'] >= reach_cut) &
                                  (72 <= data_filtered['Head Tube Angle']) & (data_filtered['Head Tube Angle'] <= 76)]
    if data_filtered.empty:
        st.info("No aggressive matches at this strictness. Try raising the stack quantile or lowering the reach quantile.")

# Show results
st.header("Recommended Bikes Based on Your Preferences")
if closest_frame_size:
    st.subheader(f"Closest Matching Frame Size for Your Height: **{closest_frame_size}**")
else:
    st.warning("No matching or close frame size found based on height and category.")

# Fully expanded display 
st.markdown("""
    <style>
    div[data-testid="stDataFrame"] div[role="grid"] {
        height: calc(100vh - 250px) !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

if data_filtered.empty:
    st.error("No bikes match all selected filters. Showing the closest available options in your category instead.")
    fallback_recommendations = data[category_mask]
    fallback_recommendations = fallback_recommendations.drop_duplicates(subset=["Model"]).head(5)[["Brand", "Model", "Frame Size"]].reset_index(drop=True)
    st.dataframe(fallback_recommendations, use_container_width=True)
else:
    top_recommendations = data_filtered.drop_duplicates(subset=["Model"]).head(5)[["Brand", "Model", "Frame Size"]].reset_index(drop=True)
    st.subheader("Top 5 Recommended Bikes (Unique Models):")
    st.dataframe(top_recommendations, use_container_width=True)

# Fit Adjustments Summary
st.header("Fit Adjustments Summary")
seat_height = inseam * 0.883
handlebar_reach = height * 0.45

st.markdown(f"- **Recommended Seat Height:** {seat_height:.1f} cm (0.883 × inseam)")
st.markdown(f"- **Recommended Handlebar Reach:** {handlebar_reach:.1f} cm (~45% of rider height)")
st.caption("Consider a comfort range of ±1–2 cm to account for personal preference and setup.")

st.success("All recommendations are based on optimal geometry and fit for your preferences!")
