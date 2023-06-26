# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 18:19:01 2023

@author: Lasse
"""

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import Data_Explo_HELPER as halp
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Interactive plot with custom data source'),
    dcc.Graph(id="graph_peso"),
    dcc.Graph(id="graph_pao"),
    html.P("Number of bars:"),
    dcc.Slider(id="slider_peso_height", min=0, max=-5, value=4, step=1),
    dcc.Slider(id="slider_pao_height", min=5, max=15, value=4, step=1),
    dcc.Slider(id="slider_peso_distance", min=10, max=300, value=4, step=20),
    dcc.Slider(id="slider_pao_distance", min=10, max=300, value=4, step=20),
    dcc.Checklist(id="radioItems", options=['Calculate Peaks'])
])


@app.callback(
    Output("graph", "figure"), 
    Input("slider", "value"))
def update_bar_chart(size):
    data = np.random.normal(3, 2, size=size) # replace with your own data source
    fig = go.Figure(
        data=[go.Bar(y=data)],
        layout_title_text="Native Plotly rendering in Dash"
    )
    return fig

app.run_server(debug=True)




def peak_adder(patient,esoData,pesoHeight,pesoDistance,paoHeight,paoDistance):
    from scipy.signal import find_peaks

    #Set patient


    parts = int(len(esoData.columns)/12)

    for part in range(1,parts):
        #print(f"made it to part: {part}")
        ModifiedPeso,ModifiedPao,peso_peak,pao_peak = halp.prefix_Factory(part,'ModifiedPeso','ModifiedPao','peso_peak','pao_peak')
        peaks_peso = find_peaks(esoData[ModifiedPeso],height=pesoHeight,distance=pesoDistance)
        peaks_pao = find_peaks(esoData[ModifiedPao],height=paoHeight,distance=paoHeight)

        #print(f"len_peso: {breaths} \n len_pao: {len(peaks_pao[0])}")

        if len(peaks_peso[0]) > len(peaks_pao[0]):
            breaths = len(peaks_peso[0])

            for breath in range(breaths):
                suffix = str(breath)

                esoData.at[peaks_peso[0][breath],peso_peak] = 'P' + suffix
                if breath < len(peaks_pao[0]):
                    esoData.at[peaks_pao[0][breath],pao_peak] = 'P' + suffix

            #if breath == breaths-1:
                #print(f"Made it to breath {breath} out of {breaths}")
        else:
            breaths = len(peaks_pao[0])

            for breath in range(breaths):
                suffix = str(breath)

                if breath < len(peaks_peso[0]):
                    esoData.at[peaks_peso[0][breath],peso_peak] = 'P' + suffix

                esoData.at[peaks_pao[0][breath],pao_peak] = 'P' + suffix
                #if breath == breaths-1:
                    #print(f"Made it to breath {breath} out of {breaths}")
    return esoData
