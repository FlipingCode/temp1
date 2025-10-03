# backend/features/geospatial_analysis.py

import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np # Import numpy for logarithmic scaling

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
        # More robust algorithm to find all necessary columns
        lat_col, lon_col, hmpi_col = None, None, None
        station_col, pollution_col = None, None

        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ['lat', 'latitude']:
                lat_col = col
            elif col_lower in ['lon', 'long', 'longitude']:
                lon_col = col
            elif col_lower in ['hmpi', 'hpi']:
                hmpi_col = col
            elif col_lower in ['station name', 'sample_id', 'station']:
                station_col = col
            elif col_lower in ['pollution level', 'poll_level']:
                pollution_col = col

        if not all([lat_col, lon_col, hmpi_col]):
             return "<p>Error: Could not find required columns (Latitude, Longitude, HMPI/HPI).</p>"

        # Standardize column names for the rest of the function
        rename_dict = {
            lat_col: 'Latitude',
            lon_col: 'Longitude',
            hmpi_col: 'Hmpi'
        }
        if station_col:
            rename_dict[station_col] = 'Station name'
        if pollution_col:
            rename_dict[pollution_col] = 'Pollution level'
            
        df = df.rename(columns=rename_dict)

        # Drop rows where lat/lon/hmpi are missing or invalid
        df_geo = df.dropna(subset=['Latitude', 'Longitude', 'Hmpi'])
        df_geo['Latitude'] = pd.to_numeric(df_geo['Latitude'], errors='coerce')
        df_geo['Longitude'] = pd.to_numeric(df_geo['Longitude'], errors='coerce')
        df_geo['Hmpi'] = pd.to_numeric(df_geo['Hmpi'], errors='coerce')
        df_geo.dropna(subset=['Latitude', 'Longitude', 'Hmpi'], inplace=True)

        if df_geo.empty:
            return "<p>Error: No valid geospatial data to display.</p>"

        # Apply a logarithmic transformation to HMPI values for better visualization
        df_geo['Hmpi_log_scaled'] = np.log1p(df_geo['Hmpi'])
        
        # --- Start of Positioning and Layer Control Fix ---

        # Create map without initial center/zoom; we will set it automatically
        m = folium.Map(tiles=None)

        # Add base tile layers
        folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
        folium.TileLayer(
            tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            overlay=False,
            control=True,
            subdomains=['mt0', 'mt1', 'mt2', 'mt3']
        ).add_to(m)
        
        # Use the log-scaled data for the heatmap
        heat_data = [[row['Latitude'], row['Longitude'], row['Hmpi_log_scaled']] for index, row in df_geo.iterrows()]
        
        HeatMap(
            heat_data,
            name="HMPI Heatmap",
            radius=25,
            blur=20,
            min_opacity=0.5
        ).add_to(m)

        marker_cluster = MarkerCluster(name="Pollution Stations").add_to(m)
        for idx, row in df_geo.iterrows():
            popup_html = f"""
            <b>Location:</b> {row.get('Station name', 'N/A')}<br>
            <b>HMPI:</b> {row['Hmpi']:.2f}<br>
            <b style='color:{self.get_color(row.get('Pollution level', ''))};'>Level: {row.get('Pollution level', 'N/A')}</b>
            """
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=self.get_color(row.get('Pollution level', '')), icon='tint', prefix='fa')
            ).add_to(marker_cluster)

        # Add the layer control, ensuring it is not collapsed by default
        folium.LayerControl(collapsed=False).add_to(m)
        
        # Automatically fit the map to the bounds of your data points
        sw = df_geo[['Latitude', 'Longitude']].min().values.tolist()
        ne = df_geo[['Latitude', 'Longitude']].max().values.tolist()
        m.fit_bounds([sw, ne])
        
        # --- End of Positioning and Layer Control Fix ---
        
        return m._repr_html_()