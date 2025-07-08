from kafka import KafkaProducer, errors
import json, time, random
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv(dotenv_path="kafka.env")

# Retry logic for Kafka producer connection
# This will attempt to connect to the Kafka broker up to 10 times, waiting 5 seconds between attempts
for _ in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka-broker:9092',
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        break
    except errors.NoBrokersAvailable:
        print("Kafka not available, retrying in 5 seconds...")
        time.sleep(5)
else:
    raise Exception("Kafka broker not available after 10 attempts")

# Read tweet data from CSV file and produce messages to Kafka topic
# Ensure the CSV file exists in the specified path
df = pd.read_csv('data/tweets_dataset.csv')
for _, row in df.iterrows():
    message = {
        'text': row['text'],
        'sentiment': row['sentiment'],
        'created_at': row['created_at']
    }
    producer.send('tweets_topic', value=message)
    print(f"Produced tweet: {message}")
    time.sleep(5)

producer.flush()
producer.close()

