# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 09:51:58 2023

@author: Lasse
"""

import pandas as pd
import Data_Explo_HELPER as halp
import matplotlib.pyplot as plt
import os

cmd = os.path.join("patients", "patient11","esoData.csv")
esoData = pd.read_csv(cmd)


# %% print column names along with datatype for the Data Dictionary
esoData.info()
    

# %% NAN cleaning
esoData.isna().sum() 
#No NAN entries




# %% Datatype cleaning


##Check datatypes
# Datatypes are correct
#Matlab porting caused integers to be 'int64' and decimals to be 'float64'



