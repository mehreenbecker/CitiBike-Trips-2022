# CitiBike-Trips-2022
# 🚲 NYC Citi Bike Supply & Demand Analysis (2022)

## 📊 Project Overview

This project analyzes New York City's Citi Bike trip data from 2022 and integrates NOAA daily weather data to explore seasonal trends, station demand, and origin–destination patterns.

The goal of this dashboard is to support operational decisions regarding:

- Seasonal fleet scaling
- Station rebalancing
- Dock capacity expansion
- Waterfront station planning

The project culminates in a multi-page Streamlit dashboard presenting actionable insights.

---

## 📁 Repository Structure

Large raw datasets are excluded from the repository to comply with file size limits.

---

## 📈 Dashboard Pages

The Streamlit dashboard includes:

### 1️⃣ Intro Page
Overview of the dataset, KPIs, and project objectives.

### 2️⃣ Trips vs Temperature
Dual-axis line chart showing seasonal ridership trends and weather correlation.

### 3️⃣ Popular Stations
Bar chart of the top 20 starting stations highlighting demand concentration.

### 4️⃣ Origin–Destination Map
Interactive Kepler.gl visualization of trip corridors and clustering.

### 5️⃣ Additional Insights
Trip duration analysis by rider type (member vs casual).

### 6️⃣ Recommendations
Strategic suggestions for supply scaling, rebalancing, and station expansion.

---

## 🔍 Key Insights

- Strong seasonality: peak ridership during warmer months.
- Demand is concentrated in a relatively small set of high-traffic stations.
- Waterfront corridors show consistent and dense trip flows.
- Member riders exhibit shorter, commuter-like trips; casual riders show longer recreational patterns.

---

## 🚀 How to Run Locally

1. Clone the repository:
git clone https://github.com/mehreenbecker/CitiBike-Trips-2022.git
cd CitiBike-Trips-2022

2. Create and activate a virtual environment:
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Run the dashboard:
streamlit run app_Part_2.py

---

## 🌐 Live Dashboard

[Add your Streamlit Cloud link here once deployed]

---

## 📊 Data Sources

- NYC Citi Bike Trip Data (2022)
- NOAA Weather Data (LGA station)

---

## 👩‍💻 Author

Mehreen Werth  
Data Analytics & Visualization Project

