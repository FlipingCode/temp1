# This is output a CSV file in the Data Folder

import pandas as pd
import os

class HMPIOutput:
    def output(self, df):
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/hmpi_results.csv', index=False)