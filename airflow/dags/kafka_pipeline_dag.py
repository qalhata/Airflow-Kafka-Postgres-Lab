from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from kafka import KafkaProducer, errors
import json
import time
import pandas as pd

def get_kafka_producer():
    """Establishes a connection to Kafka, with retries."""
    for _ in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=['kafka-broker:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            print("Successfully connected to Kafka.")
            return producer
        except errors.NoBrokersAvailable:
            print("Kafka not available, retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Kafka broker not available after 10 attempts")

@dag(
    'kafka_producer_stream_dag',
    default_args={'owner': 'airflow', 'retries': 1},
    description='Simulates Kafka producers for tweet and sensor data',
    schedule_interval='@once',
    start_date=days_ago(1),
    catchup=False,
    tags=['kafka', 'producer']
)
def kafka_producer_stream_dag():

    @task
    def produce_tweets_from_csv():
        """Reads tweets from a CSV and produces them to a Kafka topic."""
        producer = get_kafka_producer()
        df = pd.read_csv('/opt/airflow/data/tweets_dataset.csv')
        print(f"Producing {len(df)} tweets from CSV...")
        for _, row in df.iterrows():
            # The CSV only contains 'id' and 'text'.
            message = {'text': row['text']}
            producer.send('tweets_topic', value=message)
        producer.flush()
        producer.close()
        print("Finished producing tweets.")

    @task
    def produce_sensors_from_csv():
        """Reads sensor data from a CSV and produces it to a Kafka topic."""
        producer = get_kafka_producer()
        # This task assumes a 'sensor_dataset.csv' exists in the data directory.
        # If not, it will fail, which is expected behavior.
        df = pd.read_csv('/opt/airflow/data/sensor_dataset.csv')
        print(f"Producing {len(df)} sensor readings from CSV...")
        for _, row in df.iterrows():
            message = {'device_id': int(row['device_id']), 'temperature': float(row['temperature']), 'timestamp': int(row['timestamp'])}
            producer.send('sensors_topic', value=message)
        producer.flush()
        producer.close()
        print("Finished producing sensor data.")

    produce_tweets_from_csv() >> produce_sensors_from_csv()

kafka_producer_stream_dag()