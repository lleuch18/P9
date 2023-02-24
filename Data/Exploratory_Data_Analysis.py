# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:34:21 2023

@author: Lasse
"""

import pandas as pd
import Data_Explo_HELPER as halp
import matplotlib.pyplot as plt



breathD = halp.dataloader(41, 260, "breathD.csv", "breathD")
#esoData = halp.dataloader(12, 17982, "esoData.csv", "esoData")
esoData = pd.read_csv("esoData.csv")
#FFFT = halp.dataloader(6, 36001, "FFFT.csv", "FFFT")
FFFT = pd.read_csv("FFFT.csv")

print(FFFT)

plt.plot(FFFT['Flow'])

# %% print column names along with datatype for the Data Dictionary
for col in breathD.columns:
    print("Name:    " + "\n" + col)
    print(breathD[col].dtype)
    
    
    print("\n")
FFFT['Flow'].dtype


breathD.dtypes.value_counts()
breathD.isna().sum()


