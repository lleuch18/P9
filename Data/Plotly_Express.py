# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 18:19:01 2023

@author: Lasse
"""

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import Data_Explo_HELPER as halp
import pandas as pd


app = Dash(__name__)

app.layout = html.Div([
    html.H4('Testing of building easy dashboard'),
    dcc.Dropdown(
        id="1stDropDown",
        options = ["breathD", "esoData", "FFFT"],
        value=["Montreal"]
    ),
    dcc.Dropdown(
    id='2ndDropDown',
),
    dcc.Dropdown(
        id="3rdDropDown",
        options = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
        value=["Montreal"]
        ),
    
    dcc.Graph(id="graph"
              ),
    dcc.Checklist(id="radioItems", options=["df_Length"]),
    dcc.Textarea(
        id="texttest",
    )
])


@app.callback(
    Output("2ndDropDown", "options"),
    [Input("1stDropDown", "value"),
     Input("3rdDropDown","value")]
    )
def update_2nd_DropDown(i1,i2):
    global df
    df = halp.patientManager(i1,i2)
    output_List = df.columns.tolist()
    return output_List

@app.callback(Output("2ndDropDown","value"),
    Input("3rdDropDown", "value"))
def update_3rd_DropDown(value):
    global patient
    patient = value
    return patient

@app.callback(
    Output("texttest", "value"),
    Input("radioItems","value"))
def df_Length(value):
    return "Length is: \n" + str(len(df)) #length

@app.callback(
    Output("graph", "figure"),
    Input("2ndDropDown", "value"))   
def update_graph(column):
    print(column)
    fig = px.scatter(
        df, x="Time", y=column)
    return fig


app.run_server(debug=True)