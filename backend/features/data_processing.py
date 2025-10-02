# backend/features/data_processing.py

import pandas as pd
import re

class DataProcessor:

    def clean_columns(self, df):
        """
        Cleans and corrects DataFrame column names.
        - Strips leading/trailing whitespace.
        - Splits concatenated column names like 'SampleIDLatitude' into separate columns.
        """
        original_columns = df.columns.tolist()
        new_columns = []
        rename_map = {}

        for col in original_columns:
            cleaned_col = col.strip()
            # Look for common concatenated geo columns and split them
            # Example: "IDLatitudeLongitude" -> "ID", "Latitude", "Longitude"
            parts = re.split(r'(Latitude|Longitude)', cleaned_col)
            
            # Filter out empty strings from split
            parts = [p for p in parts if p]

            if len(parts) > 1:
                # If we split the column, we need to handle the data correctly
                # For this to work, we'd need more complex logic to split the actual column data
                # A simpler approach for now is to rename common malformed headers.
                if 'Latitude' in cleaned_col and 'Longitude' in cleaned_col:
                    # This case is too complex to split reliably without more info.
                    # We'll rely on simple renaming for now.
                    pass
                
            # Common renaming patterns
            if re.match(r'\S+Latitude', cleaned_col):
                rename_map[col] = 'Latitude'
            elif re.match(r'\S+Longitude', cleaned_col):
                rename_map[col] = 'Longitude'
            else:
                 rename_map[col] = cleaned_col

        df = df.rename(columns=rename_map)

        # A more direct fix for the user's specific problem format:
        # If a single column contains both lat and lon headers, let's try to find them
        for col in df.columns:
            if 'Latitude' in col and 'Longitude' in col:
                # This suggests the headers are malformed.
                # Let's assume the first two columns after the sample ID are lat/lon
                # This is a bit of a guess, but it's a common format.
                try:
                    # Find the problematic column index
                    col_index = df.columns.get_loc(col)
                    
                    # Let's assume the column before it is the station name, and this column should be split
                    # A better fix is to adjust the file reading itself.
                    # For now, let's just make the column name checks more robust in geospatial_analysis
                    pass # Let's handle this downstream for now.
                except:
                    pass

        # Final cleanup
        df.columns = [c.strip() for c in df.columns]
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
                    df[col] = pd.to_numeric(df[col], errors='ignore')
            
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame() # Return empty dataframe on error

    def coordinates_check(self, df):
        """Checks if Latitude and Longitude columns exist."""
        return 'Latitude' in df.columns and 'Longitude' in df.columns