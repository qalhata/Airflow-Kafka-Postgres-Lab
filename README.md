# Data Engineering Lab: Real-time Pipelines with Kafka and Airflow

## Overview

This project is a self-contained data engineering laboratory environment built with Docker Compose. It showcases how to build, orchestrate, and monitor real-time data pipelines using Apache Airflow and Apache Kafka.

It includes two main examples:
1.  A standard ETL pipeline that streams sensor data via Kafka and stores it in a PostgreSQL database.
2.  An advanced NLP pipeline that consumes tweet data from Kafka, performs Named Entity Recognition (NER) using spaCy, and stores the structured results in PostgreSQL.

This lab is designed to be a practical, hands-on introduction to the integration of these powerful data engineering tools.

## Core Technologies

-   **Orchestration:** [Apache Airflow](https://airflow.apache.org/)
-   **Data Streaming:** [Apache Kafka](https://kafka.apache.org/) & [Zookeeper](https://zookeeper.apache.org/)
-   **Database:** [PostgreSQL](https://www.postgresql.org/)
-   **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
-   **NLP:** [spaCy](https://spacy.io/)
-   **Core Python:** `kafka-python`, `pandas`, `psycopg2-binary`

## Project Structure

The project is organized to separate infrastructure configuration from application code.

-   `docker-compose.yml`: The single source of truth for defining and running all services (Airflow, Kafka, Postgres, etc.).
-   `airflow/`: Contains Airflow-specific configurations and code.
    -   `Dockerfile`: Builds the custom Airflow image, installing all Python dependencies.
    -   `requirements.txt`: Lists all Python packages needed for the pipelines.
    -   `dags/`: The heart of the project, containing the Airflow DAGs (pipeline definitions).
    -   `kafka/`: Contains the Python scripts for Kafka producers and consumers that are executed by the DAGs.
-   `postgres/`: Contains the database initialization script (`db_init.sql`).
-   `logs/`, `plugins/`, `data/`: Standard Airflow directories mounted into the containers for persistence and extensibility.

## Pipelines Explained

### 1. Basic ETL: `kafka_pipeline_dag`
This DAG demonstrates a fundamental streaming ETL process.
-   **Producer (`kafka_producer_stream_dag`)**: A separate DAG generates sample sensor data and publishes it to the `sensors_topic` in Kafka.
-   **Consumer (`kafka_pipeline_dag`)**: This DAG runs a consumer script that subscribes to the `sensors_topic`, reads the data, and writes it into the `sensors` table in our PostgreSQL database.

### 2. NLP Pipeline: `nlp_kafka_spacy_pipeline`
This DAG showcases a more complex, multi-stage data processing pipeline.
-   **Producer (`kafka_producer_stream_dag`)**: The same producer DAG also publishes sample tweet messages to the `tweets_topic`.
-   **ETL Process (`nlp_kafka_spacy_pipeline`)**:
    1.  **Ingest**: A task consumes messages from the `tweets_topic`.
    2.  **Process**: The text from the tweets is processed by a powerful spaCy model to perform Named Entity Recognition (NER), identifying entities like people, organizations, and locations.
    3.  **Save**: The final task connects to PostgreSQL and saves the original tweet along with the structured JSON of its extracted entities into the `tweet_entities` table.

## How to Run the Lab

### Prerequisites

-   Docker
-   Docker Compose

### Step 1: Launch the Environment

Navigate to the project's root directory (`workspace3`) in your terminal and run the following command. This will build the custom Airflow image and start all the necessary services.

```bash
docker-compose up --build -d
