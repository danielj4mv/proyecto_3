from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from datetime import datetime, timedelta

default_args = {
    'owner': 'user',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 28),
    'email': ['user@mail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'process_and_clean_diabetes_data',
    default_args=default_args,
    description='Extract and preprocess diabetes data',
    schedule_interval=timedelta(days=1),
)

def get_engine():
    user = 'airflow'
    password = 'airflow'
    host = 'postgres'  # Asegúrate que el hostname coincide con el nombre del servicio en docker-compose
    port = 5432
    dbname = 'airflow'
    return create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')



def clean_diagnostic_columns(df, columns):
    for column in columns:
        # Reemplaza cualquier caracter no-numérico con nada
        df[column] = df[column].str.replace(r'\D', '', regex=True)
        # Convierte a float; usa to_numeric para manejar errores de conversión
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def extract_and_preprocess_data():
    engine = get_engine()
    
    # Leer los datos directamente usando el engine
    df = pd.read_sql('SELECT * FROM diabetes_data', engine)
    
    # Preprocesamiento general de los datos
    df.replace('?', pd.NA, inplace=True)
    df.drop(['weight', 'payer_code', 'medical_specialty', 'max_glu_serum', 'a1cresult'], axis=1, inplace=True)
    df_cleaned = df.dropna()

    # Limpieza específica de las columnas diag_1, diag_2, diag_3
    columns_to_clean = ['diag_1', 'diag_2', 'diag_3']
    df_cleaned = clean_diagnostic_columns(df_cleaned, columns_to_clean)

    # Eliminar filas con cualquier valor NaN restante
    df_cleaned = df.dropna()
    
    # Guardar los datos limpios en una nueva tabla
    df_cleaned.to_sql('diabetes_df_clean', engine, if_exists='replace', index=False)
    
    try:
        df_cleaned.to_csv('/opt/airflow/data/success_clean.csv', index=False)
    except Exception as e:
        print("Error reading from database:", e)


preprocess_task = PythonOperator(
    task_id='extract_and_preprocess_data',
    python_callable=extract_and_preprocess_data,
    dag=dag
)

preprocess_task
