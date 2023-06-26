function FFFT = FFFT_divider(patientdata)

FFFT.Flow = patientdata.Flow
FFFT.FCO2 = patientdata.FCO2
FFFT.FO2 = patientdata.FO2
FFFT.TimeMinRel = patientdata.TimeMinRel
FFFT.TimeMinAbs = patientdata.TimeMinAbs

%Pull out rawTime in order to transpose it
temp_time = patientdata.rawTime 
temp_time_trans = temp_time.' 

FFFT.rawTime = temp_time_trans

end