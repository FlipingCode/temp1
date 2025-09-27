# Data Processing
# Only CSV  and XLSX initially

import os
import pandas as pd

class DataProcessor:

    def __init__(self):
        
        # Essential metals to be checked in every dataset
        self.required_columns = ["as", "cd", "cr", "pb", "hg", "ni", "cu", "zn", "fe", "mn", "co", "al", "se", "sb", "ba", "v"]


        # Optional Data
        self.optional_columns = [
            "sample_id", "latitude", "longitude", "location", "date_collected"
        ]

        # Normalize common variations of column names
        self.column_mappings = {
            # Samples
            "sample_id": "sample_id",
            "sampleid": "sample_id",
            "id": "sample_id",
            "sample": "sample_id",
            "ss" : "sample_id",
            "station_na" : "sample_id",
            "station_no" : "sample_id",
            "station_name" : "sample_id",
            "station" : "sample_id",
            "site_name" : "sample_id",
            "site" : "sample_id",
            "monitoring_station" : "sample_id",
            "station_no" : "sample_id",
            "location": "sample_id",
            "place": "sample_id",
            "station_id": "sample_id",

            # Geo-Coordinates
            "lat": "latitude",
            "latitude": "latitude",
            "lon": "longitude",
            "lng": "longitude",
            "long": "longitude",
            "longitude": "longitude",

            # Dates
            "date": "date_collected",
            "date_collected": "date_collected",
            "sampling_date": "date_collected",
            "collection_date": "date_collected"
        }

        # Map full names of metals to their standard symbols
        self.metal_mappings = {
            "arsenic": "as",
            "cadmium": "cd",
            "chromium": "cr",
            "copper": "cu",
            "iron": "fe",
            "manganese": "mn",
            "nickel": "ni",
            "lead": "pb",
            "zinc": "zn"
        }

    def load(self,file_input):
        #Loading Data into a dataframe
        # Check if input is file-like or path

        if hasattr(file_input, 'filename'):
            filename = file_input.filename
        else:
            filename = file_input  # filepath string

        ext = os.path.splitext(filename)[1].lower()

        loaders = {
            '.csv': pd.read_csv,
            '.xls': pd.read_excel,
            '.xlsx': pd.read_excel,
            }
        
        if ext not in loaders:
            raise ValueError(f"Unsupported file format: {ext}. Please upload CSV or Excel.")
        
        df = loaders[ext](file_input)
        print(f"Loaded data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        df = self.cleaning_data(df)

        return df

    def cleaning_data(self, df):

        # 1. Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        df.rename(columns={k.lower(): v for k, v in self.column_mappings.items()}, inplace=True)
        df.rename(columns={k.lower(): v for k, v in self.metal_mappings.items()}, inplace=True)

        if 'sample_id' not in df.columns:
            df['sample_id'] = [f"Station {i+1}" for i in range(len(df))]
        df.insert(0, 'sample_id', df.pop('sample_id'))

        # 2. Strip and lowercase all string/object columns
        for col in df.select_dtypes(include='object').columns:
            if col != 'sample_id':   # keep station names as-is
                df[col] = df[col].astype(str).str.strip().str.lower()
                df[col] = df[col].replace({'': pd.NA, 'nd': pd.NA})
            else:  # still strip spaces but don’t lowercase
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace({'': pd.NA, 'nd': pd.NA})

        # 3. Convert metal columns to numeric
        for col in df.columns:
            if col not in ['sample_id', 'latitude', 'longitude', 'location', 'date_collected']:
                # Try to convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce').clip(lower=0).fillna(0)

        # 4. Handle coordinates if present
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
            # Keep only valid coordinate ranges
            df = df[
                df['Latitude'].between(-90, 90, na=False) &
                df['Longitude'].between(-180, 180, na=False)
            ]

        return df

    def coordinates_check(self, df):
        has_coordinates = False
        cols = [c.lower() for c in df.columns]
        if 'latitude' in cols and 'longitude' in cols:
            has_coordinates = True

        return has_coordinates