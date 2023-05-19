# -*- coding: utf-8 -*-
"""
Created on Mon May  8 08:54:29 2023

@author: Lasse
"""
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Data_Explo_HELPER as halp
import math
from typing import List
import Compl_Algo_Helper as comp_halp


# %% Function for adding text to each peak
def peak_adder(patient,esoData,pesoHeight,pesoDistance,paoHeight,paoDistance,verbose=False):
    from scipy.signal import find_peaks

    #Set patient


    parts = int(len(esoData.columns)/12)-1
    #print(f"num_parts: {parts}")

    for part in range(1,parts):
        if verbose:
            print(f"made it to part: {part}")
        ModifiedPeso,ModifiedPao,peso_peak,pao_peak = halp.prefix_Factory(part,'ModifiedPeso','ModifiedPao','peso_peak','pao_peak')
        peaks_peso = find_peaks(esoData[ModifiedPeso],height=pesoHeight,distance=pesoDistance)
        peaks_pao = find_peaks(esoData[ModifiedPao],height=paoHeight,distance=paoDistance)

       

        if len(peaks_peso[0]) > len(peaks_pao[0]):
            breaths = len(peaks_peso[0])

            for breath in range(breaths):
                suffix = str(breath)

                esoData.at[peaks_peso[0][breath],peso_peak] = 'P' + suffix
                if breath < len(peaks_pao[0]):
                    esoData.at[peaks_pao[0][breath],pao_peak] = 'P' + suffix
                    
        
            if verbose:
                if breath == breaths-1:
                    print(f"Made it to breath {breath} out of {breaths}")
        else:
            breaths = len(peaks_pao[0])

            for breath in range(breaths):
                suffix = str(breath)

                if breath < len(peaks_peso[0]):
                    esoData.at[peaks_peso[0][breath],peso_peak] = 'P' + suffix

                esoData.at[peaks_pao[0][breath],pao_peak] = 'P' + suffix
                if verbose:
                    if breath == breaths-1:
                        print(f"Made it to breath {breath} out of {breaths}")
        if verbose:
            print(f"len_peso: {breaths} \n len_pao: {len(peaks_pao[0])}")
    return esoData



# %% Function for plotting peaks of ModifiedPeso and ModifiedPao
def peak_plotter(part,esoData):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from plotly.offline import plot, iplot, init_notebook_mode



    #inspStart,expStart,Time,ModifiedPeso,ExpVolStart,breath, ModifiedPao = halp.prefix_Factory(part,'inspStart','expStart','Time','ModifiedPeso','ExpVolStart','breath','ModifiedPao')
    ModifiedPeso,ModifiedPao,peso_peak,pao_peak,Time,ModifiedFlow = halp.prefix_Factory(part,
                                                                                        'ModifiedPeso',
                                                                                        'ModifiedPao',
                                                                                        'peso_peak',
                                                                                        'pao_peak',
                                                                                        'Time',
                                                                                       'ModifiedFlow')

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
        ))
    plot(fig)
    
def insp_Adder(esoData,breathD):
    parts = int(len(esoData.columns)/12)+1
    
    b_amt = len(breathD)
    
    for part in range(1,parts):
        inspStart,expStart,ExpVolStart = halp.prefix_Factory(part,'inspStart','expStart','ExpVolStart')  
    
        
        
        for breath in range(b_amt):
            suffix = str(breath)
            if np.isnan(breathD.at[breath,inspStart]) == False:
                if breath != 0 and breath % 100 == 0:
                    print(f"Made it to breath: {breath} in part: {part}")
                for i in range(len(esoData)):
                    if i == breathD.at[breath,inspStart]: #if i == breathD.at[breath,'6expStart']:
                        esoData.at[i,inspStart] = 'I' + suffix
    
                    if i == breathD.at[breath,expStart]:
                        esoData.at[i,expStart] = 'E' + suffix
                        
                    if i == breathD.at[breath,ExpVolStart]:
                        esoData.at[i,ExpVolStart] = 'EV' + suffix
    return esoData

def flow_plotter(part,esoData):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from plotly.offline import plot, iplot, init_notebook_mode


    Time,ModifiedFlow,flow_valley,flow_peak = halp.prefix_Factory(part,
                                                                  'Time',
                                                                  'ModifiedFlow',
                                                                  'flow_valley',
                                                                  'flow_peak')
    trace1 = go.Scatter(x=esoData[Time], 
                       y = esoData[ModifiedFlow],
                       mode='markers+text',
                       text=esoData[flow_valley]
                       )
    trace2 = go.Scatter(x=esoData[Time], 
                       y = esoData[ModifiedFlow],
                       mode='markers+text',
                       #text=esoData['1flow_valley']
                    text=esoData[flow_peak]

                       )

    fig = make_subplots(rows=2,cols=1)
    fig.add_trace(trace1,row=1,col=1)
    fig.add_trace(trace2,row=2,col=1)
    fig['layout'].update(height = 600, width = 800, title = "Extracting insp- and expiratory flow",xaxis=dict(
          tickangle=-90
        ),
        yaxis_title="Flow (L/S)",
        xaxis_title="Time (S" + comp_halp.get_super('-2')+')')
    
    
    fig.update_layout(
        title={
            'text': "Extracting insp- and expiratory flow",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    plot(fig)
    
def flow_peaker(esoData,peak_flowHeight, peak_flowDistance, valley_height, valley_distance,plot_part ):
    import numpy as np
    from scipy.signal import argrelextrema

    from scipy.signal import find_peaks

   

    parts = int(len(esoData.columns)/12)+1
    print(f"num_parts: {parts}")


    for part in range(1,parts):
        print(f"made it to part: {part}")
        ModifiedFlow,flow_peak,flow_valley = halp.prefix_Factory(part,
                                                 'ModifiedFlow',
                                                 'flow_peak',
                                                 'flow_valley')

        #Find Peaks
        peaks_flow = find_peaks(esoData[ModifiedFlow],height=peak_flowHeight,distance=peak_flowDistance)

        #invert Data for peak finding
        valleys_flow = find_peaks(esoData[ModifiedFlow]*(-1),height=valley_height,distance=valley_distance)






        breaths = len(peaks_flow[0])

        for breath in range(breaths):
            suffix = str(breath)

            esoData.at[peaks_flow[0][breath],flow_peak] = 'P' + suffix

            if breath < len(valleys_flow[0]):
                esoData.at[valleys_flow[0][breath],flow_valley] = 'V' + suffix

        if plot_part == part: #breath == breaths-1 
            print(f"flow_peaks: {len(peaks_flow[0])} \n flow_valles: {len(valleys_flow[0])}")
    return esoData

def insp_plotter(esoData,part, eso = False, pao = False, flow = False):
    
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from plotly.offline import plot, iplot, init_notebook_mode
    
    
    
    inspStart,expStart,Time,ModifiedPeso,ExpVolStart,breath, ModifiedPao,ModifiedFlow = halp.prefix_Factory(part,
                                                                                                            'inspStart',
                                                                                                            'expStart',
                                                                                                            'Time',
                                                                                                            'ModifiedPeso',
                                                                                                            'ExpVolStart',
                                                                                                            'breath',
                                                                                                            'ModifiedPao',
                                                                                                            'ModifiedFlow')
    fig = make_subplots(rows=3,cols=1,subplot_titles = (ModifiedPao,ModifiedPeso,ModifiedFlow))
    if eso == True:
        trace1 = go.Scatter(
            x=esoData[Time],
            y=esoData[ModifiedPao],
            mode='markers+text',
            textposition='top center',
            text=esoData[inspStart],
            name=ModifiedPao,
            marker=dict(
                color='green',
                size=1
                       )
        )
        fig.add_trace(trace1,row=1,col=1)
    
    if pao == True:
        trace2 = go.Scatter(
            x=esoData[Time],
            y=esoData[ModifiedPeso],
            mode='markers+text',
            textposition='top center',
            text=esoData[expStart],
            name=ModifiedPeso,
            marker=dict(
                color='magenta',
                size=1
                       )
        )
        fig.add_trace(trace2,row=2,col=1)
    if flow == True:
        trace3 = go.Scatter(
            x=esoData[Time],
            y=esoData[ModifiedFlow],
            mode='markers+text',
            textposition='top center',
            text=esoData[ExpVolStart],
            name=ModifiedFlow,
            marker=dict(
                color='magenta',
                size=1
                       )
        )
        fig.add_trace(trace3,row=3,col=1)
    

    
    
    
    fig['layout'].update(height = 600, width = 800, title = "Peaks Pao vs. Peso",xaxis=dict(
          tickangle=-90
        ))
    plot(fig)