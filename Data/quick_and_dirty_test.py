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
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot, iplot, init_notebook_mode
import Peak_Helper as peak_halp
from scipy.signal import find_peaks
import scipy.integrate as integrate
import scipy.special as special






# %% Detect low-Pmus breaths


# %% Load data and set column names

patient = 11
PS, PEEP = halp.Ventilator().get_Settings(str(patient))
breathD,esoData,FFFT = halp.patientManager(patient,'entire')

# Extract relevant breaths
breath_indexes = {1 : {1 : {'start' : 10.40*100,'stop' : 18.1*100},
                       2 : {'start' : 61.5*100,'stop' : 68*100},
                       3 : {'start' : 98*100,'stop' : 107*100},
                       4 : {'start' : 125*100,'stop' : 132*100}},
                  
                  2 : {1 : {'start' : 148*100,'stop' : 152*100}},
                       
                  3 : {1 : {'start' : np.nan,'stop' : np.nan}},
                       
                  4 : {1 : {'start' : 294.45*100,'stop' : 305*100}}                      
                       
                  }

#Manual detection
part = 8
Time,ModifiedPeso,ModifiedPao,ModifiedFlow,insp_flow,exp_flow,peso_peak,pao_peak,flow_peak,flow_valley,Vt = halp.prefix_Factory(part, 
                                                                                                                    'Time',
                                                                                                                    'ModifiedPeso',
                                                                                                                    'ModifiedPao',
                                                                                                                    'ModifiedFlow',
                                                                                                                    'insp_flow',
                                                                                                                    'exp_flow',
                                                                                                                    'peso_peak',
                                                                                                                    'pao_peak',
                                                                                                                    'flow_peak',
                                                                                                                    'flow_valley',
                                                                                                                    'Vt')

temp_df = pd.DataFrame(np.nan,index=esoData.index,columns=[ModifiedPeso,ModifiedPao,ModifiedFlow])
def zeroin(row,insp=False,exp=False):
    if insp:
        if row < 0: row = 0
        return row

    if exp:
        if row > 0: row = 0
        return row

for timeframe in range(1,len(breath_indexes[part])+1):
    start = breath_indexes[part][timeframe]['start']
    stop = breath_indexes[part][timeframe]['stop']
    
    temp_df.loc[start:stop,ModifiedPao] = esoData.loc[start:stop,ModifiedPao]
    temp_df.loc[start:stop,ModifiedPeso] = esoData.loc[start:stop,ModifiedPeso]
    temp_df.loc[start:stop,ModifiedFlow] = esoData.loc[start:stop,ModifiedFlow]
    
    esoData_temp = esoData.copy()
    esoData_temp = esoData_temp[ModifiedFlow].apply(lambda row: zeroin(row,insp=True))
    temp_df.loc[start:stop,insp_flow] = esoData_temp.loc[start:stop]
    
    esoData_temp = esoData.copy()
    esoData_temp = esoData_temp[ModifiedFlow].apply(lambda row: zeroin(row,exp=True))
    temp_df.loc[start:stop,exp_flow] = esoData_temp.loc[start:stop]
    
    

    
    
# %% Detect peaks and valleys for flow & pao
flow_settings = {1 : {'height' : 5,'dis' : 230},
                 2 : {'height' : 5.3,'dis' : 255},
                 3 : {'height' : 4.9,'dis' : 255},
                 4 : {'height' : 5.7,'dis' : 300},
                 5 : {'height' : 5.7,'dis' : 300},
                 6 : {'height' : 6.7,'dis' : 350},
                 7 : {'height' : 6.6,'dis' : 350},
                 8 : {'height' : 5.1,'dis' : 280}}

#Detect peaks in order to perform variable extraction algorithm
#peaks_peso = find_peaks(temp_df[ModifiedPeso],height=-3,distance=150)
peaks_pao = find_peaks(temp_df[ModifiedPao],height=11.5,distance=150)
peaks_flow = find_peaks(temp_df[ModifiedFlow],height=10,distance=250)
valleys_flow = find_peaks(temp_df[ModifiedFlow]*(-1),
                          height=flow_settings[part]['height'],
                          distance=flow_settings[part]['dis'])


# %% Extract values during detected timeframes
cnt_flow_peak = 0
cnt_flow_valley = 0
cnt_pao = 0
# Set peak and valley markers
for timeframe in range(1,len(breath_indexes[part])+1):
    
    
    start = int(breath_indexes[part][timeframe]['start'])
    stop = int(breath_indexes[part][timeframe]['stop'])+1
    
    
    for i in range(start,stop):
        suffix = str(cnt_pao)
        if i in peaks_pao[0]:
            temp_df.at[i,pao_peak] = 'P' + suffix
            cnt_pao +=1
            
    
    for i in range(start,stop):
        suffix_peak = str(cnt_flow_peak)
        suffix_valley = str(cnt_flow_valley)
        if i in peaks_flow[0]:
            temp_df.at[i,flow_peak] = 'P' + suffix_peak
            cnt_flow_peak += 1
        if i in valleys_flow[0]:
            temp_df.at[i,flow_valley] = 'V' + suffix_valley
            cnt_flow_valley += 1
            
# Extract Vt and Pao
var_df = pd.DataFrame(index=np.arange(len(peaks_pao[0])),columns=[ModifiedPao,Vt])

for peak in np.arange(len(peaks_pao[0])):
    #Pao delivered by vent
    var_df.at[peak,ModifiedPao] = peaks_pao[1]['peak_heights'][peak-1]#-PEEP[part-1]
    

    var_df.at[peak,Vt] = comp_halp.flow_extracter(temp_df, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True,intgrate=True)
    var_df.at[peak,Vt] = var_df.at[peak,Vt]
for i in range(len(var_df)):

    
    if var_df.at[i,Vt] is None:
        var_df.at[i,Vt] = var_df.loc[i-2:i,Vt].mean()


# %% Estimating Compliance during detected timeframes 

hk_cost = {}
hk_C_loss = {}
hk_peak = {}

var_df.at[1,Vt] = var_df.at[0,Vt]
var_df.at[2,Vt] = var_df.at[0,Vt]

var_df[Vt] = var_df[Vt].apply(lambda x: x*1000)


from scipy.optimize import Bounds
import numpy as np
from scipy.optimize import line_search
from scipy.optimize import minimize
bounds = Bounds([10], [70])

x0 = 20*np.ones(9)

pao_min = var_df[ModifiedPao].to_numpy()
Vt_min = var_df[Vt].to_numpy()
PEEP_min = PEEP[part]*np.ones(9)
pao_var_min = np.array([0.35,0.35,0.35,0.35,0.35,0.35,0.35,0.35,0.35])



res = minimize(comp_halp.compliance_cost_no_flow_min, x0, method='trust-constr', 
               #constraints=[linear_constraint, nonlinear_constraint],
               args=(pao_min,Vt_min,PEEP_min,pao_var_min),
               options={'verbose': 1}, bounds=bounds)

res.x


for C in np.arange(10,100,0.25):
    j_best = 1000000
    C_best = 0.0000 #Same logic but reversed
    best_loss = 10000000
    
    global loss_tot
    loss_tot = 0
    
    for peak in range(len(var_df)):
        
        j = comp_halp.compliance_cost_no_flow(Vt=var_df.at[peak,Vt],
                                          pao=var_df.at[peak,ModifiedPao],
                                          PEEP=PEEP[part-1]+1,
                                          C=C,
                                          no_pmus=True,
                                          pao_var=var_df[ModifiedPao].var(),
                                          verbose=False
                                         
                                          )
        

        
        loss_tot += j
    if loss_tot < best_loss:    
        best_loss = loss_tot
        C_best = C
        
        
    if C > 11:
        if hk_C_loss[C-0.25]['loss_tot']-loss_tot < 0.01*loss_tot:
            print(f"best-loss: {hk_C_loss[C-0.25]['loss_tot']-loss_tot} \n 0.01*loss_tot: {0.01*loss_tot}")
            print(f"Condition of interest activated at {C}")
            best_loss = loss_tot
            C_best = C
            break
    
        
        
    hk_C_loss[C] = {'C' : C,'loss_tot' : loss_tot}  
hk_cost[part] = {'best_loss' : best_loss,'C_best' : C,'hk_C_loss' : hk_C_loss}


loss_df = pd.DataFrame(index=np.arange(len(hk_cost[1]['hk_C_loss'])))

C_range = np.arange(10,hk_cost[part]['C_best'],0.25)



C, Loss = halp.prefix_Factory(part, 'C','Loss')
for C in C_range:
    loss_df.at[C,'C'] = hk_cost[1]['hk_C_loss'][C]['C']
    loss_df.at[C,'Loss'] = hk_cost[1]['hk_C_loss'][C]['loss_tot']

fig = px.scatter(loss_df,x=loss_df['C'],y=loss_df['Loss'])
fig['layout'].update(height = 600, width = 800, title = "Loss vs. Compliance",xaxis=dict(
      tickangle=-90
    ),
    yaxis_title="J",
    xaxis_title="C")

fig.update_layout(
    title={
        'text': "Loss vs. Compliance",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

plot(fig)
          
       
for i in range(len(var_df)):
    C = (var_df.at[i,Vt]*1000)/var_df.at[i,ModifiedPao]
    print(C)


#Plot estimated Pao vs calculated Pao

def calc_pao_fun(Vt,PAO,C,PEEP):
    PAO = (Vt/C)+PEEP
    return PAO

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot, iplot, init_notebook_mode




calc_pao = pd.DataFrame(index=np.arange(len(var_df)),columns=['calc_pao'])
parts = int(len(esoData.columns)/12)

peaks = len(var_df)


for breath in range(peaks):
    # Create Prefixes
    ModifiedFlow,ModifiedPao,Vt = halp.prefix_Factory(part,'ModifiedFlow','ModifiedPao','Vt')
    
    calc_pao.at[breath,ModifiedPao] = calc_pao_fun(Vt=var_df.at[breath,Vt],
                                                   PAO=var_df.at[breath,ModifiedPao],
                                                     PEEP=PEEP[part]+1,
                                                     C=hk_cost[part]['C_best'])


part = 1

ModifiedPeso,breath_col,peso = halp.prefix_Factory(part,'ModifiedPeso','breath_col','peso')
print(f"breath col: {breath_col}")
trace1 = go.Scatter(
    x=var_df.index,
    y=var_df[ModifiedPao],
    name=ModifiedPao,
    marker=dict(
        color='rgb(34,163,192)'
               )
)
trace2 = go.Scatter(
    x=calc_pao.index,
    y=calc_pao[ModifiedPao],
    name='Calculated Pao',
    yaxis='y2'

)



fig = make_subplots(rows=2,cols=1,specs=[[{"secondary_y": True}],[{'rowspan' : 1}]]) #,
fig.add_trace(trace1,row=1,col=1)
fig.add_trace(trace2,row=1,col=1,secondary_y=True) #secondary_y=True,
fig['layout'].update(height = 600, width = 800, title = "Pao vs. Estimated Pao",xaxis=dict(
      tickangle=-90
    ))

fig.update_layout(
    title={
        'text': "Pao vs. Estimated Pao",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

plot(fig)    

# %% Bland Altman Plot calc vs. measured PAo
import statsmodels.api as sm
part=1
test = sm.graphics.mean_diff_plot(var_df[str(part)+'ModifiedPao'],calc_pao[str(part)+'ModifiedPao'])
plot(test)

# %% Plotting detected timeframes for manual inspection
trace1 = go.Scatter(x=esoData.index, 
                   y = esoData[ModifiedPao],
                   mode='markers+text',
                   #text=temp_df[pao_peak]
                   )
trace2 = go.Scatter(x=esoData.index, 
                   y = esoData[ModifiedPeso],
                   mode='markers+text'
                   )

trace3 = go.Scatter(x=temp_df.index, 
                   y = temp_df[exp_flow],
                   mode='markers+text',
                   text=temp_df[flow_peak]
                   )

trace4 = go.Scatter(x=temp_df.index, 
                   y = temp_df[insp_flow],
                   mode='markers+text',
                   text = temp_df[flow_valley]
                   )

fig = make_subplots(rows=2,cols=1,subplot_titles=(ModifiedPao,ModifiedPeso,ModifiedFlow,insp_flow))
fig.add_trace(trace1,row=1,col=1)
fig.add_trace(trace2,row=2,col=1)
fig.add_trace(trace3,row=2,col=1)
fig.add_trace(trace4, row=2,col=2)
fig['layout'].update(height = 600, width = 800, title = "Extracting insp- and expiratory flow",xaxis=dict(
      tickangle=-90
    ),
    yaxis_title="P (mmH2O)",
    xaxis_title="Time (S" + comp_halp.get_super('-2')+')')


fig.update_layout(
    title={
        'text': "Timeframes with Pmus = ~0",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
plot(fig)    

fig = px.scatter(esoData,x=esoData.index,y=esoData[ModifiedPeso])
plot(fig)



