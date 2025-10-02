# backend/features/geospatial_analysis.py

import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster

class GeoSpatialAnalyser:
    def get_color(self, level):
        if level == 'Perfect' or level == 'Good':
            return 'green'
        elif level == 'Moderate':
            return 'orange'
        elif level == 'Poor':
            return 'red'
        elif level == 'Very Poor':
            return 'darkred'
        else: # Extremely Poor
            return 'black'

    def geospatial_analysis(self, df):
        # *** FIX: Make column name check case-insensitive ***
        df.columns = [str(c).capitalize() for c in df.columns]

        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            return "<p>Error: Data does not contain 'Latitude' and 'Longitude' columns.</p>"
        
        # Drop rows where lat/lon are missing or invalid
        df_geo = df.dropna(subset=['Latitude', 'Longitude', 'Hmpi'])
        df_geo = df_geo[pd.to_numeric(df_geo['Latitude'], errors='coerce').notna()]
        df_geo = df_geo[pd.to_numeric(df_geo['Longitude'], errors='coerce').notna()]
        
        if df_geo.empty:
            return "<p>Error: No valid geospatial data to display.</p>"

        map_center = [df_geo['Latitude'].mean(), df_geo['Longitude'].mean()]
        
        m = folium.Map(location=map_center, zoom_start=8)

        folium.TileLayer(
            tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            overlay=False,
            control=True,
            subdomains=['mt0', 'mt1', 'mt2', 'mt3']
        ).add_to(m)

        folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)

        heat_data = [[row['Latitude'], row['Longitude'], row['Hmpi']] for index, row in df_geo.iterrows()]
        HeatMap(heat_data, name="HMPI Heatmap", radius=15).add_to(m)

        marker_cluster = MarkerCluster(name="Pollution Stations").add_to(m)
        for idx, row in df_geo.iterrows():
            popup_html = f"""
            <b>Location:</b> {row.get('Station name', 'N/A')}<br>
            <b>HMPI:</b> {row['Hmpi']:.2f}<br>
            <b style='color:{self.get_color(row['Pollution level'])};'>Level: {row['Pollution level']}</b>
            """
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=self.get_color(row['Pollution level']), icon='tint', prefix='fa')
            ).add_to(marker_cluster)

        folium.LayerControl().add_to(m)
        
        return m._repr_html_()