import os
import mlflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
#from sklearn.impute import SimpleImputer
import pandas as pd
from datetime import datetime, timedelta

# Configuración del entorno
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://s3:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'mlflows3'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'mlflows3'
os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow-webserver:5000'

mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
mlflow.set_experiment("diabetes_model_training")

default_args = {
    'owner': 'user',
    'start_date': datetime(2024, 3, 28),
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

dag = DAG(
    'train_models_with_mlflow',
    default_args=default_args,
    description='Train machine learning models and track with MLflow',
    schedule_interval='@weekly',
    catchup=False
)

def fetch_data():
    hook = PostgresHook(postgres_conn_id='postgres_test_conn', schema='airflow')
    df = hook.get_pandas_df("SELECT encounter_id, number_diagnoses, admission_type_id, discharge_disposition_id, admission_source_id, time_in_hospital, num_lab_procedures, num_procedures, num_medications, number_outpatient, number_emergency, number_inpatient, readmitted FROM diabetes_df_clean")
    #df = hook.get_pandas_df("SELECT * FROM diabetes_df_clean")

    return df


def train_model(model, model_name, production=False):
    df = fetch_data()
    X = df.drop(['readmitted'], axis=1)
    y = df['readmitted']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    with mlflow.start_run():

        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        mlflow.log_param("model_type", model_name)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)
        
        if production:
            client = mlflow.tracking.MlflowClient()
            run_id = mlflow.active_run().info.run_id
            model_uri = f"runs:/{run_id}/model"
            version_info = client.create_model_version(name=model_name, source=model_uri, run_id=run_id)
            version = version_info.version
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage="Production",
                archive_existing_versions=True
            )



task_fetch_data = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    dag=dag
)

task_train_rf = PythonOperator(
    task_id='train_random_forest',
    python_callable=lambda: train_model(RandomForestClassifier(n_estimators=100, random_state=42), "Random_Forest_Model_dac"),
    dag=dag
)

task_train_gb = PythonOperator(
    task_id='train_gradient_boosting',
    python_callable=lambda: train_model(GradientBoostingClassifier(n_estimators=100, random_state=42), "Gradient_Boosting_Model_dac", production=True),
    dag=dag
)

task_fetch_data >> [task_train_rf, task_train_gb]
