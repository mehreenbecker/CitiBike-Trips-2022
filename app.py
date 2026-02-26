import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from numerize.numerize import numerize
import streamlit.components.v1 as components

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Citi Bike + Weather Dashboard (2022)",
    layout="wide"
)

st.title("Citi Bike Usage & Weather Dashboard (2022)")
st.write(
    "This dashboard explores Citi Bike trip activity in NYC during 2022 "
    "and its relationship with daily weather conditions from NOAA."
)

# ----------------------------
# Load data
# ----------------------------
DATA_DIR = Path("data_processed")

@st.cache_data
def load_data():
    weather = pd.read_csv(DATA_DIR / "weather_lga_2022.csv")
    daily = pd.read_csv(DATA_DIR / "daily_citibike_2022.csv")

    weather["date"] = pd.to_datetime(weather["date"])
    daily["date"] = pd.to_datetime(daily["date"])

    df = weather.merge(daily, on="date", how="left")
    df["trip_count"] = df["trip_count"].fillna(0).astype(int)

    # NOAA temp is tenths °C
    df["TAVG_C"] = df["TAVG"] / 10

    return df.sort_values("date")

df_daily = load_data()

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Trips (2022)", numerize(int(df_daily["trip_count"].sum())))
col2.metric("Peak Daily Trips", numerize(int(df_daily["trip_count"].max())))
col3.metric("Average Temp (°C)", f"{df_daily['TAVG_C'].mean():.1f}")

st.markdown("---")

# ----------------------------
# Plot 1: Popular Stations
# ----------------------------
st.subheader("Most Popular Starting Stations")

# Load precomputed top stations file
# (If you saved one earlier, otherwise compute in notebook and export small CSV)
try:
    top_stations = pd.read_csv("data/top_20_stations.csv")
except:
    st.warning("No precomputed top stations file found. Please create and save top_20_stations.csv in /data.")
    top_stations = None

if top_stations is not None:

    fig_bar = px.bar(
        top_stations.sort_values("trip_count"),
        x="trip_count",
        y="start_station_name",
        orientation="h",
        title="Top 20 Starting Stations (2022)",
        labels={"trip_count": "Trips", "start_station_name": "Starting Station"},
    )

    fig_bar.update_layout(
        height=650,
        margin=dict(l=20, r=20, t=60, b=20),
        title_x=0.02,
    )

    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>Trips: %{x:,}<extra></extra>"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ----------------------------
# Plot 2: Dual-axis line chart
# ----------------------------
st.subheader("Daily Trips vs Temperature")

fig_dual = make_subplots(specs=[[{"secondary_y": True}]])

fig_dual.add_trace(
    go.Scatter(
        x=df_daily["date"],
        y=df_daily["trip_count"],
        name="Trip Count",
        mode="lines"
    ),
    secondary_y=False,
)

fig_dual.add_trace(
    go.Scatter(
        x=df_daily["date"],
        y=df_daily["TAVG_C"],
        name="Average Temp (°C)",
        mode="lines"
    ),
    secondary_y=True,
)

fig_dual.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=60, b=20),
    hovermode="x unified",
    title="Daily Citi Bike Trips vs Average Temperature (2022)",
    title_x=0.02,
)

fig_dual.update_yaxes(title_text="Trips", secondary_y=False)
fig_dual.update_yaxes(title_text="Temperature (°C)", secondary_y=True)

st.plotly_chart(fig_dual, use_container_width=True)

st.markdown("---")

# ----------------------------
# Kepler Map Embed
# ----------------------------
st.subheader("Origin-Destination Map (Kepler.gl)")

html_path = Path("kepler_od_map.html")  # Make sure this file exists in project root

if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")
    components.html(html_content, height=650, scrolling=True)
else:
    st.warning("Kepler HTML map file not found. Please place it in the project root.")