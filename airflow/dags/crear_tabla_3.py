import os
import requests
import pandas as pd
import psycopg2.extras
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

default_args = {
    'owner': 'user',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 28),
    'email': ['user@mail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

dag = DAG(
    'Cargar_Datos_Diabetes',
    default_args=default_args,
    description='Download, store and process diabetes data',
    schedule_interval=timedelta(days=20),
)

def download_data(**kwargs):
    _data_root = '/opt/airflow/data/Diabetes'
    _data_filepath = os.path.join(_data_root, 'Diabetes.csv')
    os.makedirs(_data_root, exist_ok=True)
    if not os.path.isfile(_data_filepath):
        url = 'https://docs.google.com/uc?export=download&id=1k5-1caezQ3zWJbKaiMULTGq-3sz6uThC'
        r = requests.get(url, allow_redirects=True)
        if r.status_code == 200:
            with open(_data_filepath, 'wb') as f:
                f.write(r.content)

def get_data(**kwargs):
    _data_root = '/opt/airflow/data/Diabetes'
    _data_filepath = os.path.join(_data_root, 'Diabetes.csv')
    df = pd.read_csv(_data_filepath)
    return df

def store_data(**kwargs):
    df = kwargs['ti'].xcom_pull(task_ids='get_data_task')
    if 'A1Cresult' in df.columns:
       df = df.drop(columns=['A1Cresult'])
    
    rename_columns = {
        'A1Cresult':'a1cresult',
        'glyburide-metformin': 'glyburide_metformin',
        'glipizide-metformin': 'glipizide_metformin',
        'glimepiride-pioglitazone': 'glimepiride_pioglitazone',
        'metformin-rosiglitazone': 'metformin_rosiglitazone',
        'metformin-pioglitazone': 'metformin_pioglitazone'
    }
    df.rename(columns=rename_columns, inplace=True)    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_test_conn', schema='airflow')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # Borrar el contenido existente y recrear la tabla
    cursor.execute("DROP TABLE IF EXISTS diabetes_data;")
    cursor.execute("""
        CREATE TABLE diabetes_data (
            "encounter_id" INT,
            "patient_nbr" INT,
            "race" VARCHAR(50),
            "gender" VARCHAR(50),
            "age" VARCHAR(20),
            "weight" VARCHAR(50),
            "admission_type_id" INT,
            "discharge_disposition_id" INT,
            "admission_source_id" INT,
            "time_in_hospital" INT,
            "payer_code" VARCHAR(50),
            "medical_specialty" VARCHAR(255),
            "num_lab_procedures" INT,
            "num_procedures" INT,
            "num_medications" INT,
            "number_outpatient" INT,
            "number_emergency" INT,
            "number_inpatient" INT,
            "diag_1" VARCHAR(50),
            "diag_2" VARCHAR(50),
            "diag_3" VARCHAR(50),
            "number_diagnoses" INT,
            "max_glu_serum" VARCHAR(50),
            "a1cresult" VARCHAR(50),
            "metformin" VARCHAR(50),
            "repaglinide" VARCHAR(50),
            "nateglinide" VARCHAR(50),
            "chlorpropamide" VARCHAR(50),
            "glimepiride" VARCHAR(50),
            "acetohexamide" VARCHAR(50),
            "glipizide" VARCHAR(50),
            "glyburide" VARCHAR(50),
            "tolbutamide" VARCHAR(50),
            "pioglitazone" VARCHAR(50),
            "rosiglitazone" VARCHAR(50),
            "acarbose" VARCHAR(50),
            "miglitol" VARCHAR(50),
            "troglitazone" VARCHAR(50),
            "tolazamide" VARCHAR(50),
            "examide" VARCHAR(50),
            "citoglipton" VARCHAR(50),
            "insulin" VARCHAR(50),
            "glyburide_metformin" VARCHAR(50),
            "glipizide_metformin" VARCHAR(50),
            "glimepiride_pioglitazone" VARCHAR(50),
            "metformin_rosiglitazone" VARCHAR(50),
            "metformin_pioglitazone" VARCHAR(50),
            "change" VARCHAR(10),
            "diabetesMed" VARCHAR(10),
            "readmitted" VARCHAR(50)
        );
    """)

    # Preparar la consulta de inserción
    columns = [f'"{column}"' for column in df.columns]
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO diabetes_data ({', '.join(columns)}) VALUES ({placeholders})"

    # Insertar datos fila por fila
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()

    # Opcional: Exportar a CSV el éxito del proceso
    try:
        df_success = pd.read_sql('SELECT * FROM  ', conn)
        df_success.to_csv('/opt/airflow/data/success.csv', index=False)
    except Exception as e:
        print("Error reading from database:", e)

# Configurar tareas en el DAG
download_task = PythonOperator(
    task_id='download_data_task',
    python_callable=download_data,
    dag=dag,
)

get_data_task = PythonOperator(
    task_id='get_data_task',
    python_callable=get_data,
    dag=dag,
    provide_context=True
)

store_data_task = PythonOperator(
    task_id='store_data_task',
    python_callable=store_data,
    dag=dag,
    provide_context=True
)

# Definir dependencias
download_task >> get_data_task >> store_data_task
