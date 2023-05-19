# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 17:02:20 2023

@author: Lasse
"""
# %% Original Attempt at loading data (since switched to saving matlab array struct to .csv and loading it that way)


patient = 11
breathD,esoData,FFFT = halp.patientManager(patient,'entire')


#Manual detection
part = 3
Time,ModifiedPeso,ModifiedPao,pao_peak,peso_peak = halp.prefix_Factory(part, 'Time','ModifiedPeso','ModifiedPao','pao_peak','peso_peak')

esoData = peak_halp.peak_adder(patient=11, esoData=esoData, pesoHeight=-3, pesoDistance=150, paoHeight=11.5, paoDistance=150)


trace1 = go.Scatter(
    x=esoData[Time],
    y=esoData[ModifiedPao],
    mode='markers+text',
    textposition='top center',
    text=esoData[pao_peak],
    name=ModifiedPao,
    marker=dict(
        color='green',
        size=1
               )
)

trace2 = go.Scatter(
    x=esoData[Time],
    y=esoData[ModifiedPeso],
    mode='markers+text',
    textposition='top center',
    text=esoData[peso_peak],
    name=ModifiedPeso,
    marker=dict(
        color='magenta',
        size=1
               )
)




fig = make_subplots(rows=2,cols=1,subplot_titles=('ModifiedPao','ModifiedPeso'))
fig.add_trace(trace1,row=1,col=1)
fig.add_trace(trace2,row=2,col=1)
fig['layout'].update(height = 600, width = 800, title = "Peaks Pao vs. Peso",xaxis=dict(
      tickangle=-90
    ),
    yaxis_title="P (cmH2O)",
    xaxis_title="Time (S" + comp_halp.get_super('-2')+')')

fig['layout']['xaxis']['title']="Time (S" + comp_halp.get_super("-2")+")"
fig['layout']['xaxis2']['title']="Time (S" + comp_halp.get_super("-2")+")"
fig['layout']['yaxis']['title']="P (cmH2O)"
fig['layout']['yaxis2']['title']="P (cmH2O)"

plot(fig)

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




######
#PLOTYXPRESS SUBPLOTTER
######
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4"))

fig.add_trace(
    go.Scatter(x=[1, 2, 3], y=[4, 5, 6]),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=[20, 30, 40], y=[50, 60, 70]),
    row=1, col=2
)

fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
fig.show()




####### CHECK DATA QUALITY THROUGH AMT OF CORRUPTED DATA #######
###NOTE: DIFFERING PART LENGTHS IMPUTATED BY NAN, WHICH MISREPRESENTS ACTUAL LENGTH###
save_csv = False
if save_csv:

    pt_dic = {}

    for patient in range(1,23):
        breathD, esoData, FFFT = halp.patientManager(patient,"entire")
        part_dic = {}


        quality_check = True
        parts = int(len(esoData.columns)/12)
        if quality_check:
            for part in range(1,parts+1):
                prefix = str(part)
                peso = prefix + 'peso'
                pao = prefix + 'pao'

                eso_count = 0
                pao_count = 0

                for i in range(len(esoData)):
                    if esoData.at[i,peso] < 130:
                        eso_count +=1
                    if esoData.at[i,pao] < 130:
                        pao_count +=1
                #print(color.BOLD + f"***for part{part}***" + color.END)
                #print(color.RED + f"Percentage peso corrupted data = {eso_count/len(esoData)*100}%" + color.END)
                #print(color.RED + f"Percentage pao corrupted data = {pao_count/len(esoData)*100}%" + color.END)
                part_dic[part] = {'peso' : round(eso_count/len(esoData)*100,2), 'pao' : round(pao_count/len(esoData)*100,2)}
            pt_dic[patient] = part_dic
            
        
    import csv

        
    field_names = ['peso', 'pao']
    for patient in range(1,23):
        suffix=str(patient)
        file_name = 'patient' + suffix + '.csv'

        corruption_data = []
        for part in range(1,len(pt_dic[patient])+1):

            corruption_data.append(pt_dic[patient][part])

        with open(file_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(corruption_data)



if special_test:
    if C % 100 == 0:
        print(color.BOLD + f"Value of hk_cost_form at C {C} is j = {hk_cost_form[C]}" + color.END)
        
        
        if special_test:
            print(f"values in hk_cost_form for breath {breath} are {hk_cost_form}")



def grid_search(esoData, esoData_bins,breathD,pat_Nr,verbose=False):
    #Grid search used for this step
    b_amt = len(esoData_bins)
    parts = int(len(esoData.columns)/12)
    #Retrieve vent settings
    PS, PEEP = halp.Ventilator().get_Settings(str(pat_Nr))
    #Define values for C
    #C_range = np.arange(1,120,0.1)
    C_range = np.arange(100,400,0.5)
    
    special_test = False

    #Housekeeping variables
    hk_parts = {}
    hk_breath = {}
    hk_cost_form = {}
    
    j = 0

    if verbose:
        halp.verbose_fnc(color.BOLD + f"****CURRENT PATIENT IS: {pat_Nr}****" + color.END)
    #For every part
    for part in range(1,parts+1):
        
        tot_loss = 0
        if verbose:
            halp.verbose_fnc(color.UNDERLINE + f"**CURRENT PART IS: {part}**" + color.END)

        tot_loss = 0
        peso, pao, Vt = halp.suffix_Factory(part,True,True,True)
        
        
        #Loop through every breath
        for breath in range(b_amt):
            if np.isnan(breath) == False:
                j_best = 100000
                C_best = 0.0000
                #Loop through all C values
                for C in C_range:
                    j = compliance_cost(esoData_bins.at[breath,peso], esoData_bins.at[breath,pao], breathD.at[breath,Vt],PEEP[part-1],C)
                    if verbose:
                        if C % 50 == 0:
                            print(color.RED + f"value of j at C{C} is j = {j}")
    
                    #Housekeep best current loss, best C
                    if j < j_best:
                        j_best = j
                        C_best = C
                #Housekeep loss for current breath
                    if np.isnan(j) == False:
                        hk_cost_form[C] = j
                    
                    
                
                
                if verbose:
                    if breath % 100 == 0:
                        halp.verbose_fnc(color.DARKCYAN + f"j_best for breath {breath} is: {j_best}" + color.END,color.DARKCYAN + f"C_best is: {C_best}" + color.END)
                
                
                hk_breath[breath] = {"j" : j_best, "C" : C_best, "cost_form" : hk_cost_form}
               # for i in range(100,150,1):
                    #if np.isnan(hk_breath[breath]['cost_form'][i]) == False:
                        #print(f"value of hk_cost_form at C = {i} is {hk_breath[breath]['cost_form'][i]}")
                #for i in hk_cost_form:
                    #if np.isnan(hk_cost_form[i]) == False:
                        #print(color.BOLD + f"Before clear index {i} was not a nan" + color.END)
                #reset hk_cost_form
                #hk_cost_form.clear()
                tot_loss += j_best
        if verbose:    
            halp.verbose_fnc(color.RED + f"total loss for part {part} is: {tot_loss}" + color.END)
        #Housekeep total loss for entire part
        hk_parts[part] = {"tot_loss" : tot_loss, "hk_breath" : hk_breath}
        print(color.BOLD + f"Length of hk_parts at part {part} is {len(hk_parts)}" + color.END)
        
    return hk_parts



### Quick Testing
patient = 11

#load data
breathD,esoData,FFFT = halp.patientManager(patient,'entire')

#Perform bucketing
esoData_bins = comp_halp.bin_divider(esoData,breathD)


hk_parts = comp_halp.grid_search(esoData, esoData_bins,breathD,patient,verbose=True)




esoData['1peso'].std()
esoData_bins['3peso'].std()



np.isnan(esoData_bins.at[134,'3peso'])

var = esoData_bins['1ModifiedPeso'].var()
peso = esoData_bins.at[13,'1ModifiedPeso']
Vt = breathD.at[13,'1Vt']
pao = esoData.at[13,'1ModifiedPao']
PEEP = 5
C = 100


#Manual calculation
#j = ((Peso - ((Vt/C) + PEEP - pao))**2)/Peso.var()
(peso - ((Vt*100)/C)+PEEP-pao)**2/var
(esoData_bins.at[13,'1ModifiedPeso']-((breathD.at[13,'1Vt']*100)/100)+5-esoData.at[13,'1ModifiedPao'])**2/esoData_bins['1ModifiedPeso'].var()


j = comp_halp.compliance_cost(peso, Vt, pao, PEEP, C,esoData_bins['1ModifiedPeso'].std())

# %%
#Flow cost function for estimating Raw
def flow_cost(flow,Palv,Raw,t,exp_t_const,flow_var):
    j = ((flow -(Palv/Raw)*math.log(-t/exp_t_const))**2)/flow_var
    
    return j

# Grid search
Raw_range = np.arange(0.1,5,0.01)

j_best = 0
Raw_best = 100000

for Raw in Raw_range:
    for breath in range(b_amt):
        
        j = flow_cost(flow, Palv, Raw, t, exp_t_const, flow_var)
        
    
    
    
    
    
    
    
    
    
    PSV = ((Peak Pressure – Plateau Pressure) / Set Flow) x Peak Flow
    
# %% Old Bin Divider (max of pressure, instead of a pressure difference)
def bin_divider(esoData,breathD, verbose=False):
    # Amount of breaths
    b_amount = len(breathD)
    print(f"b_amount is: {b_amount}")
    

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
                esoData_bins.at[breath,breath_col] = breath
                

            elif breath+1 < b_amount:                

                insp_cur = breathD.at[breath, inspStart]
                insp_next = breathD.at[breath+1, inspStart]            
                #Calculate the mean of peso and pao during the current breath

                esoData_bins.at[breath,peso] = esoData.loc[insp_cur:insp_next,peso].max()#.mean()
                esoData_bins.at[breath,pao] = esoData.loc[insp_cur:insp_next,pao].max()#.mean()
                if np.isnan(esoData_bins.at[breath,peso]) == False: 
                    #Create a breath column for plotting purposes
                    esoData_bins.at[breath,breath_col] = breath

    return esoData_bins


# %% Old Dashboard
app = Dash(__name__)

app.layout = html.Div([
    html.H4('Improved Dashboard Demo'),
    dcc.Dropdown(
        id="1stDropDown",
        options = ["breathD", "esoData", "FFFT"],
        value=["Montreal"]
    ),
    dcc.Dropdown(
    id='2ndDropDown',
),
    #dcc.Dropdown(
       # id="3rdDropDown",
        #options = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
       # value=["Montreal"]
        #),
    
    dcc.Graph(id="graph"
              ),
    dcc.Checklist(id="radioItems", options=["df_Length"]),
    dcc.Textarea(
        id="texttest",
    )
])


@app.callback(
    Output("2ndDropDown", "options"),
    Input("1stDropDown", "value")
    #[Input("3rdDropDown","value")]
    )
def update_2nd_DropDown(i1):
    global df
    df = halp.patientManager(11,i1)
    output_List = df.columns.tolist()
    return output_List

#@app.callback(Output("2ndDropDown","value"),
 #   Input("3rdDropDown", "value"))
#def update_3rd_DropDown(value):
  #  global patient
  #  patient = value
   # return patient
   
@app.callback(
    Output("graph", "figure"),
    Input("2ndDropDown", "value"))   
def update_graph(column):
    print(column)
    fig = px.scatter(
        df, x="1Time", y=column)
    return fig

@app.callback(
    Output("texttest", "value"),
    Input("radioItems","value"))
def df_Length(value):
    return "Length is: \n" + str(len(df)) #length




app.run_server(debug=True)

# %% Grid Search while breathD determined breath length
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

# %% OLD Calculation of variables needed for Pplat - b4 switch to peak detection
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
    
# %% Old flow calculations
         
    
if peak+1 < len(peaks_flow[0]):
    while valleys_flow[0][peak+cnt_insp] > peaks_flow[0][peak+1]:
        cnt_insp -= 1

    y_inspVt = esoData.loc[valleys_flow[0][peak+cnt_insp]:peaks_flow[0][peak+1],ModifiedFlow]                
    x_inspVt = np.arange(valleys_flow[0][peak+cnt_insp],peaks_flow[0][peak+1]+1)
    esoData_bins.at[peak,insp_Vt] = integrate.simpson(y_inspVt,x_inspVt)#,even='last',axis=0

#cnt_insp = 0


    while valleys_flow[0][peak+1] < peaks_flow[0][peak+cnt_exp]:
        cnt_exp -= 1
    
    
##### NÅR ALDRIG DENNE DEL IGEN####
#else:                    
    y_expVt = esoData.loc[peaks_flow[0][peak+cnt_exp]:valleys_flow[0][peak+1],ModifiedFlow]
    x_expVt = np.arange(peaks_flow[0][peak+cnt_exp],valleys_flow[0][peak+1]+1)
    esoData_bins.at[peak,exp_Vt] = integrate.simpson(y_expVt,x_expVt)#,even='last',axis=0                    

    #cnt_exp=0



