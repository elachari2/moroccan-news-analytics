import pandas as pd
import json
from minio import Minio
import io
import os
import datetime
import re
import psycopg2
from psycopg2.extras import execute_values
from textblob import TextBlob
from deep_translator import GoogleTranslator

class ProcessingEngine:
    def __init__(self):
        self.minio_client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False
        )
        self.bucket = "data-lake"
        self.db_url = os.getenv("DB_URL", "postgresql://admin:adminpassword@postgres/news_dw")
        
        if not self.minio_client.bucket_exists(self.bucket):
            self.minio_client.make_bucket(self.bucket)

    def run_bronze_to_silver(self):
        """Clean data and move from Bronze to Silver layer"""
        print("Starting Bronze to Silver transformation...")
        
        objects = self.minio_client.list_objects(self.bucket, prefix="bronze/", recursive=True)
        all_articles = []

        for obj in objects:
            try:
                response = self.minio_client.get_object(self.bucket, obj.object_name)
                data = json.loads(response.read().decode('utf-8'))
                if isinstance(data, list):
                    all_articles.extend(data)
                else:
                    all_articles.append(data)
            except Exception as e:
                print(f"Error reading {obj.object_name}: {e}")

        if not all_articles:
            print("No data found in Bronze.")
            return

        df = pd.DataFrame(all_articles)
        
        # Cleaning
        df['title'] = df['title'].apply(self.clean_text)
        df['content'] = df['content'].apply(self.clean_text)
        
        # Remove duplicates within the batch
        df = df.drop_duplicates(subset=['title'])
        
        try:
            conn = psycopg2.connect(self.db_url)
            existing_titles_df = pd.read_sql("SELECT title FROM gold_news_analytics", conn)
            existing_titles = set(existing_titles_df['title'].tolist())
            conn.close()
            
            # Filter out existing articles
            df = df[~df['title'].isin(existing_titles)]
        except Exception as e:
            print(f"Error checking existing titles: {e}")

        if df.empty:
            print("No new articles to process after duplicate filtering.")
            return

        df['word_count'] = df['content'].apply(lambda x: len(x.split()))
        
        # Save to Gold (Postgres)
        self.save_to_postgres(df)
        print(f"Successfully processed {len(df)} new articles to Gold layer.")

    def clean_text(self, text):
        if not text: return ""
        text = re.sub(r'<.*?>', '', text) 
        text = text.strip()
        return text

    def save_to_postgres(self, df):
        """Insert data into PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Prepare data for insertion
            records = [
                (
                    r['source'], r['title'], r['content'], r['category'], 
                    r['published_date'], r['title'], r['word_count']
                ) 
                for _, r in df.iterrows()
            ]
            
            query = """
                INSERT INTO gold_news_analytics 
                (source, title, content, category, published_date, cleaned_text, word_count)
                VALUES %s
            """
            
            execute_values(cur, query, records)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    engine = ProcessingEngine()
    engine.run_bronze_to_silver()
