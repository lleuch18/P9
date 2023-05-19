# -*- coding: utf-8 -*-
"""
Created on Mon May 15 12:37:27 2023

@author: Lasse
"""

#Step 1: Detect frame where peso peaks are more than 5 seconds apart
#Step 2: Detect peaks in PAO in the same timeframe
#Step 3: Calc insp flow in the same timeframe

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

#Patient data and column names
patient = 11
PS, PEEP = halp.Ventilator().get_Settings(str(patient))
breathD,esoData,FFFT = halp.patientManager(patient,'entire')

part = 1

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


# %% Step 1: Peso peaks more than 5 seconds apart
#First detect peso peaks

flow_settings = {1 : {'height' : 5,'dis' : 230},
                 2 : {'height' : 5.3,'dis' : 255},
                 3 : {'height' : 4.9,'dis' : 255},
                 4 : {'height' : 5.7,'dis' : 300},
                 5 : {'height' : 5.7,'dis' : 300},
                 6 : {'height' : 6.7,'dis' : 350},
                 7 : {'height' : 6.6,'dis' : 350},
                 8 : {'height' : 5.1,'dis' : 280}}

peaks_peso = find_peaks(esoData[ModifiedPeso],height=-3,distance=150)
peaks_pao = find_peaks(esoData[ModifiedPao],height=11.5,distance=150)
peaks_flow = find_peaks(esoData[ModifiedFlow],height=10,distance=250)
valleys_flow = find_peaks(esoData[ModifiedFlow]*(-1),
                          height=flow_settings[part]['height'],
                          distance=flow_settings[part]['dis'])

#Remove all peaks above threshold
#temp=[]
#for peak in range(1,len(peakss_peso[1]['peak_heights'])):
#    if peakss_peso[1]['peak_heights'][peak] >= 3:
 #       temp.append(peak)

#peaks_peso= {}


#temp = np.array(temp)
#peaks_peso[1]={'peak_heights' : np.delete(peakss_peso[1]['peak_heights'],temp)}
#peaks_peso[0]=np.delete(peakss_peso[0],temp)
#len(peaks_peso[0])
        


hk_peaks = {}
cnt=0
#Find all relevant timeframes
for peak in range(1,len(peaks_peso[0])):
    if peaks_peso[0][peak]-peaks_peso[0][peak-1] >= 525:
        if peaks_peso[1]['peak_heights'][peak] < 2.8:
            print(f"Activated Condition at: {peak}")
            cnt+=1
            hk_peaks[cnt] = {'start' : peaks_peso[0][peak-1], 'stop' : peaks_peso[0][peak] }

#Ensure that only peaks with threshold=-1.3 are counted
timeframe_df = pd.DataFrame(np.nan,index=esoData.index,columns=[ModifiedPeso,ModifiedPao,ModifiedFlow])
for timeframe in range(1,len(hk_peaks)):
    start = hk_peaks[timeframe]['start']
    stop = hk_peaks[timeframe]['stop']
    timeframe_df.loc[start:stop,ModifiedPeso] = esoData.loc[start:stop,ModifiedPeso]
    #timeframe_df.loc[start:stop,ModifiedPeso].apply(lambda row: filer(row))
    
# Filter for a threshold, followed by a median filter that removes unwanted values    
for i in range(len(timeframe_df)):
    #if np.isnan(timeframe_df.at[i,ModifiedPeso]):
    if timeframe_df.at[i,ModifiedPeso] > -1.3: timeframe_df.at[i,ModifiedPeso] = -1.3
        
for timeframe in range(1,len(hk_peaks)):
    start = hk_peaks[timeframe]['start']
    stop = hk_peaks[timeframe]['stop']
    if timeframe_df.at[start,ModifiedPeso] > timeframe_df.loc[start/2:stop/2,ModifiedPeso].median():
        cnt=0
        while timeframe_df.at[start+cnt,ModifiedPeso] > timeframe_df.loc[start/2:stop/2,ModifiedPeso].median():
            timeframe_df.at[start+cnt,ModifiedPeso] = np.nan #timeframe_df.loc[start/2:stop/2,ModifiedPeso].median() #np.nan
            cnt+=1
    if timeframe_df.at[stop,ModifiedPeso] > timeframe_df.loc[start/2:stop/2,ModifiedPeso].median():
        cnt=0
        while timeframe_df.at[stop+cnt,ModifiedPeso] > timeframe_df.loc[start/2:stop/2,ModifiedPeso].median():
            timeframe_df.at[stop+cnt,ModifiedPeso] = np.nan #timeframe_df.loc[start:stop,ModifiedPeso].median() #np.nan
            cnt-=1
            
    #Since indexes have been cut, set new start and stop indexes
    cnt_start=0
    while np.isnan(timeframe_df.at[start+cnt_start,ModifiedPeso]):
        cnt_start+=1
    hk_peaks[timeframe]['start'] = hk_peaks[timeframe]['start']+cnt_start
    print(f"start_count index was moved {hk_peaks[timeframe]['start']+cnt_start-hk_peaks[timeframe]['start']}")
    cnt_stop=0
    while np.isnan(timeframe_df.at[stop+cnt_stop,ModifiedPeso]):
        cnt_stop-=1
    hk_peaks[timeframe]['stop'] = hk_peaks[timeframe]['stop']+cnt_stop
    print(f"ctop_cnt index was moved {hk_peaks[timeframe]['stop']-hk_peaks[timeframe]['stop']+cnt_stop}")

# %% Detect PAO peaks in the relevant sections

#Set only pao data which corresponds to detected peso areas
for timeframe in range(1,len(hk_peaks)):
    start = hk_peaks[timeframe]['start']
    stop = hk_peaks[timeframe]['stop']    
    timeframe_df.loc[start:stop,ModifiedPao] = esoData.loc[start:stop,ModifiedPao]


#Detect peaks in these areas
hk_pao_tf = {}
for timeframe in range(1,len(hk_peaks)):
    start = hk_peaks[timeframe]['start']
    stop = hk_peaks[timeframe]['stop']
    temp_peak = find_peaks(timeframe_df.loc[start:stop,ModifiedPao],height=11.5,distance=150)
    hk_pao_tf[timeframe] = {'peaks' : temp_peak[0],'start' : start,'stop' : stop}

#Remove areas with 0 peaks in both peso and pao
for timeframe in range(1,len(hk_pao_tf)):
    if not hk_pao_tf[timeframe]['peaks'].size:
        start = hk_pao_tf[timeframe]['start']
        stop = hk_pao_tf[timeframe]['stop']
        timeframe_df.loc[start:stop,ModifiedPao] = np.nan
        timeframe_df.loc[start:stop,ModifiedPeso] = np.nan


tf_peaks_pao = find_peaks(timeframe_df[ModifiedPao],height=11.5,distance=150)
tf_peaks_peso = find_peaks(timeframe_df[ModifiedPeso],height=-3,distance=150)
for peak in range(len(tf_peaks_pao[0])):
    suffix = str(peak)    
    timeframe_df.at[tf_peaks_pao[0][peak],pao_peak] = 'P' + suffix



# %% Plot Section

#Extract relevant timeframes for plotting

#Plot peso at all relevant timeframes
trace1 = go.Scatter(
    x=timeframe_df.index,
    y=timeframe_df[ModifiedPeso],
    name=ModifiedPeso,
    marker=dict(
        color='rgb(34,163,192)'
               )
)
trace2 = go.Scatter(
    x=timeframe_df.index,
    y=timeframe_df[ModifiedPao],
    mode='markers+text',
    textposition='top center',
    text=timeframe_df[pao_peak],
    name='Modified Pao',
    yaxis='y2'

)



fig = make_subplots(rows=2,cols=1) #,
fig.add_trace(trace1,row=1,col=1)
fig.add_trace(trace2,row=2,col=1) #secondary_y=True,
fig['layout'].update(height = 600, width = 800, title = "Pao vs. Estimated Pao",xaxis=dict(
      tickangle=-90
    ))

fig.update_layout(
    title={
        'text': "Peso Timeframes  ~=0",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

plot(fig)   











