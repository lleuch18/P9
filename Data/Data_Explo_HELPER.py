# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 16:42:42 2023

@author: Lasse
"""

import pandas as pd
import numpy as np



# %% All data is saved in a single row, and must thus be rearranged

# %% rearrange breathD (each column has 260 rows)

def dataloader(numCols, numRows, filepath, dfName):
    """
    

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
    
    numcols = numCols
    numrows = numRows
    
    if dfName == "breathD":
        colnames = ['VA', 'bd', 'VCO2', 'EELV', 'EE', 'Vtexp', 'VCO2exp', 'VO2exp', 
               'FetCO2', 'FetCO2Monitor', 'FetO2','FetO2Monitor', 'FiO2', 'FiO2Monitor',
               'FiO2Raw', 'Vtinsp', 'VCO2insp', 'VO2insp', 'dVt', 'Vt', 'VO2', 'RQ',
               'VolCal', 'dTCO2', 'dTO2', 'validBreath', 'validRQ', 'validSync',
               'validVCO2', 'validVol', 'cummulValidRQ', 'inspStart', 'expStart',
               'remPoints', 'TrappingFraction', 'ShortBreath', 'FetCO2StdDev2',
               'ExpVolStart', 'breathDuration','FetCO2Raw', 'Rf'
               ]
    elif dfName == "esoData":
        colnames = ['Time', 'flow', 'pao', 'peso', 'pgastric', 'vol', 'ptp', 'ModifiedFlow',
               'ModifiedPao', 'ModifiedPeso', 'TimeMinRel', 'TimeMinAbs']
    elif dfName == "FFFT":
    #Flow, FCO2, FO2, Time
        colnames = ['Flow', 'FCO2', 'FO2', 'TimeMinRel', 'TimeMinAbs', 'rawTime']

    df = pd.read_csv(filepath)
    mod_df = pd.DataFrame(index=np.arange(numrows), columns=colnames)
    
    count=0
    
    for j in range(numcols): #Loop through every column
        for i in range(numrows): #Loop through every row
            mod_df.iat[i,j] = df.iat[0,count+i] #For every loop, add the next 260 entries to mod_BreathD
        count+=numrows
    return mod_df


        
def MovingAverage(cols, df, verbose=False):
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