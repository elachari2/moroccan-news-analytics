from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
import json
import pandas as pd
from minio import Minio
import io

# Add scripts paths
sys.path.append('/opt/airflow/scripts')

from scraper.scraper import NewsScraper
from transformation.processing_engine import ProcessingEngine

default_args = {
    'owner': 'ZOUBAIDA_SALMA', 
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def ingest_batch():
    scraper = NewsScraper()
    news = scraper.get_all_news()
    
    # Save to MinIO Bronze
    client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
    if not client.bucket_exists("data-lake"):
        client.make_bucket("data-lake")
        
    content = json.dumps(news).encode('utf-8')
    filename = f"bronze/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    client.put_object("data-lake", filename, io.BytesIO(content), len(content))
    print(f"Ingested {len(news)} articles to {filename}")

def transform_data():
    engine = ProcessingEngine()
    engine.run_bronze_to_silver()
    print("Transformation complete.")

with DAG(
    'moroccan_news_pipeline',
    default_args=default_args,
    description='Pipeline for Moroccan News Analysis',
    schedule_interval=timedelta(hours=6),
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id='ingest_from_sources',
        python_callable=ingest_batch
    )

    t2 = PythonOperator(
        task_id='transform_to_silver',
        python_callable=transform_data
    )

    t1 >> t2
