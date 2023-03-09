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


# %% Creates patient directories for every patient
import os
for patient in range(1,24):
    patientnr = "patient" + str(patient)
    cmd = 'mkdir ' + os.path.join("patients", patientnr)
    os.system(cmd)
    
# %% Every patient goes through several rotations during the clinical trial. Create folder for each part.
import os
for patient in range(1,24):
    for part in range(1,13):
        patientnr = "patient" + str(patient)
        partnr = "part" + str(part)        
        cmd = 'mkdir ' + os.path.join("patients", patientnr,partnr)
        os.system(cmd)
# %% Remove all files and subdirs in order to simplify making changes
import os
for patient in range(1,24):
        patientnr = "patient" + str(patient)        
        cmd = 'RMDIR /s /q ' + os.path.join("patients", patientnr)
        os.system(cmd)
    
#%% Testing parts of the patientmanager helper function

import Data_Explo_HELPER as halp
hotfix_dict = {1: 260, 2:195, 3:224, 4:280, 5:142, 6:184,7:264,
               8:296,9:274,10:185,11:178,12:181,13:163,14:220,15:278,
               16:355, 17:158, 18:292, 19:96, 20:136, 21:133, 22:217}

filepath_breathD = os.path.join("patients","patient1","breathD.csv")
breathD = halp.breathDLoader(41, hotfix_dict[1], filepath_breathD, "breathD")

breathD = halp.NaN_Cleaner(breathD,verbose=True)
breathD = halp.movingAverage(breathD, breathD.columns)  
            
breathD.info()


df = halp.patientManager('1', 'FFFT')

# %% Datatype cleaning

##Check datatypes
#Matlab porting caused integers to be 'int64' and decimals to be 'float64'


#Typecast dataframe to 'float64' if mixed, and int64 if only integers

#%% Check if column dVt is the change in Vt since last measurement (IT IS NOT)
for i in range(5,30,5):
    print("Difference Between Neighbouring Indexes:")
    print(breathD.at[i,'Vt']-breathD.at[i+1,'Vt'])
    print("dVt at 1. index:")
    print(breathD.at[i,'dVt'])
    print("dVt at 2. index:")
    print(breathD.at[i+1,'dVt'])
    


#%% Testing dataframe concatination
d1 = {
    'Name':['Ram','Shyam','Seeta','Geeta'],
    'Grades':['A','C','A','B']
}

d2 = {
    'Name':['Jhon','Wilson','Mike'],
    'Grades':['D','C','A']
}


d3 = {
    'Name':['Jhsdf','Wilsdf','Mike','Ken','Bent'],
    'Grades':['D','C','A','K','U']
}

df1 = pd.DataFrame(d1)
df2 = pd.DataFrame(d2)
df3 = pd.DataFrame(d3)


result = pd.concat([df1,df2,df3],axis=1)
result = pd.concat([df2])


for i in range(10):
    print(i)
    
#%% Verbose code. Used at beginning of project, before complexity of dataloading was mapped out.
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
    
#Static hot-fix for getting the right amount of rows to load breathD
hotfix_dict = {'1': 260, '2':195, '3':224, '4':280, '5':142, '6':184,'7':264,
               '8':296,'9':274,'10':185,'11':178,'12':181,'13':163,'14':220,'15':278,
               '16':355, '17':158, '18':292, '19':96, '20':136, '21':133, '22':217}




#%% Df list should be replaced with 0 to access the right index
match nrParts:            
    case 1:                    
        #breathD = pd.concat(temp_breathD[0])
        #esoData = pd.concat(temp_esoData[df_list])
        #FFFT = pd.concat(temp_FFFT[df_list])
        return temp_breathD[0], temp_esoData[0], temp_FFFT[0]
    case 2:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1])
        return breathD, esoData, FFFT
    case 3:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2])
        return breathD, esoData, FFFT
    case 4:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3])
        return breathD, esoData, FFFT
    case 5:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3],temp_breathD[df_list+4])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3],temp_esoData[df_list+4])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3],temp_FFFT[df_list+4])
        return breathD, esoData, FFFT
    case 6:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3],temp_breathD[df_list+4],temp_breathD[df_list+5])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3],temp_esoData[df_list+4],temp_esoData[df_list+5])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3],temp_FFFT[df_list+4],temp_FFFT[df_list+5])
        return breathD, esoData, FFFT
    case 7:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3],temp_breathD[df_list+4],temp_breathD[df_list+5],temp_breathD[df_list+6])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3],temp_esoData[df_list+4],temp_esoData[df_list+5],temp_esoData[df_list+6])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3],temp_FFFT[df_list+4],temp_FFFT[df_list+5],temp_FFFT[df_list+6])
        return breathD, esoData, FFFT
    case 8:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3],temp_breathD[df_list+4],temp_breathD[df_list+5],temp_breathD[df_list+6],
                            temp_breathD[df_list+7])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3],temp_esoData[df_list+4],temp_esoData[df_list+5],temp_esoData[df_list+6],
                            temp_esoData[df_list+7])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3],temp_FFFT[df_list+4],temp_FFFT[df_list+5],temp_FFFT[df_list+6],
                         temp_FFFT[df_list+7])
        return breathD, esoData, FFFT
    case 9:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3],temp_breathD[df_list+4],temp_breathD[df_list+5],temp_breathD[df_list+6],
                            temp_breathD[df_list+7],temp_breathD[df_list+8])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3],temp_esoData[df_list+4],temp_esoData[df_list+5],temp_esoData[df_list+6],
                            temp_esoData[df_list+7],temp_esoData[df_list+8])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3],temp_FFFT[df_list+4],temp_FFFT[df_list+5],temp_FFFT[df_list+6],
                         temp_FFFT[df_list+7], temp_FFFT[df_list+8])
        return breathD, esoData, FFFT
    case 10:                    
        breathD = pd.concat(temp_breathD[df_list],temp_breathD[df_list+1],temp_breathD[df_list+2],
                            temp_breathD[df_list+3],temp_breathD[df_list+4],temp_breathD[df_list+5],temp_breathD[df_list+6],
                            temp_breathD[df_list+7],temp_breathD[df_list+8],temp_breathD[df_list+9])
        esoData = pd.concat(temp_esoData[df_list],temp_esoData[df_list+1],temp_esoData[df_list+2],
                            temp_esoData[df_list+3],temp_esoData[df_list+4],temp_esoData[df_list+5],temp_esoData[df_list+6],
                            temp_esoData[df_list+7],temp_esoData[df_list+8],temp_esoData[df_list+9])
        FFFT = pd.concat(temp_FFFT[df_list],temp_FFFT[df_list+1],temp_FFFT[df_list+2],
                         temp_FFFT[df_list+3],temp_FFFT[df_list+4],temp_FFFT[df_list+5],temp_FFFT[df_list+6],
                         temp_FFFT[df_list+7], temp_FFFT[df_list+8],temp_FFFT[df_list+9])
        return breathD, esoData, FFFT
