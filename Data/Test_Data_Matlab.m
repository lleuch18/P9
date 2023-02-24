%%
clc
clear all

load('./protpesData/protpes001_forstud.mat')
patientData = parts{1}

breathD = patientData(1)

class(breathD.inspStart(40))

%% Divide breath-by-breath data into structs of even sizes, in orderr to convert to CSV format
%Step 1 transfer individual structs to new struct
Flow_FCO2_FO2_Time.Flow = breathD.Flow
Flow_FCO2_FO2_Time.FCO2 = breathD.FCO2
Flow_FCO2_FO2_Time.FO2 = breathD.FO2
Flow_FCO2_FO2_Time.TimeMinRel = breathD.TimeMinRel
Flow_FCO2_FO2_Time.TimeMinAbs = breathD.TimeMinAbs

%Pull out rawTime in order to transpose it
temp_time = breathD.rawTime 
temp_time_trans = temp_time.' 

Flow_FCO2_FO2_Time.rawTime = temp_time_trans

%Step 2 remove the pulled out structs from breathD


%% Remove prreviously pulled out structs fromm breathD
fn = fieldnames(breathD)
fn_remove = fieldnames(Flow_FCO2_FO2_Time)

for k =1:numel(fn) %loop through every fieldname of breathD
    for j = 1:numel(fn_remove) %loop through every field names to be removed
        if strcmp(fn{k},fn_remove{j}) %If name of field matches name to be removed, remove field            
           %breathD.(fn{k}) = [];
           breathD = rmfield(breathD,fn{k});           
        end
    end    
end
breathD = rmfield(breathD,'TimeStamp') %Timestamp is emptry at the beginning (prob for anonymization)

%% Pull out esoData

esoData = breathD.esoData

esoData = rmfield(esoData, 'TimeStamp')
esoData = rmfield(esoData, 'Filename')
breathD = rmfield(breathD,'esoData')

%% Try writing the struct to excel format
%breathD
writetable(struct2table(breathD), 'breathD.csv')

%esoData
writetable(struct2table(esoData), 'esoData.csv')

%FFFT
writetable(struct2table(Flow_FCO2_FO2_Time), 'FFFT.csv')





