# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:51:48 2023

@author: Lasse
"""
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Data_Explo_HELPER as halp
import Compl_Algo_Helper as comp_halp
import math
from typing import List
from plotly.subplots import make_subplots
from plotly.offline import plot, iplot, init_notebook_mode
import Peak_Helper as peak_halp




# %% Plot Vt integration


#The correct flow settings for synchronizing peaks and valleys
flow_settings = {1 : {'height' : 5,'dis' : 230},
                 2 : {'height' : 5.3,'dis' : 255},
                 3 : {'height' : 4.9,'dis' : 255},
                 4 : {'height' : 5.7,'dis' : 300},
                 5 : {'height' : 5.7,'dis' : 300},
                 6 : {'height' : 6.7,'dis' : 350},
                 7 : {'height' : 6.6,'dis' : 350},
                 8 : {'height' : 5.1,'dis' : 280}}


#Set patient
patient = 11
part = 1





#load data
breathD,esoData,FFFT = halp.patientManager(patient,'entire')
esoData = peak_halp.flow_peaker(esoData,peak_flowHeight = 10, peak_flowDistance = 150, valley_height = flow_settings[part]['height'], valley_distance = flow_settings[part]['dis'],plot_part = part)


def zeroin(row,insp=False,exp=False):
    if insp:
        if row < 0: row = 0
    if exp:
        if row > 0: row = 0
    return row

#Inspiration
#esoData['1ModifiedFlow'] = esoData['1ModifiedFlow'].apply(lambda row: zeroin(row=row,insp=True))
#peak_halp.flow_plotter(part,esoData)


#Expiration
patient = 6
breathD,esoData,FFFT = halp.patientManager(patient,'entire')
part  = 1
fig = px.scatter(x=esoData.index, y=esoData[str(part)+'ModifiedFlow'])
plot(fig)
esoData = peak_halp.flow_peaker(esoData,peak_flowHeight = 10, peak_flowDistance = 150, valley_height = flow_settings[part]['height'], valley_distance = flow_settings[part]['dis'],plot_part = part)


esoData['1ModifiedFlow'] = esoData['1ModifiedFlow'].apply(lambda row: zeroin(row=row,exp=True))

peak_halp.flow_plotter(part,esoData)



# %% Plot Peso vs. Estimated Peso

# %% Plot estimated Peso vs measured Peso
def calc_peso_fun(Vt,PAO,C,PEEP):
    peso = (Vt/C)+PEEP-PAO
    return peso






def compare_plotter(part,esoData_bins,calc_peso):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from plotly.offline import plot, iplot, init_notebook_mode
    
    ModifiedPeso,breath_col,peso = halp.prefix_Factory(part,'ModifiedPeso','breath_col','peso')
    print(f"breath col: {breath_col}")
    trace1 = go.Scatter(
        x=esoData_bins[breath_col],
        y=esoData_bins[ModifiedPeso],
        name=ModifiedPeso,
        marker=dict(
            color='rgb(34,163,192)'
                   )
    )
    trace2 = go.Scatter(
        x=calc_peso[breath_col],
        y=calc_peso[peso],
        name='Calculated Peso',
        yaxis='y2'
    
    )
    

    
    fig = make_subplots(rows=2,cols=1,specs=[[{"secondary_y": True}],[{'rowspan' : 1}]]) #,
    fig.add_trace(trace1,row=1,col=1)
    fig.add_trace(trace2,row=1,col=1,secondary_y=True) #secondary_y=True,
    fig['layout'].update(height = 600, width = 800, title = "Peso vs. Estimated Peso",xaxis=dict(
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
    
    

#Amt of patients

# %% Perform grid_search
patient = 6
breathD,esoData,FFFT = halp.patientManager(patient,'entire')




#Load Vent_Settings
Vent_Setting = halp.Ventilator()
PS, PEEP = halp.Ventilator().get_Settings(str(patient))

esoData_bins = comp_halp.bin_divider(esoData,breathD,patient)

# Perform grid search
hk_cost = {}

hk_cost = comp_halp.grid_search_no_flow(esoData, esoData_bins, breathD, patient,verbose=False)


# %% Calc Peso and Compare    
calc_peso = pd.DataFrame(index=np.arange(len(breathD)),columns=['breath_col','calc_peso'])
parts = int(len(esoData.columns)/12)

b_amt = len(breathD)

for part in range(1,parts):
    for breath in range(b_amt):
        # Create Prefixes
        ModifiedFlow,ModifiedPao,insp_Vt,ModifiedPeso,breath_col,peso = halp.prefix_Factory(part,'ModifiedFlow','ModifiedPao','insp_Vt','ModifiedPeso','breath_col','peso')
        
        if np.isnan(esoData_bins.at[breath,ModifiedPao]) == False:    
            calc_peso.at[breath,peso] = calc_peso_fun(Vt=esoData_bins.at[breath,insp_Vt]*1000,
                                                           PAO=esoData_bins.at[breath,ModifiedPao],
                                                             PEEP=PEEP[part],
                                                             C=10)
            calc_peso.at[breath,breath_col] = breath

part = 1

compare_plotter(part,esoData_bins, calc_peso)

# %% Plot Cost Function
loss_df = pd.DataFrame(index=np.arange(len(hk_cost[1]['hk_C_loss'])))

C_range = np.arange(50,400,0.5)


for part in range(parts):
    C, Loss = halp.prefix_Factory(part, 'C','Loss')
    for C in C_range:
        loss_df.at[C,'C'] = hk_cost[1]['hk_C_loss'][C]['C']
        loss_df.at[C,'Loss'] = hk_cost[1]['hk_C_loss'][C]['tot_C_loss']
        
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



# %% Bland-Altman Plot
import statsmodels.api as sm
part=1
test = sm.graphics.mean_diff_plot(esoData_bins[str(part)+'ModifiedPeso'],calc_peso[str(part)+'peso'])
plot(test)

# %% Plot Modified Peso
part = 2

fig = px.scatter(esoData,x=esoData.index,y=esoData[str(part)+'ModifiedPao'])

plt.show()


