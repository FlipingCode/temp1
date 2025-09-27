#HMPI Calculations

import pandas as pd

class HMPICalculation:

    def __init__(self):
        self.standards = {
            'as': {'S': 0.01, 'W': 100, 'I': 0},
            'cd': {'S': 0.003, 'W': 333.3, 'I': 0},
            'cr': {'S': 0.05, 'W': 20, 'I': 0},
            'cr+6': {'S': 0.05, 'W': 20, 'I': 0},
            'pb': {'S': 0.01, 'W': 100, 'I': 0},
            'hg': {'S': 0.001, 'W': 1000, 'I': 0},
            'ni': {'S': 0.02, 'W': 50, 'I': 0},
            'cu': {'S': 1.5, 'W': 0.67, 'I': 0},
            'zn': {'S': 3, 'W': 0.33, 'I': 0},
            'fe': {'S': 0.3, 'W': 3.33, 'I': 0},
            'mn': {'S': 0.1, 'W': 10, 'I': 0},
            'co': {'S': 0.05, 'W': 20, 'I': 0},
            'al': {'S': 0.2, 'W': 5, 'I': 0},
            'se': {'S': 0.01, 'W': 100, 'I': 0},
            'sb': {'S': 0.005, 'W': 200, 'I': 0},
            'ba': {'S': 0.7, 'W': 1.43, 'I': 0},
            'v': {'S': 0.05, 'W': 20, 'I': 0}
        }

    def calculate(self, df):
        hmpi_list = []
        poll_list=[]

        for index, row in df.iterrows():
            num = 0
            den = 0

            # Only consider metals present in DataFrame and not NaN
            present_metals = [metal for metal in self.standards if metal in row and pd.notna(row[metal])]

            for metal in present_metals:
                Mi = row[metal]
                Si = self.standards[metal]['S']
                Ii = self.standards[metal]['I']
                Wi = self.standards[metal]['W']

                Qi = 100 * (Mi - Ii) / (Si - Ii)
                num += Wi * Qi
                den += Wi
            
            hmpi = num / den if den != 0 else 0
            hmpi_list.append(hmpi)

            poll_level='Perfect'
            if(hmpi<=10): 
                poll_level='Perfect'
            elif(hmpi<=50): 
                poll_level= 'Good'
            elif(hmpi<=100): 
                poll_level= 'Moderate'
            elif(hmpi<=200): 
                poll_level= 'Poor'
            elif(hmpi<=400): 
                poll_level= 'Very Poor'
            else: 
                poll_level= 'Extremely Poor'
            poll_list.append(poll_level)

        df['HMPI'] = hmpi_list
        df['Pollution Level']=poll_list
        return df