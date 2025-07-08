from kafka import KafkaConsumer
import psycopg2, json


conn = psycopg2.connect(
    dbname="streamdb",
    user="postgres",
    password="yourpassword",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()


sensor_consumer = KafkaConsumer(
    'sensor_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='pg-consumer',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeeout_ms=5000
)

tweet_consumer = KafkaConsumer(
    'tweets_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=5000
)


for message in sensor_consumer:
    data = message.value
    cursor.execute(
        """
        INSERT INTO sensor_readings (device_id, temperature, timestamp)
        VALUES (%s, %s, %s)
    """, (data['device_id'], data['temperature'], data['timestamp'])
    )
    conn.commit()
    print("[Sensor_Consumer] Inserted:", data)



for message in tweet_consumer:
    data = message.value
    cursor.execute(
        "INSERT INTO tweets (text, sentiment, created_at) VALUES (%s, %s, %s)",
        (data['text'], data['sentiment'], data['created_at'])
    )
    conn.commit()
    print("[Tweet] Inserted:", data)

cursor.close()
conn.close()
