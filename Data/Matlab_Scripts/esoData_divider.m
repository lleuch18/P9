function esoData = esoData_divider(patientdata)
esoData = patientdata.esoData

esoData = rmfield(esoData, 'TimeStamp')
esoData = rmfield(esoData, 'Filename')

end