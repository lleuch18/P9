%%
clc
clear all




%% Divide breath-by-breath data into structs of even sizes, in order to convert to CSV format
%Step 1 transfer individual structs to new struct


%Step 2 remove the pulled out structs from breathD
%% Remove prreviously pulled out structs fromm breathD


%% Pull out esoData


%% Works
patientNumber = 'patient5'
filepath = strcat("C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data\protpesData\",patientNumber)
%Loads patient data from the filepath
patientdata_temp = dataloader(filepath)
patientdata = patientdata_temp.parts{1}
%% Works
FFFT = FFFT_divider(patientdata)
esoData = esoData_divider(patientdata)

%% Works
patientdata = datacleaner(patientdata,FFFT)

%% 
for nr=1:23
    patientNumber = strcat('patient', int2str(nr));
    Mat_to_CSV_Porter(patientNumber)
end






