# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 17:02:20 2023

@author: Lasse
"""
# %% Original Attempt at loading data (since switched to saving matlab array struct to .csv and loading it that way)

import scipy.io
import numpy as np
import pandas as pd

#Load array of structs - 4th column is "parts"
mat = scipy.io.loadmat('./protpesData/protpes001_forstud.mat')

#Load struct containing patient data
parts_struct = mat["parts"]

#
breathD = np.array(parts_struct[()][:,:])

#  Create Test section
#dataframe of all patient data
#Convert dictionary to series
test_struct = pd.Series(mat)


#Convert series to dataframe. two columns; label and list. 
test_Series = pd.DataFrame({'label':test_struct.index,'list':test_struct.values})  

#Access patient data in 'parts' colummn of dataframe (3rd row in list column)
test_patientD = test_Series.loc[3,'list']    

#Convert array of objects into a pandas dataframe        
patientD_DF = pd.DataFrame(test_patientD)

test_breathD = patientD_DF.loc[0,0]


#  PATIENT DATA AND ESO DATA UNPACKED IN MATLAB
patientD_mat = scipy.io.loadmat('./Breath_Data.mat')

test_struct = pd.Series(patientD_mat)

test_Series = pd.DataFrame({'label':test_struct.index,'list':test_struct.values}) 

test_patientD = test_Series.loc[3,'list']  

testtest = pd.DataFrame.from_dict(patientD_mat)


# %% Check indexes of NAN values
#Finds NAN indexes
index = breathD[col].index[breathD[col].isna()]
#Appends indexes to list
df_index = breathD.index.values.tolist()
#Use list comprehension to create a list containing NAN indexes
[df_index.index(i) for i in index]
#Run the Moving Average Filter over the 20 value


# %% Check inequality between Vt and Vtinsp (They are equal at avery index)
for i in range(259):    
    if breathD.at[i,'Vt'] != breathD.at[i,'Vtinsp']:
        print("They differ at index:")
        print(i)
        
# %% Find the avg breath duration when shortbreath == 1
balance = 0
count = 0
for i in range(259):
    if breathD.at[i,"ShortBreath"] == 1:
        balance += breathD.at[i,"breathDuration"]
        count += 1
print(balance/count)