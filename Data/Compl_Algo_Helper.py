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
from scipy.signal import find_peaks
import scipy.integrate as integrate
import scipy.special as special
import math
import importlib

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


def compliance_cost_no_flow_min(x,Vt_min, pao_min, PEEP_min, pao_var_min):
    #return ((0- ((Vt_min/x) + PEEP_min-pao_min))**2)/pao_var_min
    j=0
    for peak in range(len(pao_min)):
        j += ((0- ((Vt_min[peak]/x[peak]) + PEEP_min[peak]-pao_min[peak]))**2)/pao_var_min[peak]
    return j


def compliance_cost_no_flow (Vt, pao, PEEP, C,peso_var=None,breath=None,peso=None,pao_var=None,verbose=False,no_pmus=False):
    if no_pmus:        
        if verbose:
            print(f" Vt: {Vt} \n pao: {pao} \n PEEP: {PEEP} \n C: {C} \n Pao_var: {pao_var}  ")
        return ((0- ((Vt/C) + PEEP-pao))**2)/pao_var
    else:    
        j = ((peso - ((Vt/C) + PEEP - pao))**2)/peso_var #+ (Raw*insp_flow)
        if verbose:
            print(f"peso: {peso} \n" + f"Vt: {Vt} \n pao: {pao} \n PEEP: {PEEP} \n C: {C}  ")
        
        return j


    

def Pplat_method(Vt,PIP,PEEP,exp_t_const,mean_insp_flow):
    Pplat = ((Vt*PIP)-(Vt*PEEP))/Vt+(exp_t_const*mean_insp_flow)
    
    return Pplat

def flow_extracter(esoData, peak,ModifiedFlow, peaks_flow, valleys_flow,insp=False,exp=False,intgrate=False):
    
    def zeroin_insp(row):
        if row < 0: row = 0
        return row
    
    def zeroin_exp(row):
        if row > 0: row = 0
        return row
    
    
    
    cnt_insp = 0
    cnt_exp = 0
    
    if peak+1 < len(peaks_flow[0]):
        
        #Ensure that peaks always get set to the correct index (sometimes they skip a peak otherwise)
        while valleys_flow[0][peak+cnt_insp] > peaks_flow[0][peak+1]: cnt_insp -= 1          
    
        while valleys_flow[0][peak+1] < peaks_flow[0][peak+cnt_exp]: cnt_exp -= 1
        
        
        # %% Insp
        if insp and not intgrate:
                       
            insp_eso = pd.DataFrame(columns=['modflow'])
            insp_eso['modflow'] = esoData[ModifiedFlow].apply(lambda row: zeroin_insp(row))
            #If valleys are at a plateau, skip to the next peak
            
            if peak == 0:
                return insp_eso.loc[0:valleys_flow[0][peak],'modflow'].mean()
            else:
                if esoData.at[valleys_flow[0][peak+1],ModifiedFlow]-esoData.at[valleys_flow[0][peak],ModifiedFlow] == 0: 
                    print(f"activated skip condition at peak {peak}")
                    peak += 1
                    print(f"peak = {peak}")
                return insp_eso.loc[valleys_flow[0][peak]:valleys_flow[0][peak+1],'modflow'].mean()
            
        if intgrate and insp:
            #print(f"made it to FLOW EXTRACTOR at peak {peak}") 
            insp_eso = pd.DataFrame(columns=['modflow'])
            insp_eso['modflow'] = esoData[ModifiedFlow].apply(lambda row: zeroin_insp(row))
            #If valleys are at a plateau, skip to the next peak
            
            if peak == 0 and esoData.at[valleys_flow[0][peak],ModifiedFlow] > 0:
                y_inspVt = insp_eso.loc[0:valleys_flow[0][peak],'modflow']
                
            else:
                if insp_eso.loc[valleys_flow[0][peak]:valleys_flow[0][peak+1],'modflow'].sum() == 0: 
                    print(f"activated skip condition at peak {peak}")
                    peak += 1
                    print(f"peak = {peak}")
                y_inspVt = insp_eso.loc[valleys_flow[0][peak]:valleys_flow[0][peak+1],'modflow']

            y_inspVt = y_inspVt.loc[y_inspVt > 0]
            y_inspVt = y_inspVt

            
            x_inspVt = np.arange(0,len(y_inspVt))
            debug_insp=False
            if debug_insp:
                print(f"index valleys_flow[0][{peak}]: {valleys_flow[0][peak]}")
                print(f"undivided sum: {integrate.simpson(y_inspVt,x_inspVt)}")
                print(f"index valleys_flow[0][{peak+1}]: {valleys_flow[0][peak+1]}")
                print(f"len y_inspVt: {len(y_inspVt)} \n len x_inspVt: {len(x_inspVt)}")
                print(f"sum of valleys_flow[0][peak]:valleys_flow[0][peak+1] : {y_inspVt.sum()}")
                #Units of flow expressed in L/min. Divide by 60 give L/S, and divide by 100 to give 1/100th seconds, since it's measured at 100Hz
                #Without division, the calculation assumes that the duration is ~100 seconds instead of  ~1second
            return (integrate.simpson(y_inspVt,x_inspVt))/(60*100)
            
        # %% Exp
        if exp and not intgrate:
            exp_eso = pd.DataFrame(columns=['modflow'])
            exp_eso['modflow'] = esoData[ModifiedFlow].apply(lambda row: zeroin_exp(row))
            
            return exp_eso.loc[peaks_flow[0][peak]:peaks_flow[0][peak+1],'modflow'].mean()
        
        
        if intgrate and exp:

            
            exp_eso = pd.DataFrame(columns=['modflow'])
            exp_eso['modflow'] = esoData[ModifiedFlow].apply(lambda row: zeroin_exp(row))
            
            y_expVt = exp_eso.loc[peaks_flow[0][peak]:peaks_flow[0][peak+1],'modflow']
            y_expVt = y_expVt.loc[y_expVt < 0]
            x_expVt = np.arange(0,len(y_expVt))
            
            debug_exp = False
            if debug_exp:
                print(f"index peaks_flow[0][{peak}]: {peaks_flow[0][peak]}")
                print(f"index peaks_flow[0][{peak+1}]: {peaks_flow[0][peak+1]}")
                print(f"len y_expVt: {len(y_expVt)} \n len x_expVt: {len(x_expVt)}")
                print(f"sum of valleys_flow[0][peak]:valleys_flow[0][peak+1] : {y_expVt.sum()}")
            #Units of flow expressed in L/min. Divide by 60 give L/S, and divide by 100 to give 1/100th seconds, since it's measured at 100Hz
            return abs(integrate.simpson(y_expVt,x_expVt))/(60*100)
        
            
        
    
# %% bin divider
def bin_divider(esoData,breathD,pat_Nr, verbose=False):
    #Load PS and PEEP Settings
    PS, PEEP = halp.Ventilator().get_Settings(str(pat_Nr))
    
    # Amount of breaths
    len_breathD = len(breathD)

   
    

    #Divide Peso into bins according to each breath
    esoData_bins = pd.DataFrame(index=range(len_breathD))
    #print("created DF")
    parts = int(len(esoData.columns)/12)+1

    for part in range(1,parts):


        print(f"bin_divider started part: {part}")
        ModifiedPeso,ModifiedPao,peak_col,ModifiedFlow,exp_Flow,insp_Flow,insp_Vt,exp_Vt,exp_Time_Const,Pplat,insp_Raw,exp_Raw = halp.prefix_Factory(part, 'ModifiedPeso',
                                                                'ModifiedPao',
                                                                'breath_col',
                                                                'ModifiedFlow',
                                                                'exp_Flow',
                                                                'insp_Flow',
                                                                'insp_Vt',
                                                                'exp_Vt',
                                                                'exp_Time_Const',
                                                                'Pplat',
                                                                'insp_Raw',
                                                                'exp_Raw')
        
        #Settings to assure synchornicity between peaks and valleys
        flow_settings = {1 : {'height' : 5,'dis' : 230},
                         2 : {'height' : 5.3,'dis' : 255},
                         3 : {'height' : 4.9,'dis' : 255},
                         4 : {'height' : 5.7,'dis' : 300},
                         5 : {'height' : 5.7,'dis' : 300},
                         6 : {'height' : 6.7,'dis' : 350},
                         7 : {'height' : 6.6,'dis' : 350},
                         8 : {'height' : 5.1,'dis' : 280}}
        #print(f"{ModifiedPeso} \n {ModifiedPao} \n {peak_col} ")
        if part == 7:
            peaks_peso = find_peaks(esoData[ModifiedPeso],height=-5.1,distance=150)
            peaks_pao = find_peaks(esoData[ModifiedPao],height=11.5,distance=150)
            peaks_flow = find_peaks(esoData[ModifiedFlow],height=10,distance=250)
            valleys_flow = find_peaks(esoData[ModifiedFlow]*(-1),
                                      height=flow_settings[7]['height'],
                                      distance=flow_settings[7]['dis'])
        elif part == 8:
            peaks_peso = find_peaks(esoData[ModifiedPeso],height=-7,distance=150)
            peaks_pao = find_peaks(esoData[ModifiedPao],height=11.5,distance=150)
            peaks_flow = find_peaks(esoData[ModifiedFlow],height=10,distance=250)
            valleys_flow = find_peaks(esoData[ModifiedFlow]*(-1),
                                      height=flow_settings[8]['height'],
                                      distance=flow_settings[8]['dis'])
        else:        
            peaks_peso = find_peaks(esoData[ModifiedPeso],height=-3,distance=150)
            peaks_pao = find_peaks(esoData[ModifiedPao],height=11.5,distance=150)
            peaks_flow = find_peaks(esoData[ModifiedFlow],height=10,distance=250)
            valleys_flow = find_peaks(esoData[ModifiedFlow]*(-1),
                                      height=flow_settings[part]['height'],
                                      distance=flow_settings[part]['dis'])

        peaks = len(peaks_peso[0])
        #if verbose:
        print(f"amt of peso_peaks at part {part}: {len(peaks_peso[0])} \n amt of pao_peaks at {part}: {len(peaks_pao[0])}")
        print(peaks)
        print(len(range(peaks)))

        for peak in range(peaks):
            
            if verbose: print(f"bin_divider made it to peak: {peak}")              
                #Calculate the mean of peso and pao during the current breath
            if peak == 0:
                #Peso height
                esoData_bins.at[peak,ModifiedPeso] = peaks_peso[1]['peak_heights'][peak]-esoData.loc[1:peaks_peso[0][peak],ModifiedPeso].min()
            else:
                #Peso Height
                esoData_bins.at[peak,ModifiedPeso] = peaks_peso[1]['peak_heights'][peak]-esoData.loc[peaks_peso[0][peak-1]:peaks_peso[0][peak],ModifiedPeso].min()
                if esoData_bins.at[peak,ModifiedPeso] > 22:
                    esoData_bins.at[peak,ModifiedPeso] = esoData_bins.loc[peak-5:peak+5,ModifiedPeso].median()
                
            #Pao height: Subtract peak height from delivered PEEP, to get pressure delivered by the vent
            #print(f"currently at peak {peak}")
            #esoData_bins.at[peak,ModifiedPao] = peaks_pao[1]['peak_heights'][peak-1]-PEEP[part]
            #esoData_bins.at[peak,ModifiedPao] = peaks_pao[1]['peak_heights'][peak]
            
            # Flow Part 
            #Exp_Flow mean
            #Everything above 0 between two valleys is insp flow
            esoData_bins.at[peak,exp_Flow] = flow_extracter(esoData, peak, ModifiedFlow, peaks_flow, valleys_flow,exp=True)
            #Insp_Flow mean
            esoData_bins.at[peak,insp_Flow] = flow_extracter(esoData, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True)
            #insp_Vt by integrating the inspiratory flow signal
            esoData_bins.at[peak,insp_Vt] = flow_extracter(esoData,peak,ModifiedFlow,peaks_flow,valleys_flow,insp=True,intgrate=True)
            #exp_Vt by integrating the expiratory flow_signal
            esoData_bins.at[peak,exp_Vt] = flow_extracter(esoData,peak,ModifiedFlow,peaks_flow,valleys_flow,exp=True,intgrate=True)
            
            full=False
            if full == True:
                #Te, Pplat and Raw only necessary for the full cost function
                #Exp_Time_Constant = exp_Vt/exp_flow
                esoData_bins.at[peak,exp_Time_Const] = esoData_bins.at[peak,exp_Vt]/esoData_bins.at[peak,exp_Flow]
                #Calculate Pplat
                esoData_bins.at[peak,Pplat] = Pplat_method(esoData_bins.at[peak,insp_Vt],
                                                           esoData_bins.at[peak,ModifiedPao],
                                                           PEEP[part-1],
                                                           esoData_bins.at[peak,exp_Time_Const],
                                                           esoData_bins.at[peak,insp_Flow]
                                                           )
                #Calculate Raw = (PIP-Pplat)/Flow
                esoData_bins.at[peak,insp_Raw] = (esoData_bins.at[peak,ModifiedPao]-esoData_bins.at[peak,Pplat])/esoData_bins.at[peak,insp_Flow]
                esoData_bins.at[peak,exp_Raw] = (esoData_bins.at[peak,ModifiedPao]-esoData_bins.at[peak,Pplat])/esoData_bins.at[peak,exp_Flow]
 
            
            #insp_Vt by integrating the flow 
            if verbose:

                debug_insp = False
                if debug_insp:
                    print(f"valleys_flow[{peak}] : {valleys_flow[0][peak]}")
                    #print(f"peak_flow[{peak}] : {peaks_flow[0][peak+1]}")
                    #print(f"len y_inspVt: {len(esoData.loc[valleys_flow[0][peak]:peaks_flow[0][peak+1],ModifiedFlow])} " + f" at peak: {peak}")
                    #print(f"len x_inspVt: {len(np.arange(valleys_flow[0][peak],peaks_flow[0][peak+1]+1))} ")

            if verbose:

                debug_exp = False
                if debug_exp:    
                    #exp_Vt by integrating the expiratory flow_signal
                    print(f"valleys_flow[0][{peak}+1] : {valleys_flow[0][peak+1]}")
                    #print(f"peak_flow[0][{peak}] : {peaks_flow[0][peak]}")
                    #print(f"len y_expVt: {len(esoData.loc[peaks_flow[0][peak]:valleys_flow[0][peak+1],ModifiedFlow])} " + f" at peak: {peak}")
                    #print(f"len x_expVt: {len(np.arange(peaks_flow[0][peak],valleys_flow[0][peak+1]+1))} ")

            if np.isnan(esoData_bins.at[peak,ModifiedPeso]) == False: 
                #Create a breath column for plotting purposes
                esoData_bins.at[peak,peak_col] = peak

    return esoData_bins




# %% Grid_Search
def grid_search_full(esoData, esoData_bins,breathD,pat_Nr,verbose=False):
    importlib.reload(halp)
    #Grid search used for this step
    b_amt = len(breathD)
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

        C_best = 0.0000 #Same logic but reversed
        best_C_loss = 10000000
        global tot_C_loss
        tot_C_loss = 0

        
        if verbose: halp.verbose_fnc(color.UNDERLINE + f"**CURRENT PART IS: {part}**" + color.END)
            
        #Set prefixes for retrieving correct parts
        ModifiedPeso,ModifiedPao,peak_col,ModifiedFlow,exp_Flow,insp_Flow,insp_Vt,exp_Vt,exp_Time_Const,Pplat,insp_Raw,exp_Raw = halp.prefix_Factory(part, 'ModifiedPeso',
                                                                'ModifiedPao',
                                                                'breath_col',
                                                                'ModifiedFlow',
                                                                'exp_Flow',
                                                                'insp_Flow',
                                                                'insp_Vt',
                                                                'exp_Vt',
                                                                'exp_Time_Const',
                                                                'Pplat',
                                                                'insp_Raw',
                                                                'exp_Raw')
        
        #Set a specific compliance
        for C in C_range:
            #reset tot loss at every compliance
            #print(f"tot_C_loss pre-reset: {tot_C_loss}")
            tot_C_loss = 0
           # print(f"Total loss post reset is \n {tot_C_loss}")
            

        #Loop through every breath
            for breath in range(b_amt):

                    #Check if current breath exists or is NaN (necessary for variable trial test lengths)
                if np.isnan(esoData_bins.at[breath,ModifiedPeso]) == False: 
                    #Calculate loss for current breath
                    j = compliance_cost_full(esoData_bins.at[breath,ModifiedPeso],
                                        esoData_bins.at[breath,ModifiedPao],
                                        esoData_bins.at[breath,insp_Vt],
                                        PEEP[part-1],
                                        esoData_bins.at[breath,insp_Raw],
                                        esoData_bins.at[breath,insp_Flow],
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


def grid_search_no_flow(esoData, esoData_bins,breathD,pat_Nr,verbose=False):

    
    #Grid search used for this step
    b_amt = len(breathD)
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
        C_best = 0.0000 #Same logic but reversed
        best_C_loss = 10000000
        global tot_C_loss
        tot_C_loss = 0

        
        if verbose: halp.verbose_fnc(color.UNDERLINE + f"**CURRENT PART IS: {part}**" + color.END)
            
        #Set prefixes for retrieving correct parts
        ModifiedPeso,ModifiedPao,peak_col,insp_Vt,exp_Vt= halp.prefix_Factory(part, 'ModifiedPeso',
                                                                'ModifiedPao',
                                                                'breath_col',
                                                                'insp_Vt',
                                                                'exp_Vt')    
        #Set a specific compliance
        for C in C_range:
            #reset tot loss at every compliance
            #print(f"tot_C_loss pre-reset: {tot_C_loss}")
            tot_C_loss = 0
           # print(f"Total loss post reset is \n {tot_C_loss}")
        #Loop through every breath
            for breath in range(b_amt):

                #Check if current breath exists or is NaN (necessary for variable trial test lengths)
                if np.isnan(esoData_bins.at[breath,ModifiedPeso]) == False: 
                    #Calculate loss for current breath
                    if breath == 50 and C in np.arange(50,350,50):
                        print(f"at breath 50 Vt/C: {(esoData_bins.at[breath,insp_Vt]*1000)/C} \n pao: {esoData_bins.at[breath,ModifiedPao]} \n peso: {esoData_bins.at[breath,ModifiedPeso]} ")
                    j = compliance_cost_no_flow(peso = esoData_bins.at[breath,ModifiedPeso], #cmH2O
                                        pao = esoData_bins.at[breath,ModifiedPao],
                                        #pao = PS[part],#cmH2O
                                        Vt = (esoData_bins.at[breath,insp_Vt]*1000)*10, #L, converted to mL
                                        PEEP = PEEP[part],#cmH2O
                                        C = C,
                                        peso_var = esoData_bins[ModifiedPeso].var(),
                                        breath = breath,
                                        verbose=False)
                    #if np.isnan(j): print(f"J is NaN at breath {breath}")

                    
                    if verbose:
                        if breath % 90 == 0 and C == C_range[0]: print(f"breath {breath} j = {j}")

                    #Increase total loss for the part by the loss for current breath
                    if np.isnan(j) == False: tot_C_loss += j

            
            
            #print(f"tot_C_loss: {tot_C_loss}")      
            if tot_C_loss < best_C_loss:
                best_C_loss = tot_C_loss
                C_best = C
            
            hk_C_loss[C] = {"C" : C, "tot_C_loss" : tot_C_loss}

            
                    

            
        #Housekeep for entire part
        hk_parts[part] = {"C_best" : C_best, "best_C_loss" : best_C_loss,"hk_C_loss" : hk_C_loss}

    return hk_parts


def get_super(x):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)