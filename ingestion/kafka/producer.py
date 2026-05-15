import time
import json
import random
from kafka import KafkaProducer

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=json_serializer
)

topics = ["Politique", "Sport", "Culture", "Économie"]

print("Simulation du Producer Kafka lancée...")
while True:
    data = {
        "source": "Streaming_Live",
        "title": f"Flash Info {random.randint(100, 999)}",
        "content": "Alerte en temps réel sur l'actualité au Maroc.",
        "category": random.choice(topics),
        "url": "http://live-news.ma/flash",
        "timestamp": time.time()
    }
    producer.send('raw_news', data)
    print(f"Envoyé: {data['title']}")
    time.sleep(10)
