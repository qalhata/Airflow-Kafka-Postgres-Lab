from kafka import KafkaConsumer
import psycopg2, json

try:
    # Connect to the PostgreSQL container using its service name from docker-compose.yml
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="postgres-stream",
        port="5432"
    )
    cursor = conn.cursor()
    print("Successfully connected to PostgreSQL.")
    
    # Connect to the Kafka container using its service name from docker-compose.yml
    sensor_consumer = KafkaConsumer(
        'sensors_topic', # This should match the producer's topic
        bootstrap_servers='kafka-broker:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='pg-sensor-consumer-dag', # Use a unique group_id
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000 # Corrected typo and set timeout
    )
    print("Successfully connected to Kafka topic 'sensors_topic'.")
    
    for message in sensor_consumer:
        data = message.value
        print(f"[Sensor_Consumer] Received: {data}")
        # Assumes a table named 'sensor_readings' exists from db_init.sql
        cursor.execute(
            "INSERT INTO sensor_readings (device_id, temperature, timestamp) VALUES (%s, %s, %s)",
            (data['device_id'], data['temperature'], data['timestamp'])
        )
        conn.commit()
        print(f"[Sensor_Consumer] Inserted: {data}")
finally:
    if 'conn' in locals() and conn is not None:
        cursor.close()
        conn.close()
        print("PostgreSQL connection closed.")
