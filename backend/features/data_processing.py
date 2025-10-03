# backend/features/data_processing.py

import pandas as pd
import re

class DataProcessor:

    def clean_columns(self, df):
        """
        Cleans and standardizes DataFrame column names, focusing on identifying
        geospatial columns.
        """
        rename_map = {}
        for col in df.columns:
            cleaned_col = col.strip().lower()
            if cleaned_col in ['lat', 'latitude']:
                rename_map[col] = 'Latitude'
            elif cleaned_col in ['lon', 'long', 'longitude']:
                rename_map[col] = 'Longitude'
            else:
                # Keep other columns as they are, just stripped of whitespace
                rename_map[col] = col.strip()

        df = df.rename(columns=rename_map)
        return df

    def load(self, filepath):
        """Loads data from CSV or Excel and cleans it."""
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                raise ValueError("Unsupported file type")

            # Clean the column headers
            df = self.clean_columns(df)
            
            # Convert numeric columns, coercing errors
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Use a regex to check if the column seems to contain numbers
                    # before trying to convert. This is a simple heuristic.
                    if df[col].str.contains(r'^\d+\.?\d*$', na=False).sum() > 0:
                         df[col] = pd.to_numeric(df[col], errors='coerce')

            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame() # Return empty dataframe on error

    def coordinates_check(self, df):
        """Checks if Latitude and Longitude columns exist."""
        return 'Latitude' in df.columns and 'Longitude' in df.columns