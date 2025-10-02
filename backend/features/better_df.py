# backend/features/better_df.py

import pandas as pd

class PrettyColumns:
    def prettify(self, df):
        """
        Cleans up column names for display.
        - Replaces underscores with spaces.
        - Title cases the words.
        - Makes a special exception for acronyms like HMPI.
        """
        rename_map = {}
        for col in df.columns:
            # General rule: replace underscores and title case the words
            new_col_name = col.replace('_', ' ').title()
            
            # Specific exception for the HMPI acronym
            if col.lower() == 'hmpi':
                new_col_name = 'HMPI'
            
            rename_map[col] = new_col_name
            
        df = df.rename(columns=rename_map)
        return df