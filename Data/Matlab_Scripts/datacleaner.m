function patientdata = datacleaner(patientdata,FFFT)
fn = fieldnames(patientdata)
fn_remove = fieldnames(FFFT)

for k =1:numel(fn) %loop through every fieldname of breathD
    for j = 1:numel(fn_remove) %loop through every field names to be removed
        if strcmp(fn{k},fn_remove{j}) %If name of field matches name to be removed, remove field            
           %breathD.(fn{k}) = [];
           patientdata = rmfield(patientdata,fn{k});           
        end
    end    
end
patientdata = rmfield(patientdata,'TimeStamp') %Timestamp is emptry at the beginning (prob for anonymization)

patientdata = rmfield(patientdata,'esoData')

end