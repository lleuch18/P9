function Mat_to_CSV_Porter(patientNumber)
%concatenates the patientNumber to the parent directory filepath
filepath = strcat("C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data\protpesData\",patientNumber);
%Loads patient data from the filepath
patientdata_temp = dataloader(filepath);

%For every part of patient data from the clinical trial, divide into
%breathD, FFFT and esoData. Then clean it, and write to csv.
for part = 1:1:numel(patientdata_temp.parts);
     
    patientdata = patientdata_temp.parts{part};
    
    %Pulls out the FFFT and esoData from the patientdata. This is done to
    %create scalar structs (even sized fields), in order to allow for writing
    %tables to csv.
    FFFT = FFFT_divider(patientdata);
    esoData = esoData_divider(patientdata);
    
    %Removes the previously pulled out fields from the original data
    patientdata = datacleaner(patientdata,FFFT);
    
    %Convert partnr to string in order to concatenate into a filepath
    partstr = int2str(part);
    Write_To_CSV(patientdata,esoData,FFFT,patientNumber,partstr);
end
end