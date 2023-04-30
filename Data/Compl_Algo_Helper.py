# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 05:25:49 2023

@author: Lasse
"""

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import Data_Explo_HELPER as halp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   
   
def data_Filtering(esoData,verbose=False):
    parts = int(len(esoData.columns)/12)+1
    
    if verbose:
        print("data_Filtering created parts")

    for part in range(1,parts):
        if verbose:
            print(f"data_Filtering made it to part {part} of {parts}")
        prefix = str(part)
        peso = prefix + 'peso'
        esoData = halp.dynamic_moving_median(esoData,peso,165,20,10,verbose)
        if verbose:
            print("data_Filtering completed median")
        esoData = halp.unsquare_moving_average(esoData, peso, 5)
        if verbose:
            print("data_Filtering completed average \n")
    return esoData


def compliance_cost(peso, Vt, pao, PEEP,C,peso_var,verbose=False):
    #Conversion factors
    Vt = Vt*100 #Convert from L to mL
    #PEEP = PEEP * 0.073555913 #Convert from mmH2O to mmHg
    
    #Vt gets scaled from L to mL
    j = (peso - (Vt/C) + PEEP - pao)**2/peso_var
    
    #(Peso - ((Vt*100)/C)+PEEP-pao)**2/var
    if verbose:
        print(f"peso: {peso} \n" + f"Vt: {Vt} \n pao: {pao} \n PEEP: {PEEP} \n C: {C} ")
    
    #print(f"value of Peso.var(): {Peso.var()}")
    return j

def compliance_cost_full(peso, Vt, pao, PEEP, Raw, insp_flow, C,peso_var,verbose=False):
    #Conversion factors
    Vt = Vt*100 #Convert from L to mL
    #PEEP = PEEP * 0.073555913 #Convert from mmH2O to mmHg
    
    #Vt gets scaled from L to mL
    j = (peso - (Vt/C) + (Raw*insp_flow) + PEEP - pao)**2/peso_var
    
    #(Peso - ((Vt*100)/C)+PEEP-pao)**2/var
    if verbose:
        print(f"peso: {peso} \n" + f"Vt: {Vt} \n pao: {pao} \n PEEP: {PEEP} \n C: {C} \n Raw: {Raw}, \n insp_flow: {insp_flow} ")
    
    #print(f"value of Peso.var(): {Peso.var()}")
    return j


def bin_divider(esoData,breathD, verbose=False):
    # Amount of breaths
    b_amount = len(breathD)
    

    #Divide Peso into bins according to each breath
    esoData_bins = pd.DataFrame(index=range(b_amount))
    print("created DF")
    parts = int(len(esoData.columns)/12)

    for part in range(1,parts+1):
        if verbose:
            print(f"bin_divider started part: {part}")
        prefix = str(part)
        peso = prefix + 'ModifiedPeso'
        pao = prefix + 'ModifiedPao'
        breath_col = prefix + 'breath'
        inspStart = prefix + 'inspStart'
        for breath in range(b_amount):
            if verbose:
                print(f"bin_divider made it to breath: {breath}")
            #Retrieve index value for cur inspiratory and next inspiratory start
            if breath == 0:
                insp_cur = 0
                insp_next = breathD.at[breath,inspStart]            
                #Calculate the mean of peso and pao during the current breath
                esoData_bins.at[breath,peso] = esoData.loc[insp_cur:insp_next,peso].max()#.mean()
                esoData_bins.at[breath,pao] = esoData.loc[insp_cur:insp_next,pao].max()#.mean()
                

            else:
                insp_cur = breathD.at[breath, inspStart]
                insp_next = breathD.at[breath, inspStart]            
                #Calculate the mean of peso and pao during the current breath

            esoData_bins.at[breath,peso] = esoData.loc[insp_cur:insp_next,peso].max()#.mean()
            esoData_bins.at[breath,pao] = esoData.loc[insp_cur:insp_next,pao].max()#.mean()
            if np.isnan(esoData_bins.at[breath,peso]) == False: 
                #Create a breath column for plotting purposes
                esoData_bins.at[breath,breath_col] = breath

    return esoData_bins


def grid_search(esoData, esoData_bins,breathD,pat_Nr,verbose=False):
    #Grid search used for this step
    b_amt = len(esoData_bins)
    parts = int(len(esoData.columns)/12)
    #Retrieve vent settings
    PS, PEEP = halp.Ventilator().get_Settings(str(pat_Nr))
    #Define values for C
    C_range = np.arange(100,400,0.5)
    

    #Housekeeping variables
    hk_parts = {}
    
    special_test = False


    if verbose:
        halp.verbose_fnc(color.BOLD + f"****CURRENT PATIENT IS: {pat_Nr}****" + color.END)
    #For every part
    for part in range(1,parts+1):
        #Reset stats at every part
        j_best = 100000 #High value so that j is always set even at low output values
        C_best = 0.0000 #Same logic but reversed
        b_best = 0        
        tot_loss = 0
        
        if verbose:
            halp.verbose_fnc(color.UNDERLINE + f"**CURRENT PART IS: {part}**" + color.END)
            
        #Set prefixes for retrieving correct parts

        ModifiedPeso,ModifiedPao,Vt = halp.prefix_Factory(part, 'ModifiedPeso','ModifiedPao','Vt')
        
        #Set a specific compliance
        for C in C_range:

        #Loop through every breath
            for breath in range(b_amt):

                    #Check if current breath exists or is NaN
                if np.isnan(esoData_bins.at[breath,ModifiedPeso]) == False:                    
                    #Calculate loss for current breath
                    j = compliance_cost(esoData_bins.at[breath,ModifiedPeso], esoData_bins.at[breath,ModifiedPao], breathD.at[breath,Vt],PEEP[part-1],C,esoData_bins[ModifiedPeso].std())
                    
                    if verbose:
                        if breath % 90 == 0 and C == C_range[0]:
                            print(f"breath {breath} j = {j}")

    
                    #Housekeep best current loss, best C
                    if j < j_best:
                        j_best = j
                        C_best = C
                        b_best = breath
                
                    #Increase total loss for the part by the loss for current breath
                    tot_loss += j
                
        if verbose:    
            halp.verbose_fnc(color.RED + f"total loss for part {part} is: {tot_loss}" + color.END)
            
        #Housekeep for entire part
        hk_parts[part] = {"tot_loss" : tot_loss, "j_best" : j_best, "C_best" : C_best, 'b_best' : b_best}
        #print(color.BOLD + f"Length of hk_parts at part {part} is {len(hk_parts)}" + color.END)
        
    return hk_parts


def grid_search_full(esoData, esoData_bins,breathD,pat_Nr,verbose=False):
    #Grid search used for this step
    b_amt = len(esoData_bins)
    parts = int(len(esoData.columns)/12)
    #Retrieve vent settings
    PS, PEEP = halp.Ventilator().get_Settings(str(pat_Nr))
    #Define values for C
    C_range = np.arange(50,400,0.5)
    

    #Housekeeping variables
    hk_parts = {}
    hk_C_loss = {}
    
    special_test = False


    if verbose: halp.verbose_fnc(color.BOLD + f"****CURRENT PATIENT IS: {pat_Nr}****" + color.END)
    #For every part
    for part in range(1,parts+1):
        #Reset stats at every part
        j_best = 100000 #High value so that j is always set even at low output values
        C_best = 0.0000 #Same logic but reversed
        b_best = 0
        best_C_loss = 10000000
        global tot_C_loss
        tot_C_loss = 0

        
        if verbose: halp.verbose_fnc(color.UNDERLINE + f"**CURRENT PART IS: {part}**" + color.END)
            
        #Set prefixes for retrieving correct parts
        ModifiedPeso, ModifiedPao, Vt,Raw_insp,MeanInspFlow = halp.prefix_Factory(part,'ModifiedPeso','ModifiedPao','Vt','Raw_insp','MeanInspFlow')
        
        #Set a specific compliance
        for C in C_range:
            #reset tot loss at every compliance
            #print(f"tot_C_loss pre-reset: {tot_C_loss}")
            tot_C_loss = 0
           # print(f"Total loss post reset is \n {tot_C_loss}")
            

        #Loop through every breath
            for breath in range(1,b_amt):

                    #Check if current breath exists or is NaN
                if np.isnan(esoData_bins.at[breath,ModifiedPeso]) == False: 
                    #print(f"current proccesed breath: {breath}")
                    #Calculate loss for current breath
                    j = compliance_cost_full(esoData_bins.at[breath,ModifiedPeso],
                                        esoData_bins.at[breath,ModifiedPao],
                                        breathD.at[breath,Vt],
                                        PEEP[part-1],
                                        breathD.at[breath,Raw_insp],
                                        breathD.at[breath,MeanInspFlow],
                                        C,
                                        esoData_bins[ModifiedPeso].std())
                    #if np.isnan(j): print(f"J is NaN at breath {breath}")

                    
                    if verbose:
                        if breath % 90 == 0 and C == C_range[0]: print(f"breath {breath} j = {j}")

                    #Increase total loss for the part by the loss for current breath
                    if np.isnan(j) == False: tot_C_loss += j
                    #print(f"tot_c_loss at C: {C} is {tot_C_loss}")
                    #if breath % 10 == 0:
                        #print(f"tot_C_loss: {tot_C_loss}")
            
            
            #print(f"tot_C_loss: {tot_C_loss}")      
            if tot_C_loss < best_C_loss:
                best_C_loss = tot_C_loss
                C_best = C
            
            hk_C_loss[C] = {"C" : C, "tot_C_loss" : tot_C_loss}

            
                    
                
        #if verbose: halp.verbose_fnc(color.RED + f"total loss for part {part} is: {tot_C_loss}" + color.END)
            
        #Housekeep for entire part
        hk_parts[part] = {"C_best" : C_best, "best_C_loss" : best_C_loss,"hk_C_loss" : hk_C_loss}
        #print(color.BOLD + f"Length of hk_parts at part {part} is {len(hk_parts)}" + color.END)
        
    return hk_parts
