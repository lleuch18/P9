function Write_To_CSV(patientdata, esoData, FFFT, patientNumber, part)
% Write the struct to excel format
%Concatinates filepath for parent directory, with patientNumber and
%corresponding filename

%Split patientNumber, in order to retrieve to int for easier file
%structuring
temp_patientNr = split(patientNumber,'t');
temp_patientNr = temp_patientNr{3};

%breathD
filepath_breathD = strcat('C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data\patients\',patientNumber,'\part', part,'\breathD',temp_patientNr,part,'.csv')
writetable(struct2table(patientdata), filepath_breathD)

%esoData
filepath_esoData = strcat('C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data\patients\',patientNumber,'\part',part,'\esoData',temp_patientNr,part,'.csv')
writetable(struct2table(esoData), filepath_esoData)

%FFFT
filepath_FFFT = strcat('C:\Users\Lasse\OneDrive\Skrivebord\ST9\P9\Data\patients\',patientNumber,'\part',part,'\FFFT',temp_patientNr,part,'.csv')
writetable(struct2table(FFFT), filepath_FFFT)
end