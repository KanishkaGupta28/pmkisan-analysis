import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import json
import urllib.request

df = pd.read_csv("pmkisan_data.csv")

# ── State-level aggregation (since we don't have district shapefile) ──────
state_avg = df.groupby('State').agg({
    'Uptake_Pct': 'mean',
    'Gap_Farmers': 'sum',
    'Eligible_Farmers': 'sum',
    'Enrolled_Farmers': 'sum'
}).reset_index()
state_avg['Uptake_Pct'] = state_avg['Uptake_Pct'].round(1)

# ── Download India states GeoJSON ─────────────────────────────────────────
url = "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"
urllib.request.urlretrieve(url, "india_states.geojson")

# ── Build Folium Choropleth Map ───────────────────────────────────────────
m = folium.Map(location=[22, 82], zoom_start=5, tiles='CartoDB positron')

folium.Choropleth(
    geo_data="india_states.geojson",
    name="PM-KISAN Uptake",
    data=state_avg,
    columns=["State", "Uptake_Pct"],
    key_on="feature.properties.NAME_1",
    fill_color="RdYlGn",
    fill_opacity=0.8,
    line_opacity=0.3,
    legend_name="PM-KISAN Uptake (%)",
    nan_fill_color="lightgray",
).add_to(m)

# Add tooltips
folium.GeoJson(
    "india_states.geojson",
    style_function=lambda x: {'fillOpacity': 0, 'weight': 0},
    tooltip=folium.GeoJsonTooltip(fields=['NAME_1'], aliases=['State:'])
).add_to(m)

# Add markers for bottom 10 districts
bottom10 = df.nsmallest(10, 'Uptake_Pct')
state_coords = {
    "Jharkhand": [23.6, 85.2], "Bihar": [25.09, 85.3],
    "Odisha": [20.9, 84.8], "Rajasthan": [27.02, 74.2],
    "Uttar Pradesh": [26.8, 80.9], "West Bengal": [22.9, 87.8],
    "Maharashtra": [19.7, 75.7], "Madhya Pradesh": [22.9, 78.6]
}

for _, row in bottom10.iterrows():
    coords = state_coords.get(row['State'], [22, 82])
    coords = [coords[0] + np.random.uniform(-1, 1),
              coords[1] + np.random.uniform(-1, 1)]
    folium.CircleMarker(
        location=coords,
        radius=10,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{row['District']}, {row['State']}</b><br>"
            f"Uptake: {row['Uptake_Pct']}%<br>"
            f"Gap: {row['Gap_Farmers']:,} farmers",
            max_width=200
        ),
        tooltip=f"{row['District']}: {row['Uptake_Pct']}%"
    ).add_to(m)

folium.LayerControl().add_to(m)
m.save("outputs/india_pmkisan_map.html")
print(" Choropleth map saved: outputs/india_pmkisan_map.html")
print("Open this file in your browser to see the map!")