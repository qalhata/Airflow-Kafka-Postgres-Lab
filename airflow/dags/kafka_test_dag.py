from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.providers.postgres.hooks.postgres import PostgresHook
from kafka import KafkaProducer, KafkaConsumer
import json
import time
from random import randint, uniform

@dag(dag_id="kafka_consumer_dag", schedule_interval=None, start_date=days_ago(1), catchup=False, tags=["kafka", "postgres", "streaming"])
def kafka_consumer_dag():

    @task()
    def produce_sensor_data():
        """Produces 10 sample sensor messages to the 'sensors_topic'."""
        producer = KafkaProducer(
            bootstrap_servers=['kafka-broker:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Producing 10 sensor messages...")
        for i in range(10):
            data = {
                'device_id': randint(1, 100),
                'temperature': round(uniform(15.0, 30.0), 2),
                'timestamp': int(time.time())
            }
            producer.send('sensors_topic', value=data)
            print(f"Sent: {data}")
            time.sleep(0.1)
        producer.flush()
        producer.close()

    @task()
    def consume_and_load_to_db():
        """Consumes messages from 'sensors_topic' and loads them into PostgreSQL."""
        consumer = KafkaConsumer(
            'sensors_topic',
            bootstrap_servers='kafka-broker:9092',
            auto_offset_reset='earliest',
            group_id='airflow-db-loader-consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=5000  # Stop after 5s of no new messages
        )
        
        hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        print("Consuming messages and loading to DB...")
        
        # Collect all messages for a bulk insert
        records_to_insert = [
            (msg.value['device_id'], msg.value['temperature'], msg.value['timestamp'])
            for msg in consumer
        ]
        
        if records_to_insert:
            cursor.executemany(
                "INSERT INTO sensor_readings (device_id, temperature, timestamp) VALUES (%s, %s, %s)",
                records_to_insert
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Loaded {len(records_to_insert)} messages into the database.")

    produce_sensor_data() >> consume_and_load_to_db()

kafka_consumer_dag = kafka_consumer_dag()
