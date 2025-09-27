# pretty_columns.py
# Class to prettify dataframe columns

class PrettyColumns:
    def __init__(self):
        self.pretty_map = {
            "sample_id": "Sample ID",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "location": "Location",
            "date_collected": "Date Collected",
            "as": "As",
            "pb": "Pb",
            "cd": "Cd",
            "cr": "Cr",
            "cr+6": "Cr+6",
            "ni": "Ni",
            "cu": "Cu",
            "zn": "Zn",
            "fe": "Fe",
            "mn": "Mn",
            "co": "Co",
            "al": "Al",
            "se": "Se",
            "sb": "Sb",
            "ba": "Ba",
            "hg": "Hg",
            "v": "V"
        }

    def prettify(self, df):
        """
        Return a copy of df with pretty column names.
        Only renames columns that exist in df.
        """
        return df.rename(columns={k: v for k, v in self.pretty_map.items() if k in df.columns})
