# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:37:50 2023

@author: Lasse
"""

import pandas as pd
import Data_Explo_HELPER as halp
import matplotlib.pyplot as plt
import os




breathD = halp.dataloader(41, 260, "breathD.csv", "breathD")
# %% NAN cleaning
halp.NaN_Cleaner(breathD,verbose=True)
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


    

    
