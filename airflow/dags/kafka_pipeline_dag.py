# dags/kafka_pipeline_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess
import os

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'kafka_producer_stream_dag',
    default_args=default_args,
    description='Simulates Kafka producers for tweet and sensor data',
    schedule_interval='@once',
    start_date=days_ago(1),
    catchup=False
)

produce_tweets = BashOperator(
    task_id='run_producer_tweets',
    bash_command='python /opt/airflow/kafka/producer_tweets.py',
    dag=dag
)

produce_sensors = BashOperator(
    task_id='run_producer_sensors',
    bash_command='python /opt/airflow/kafka/producer_sensors.py',
    dag=dag
)

produce_tweets >> produce_sensors