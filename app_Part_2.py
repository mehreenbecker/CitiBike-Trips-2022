import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from numerize.numerize import numerize
import streamlit.components.v1 as components

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="NYC Citi Bike Dashboard (2022)", layout="wide")

# ----------------------------
# Paths
# ----------------------------
DATA_PROCESSED = Path("data_processed")
SAMPLE_PATH = Path("df_sample_seed32.csv")
TOP_STATIONS_PATH = DATA_PROCESSED / "top_20_stations.csv"  # adjust if yours is elsewhere
KEPLER_HTML = Path("kepler_od_map.html")  # adjust if named differently

# ----------------------------
# Cached loaders
# ----------------------------
@st.cache_data
def load_daily():
    weather = pd.read_csv(DATA_PROCESSED / "weather_lga_2022.csv")
    daily = pd.read_csv(DATA_PROCESSED / "daily_citibike_2022.csv")

    weather["date"] = pd.to_datetime(weather["date"])
    daily["date"] = pd.to_datetime(daily["date"])

    df = weather.merge(daily, on="date", how="left")
    df["trip_count"] = df["trip_count"].fillna(0).astype(int)
    df["TAVG_C"] = df["TAVG"] / 10
    return df.sort_values("date")

@st.cache_data
def load_sample():
    df = pd.read_csv(SAMPLE_PATH, low_memory=False)
    df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
    df["ended_at"] = pd.to_datetime(df["ended_at"], errors="coerce")
    df["duration_min"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
    df["month"] = df["started_at"].dt.month
    return df

@st.cache_data
def load_top_stations():
    return pd.read_csv(TOP_STATIONS_PATH)

df_daily = load_daily()
df_sample = load_sample() if SAMPLE_PATH.exists() else None
top_stations = load_top_stations() if TOP_STATIONS_PATH.exists() else None

# ----------------------------
# Sidebar pages
# ----------------------------
page = st.sidebar.selectbox(
    "Choose a page",
    [
        "Intro",
        "Trips vs Temperature",
        "Popular Stations",
        "OD Map (Kepler)",
        "Extra Insight",
        "Recommendations",
    ],
)

# ----------------------------
# Intro page
# ----------------------------
if page == "Intro":
    st.title("NYC Citi Bike Supply & Demand Dashboard (2022)")
    st.write(
        "This dashboard analyzes Citi Bike trip patterns in 2022 and links demand to daily weather conditions from NOAA. "
        "The goal is to identify seasonality, high-demand stations, and major travel corridors to support decisions about "
        "bike rebalancing and station placement."
    )

    st.markdown("### Data Sources")
    st.markdown(
        "- **Citi Bike trip data (2022)**: trip records including station information\n"
        "- **NOAA daily weather** (LGA area): temperature, precipitation, wind\n"
        "- **Derived metrics**: daily trip counts, most popular stations, OD flows"
    )

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trips (2022)", numerize(int(df_daily["trip_count"].sum())))
    c2.metric("Peak Daily Trips", numerize(int(df_daily["trip_count"].max())))
    c3.metric("Avg Temp (°C)", f"{df_daily['TAVG_C'].mean():.1f}")

    st.markdown("---")
    st.write("Use the sidebar to navigate between pages.")

# ----------------------------
# Trips vs Temperature page
# ----------------------------
elif page == "Trips vs Temperature":
    st.title("Trips vs Temperature (Seasonality)")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_daily["date"], y=df_daily["trip_count"], name="Trip count", mode="lines"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_daily["date"], y=df_daily["TAVG_C"], name="Avg temp (°C)", mode="lines"), secondary_y=True)

    fig.update_layout(
        height=500,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        title="Daily Citi Bike Trips vs Average Temperature (2022)",
        title_x=0.02,
    )
    fig.update_yaxes(title_text="Trips", secondary_y=False)
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Interpretation")
    st.write(
        "Trip volume shows a strong seasonal pattern: demand increases during warmer months and drops during colder periods. "
        "The relationship between temperature and ridership suggests that rebalancing and staffing needs should be scaled up "
        "in late spring and summer, while demand and operational pressure are lower in winter."
    )

# ----------------------------
# Popular Stations page
# ----------------------------
elif page == "Popular Stations":
    st.title("Most Popular Starting Stations")

    if top_stations is None:
        st.warning("Top stations file not found. Save top_20_stations.csv into data_processed/")
    else:
        fig_bar = px.bar(
            top_stations.sort_values("trip_count"),
            x="trip_count",
            y="start_station_name",
            orientation="h",
            title="Top 20 Starting Stations (2022)",
            labels={"trip_count": "Trips", "start_station_name": "Starting station"},
        )
        fig_bar.update_layout(height=650, margin=dict(l=20, r=20, t=60, b=20), title_x=0.02)
        fig_bar.update_traces(hovertemplate="<b>%{y}</b><br>Trips: %{x:,}<extra></extra>")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### Interpretation")
        st.write(
            "A relatively small set of stations accounts for a large share of trips, indicating that demand is concentrated "
            "around key commuting and destination hubs. These high-demand stations are strong candidates for frequent rebalancing "
            "and increased dock capacity to reduce shortages during peak periods."
        )

# ----------------------------
# Kepler map page
# ----------------------------
elif page == "OD Map (Kepler)":
    st.title("Origin–Destination Flows (Kepler.gl)")

    if KEPLER_HTML.exists():
        html = KEPLER_HTML.read_text(encoding="utf-8")
        components.html(html, height=700, scrolling=True)

        st.markdown("### Interpretation")
        st.write(
            "The OD map highlights the most common station-to-station flows, revealing corridors and clusters of repeated trips. "
            "Dense activity zones suggest where bike supply constraints are most likely (e.g., business districts, waterfront routes, "
            "and transit-adjacent areas). These clusters can guide targeted rebalancing and future station expansion."
        )
    else:
        st.warning("Kepler HTML file not found. Export your map to kepler_od_map.html and place it next to this script.")

# ----------------------------
# Extra Insight page (your “stand out” chart)
# ----------------------------
elif page == "Extra Insight":
    st.title("Extra Insight: Trip Duration by Rider Type")

    if df_sample is None:
        st.warning("Sample file df_sample_seed32.csv not found in project root.")
    else:
        # Filter out extreme durations for readability
        df_plot = df_sample[(df_sample["duration_min"] > 0) & (df_sample["duration_min"] < 180)].copy()

        fig_box = px.box(
            df_plot,
            x="member_casual",
            y="duration_min",
            title="Trip Duration by Rider Type (Sample)",
            labels={"member_casual": "Rider type", "duration_min": "Duration (minutes)"},
        )
        fig_box.update_layout(height=500, margin=dict(l=20, r=20, t=60, b=20), title_x=0.02)
        st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("### Interpretation")
        st.write(
            "Casual riders typically show longer and more variable trip durations, which aligns with recreational usage. "
            "Members tend to have shorter, more consistent trips, which supports the idea that many member rides reflect commuting. "
            "This distinction can help prioritize where and when to rebalance bikes (commuter hubs vs leisure areas)."
        )

# ----------------------------
# Recommendations page
# ----------------------------
elif page == "Recommendations":
    st.title("Recommendations")

    st.markdown("### Operational Recommendations")
    st.write(
        "- **Seasonal rebalancing:** Increase rebalancing frequency in late spring–summer when demand peaks; reduce during winter.\n"
        "- **Priority stations:** Treat the top stations as critical nodes—add dock capacity and ensure rapid restocking.\n"
        "- **Corridor focus:** Use OD flows to identify repeat corridors and schedule rebalancing around peak commuter times.\n"
        "- **Waterfront expansion:** High activity along waterfront routes suggests that adding stations/docks there can reduce shortages.\n"
    )

    st.markdown("### What to do next")
    st.write(
        "A next step would be to quantify shortages by station (if availability data is available) and build a predictive model "
        "using weather + seasonality to anticipate demand surges and proactively rebalance bikes."
    )