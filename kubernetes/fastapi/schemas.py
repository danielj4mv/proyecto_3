from pydantic import BaseModel

class CoverType(BaseModel):
   
    encounter_id: int = 149190                  
    patient_nbr: int = 86047875                            
    number_diagnoses: int = 9           
    admission_type_id: int = 1          
    discharge_disposition_id: int = 3  
    admission_source_id: int = 7    
    time_in_hospital: int = 10  
    num_lab_procedures: int = 59  
    num_procedures: int = 5 
    num_medications: int = 18
    number_outpatient: int = 0           
    number_emergency: int = 0           
    number_inpatient: int = 1
