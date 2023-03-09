# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:34:21 2023

@author: Lasse
"""

import pandas as pd
import Data_Explo_HELPER as halp
import matplotlib.pyplot as plt
import numpy as np
import os
import PySimpleGUI as sg
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #For integrating plots into the gui



# Simple Patient Manager Tool

_VARS = {'window': False}
#Create different layout views
layout1 = [[sg.Text("Patient Data Manager")],
          [sg.Text("PatientNumber", size=(25,1)),sg.InputText()],
          [sg.Text("breathD, esoData, mod_FFFT or entire", size=(25,1)),sg.InputText()],
          [sg.Button('Load'),sg.Button('View Formula')]]#, sg.Button('Close')]]

layout2 = [[sg.Text("This is where the magic happens!")],          
          [sg.Image(os.path.join('..','Figures','EOM.png'))],
          [sg.Image(os.path.join('..','Figures','CRS.png'))],
          [sg.Button('Hide Formula')]]

layout3 = [[sg.Text("Plot Tool")],          
          [sg.Text("Dataframe", size=(25,1)),sg.InputText()],
          [sg.Text("Column 1", size=(25,1)),sg.InputText()],
          [sg.Text("Column 2", size=(25,1)),sg.InputText()],
          [sg.Text("Breath Start Nr", size=(25,1)),sg.InputText()],
          [sg.Button('Plot')]]

layout4 = [[sg.Canvas(key='figCanvas')],
          [sg.Button('Exit')]]

#Create the layout
layout = [[sg.Column(layout1,visible=False, key='-COL1-'),
           sg.Column(layout2,visible=False, key='-COL2-'),
           sg.Column(layout3,visible=False, key='-COL3-'),
           sg.Column(layout4,visible=False, key='-COL4-')],
          [sg.Button('Close'),
           sg.Button('PDM'),
           sg.Button('Plot Tool'),
           sg.Button('TestPlot')]]

# Create the window
_VARS['window'] = sg.Window("Patient Data Manager", layout,resizable=True)

layout = 1 #Current visible layout




# Create an event loop
while True:
        
    event, values = _VARS['window'].read()
    
    
    if event == "PDM":
        _VARS['window'][f"-COL{layout}-"].update(visible=False)
        layout = 1
    
        _VARS['window'][f"-COL{layout}-"].update(visible=True)
    #print(layout) 
    if event == "View Formula":
                      
        _VARS['window'][f"-COL{layout}-"].update(visible=False)
         #layout = layout + 1 if layout < 3 else 1
        layout = 2
        
        _VARS['window'][f"-COL{layout}-"].update(visible=True)
    #print(layout)
        
    if event == "Plot Tool":
        
        _VARS['window'][f"-COL{layout}-"].update(visible=False)
        layout = 3        
        _VARS['window'][f"-COL{layout}-"].update(visible=True)
    #print(layout)
        break
    
    #Loads input stored in values list (0 = patientNumber, 1=dfName)
    if event == "Load":
        if values[1] == "breathD":
           breathD = halp.patientManager(values[0],values[1])
        elif values[1] == "esoData":
            esoData = halp.patientManager(values[0],values[1])
        elif values[1] == "FFFT":
            mod_FFFT = halp.patientManager(values[0],values[1])
        elif values[1] == "entire":
            breathD,esoData,mod_FFFT = halp.patientManager(values[0],values[1])
            
        
        print(f"Accessing Patient Nr. {values[0]}")
        print(f"Loading {values[1]} dataset")
        #break
    
    if event == "Plot":
        
        if values[4] == "breathD":
            halp.sub_plotter(breathD, values[5], values[6], int(values[7]))
        if values[4] == "esoData":
            halp.sub_plotter(esoData, values[5], values[6], int(values[7]))
        if values[4] == "mod_FFFT":
            halp.sub_plotter(mod_FFFT, values[5], values[6], int(values[7]))
        
    if event == "Hide Formula":
        _VARS['window'][f"-COL{layout}-"].update(visible=False)
        layout = 1        
        _VARS['window'][f"-COL{layout}-"].update(visible=True) 
        
    if event == "TestPlot":
        _VARS['window'][f"-COL{layout}-"].update(visible=False)
        layout = 4        
        _VARS['window'][f"-COL{layout}-"].update(visible=True)
        fig = plt.figure()
        fig = halp.sub_plotter(mod_FFFT, 'Time', 'flow', 4)
        halp.draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)   
       
    
        
        
    # End program if user closes window or
    # presses the OK button
    if event == "Close" or event == sg.WIN_CLOSED:            
        break
   
    
_VARS['window'].close()

# Begin The Data Exploration
#Equation of motion:
    #Pvent + Pmus = (Vt/CRS)+Raw*Vi+PEEP+PEEPi
    
#%% Calculate compliance:
    #CRS = deltaV/deltaP = Vt/(Pplat-PEEP) = Vt/{Transpulmonary Pressure}
    
# First we add a new compliance column
mod_FFFT['C'] = [None] * len(mod_FFFT)

for i in range(len(mod_FFFT)):
    mod_FFFT.at[i, 'C'] = mod_FFFT.at[i, 'C'] ###FINISH LATER



# %% Add Transpulmonary pressure 
for i in range(len(esoData)):
    esoData.at[i,'PL'] = esoData.at[i,'pao']-esoData.at[i,'peso']
    
PL_error = esoData.index[esoData['PL'] > 100].tolist()

#%%
breathD, esoData, FFFT = halp.patientManager(1, "entire")


test = halp.patientManager(1,"breathD")
