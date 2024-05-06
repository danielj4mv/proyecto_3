import streamlit as st
import requests
import json

# Título de la página
st.title('Formulario para Datos de Pacientes')
st.subheader('Información del modelo usado')
st.json(requests.get("http://10.43.101.157:8085/").json())

# Crear formulario con sus campos
with st.form(key='patient_data_form'):
    encounter_id = st.number_input('Encounter ID', value=149190)
    patient_nbr = st.number_input('Patient Number', value=86047875)
    number_diagnoses = st.number_input('Number of Diagnoses', value=9)
    admission_type_id = st.number_input('Admission Type ID', value=1)
    discharge_disposition_id = st.number_input('Discharge Disposition ID', value=3)
    admission_source_id = st.number_input('Admission Source ID', value=7)
    time_in_hospital = st.number_input('Time in Hospital', value=10)
    num_lab_procedures = st.number_input('Number of Lab Procedures', value=59)
    num_procedures = st.number_input('Number of Procedures', value=5)
    num_medications = st.number_input('Number of Medications', value=18)
    number_outpatient = st.number_input('Number of Outpatient Visits', value=0)
    number_emergency = st.number_input('Number of Emergency Visits', value=0)
    number_inpatient = st.number_input('Number of Inpatient Visits', value=1)

    submit_button = st.form_submit_button(label='Submit')

# Acción a realizar al enviar el formulario
if submit_button:
    data = {
        "Encounter_ID": encounter_id,
        "Patient_Nbr": patient_nbr,
        "Number_Diagnoses": number_diagnoses,
        "Admission_Type_ID": admission_type_id,
        "Discharge_Disposition_ID": discharge_disposition_id,
        "Admission_Source_ID": admission_source_id,
        "Time_in_Hospital": time_in_hospital,
        "Num_Lab_Procedures": num_lab_procedures,
        "Num_Procedures": num_procedures,
        "Num_Medications": num_medications,
        "Number_Outpatient": number_outpatient,
        "Number_Emergency": number_emergency,
        "Number_Inpatient": number_inpatient
    }

    # Mostrar los datos como JSON en la aplicación
    #st.json(data)

    # Generar predición
    response = requests.post("http://10.43.101.157:8085/predict", json=data)
    st.subheader('Predicción (Dias transcurridos hasta la readmisión del paciente)')
    st.json(response.json())
