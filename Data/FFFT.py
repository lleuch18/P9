# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 09:55:16 2023

@author: Lasse
"""

import pandas as pd
import Data_Explo_HELPER as halp
import matplotlib.pyplot as plt


FFFT = pd.read_csv("FFFT.csv")


# %% print column names along with datatype for the Data Dictionary
FFFT.info()
    

# %% NAN cleaning
FFFT.isna().sum() 
#No NAN entries




# %% Datatype cleaning


##Check datatypes
# Datatypes are correct
#Matlab porting caused integers to be 'int64' and decimals to be 'float64'


