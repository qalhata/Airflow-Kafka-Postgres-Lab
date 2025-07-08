# ✅ Start with a base image
FROM apache/airflow:2.7.2

# ✅ Switch to root to install system dependencies
USER root

# ✅ System packages needed for building Python wheels (esp. for spaCy, torch, etc.)
RUN apt-get update && \
    apt-get install -y gcc g++ build-essential curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ✅ Switch to airflow user before pip installations
USER airflow


RUN pip install --no-cache-dir --upgrade pip setuptools wheel Cython

# ✅ Option 1: Use COPY + requirements.txt (preferred for readability)
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

RUN python -m spacy download en_core_web_sm


# ✅ Option 2 (if no requirements.txt): install directly
# RUN pip install --no-cache-dir kafka-python fastapi uvicorn pandas ...
