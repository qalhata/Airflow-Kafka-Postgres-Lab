from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
import subprocess
import os

@dag(schedule_interval=None, start_date=days_ago(1), catchup=False, tags=["kafka", "postgres", "streaming"])
def kafka_pipeline_dag():

    @task()
    def start_kafka_producer():
        subprocess.run(["python", "/opt/airflow/kafka/producer_sensors.py"], check=True)

    @task()
    def start_kafka_consumer():
        subprocess.run(["python", "/opt/airflow/postgres/consumer_to_db.py"], check=True)

    start_kafka_producer() >> start_kafka_consumer()

kafka_pipeline_dag = kafka_pipeline_dag()
