# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 16:42:42 2023

@author: Lasse
"""

import pandas as pd
import numpy as np
import os
import PySimpleGUI as sg
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List



# Patient Manager
def patientManager(patientNumber,dfName,verbose=False):
    
    """
    
    Parameters
    ----------
    patientNumber : patient directory from which to load data
    
    dfName : name of .csv to load from patient directory, is Null unless explicitly stated
    
    entire : if true, loads entire patient directory
    
    Returns
    ----------
    df : Dataframe containing specificly requested part of patients data
    
    """
    
    #Converts the given number to a patient directory
    patient = "patient" + str(patientNumber)
    
    #filepath of parent directory
    parent_dir = os.path.join("patients", patient)   
    
    df_list = []
    
    #loads all data in patient directory 
    if dfName == "entire":
        for part in range(1,13):
            #Converts the partNr to a string, in order to create the specific filepath for the directory
            partStr = "part" + str(part)
            part_dir = os.path.join(parent_dir,partStr)
            
            #Create the suffix in order to load the specific file
            suffix = str(patientNumber) + str(part) + ".csv"
            
            #Checks if the specific parts directory is empty. If !empty, load the data.
            if os.listdir(part_dir):          
                    
                    if verbose:
                        print(f"FOR KW ENTIRE, FILEPATH IS {part_dir}")
                    df1, df2, df3 =  return_entire(part, part_dir, patientNumber, dfName)
                    df_list.append(df1);df_list.append(df2);df_list.append(df3);
        if verbose:
            print("Error at line 60:")
            print(f"type of df_list: {type(df_list)}, Length of df_list: {len(df_list)}")
        breathD, esoData, FFFT = concat_Parts(df_list, dfName)
        
        if verbose:
            print(":::AFTER CONCATINATION OF DATAFRAMES:::")
            print(f"type of breathD: {type(breathD)}, Length of breathD: {len(breathD)}, Columns of breathD: {len(breathD.columns)}")
            print(f"type of esoData: {type(esoData)}, Length of esoData: {len(esoData)}, Columns of esoData: {len(esoData.columns)}")
            print(f"type of FFFT: {type(FFFT)}, Length of FFFT: {len(FFFT)}, Columns of FFFT: {len(esoData.columns)}")
        return breathD, esoData, FFFT
        
      
    #Loads specific part of data depending on input
    if dfName in ["breathD", "esoData", "FFFT"]:
        for part in range(1, 13):
            partStr = "part" + str(part)
            part_dir = os.path.join(parent_dir,partStr)
            
            #Create the suffix in order to load the specific file
            suffix = str(patientNumber) + str(part) + ".csv"
            
            if os.listdir(part_dir):
                #Adds .csv file extension
                dfName_mod = dfName + suffix
                #creates the relative filepath from C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data
                filepath = os.path.join(part_dir,dfName_mod)           
                
                
                #breathD has special conditions requiring custom loader function
                if dfName == "breathD":
                    print(f"FILEPATH IS {filepath}")
                    df = breathDLoader(filepath,part)
                    #Rename column names to reflect part of trial data. 2 = part2, 3 = part 3 etc.
                    if part > 1:
                        df.rename(columns=lambda x: str(part)+x,inplace=True)
                    df = NaN_Cleaner(df)#,verbose=True)
                    cols = df.columns
                    df = nan_movingAverage(df, cols)                    
                    df_list.append(df)
                #esoData or FFT loaded directly
                else:
                    print(f"FILEPATH IS {filepath}")            
                    alt_df = pd.read_csv(filepath); alt_df = NaN_Cleaner(alt_df)#,verbose=True)
                    #if part > 1:
                    alt_df.rename(columns=lambda x: str(part)+x,inplace=True)
                    cols = alt_df.columns; alt_df = nan_movingAverage(alt_df, cols);
                    df_list.append(alt_df)
        df = concat_Parts(df_list, dfName)
        return df
    

#  rearrange breathD (each column has 260 rows)
def breathDLoader(filepath,part):
    """
    NOTE: Dynamic loading for esoData and FFFT turned out to be obsolete
    

    Parameters
    ----------
    numCols : Columns. # breathD = 41, esoData = 12, FFFT = 6
    
    numRows : Rows. # breathD = 260, esoData = 17982, FFFT = 36001
    
    filepath : Filepath of the .csv data.
    
    dfName : Name of the assigned dataframe (used for defining column names).

    Returns
    -------
    mod_df : A dataframe with the corresponding data and column names.

    """
    
    #Defines column names for breathD, to be used in the creation of the dataframe
    colnames = ['VA', 'bd', 'VCO2', 'EELV', 'EE', 'Vtexp', 'VCO2exp', 'VO2exp', 
           'FetCO2', 'FetCO2Monitor', 'FetO2','FetO2Monitor', 'FiO2', 'FiO2Monitor',
           'FiO2Raw', 'Vtinsp', 'VCO2insp', 'VO2insp', 'dVt', 'Vt', 'VO2', 'RQ',
           'VolCal', 'dTCO2', 'dTO2', 'validBreath', 'validRQ', 'validSync',
           'validVCO2', 'validVol', 'cummulValidRQ', 'inspStart', 'expStart',
           'remPoints', 'TrappingFraction', 'ShortBreath', 'FetCO2StdDev2',
           'ExpVolStart', 'breathDuration','FetCO2Raw', 'Rf'
           ]
        
    
    ### Load df, and dynamically define row length    
    df = pd.read_csv(filepath)
    
    #Each column represents 1 row index
    total_indexes = len(df.columns)    
    #breathD always contains 41 columns (pre-cleaning). Dividing total indexes by 41 thus gives the dynamic length of each row.
    numCols = 41
    numRows = int(total_indexes/numCols)
    
    mod_df = pd.DataFrame(index=np.arange(numRows), columns=colnames)
    if part > 1:
        mod_df.rename(columns=lambda x: str(part)+x)
    
    count=0
    
    for j in range(numCols): #Loop through every column
        for i in range(numRows): #Loop through every row
            mod_df.iat[i,j] = df.iat[0,count+i-1] #For every loop, add the next {numRows} entries to mod_BreathD
        count+=numRows
        #colnames[3] will always be 'EELV' + suffix
    mod_df.drop([colnames[3]],axis=1,inplace=True)
    return mod_df


        
def nan_movingAverage(df, cols, verbose=False):
    """
    Moving Average over to smooth out NAN values

    Parameters
    ----------
    cols : List of column names
    df : The dataframe containing the columns to be smoothed.

    Returns
    -------
    Smoothed out dataframe.
    
    Improvement ideas:
        Round up TrappingFraction to mimic remaining data entries (0.55 instead of 0.5329)

    """

    for col in cols:
        #Finds NAN indexes
        index = df[col].index[df[col].isna()]        
        #Appends indexes to list
        df_index = df.index.values.tolist()
        #Use list comprehension to create a list containing NAN indexes
        NAN_index = [df_index.index(i) for i in index]        
        #Run the Moving Average Filter over the 20 values post-NAN
        num_NAN = index.size        
        if verbose:
            print(f"NAN_index for {col}: {NAN_index}")
            print(f"NAN_index for {col}: {NAN_index}")
            print(f"num_NAN for {col}: {num_NAN}")
        for NAN in NAN_index:
            #If moving average exceeds length of df, run moving average 20 indexes backwards
            if (NAN+num_NAN > len(df)):
                df.at[NAN,col] = df.loc[(NAN-20):(NAN),col].mean()
            else:
                df.at[NAN,col] = df.loc[(NAN+num_NAN):(NAN+num_NAN)+20,col].mean()
            
            
    return df

def unsquare_moving_average(df,col,num_points):
    """
    #####NEEDS WORK######
    Loops through the specified column. If the sum of index-values at the desired range == 0, it is assumed to be a square wave. Thus, a moving average filter will 
    give it a natural smoothing.

    Parameters
    ----------
    df : dataframe
    col : column of dataframe to filter.
    num_points : the range of indexes pre- and post of current indexes to be filtered through. 

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    """
    for i in range(len(df)):
        count = num_points*10
        if df.loc[(i-num_points):(i+num_points),col].sum() % df.loc[1+(i-num_points):1+(i+num_points),col].sum() == 0:
            if i % 100 == 0:
                print(f"Moving average operation performed at index {i}")
            if df.loc[(i-count*2):(i-count),col].mean() > df.loc[1+(i-num_points):1+(i+num_points),col].mean():
                df.at[i,col] = df.loc[i-count*2:i-count,col].median()
            
            elif df.loc[(i+count*2):(i+count),col].mean() > df.loc[1+(i-num_points):1+(i+num_points),col].mean():
                #count += num_points                
                #num_points*2 will be filtered - in order to increase chance of smoothing out square wave.
                df.at[i,col] = df.loc[i+count*2:i+count,col].median()
               
            
    
    return df

def dynamic_moving_median(df, column, threshold, count_increment,median_length,verbose=False):
    """
    

    Parameters
    ----------
    df : Dataframe
    threshold : The minimum-threshold to which the median filters filters values.
    
    column : The column whose data will be filtered
    
    threshold : the threshold above which the erroneous measurement should be
    
    count_increment : how many values pre- and post the current values are considered for the median calculation.
    
    median_length : the minimum length of the intermediary dataframe used when calculating the median (if only 1 data point meets criteria, median is less reflective of true value)
    

    Returns
    -------
    df : Median_Filtered dataframe

    """
   
    for i in range(len(df)):
        if verbose:
            if i % 10000 == 0:
                print(f"total iterations of moving_median: {i}")

      
        count = 0
        if df.at[i,column] < threshold:
            while df.at[i,column] < threshold:
                #print(f"moving_median at index {i} reached count: {count}")         
                #Get index values as a series
                  
                t_series =  df.loc[(i-count):(i+count),column]            
                #Convert the series to df
                t_df = t_series.to_frame()
                
                if len(t_df.loc[t_df[column]>threshold]) >= median_length:
                    #print(f"Reached if-statement at index: {i}")
                #Find all values within t_df which are above threshold, compute median                            
                    df.at[i,column] = t_df.loc[t_df[column]>threshold].median()
                    #print(f"median = {t_df.loc[t_df[column]>threshold].median()}")
                count += count_increment
                #print(f"count = {count}")
                
    return df
                

def NaN_Cleaner(df, verbose=False):
    if verbose:
        # Detect  counts
        print("NaN counts for dataframe:")
        print(df.isna().sum())
        print("Length of breathD pre-removal:")
        print(len(df))

    # Remove rows with 1 NAN count    
    for col in df.columns:
        if df[col].isna().sum() == 1:
            df.dropna(subset=col, inplace = True)
    # Reset the index after removal of NaN rows
    df.reset_index(drop=True, inplace=True)
    if verbose:
        print("Length of dataframe post-removal:")
        print(len(df))
        
    return df
        
def sub_plotter(df,col1,col2,n):
    title1 = col1
    title2 = col2
    breath_length = math.floor(len(df)/20)
    #fig, (ax1, ax2, ax3) = plt.subplots(1,2) #, ax4
    fig, ax = plt.subplots(2,2,constrained_layout=True)
    n_next = n+1
    
    if n <= 1:
        ax1.plot(df.loc[0:breath_length,col1],df.loc[0:breath_length,col2])
        ax2.plot(df.loc[breath_length:breath_length*2,col1],df.loc[breath_length:breath_length*2,col2])
        ax3.plot(df.loc[breath_length*2:breath_length*3,col1],df.loc[breath_length*2:breath_length*3,col2])
        ax1.set_xlabel(col1);ax1.set_ylabel(col2);
        ax2.set_xlabel(col1);ax1.set_ylabel(col2);
        ax3.set_xlabel(col1);ax1.set_ylabel(col2);
        #ax4.plot(df.loc[breath_length*3:breath_length*4,col1],df.loc[breath_length*3:breath_length*4,col2])
    else:
        print(n*breath_length)
        ax[0,0].plot(df.loc[n*breath_length:breath_length*n_next,col1],df.loc[n*breath_length:breath_length*n_next,col2])
        ax[0,1].plot(df.loc[breath_length*2*n:breath_length*2*n_next,col1],df.loc[breath_length*2*n:breath_length*2*n_next,col2])
        ax[1,0].plot(df.loc[breath_length*3*n:breath_length*3*n_next,col1],df.loc[breath_length*3*n:breath_length*3*n_next,col2])
        ax[1,1].plot(df.loc[breath_length*4*n:breath_length*4*n_next,col1],df.loc[breath_length*4*n:breath_length*4*n_next,col2])
        ax[0,0].set_xlabel(col1);ax[0,0].set_ylabel(col2);
        ax[0,1].set_xlabel(col1);ax[0,1].set_ylabel(col2);
        ax[1,0].set_xlabel(col1);ax[1,0].set_ylabel(col2);
        ax[1,1].set_xlabel(col1);ax[1,1].set_ylabel(col2);
    return fig

def draw_figure(canvas,
                figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def return_entire(part,part_dir,patientNumber,dfName): #,hotfix_dict #parent_dir
    
    
    """
    

    Parameters
    ----------
    part : Which part of the data to return.
    
    parent_dir : filepath of the parent directory
    
    patientNumber : which patient number to load
    
    dfName : name of the df entered in PatientManager

    Returns
    -------
    For each part of patient data returns:
    breathD dataframe
        
    esoData dataframe
        
    FFFT dataframe
        

    """
    
    
    #Converts the partNr to a string, in order to create the specific filepath for the directory
    #partStr = "part" + str(part)
    #part_dir = os.path.join(parent_dir,partStr)
    
    #Create the suffix in order to load the specific file
    suffix = str(patientNumber) + str(part) + ".csv"
    
    
    #Create list of dataframes, to enable returning all at once. 
    #Global, in order to access dataframes at any scope in the GUI.
    global dflist        
    dfList = []
    
    #####For breathD#####
    fn_breathD = "breathD" + suffix
    filepath_breathD = os.path.join(part_dir,fn_breathD)
    #breathD has special conditions requiring custom loader function
    #breathD = breathDLoader(41, hotfix_dict[patientNumber], filepath_breathD, "breathD")    
    breathD = breathDLoader(filepath_breathD,part)
    #Rename column names, so that (starting with 2) part 2 has the prefix 2, part 3 has prefix 3 etc.
    #if part > 1:
    breathD.rename(columns=lambda x: str(part)+x,inplace=True)     
    
    #####For esoData#####
    fn_esoData = "esoData" + suffix
    filepath_esoData = os.path.join(part_dir,fn_esoData)
    esoData = pd.read_csv(filepath_esoData)
    
    #if part > 1:
    esoData.rename(columns=lambda x: str(part)+x,inplace=True)
    
    
    #####For FFFT#####
    fn_FFFT = "FFFT" + suffix
    filepath_FFFT = os.path.join(part_dir,fn_FFFT)       
    FFFT = pd.read_csv(filepath_FFFT)
    #if part > 1:
    FFFT.rename(columns=lambda x: str(part)+x,inplace=True)
    
    dfList.append(breathD);dfList.append(esoData);dfList.append(FFFT);
    
    for temp_df in dfList:
        temp_df = NaN_Cleaner(temp_df)#,verbose=True)            
        cols = temp_df.columns
        temp_df = nan_movingAverage(temp_df, cols)
    return dfList[0], dfList[1], dfList[2]


def concat_Parts(df_list,dfName):
    """
    Concatinates the different parts of the patient data into a single dataframe. Each column represents a part of the patient data.
    Does so by receiving the full list of returned dataframes, appending each to a temporary list according to their respective data (breathD, esoData, FFFT),
    and concatinating them.

    Parameters
    ----------
    df_list : The list of dataframes, created if the keyword "entire" is entered into patientDataManager
    
    dfName : The name of the df to be returned (entire, breathD, esoData or FFFT)

    Returns
    -------
    breathD, esoData and FFT, concatinated for each part of the patients trial data.

    """
    
    #Code to be executed if dfName == "entire".
    if dfName == "entire":        
        #For loop concatinates the parts into single dataframes 
        #Create temporary lists which will be concatinated into single dataframes
        temp_breathD = []
        temp_esoData = []
        temp_FFFT = []
        #Checking if df is in the specified range, assures that the correct df will be appened, since 0,3,6 etc. are breathD, 1,4,7 etc. are esoData and so forth.
        for df in range(len(df_list)):
            if df in range(0,30,3):
                temp_breathD.append(df_list[df])
            elif df in range(1,30,3):
                temp_esoData.append(df_list[df])                
            elif df in range(2,30,3):
                temp_FFFT.append(df_list[df])
                
        
        
        #Checks which length df_list has. This allows to dynamically load patient data which has varying parts, fx. 2 or 10 parts. Switch statement is
        #Necessary, since pd.concat() needs all df's to be concatinated at once (e.g. cannot use a for-loop to dynamically concatinate them)
        nrParts = len(temp_breathD)
        #print(f"Length of df_list: {nrParts}")
        match nrParts:            
            case 1:                    
                breathD = pd.concat(temp_breathD[0])
                esoData = pd.concat(temp_esoData[0])
                FFFT = pd.concat(temp_FFFT[0])
                
                
            case 2:                                
                breathD = pd.concat([temp_breathD[0],temp_breathD[1]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1]], axis=1)
                
                
            case 3:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2]], axis=1)
                
            case 4:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3]], axis=1)
                
            case 5:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3],temp_breathD[4]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3],temp_esoData[4]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3],temp_FFFT[4]], axis=1)
                
            case 6:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3],temp_breathD[4],temp_breathD[5]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3],temp_esoData[4],temp_esoData[5]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3],temp_FFFT[4],temp_FFFT[5]], axis=1)
                
            case 7: 
                               
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3],temp_breathD[4],temp_breathD[5],temp_breathD[6]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3],temp_esoData[4],temp_esoData[5],temp_esoData[6]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3],temp_FFFT[4],temp_FFFT[5],temp_FFFT[6]], axis=1)
                
                
                
            case 8:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3],temp_breathD[4],temp_breathD[5],temp_breathD[6],
                                    temp_breathD[7]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3],temp_esoData[4],temp_esoData[5],temp_esoData[6],
                                    temp_esoData[7]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3],temp_FFFT[4],temp_FFFT[5],temp_FFFT[6],
                                 temp_FFFT[7]], axis=1)
                
                
            case 9:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3],temp_breathD[4],temp_breathD[5],temp_breathD[6],
                                    temp_breathD[7],temp_breathD[8]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3],temp_esoData[4],temp_esoData[5],temp_esoData[6],
                                    temp_esoData[7],temp_esoData[8]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3],temp_FFFT[4],temp_FFFT[5],temp_FFFT[6],
                                 temp_FFFT[7], temp_FFFT[8]], axis=1)
                
            case 10:                    
                breathD = pd.concat([temp_breathD[0],temp_breathD[1],temp_breathD[2],
                                    temp_breathD[3],temp_breathD[4],temp_breathD[5],temp_breathD[6],
                                    temp_breathD[7],temp_breathD[8],temp_breathD[9]], axis=1)
                esoData = pd.concat([temp_esoData[0],temp_esoData[1],temp_esoData[2],
                                    temp_esoData[3],temp_esoData[4],temp_esoData[5],temp_esoData[6],
                                    temp_esoData[7],temp_esoData[8],temp_esoData[9]], axis=1)
                FFFT = pd.concat([temp_FFFT[0],temp_FFFT[1],temp_FFFT[2],
                                 temp_FFFT[3],temp_FFFT[4],temp_FFFT[5],temp_FFFT[6],
                                 temp_FFFT[7], temp_FFFT[8],temp_FFFT[9]], axis=1)
        
        return breathD, esoData, FFFT
    
    #Code to be executed if individual dataframes are to be loaded. 
    #Functionality is essentialy identical to previous codeblock (i.e. if dfName == entire)
    elif dfName in ["breathD", "esoData", "FFFT"]:
        temp_df = []
        for df in range(len(df_list)):            
                temp_df.append(df_list[df])
                
        nrParts = len(temp_df)
        match nrParts:            
            case 1:                    
                df = pd.concat(temp_df[0])                
                
            case 2:                                
                df = pd.concat([temp_df[0],temp_df[1]], axis=1)                
                
            case 3:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2]], axis=1)
                
            case 4:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3]], axis=1)
            case 5:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3],temp_df[4]], axis=1)
                
            case 6:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3],temp_df[4],temp_df[5]], axis=1)
                
            case 7: 
                                 
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3],temp_df[4],temp_df[5],temp_df[6]], axis=1)
                
                
            case 8:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3],temp_df[4],temp_df[5],temp_df[6],
                                    temp_df[7]], axis=1)                
                
            case 9:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3],temp_df[4],temp_df[5],temp_df[6],
                                    temp_df[7],temp_df[8]], axis=1)                
            case 10:                    
                df = pd.concat([temp_df[0],temp_df[1],temp_df[2],
                                    temp_df[3],temp_df[4],temp_df[5],temp_df[6],
                                    temp_df[7],temp_df[8],temp_df[9]], axis=1)                
        
        return df

  
            
def breathD_Transposer():
    """
        breathD is currently saved in a 1-row csv file. The breathDLoader() function then correctly loads this data into a dataframe.
        The purpose of this function, is to save the data in a correctly formatted .csv file.
    
        Returns
        -------
        None.
    
        """
    for patientNumber in range(1,22):    
        patient = "patient" + str(patientNumber)
        parent_dir = os.path.join("patients",patient)
        for part in range(1,13):
            partStr = "part" + str(part)
            part_dir = os.path.join(parent_dir,partStr)
            
            suffix = str(patientNumber) + str(part) + ".csv"
            
            directory = os.listdir(part_dir)
            if len(directory) != 0:
                #Adds .csv file extension
                dfName_mod = "breathD" + suffix
                #creates the relative filepath from C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data
                filepath = os.path.join(part_dir,dfName_mod)            
            
                breathD = breathDLoader(filepath, part)
                
                
                
                csv_name = "breathD" + str(patientNumber) + str(part) + "New" +".csv"
                tempFilePath = os.path.join(part_dir,csv_name)
                
                
                breathD = NaN_Cleaner(breathD)
                cols = breathD.columns
                breathD = nan_movingAverage(breathD, cols)
                
                breathD.to_csv(tempFilePath)
                

class Ventilator:
    
    
      
    
    def __init__(self):
        #print("NOTE: For patient 5, 16 and 21, missing values have been imputated ")
        #print("The imputated values are are:")
        #print("Patient 5: part 3 \n" + "Patient 16: part 4 \n" + "Patient 21: part 2" )
        
        
        self.PS = {'1' : [5,10,15,13,11,9,9],
              '2' : [6,4,18,16,14,12,12],
              '3' : [21,19,15,13,7,7,9,9,7,14],
              '4' : [14,12,10,8,6,12,14],
              '5' : [5,5,5], ###NOTE 3rd list value (2nd index) is actually NaN - make a note of this when calling the getter
              '6' : [12,4],
              '7' : [9,9,15,13,9,5],
              '8' : [10,10,9,10,8,10,10],
              '9' : [4,3,3,5,3,5,3],
              '10' : [3,4,3,3,3,9,7,5],
              '11' : [11,9,8,10,12,12,10,11,12],
              '12' : [4,3,12,5,3,9,4,3,6],
              '13' : [10,10],
              '14' : [10,10],
              '15' : [10,10],
              '16' : [6,4,3,4,4,12,10,8,6], ###NOTE 4rd list value (3rd index) is actually NaN - make a note of this when calling the getter
              '17' : [7,9,10,5,7,8],
              '18' : [4,3,3,9,7,5,3],
              '19' : [6,12,10,8,4],
              '20' : [6,3,4,3,12,10,8,6],
              '21' : [7,6,5,3,12,10,8,6] ###NOTE 2nd list value is actually NaN - make a note of this when calling the getter          
              }
        
        self.PEEP = {'1' : [6,6,6,6,6,6,5],
                '2' : [10,10,10,10,10,10,8],
                '3' : [8,8,8,8,8,8,8,8,8,8],
                '4' : [15,15,15,15,15,10,5],
                '5' : [4,12,8], ###NOTE 3rd list value is actually NaN - make a note of this when calling the getter
                '6' : [8,8],
                '7' : [10,10,10,10,10,10],
                '8' : [4,4,8,12,12,12,4],
                '9' : [7,7,7,10,10,4,4],
                '10' : [12,12,12,12,12,12,12,12],
                '11' : [9,9,9,6,6,3,3,3,9],
                '12' : [6,6,12,12,12,18,18,18,6],
                '13' : [3,12],
                '14' : [9,3],
                '15' : [5,5],
                '16' : [5,5,5,5,5,5,5,5,5], ###NOTE 3rd list value is actually NaN - make a note of this when calling the getter
                '17' : [8,8,8,8,8,8],
                '18' : [5,5,5,5,5,5,5],
                '19' : [4,4,4,4,4],
                '20' : [5,5,5,5,5,5,5,5],
                '21' : [10,10,10,10,10,10,10,10,10] ###NOTE 2nd list value is actually NaN - make a note of this when calling the getter
                }
    
    
    def get_Settings(self,patientNr):
        return self.PS.get(str(patientNr)),self.PEEP.get(str(patientNr))
    

def prefix_Factory(part: int, *cols: str):
    prefix = str(part)
    #Using sequence unpacking to return individual variables
    #Using 
    return tuple(prefix + col for col in cols)




    
def verbose_fnc(v1_message=None, v2_message=None,v3_message=None):
    if v1_message is not None:
        print(v1_message)
        
    if v2_message is not None:
        print(v2_message)
        
    if v3_message is not None:
        print(v3_message)
    

    



      

    
    