# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 18:53:44 2023

@author: Lasse
"""

#from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Data_Explo_HELPER as halp
import Compl_Algo_Helper as comp_halp
import math
from typing import List
#Amt of patients

            
#Set patient
patient = 11

#Load data
breathD,esoData,FFFT = halp.patientManager(patient,'entire')



# %% Calculate expiratory time constant 

#Set part and col_names
part = 1
prefix = str(part)
Vt,Vtexp,inspStart,expStart,ModifiedFlow,peak_exp_flow,exp_t_const,mean_insp_flow,ModifiedPao,PIP,Pplat,Raw_exp,Raw_insp = halp.prefix_Factory(part,
                                                                       'Vt',
                                                                       'Vtexp',
                                                                       'inspStart',
                                                                       'expStart',
                                                                       'ModifiedFlow',
                                                                       'peak_exp_flow',
                                                                       'exp_t_const',
                                                                       'MeanInspFlow',
                                                                       'ModifiedPao',
                                                                       'PIP',
                                                                       'Pplat',
                                                                       'Raw_exp',
                                                                       'Raw_insp'
                                                                       )


#Load vent settings
PS, PEEP = halp.Ventilator().get_Settings(patient)
PEEP = PEEP[part]


#Breath amt is length once NaN have been dropped
b_amt = len(breathD[Vtexp].dropna())-1

for breath in range(1,b_amt):
    #Get Vt_exp
    exp_Vt = breathD.at[breath-1,Vtexp]*100
    #print(f"exp_Vt at {breath} is {exp_Vt}")
    #get start index and expiratory length
    start_exp = breathD.at[breath,expStart]
    len_exp = breathD.at[breath+1,inspStart] - breathD.at[breath,expStart]
    #Calculate peak flow for the breath
    breathD.at[breath,peak_exp_flow] = esoData.loc[start_exp:(start_exp+len_exp),ModifiedFlow].max()
    print(f"Peak Exp Flow at {breath} is {breathD.at[breath,peak_exp_flow]}")
    #Calculate exp_t_const
    breathD.at[breath,exp_t_const] = exp_Vt/breathD.at[breath,peak_exp_flow]
    #print(f"exp_t_const at {breath} is {breathD.at[breath,exp_t_const]}")
    
    
    
# %% Calculate peak flow and PIP
for breath in range(1,b_amt):
    start_insp = breathD.at[breath,inspStart]
    len_insp = breathD.at[breath+1,expStart] - breathD.at[breath,inspStart]
    
    breathD.at[breath,mean_insp_flow] = esoData.loc[start_insp:(start_insp+len_insp),ModifiedFlow].mean()
    breathD.at[breath,PIP] = esoData.loc[start_insp:(start_insp+len_insp),ModifiedPao].max()



# %% Calculate Pplat from method described in article 1776

#Formula
def Pplat_method(Vt,PIP,PEEP,exp_t_const,mean_insp_flow):
    Pplat = ((Vt*PIP)-(Vt*PEEP))/Vt+(exp_t_const*mean_insp_flow)
    
    return Pplat

for breath in range(1,b_amt):
    breathD.at[breath,Pplat] = Pplat_method(breathD.at[breath,Vt],
                                         breathD.at[breath,PIP],
                                         PEEP,
                                         breathD.at[breath,exp_t_const],
                                         breathD.at[breath,mean_insp_flow]
                                         )
    
# %% Calculate Raw
#Raw = (PIP-Pplat)/Flow

for breath in range(1,b_amt):
    breathD.at[breath,Raw_insp] = (breathD.at[breath,PIP]-breathD.at[breath,Pplat])/breathD.at[breath,mean_insp_flow]
    breathD.at[breath,Raw_exp] = (breathD.at[breath,PIP]-breathD.at[breath,Pplat])/breathD.at[breath,peak_exp_flow]




# %% Prefix_factory

b_amt = 10

for breath in range(1,b_amt): print(breath); print(str(breath)+"Hey")

