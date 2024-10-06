from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import boto3
from rdkit import Chem
from rdkit.Chem import Descriptors
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv


load_dotenv(".env")
DB_URL = getenv("DB_URL")


def extract_data(**kwargs):
    logging.info("Extracting data for the current day")
    query = "SELECT SMILES, column2, column3 FROM molecules_table WHERE date = CURRENT_DATE"
    engine = create_engine(DB_URL)
    df = pd.read_sql(query, con=engine)
    return df.to_dict()

def transform_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract_data')
    df = pd.DataFrame(data)
    logging.info("Transforming data")
    df['MolecularWeight'] = df['SMILES'].apply(lambda x: Descriptors.MolWt(Chem.MolFromSmiles(x)))
    df['LogP'] = df['SMILES'].apply(lambda x: Descriptors.MolLogP(Chem.MolFromSmiles(x)))
    df['TPSA'] = df['SMILES'].apply(lambda x: Descriptors.TPSA(Chem.MolFromSmiles(x)))
    df['HDonors'] = df['SMILES'].apply(lambda x: Descriptors.NumHDonors(Chem.MolFromSmiles(x)))
    df['HAcceptors'] = df['SMILES'].apply(lambda x: Descriptors.NumHAcceptors(Chem.MolFromSmiles(x)))
    df['Lipinski'] = (df['MolecularWeight'] < 500) & (df['LogP'] < 5) & (df['HDonors'] <= 5) & (df['HAcceptors'] <= 10)
    return df.to_dict()

def save_to_s3(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform_data')
    df = pd.DataFrame(data)
    
    filepath = '/tmp/molecules_data.xlsx'
    df.to_excel(filepath, index=False)
    
    logging.info("Uploading file to S3.")
    s3 = boto3.client('s3',
                      endpoint_url='http://minio:9000',
                      aws_access_key_id='minio_access_key',
                      aws_secret_access_key='minio_secret_key')
    
    bucket_name = 'my-bucket'
    s3.upload_file(filepath, bucket_name, 'molecules_data.xlsx')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

dag = DAG(
    'molecules_data_pipeline',
    default_args=default_args,
    description='A DAG to process molecular data and upload it to S3',
    schedule_interval='@daily',
)

t1 = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

t2 = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

t3 = PythonOperator(
    task_id='save_to_s3',
    python_callable=save_to_s3,
    provide_context=True,
    dag=dag,
)

t1 >> t2 >> t3
