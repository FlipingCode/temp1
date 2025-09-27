# Geo-Spatial Analysis
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
import os

class GeoSpatialAnalyser:

    def __init__(self):
        pass

    @staticmethod
    def hmpi_color(hmpi):
        if hmpi <= 10:
            return '#00FF00'  # Perfect
        elif hmpi <= 50:
            return '#7CFC00'  # Good
        elif hmpi <= 100:
            return '#FFFF00'  # Moderate
        elif hmpi <= 200:
            return '#FFA500'  # Poor
        elif hmpi <= 400:
            return '#FF8C00'  # Very Poor
        else:
            return '#DC143C'  # Extremely Poor


    def geospatial_analysis(self, df):

        # Creating a list of tuples that have coordinates as (x=long,y=lat) and saving that to a geopandas dataframe
        geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        gdf.set_crs(epsg=4326, inplace=True)  # Setting WGS84 standard

        gdf['color'] = gdf['HMPI'].apply(self.hmpi_color) # Sets color for each HMPI Value
    
        gdf['Info:'] = (
            "<b>Sample ID:</b> " + gdf['sample_id'].astype(str) +
            "<br><b>HMPI:</b> " + gdf['HMPI'].round(2).astype(str) +
            "<br><b>Pollution Level:</b> " + gdf['Pollution Level']
        )

        gdf['HMPI'] = gdf['HMPI'].round(2).astype(str)
        
        m = gdf.explore(
            color='color', # Sets Color for HMPI Pointer
            popup='Info:',# Popup when clicked
            tooltip='HMPI',    # Show on hover
            tiles='CartoDB positron',  # map style
            marker_kwds={'radius': 5, 'fill': True, 'color': 'black'}, # Describe the Point
            zoom_start=15
        )

        # map_path = os.path.join('frontend', 'templates', 'map.html')
        # m.save(map_path)
        # return map_path

        return m._repr_html_()
