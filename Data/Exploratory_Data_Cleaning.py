# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:34:21 2023

@author: Lasse
"""

import pandas as pd
import Data_Explo_HELPER as halp
import matplotlib.pyplot as plt





#esoData = halp.dataloader(12, 17982, "esoData.csv", "esoData")
esoData = pd.read_csv("esoData.csv")
#FFFT = halp.dataloader(6, 36001, "FFFT.csv", "FFFT")
FFFT = pd.read_csv("FFFT.csv")

print(FFFT)

plt.plot(FFFT['Flow'])

# %% print column names along with datatype for the Data Dictionary
esoData.info()
    

# %% NAN cleaning


# Remove EELV with 260 counts
breathD.drop(columns=['EELV'],inplace=True)

## Moving average over VolCal (7-1 counts) and TrappingFraction (19-1 counts)
cols = ['VolCal', 'TrappingFraction']

breathD = halp.MovingAverage(cols, breathD)

# %% Datatype cleaning

##Check datatypes
#Matlab porting caused integers to be 'int64' and decimals to be 'float64'
breathD.info() 

#Typecast dataframe to 'float64' if mixed, and int64 if only integers

breathD = breathD.astype('float64', copy=False)

breathD.dtypes.value_counts()

breathD["Rf"].mean()

            
            



