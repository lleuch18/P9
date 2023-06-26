# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 07:25:43 2023

@author: Lasse
"""

import pandas as pd
import numpy as np
import Compl_Algo_Helper as comp_halp
import Data_Explo_HELPER as halp
from scipy.signal import find_peaks
import plotly.express as px
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#%% Load patient data, set column names
patient = 11
part = 1
PS, PEEP = halp.Ventilator().get_Settings(str(patient))
breathD,esoData,FFFT = halp.patientManager(patient,'entire')

PS, PEEP = halp.Ventilator().get_Settings(str(patient))

Time,ModifiedPeso,ModifiedPao,ModifiedFlow,insp_flow,exp_flow,peso_peak,pao_peak,flow_peak,flow_valley,Vt,exp_TE,pplat,insp_res = halp.prefix_Factory(part, 
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
                                                                                                                    'Vt',
                                                                                                                    'exp_TE',
                                                                                                                    'pplat',
                                                                                                                    'insp_res')                                                                                                                

#%% Detect flow peaks and valleys for pao & flow
flow_settings = {1 : {'height' : 5,'dis' : 230},
                 2 : {'height' : 5.3,'dis' : 255},
                 3 : {'height' : 4.9,'dis' : 255},
                 4 : {'height' : 5.7,'dis' : 300},
                 5 : {'height' : 5.7,'dis' : 300},
                 6 : {'height' : 6.7,'dis' : 350},
                 7 : {'height' : 6.6,'dis' : 350},
                 8 : {'height' : 5.1,'dis' : 280}
                 }

peaks_pao = find_peaks(esoData[ModifiedPao],height=11.5,distance=150)
peaks_flow = find_peaks(esoData[ModifiedFlow],height=10,distance=250)
valleys_flow = find_peaks(esoData[ModifiedFlow]*(-1),
                          height=flow_settings[part]['height'],
                          distance=flow_settings[part]['dis'])                                                                                                                    

#%% Calculate expiratory time constant   
def calc_te(peaks_pao,peaks_flow,valleys_flow, data: pd.DataFrame) -> pd.DataFrame:
    #Dataframe to hold TE values
    TE_frame = pd.DataFrame(index=np.arange(len(peaks_pao[0])),columns=[exp_TE])
    
            
    #At each breath, calculate expiratory flow and tidal volume
    for peak in range(len(peaks_pao[0])):
        #Check for NoneType
        if comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,exp=True) is not None or comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,exp=True,intgrate=True) is not None:        
        #max expiratory Flow (Capital F since var name taken)
        # converted from l/min to mL
            exp_Flow = comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,exp=True)*1000
            
            #exp Vt
            #converted to mL
            exp_vt = comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,exp=True,intgrate=True)*1000
            
            print(f"peak: {peak} \n exp_Flow: {exp_Flow} \n exp_vt: {exp_vt}")
        
            TE_frame.at[peak,exp_TE] = exp_vt/exp_Flow

    return TE_frame

TE_frame = calc_te(peaks_pao, peaks_flow, valleys_flow, esoData)
TE_frame.dropna(inplace=True)
type(TE_frame)

TE = TE_frame[exp_TE].mean()
print(TE)


        
    
    
    
    
        
    
#%% Calculate Pplat

def calc_pplat(peaks_pao,peaks_flow,valleys_flow, data: pd.DataFrame,part: int,TE: pd.DataFrame) -> pd.DataFrame:
    pplat_frame = pd.DataFrame(index=np.arange(len(peaks_pao[0])),columns=[pplat])
        
    for peak in range(len(peaks_pao[0])):
        
        if comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True) is not None and comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True,intgrate=True) is not None:
        
            #Derive inspiratory vt
            insp_vt = comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True,intgrate=True)*1000
            
            #Derive inspiratory flow
            insp_Flow = comp_halp.flow_extracter(data, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True)#*1000
            
            print(f"peak: {peak} \n insp_vt: {insp_vt} \n insp_flow: {insp_Flow}")
            #print(f"peak: {peak} \n PIP: {peaks_pao[1]['peak_heights'][peak-1]} \n PEEP: {PEEP[part]}")
            #print(f"peak: {peak} \n 1st part: {(insp_vt*peaks_pao[1]['peak_heights'][peak-1])} \n 2nd part: {(insp_vt*(PEEP[part]+1))} \n Denominator: {(insp_vt*TE*insp_Flow)}  ")
            pplat_frame.at[peak,pplat] = ((insp_vt*peaks_pao[1]['peak_heights'][peak-1])-(insp_vt*(PEEP[part]+1)))/(insp_vt*TE.at[peak,exp_TE]*insp_Flow)
    return pplat_frame

pplat_frame = calc_pplat(peaks_pao, peaks_flow, valleys_flow, esoData, part, TE_frame)

pplat_frame.at[2,pplat] = (pplat_frame.at[1,pplat]+pplat_frame.at[3,pplat])/2

print(pplat_frame.at[2,pplat])
print(pplat_frame[pplat].mean())


        
#%% Calculate Inspiratory resistance

def calc_insp_res(peaks_pao,peaks_flow,valleys_flow,esoData: pd.DataFrame) -> pd.DataFrame:
    insp_res_frame = pd.DataFrame(index=np.arange(len(peaks_pao[0])),columns=[insp_res])
    
    TE_frame = calc_te(peaks_pao, peaks_flow, valleys_flow, esoData)
    TE_frame.dropna(inplace=True)
    
    
    pplat_frame = calc_pplat(peaks_pao, peaks_flow, valleys_flow, esoData, part, TE_frame)
    pplat_frame.dropna(inplace=True)
    
    for peak in range(len(pplat_frame)):
        insp_res_frame.at[peak,insp_res] = abs((peaks_pao[1]['peak_heights'][peak-1]-pplat_frame.at[peak,pplat])/(comp_halp.flow_extracter(esoData, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True)*1000))
    
    return insp_res_frame

insp_res_frame = calc_insp_res(peaks_pao,peaks_flow,valleys_flow,esoData)
insp_res_frame.dropna(inplace=True)
    

#%% Implement full EOM

def calc_peso_fun(Vt,PAO,Raw,insp_Flow,C,PEEP):
    Peso = (Vt/C)+(Raw*insp_Flow)+PEEP-PAO
    return Peso


esoData_bins = comp_halp.bin_divider(esoData, breathD, 11)

eso11 = esoData_bins[ModifiedPeso]
eso11.at[78] = eso11.loc[70:77].median()
eso11.at[79] = eso11.loc[70:77].mean()
eso11.dropna(inplace=True)


peso_calc = pd.DataFrame(index=np.arange(len(peaks_pao[0])), columns=[ModifiedPeso])
for peak in range(len(eso11)):
    insp_vt = comp_halp.flow_extracter(esoData, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True,intgrate=True)*1000
    insp_Flow = comp_halp.flow_extracter(esoData, peak, ModifiedFlow, peaks_flow, valleys_flow,insp=True)#*1000
    PAO = peaks_pao[1]['peak_heights'][peak-1]
    Raw = insp_res_frame.at[peak,insp_res]
    
    peso_calc.at[peak,ModifiedPeso] = calc_peso_fun(insp_vt, PAO, Raw, insp_Flow, 14, PEEP[part]+1)
peso_calc.at[2,ModifiedPeso] = peso_calc[ModifiedPeso].mean()
peso_calc.dropna(inplace=True)

#fig = px.scatter(x=esoData.index,y=esoData[ModifiedPeso])
#plot(fig)



# %% Peso vs Calc Peso
trace1 = go.Scatter(
    x=eso11.index,
    y=eso11,
    name=ModifiedPeso,
    marker=dict(
        color='rgb(34,163,192)'
               )
)
trace2 = go.Scatter(
    x=peso_calc.index,
    y=peso_calc[ModifiedPeso],
    name='Calculated Peso',
    yaxis='y2'

)



fig = make_subplots(rows=2,cols=1,specs=[[{"secondary_y": True}],[{'rowspan' : 1}]]) #,
fig.add_trace(trace1,row=1,col=1)
fig.add_trace(trace2,row=1,col=1,secondary_y=True) #secondary_y=True,
fig['layout'].update(height = 600, width = 800, title = "Peso vs. Estimated Peso C=63.5",xaxis=dict(
      tickangle=-90
    ))

fig.update_layout(
    title={
        'text': "Peso vs. Estimated Peso",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

plot(fig)   

import statsmodels.api as sm
part=1
test = sm.graphics.mean_diff_plot(eso11,peso_calc[ModifiedPeso])
plot(test)
