from __future__ import annotations

import pendulum
import json

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator


def _ingest_from_kafka(**context):
    """
    ## Ingest Task
    This task consumes messages from the 'tweets_topic' Kafka topic.
    It will run after the 'kafka_producer_stream_dag' produces messages.
    """
    from kafka import KafkaConsumer
    # The `kafka-broker` service is defined in docker-compose.lab3.yml
    # Airflow containers can reach it using its service name.
    consumer = KafkaConsumer(
        'tweets_topic',
        bootstrap_servers=['kafka-broker:9092'],
        auto_offset_reset='earliest',
        group_id='airflow-nlp-group',
        value_deserializer=lambda x: x.decode('utf-8'),
        consumer_timeout_ms=5000,  # Stop after 5s of no new messages
        max_poll_records=20  # Process up to 20 messages per run
    )

    messages = [msg.value for msg in consumer]
    consumer.close()

    if not messages:
        print("No new messages found in tweets_topic.")
        # Use Airflow's mechanism to skip downstream tasks
        from airflow.exceptions import AirflowSkipException
        raise AirflowSkipException("No messages to process.")

    print(f"Ingested {len(messages)} messages.")
    context['ti'].xcom_push(key='texts_to_process', value=messages)


def _process_with_spacy(**context):
    """
    ## NLP Processing Task
    This task pulls the text from the ingestion task, processes it using spaCy
    to find named entities, and pushes the result.
    """
    import spacy

    # Load the model inside the task for better performance and isolation.
    # The model is downloaded when the Docker image is built.
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spaCy model 'en_core_web_sm' not found.")
        print("Please ensure it's downloaded in your Dockerfile, e.g.:")
        print("RUN python -m spacy download en_core_web_sm")
        raise

    texts = context['ti'].xcom_pull(key='texts_to_process', task_ids='ingest_from_kafka')
    if not texts:
        print("No text received from ingestion task.")
        return

    print(f"Processing {len(texts)} texts with spaCy...")

    # Use nlp.pipe for efficient processing of multiple texts
    docs = nlp.pipe(texts)
    all_entities = []

    for doc in docs:
        entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
        all_entities.append({'original_text': doc.text, 'entities': entities})

    print(f"Finished processing. Found entities in {len(all_entities)} documents.")
    # XComs can handle dicts/lists automatically (they are json-serialized)
    context['ti'].xcom_push(key='processed_entities', value=all_entities)


def _save_result(**context):
    """
    ## Save Result Task
    This task pulls the processed data and saves it to the `tweet_entities`
    table in the PostgreSQL database.
    """
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    entities = context['ti'].xcom_pull(key='processed_entities', task_ids='process_with_spacy')

    if not entities:
        print("No entities to save.")
        return

    # Use the default Airflow connection to Postgres
    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_conn()
    cursor = conn.cursor()

    print(f"---- Saving {len(entities)} processed records to database ----")

    for record in entities:
        original_text = record['original_text']
        # Convert the list of entity dicts to a JSON string for the JSONB column
        entities_json = json.dumps(record['entities'])
        cursor.execute(
            "INSERT INTO tweet_entities (original_text, entities) VALUES (%s, %s)",
            (original_text, entities_json)
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("---- All records saved successfully ----")


with DAG(
    dag_id='nlp_kafka_spacy_pipeline',
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=['nlp', 'kafka', 'spacy', 'example'],
    doc_md="""
    ### NLP Pipeline DAG
    This DAG demonstrates a simple NLP pipeline:
    1.  **Ingest**: Consumes data from a Kafka topic (simulated).
    2.  **Process**: Uses spaCy to perform Named Entity Recognition (NER).
    3.  **Save**: Stores the result (simulated by logging).
    """
) as dag:
    ingest_task = PythonOperator(
        task_id='ingest_from_kafka',
        python_callable=_ingest_from_kafka,
    )

    process_task = PythonOperator(
        task_id='process_with_spacy',
        python_callable=_process_with_spacy,
    )

    save_task = PythonOperator(
        task_id='save_result',
        python_callable=_save_result,
    )

    # Define the task dependencies
    ingest_task >> process_task >> save_task