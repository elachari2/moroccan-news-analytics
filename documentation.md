# 📄 Documentation Technique : Moroccan News Analytics

Bienvenue dans la documentation approfondie de la plateforme **Moroccan News Analytics**. Ce document fournit des détails techniques sur l'architecture, le flux de données, les schémas de base de données et les guides opérationnels.

---

## 🏗️ 1. Architecture Détaillée

Le système repose sur une architecture **Lakehouse** découplée, utilisant des conteneurs pour chaque brique fonctionnelle.

### 🧩 Composants Clés
*   **Ingestion :** Scrapers Python asynchrones.
*   **Transport :** Bus d'événements Kafka pour la résilience.
*   **Data Lake (Object Storage) :** MinIO pour le stockage immuable des données brutes.
*   **Traitement :** Moteur Spark/Pandas pour les transformations.
*   **Data Warehouse :** PostgreSQL pour le stockage dimensionnel.

---

## 📊 2. Modèle de Données (PostgreSQL)

Les données Gold sont structurées dans PostgreSQL pour optimiser les performances du Dashboard.

### Table `news_articles`
| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | SERIAL | Clé primaire unique. |
| `source` | VARCHAR(50) | Nom du site (Hespress, Akhbarona). |
| `title` | TEXT | Titre nettoyé de l'article. |
| `content` | TEXT | Corps de l'article (sans HTML). |
| `url` | TEXT | URL source (utilisée pour la déduplication). |
| `category` | VARCHAR(50) | Catégorie prédite ou extraite. |
| `sentiment` | VARCHAR(20) | Polarité (Positif, Négatif, Neutre). |
| `published_date` | TIMESTAMP | Date de publication originale. |
| `ingested_at` | TIMESTAMP | Date d'entrée dans le système. |

---

## 🚀 3. Pipeline ETL & Qualité (DQ)

Le pipeline est divisé en trois phases critiques :

### 🥉 Phase Bronze (Raw Ingestion)
*   **Action :** Capture des articles via `BeautifulSoup`.
*   **Kafka Topic :** `news-topic` (Partitionné par source).
*   **Stockage :** `minio/data-lake/bronze/YYYY/MM/DD/*.json`.

### 🥈 Phase Silver (Data Refining)
*   **Nettoyage :** Suppression des scripts JS, styles CSS et balises HTML.
*   **Validation :** Rejet des articles sans titre ou avec un contenu < 100 caractères.
*   **Format :** Conversion JSON ➔ Parquet (optimisation du stockage et de la lecture).

### 🥇 Phase Gold (Analytics Ready)
*   **Enrichissement :** Calcul du sentiment (via modèle NLP local ou API).
*   **Chargement :** Upsert (Update or Insert) dans Postgres pour éviter les doublons même en cas de re-run du pipeline.

---

## 📨 4. Configuration Kafka

Le cluster Kafka gère le flux de données entre l'ingestion et le stockage.

*   **Zookeeper :** Gère l'élection du leader et la metadata du cluster.
*   **Broker :** Un seul broker configuré (extensible).
*   **Topic `news-topic` :** 
    *   Replication Factor : 1
    *   Partitions : 3 (pour permettre le parallélisme des consommateurs).

---

## 🛠️ 5. Guide d'Extension : Ajouter une Source

Pour ajouter un nouveau journal (ex: *Le360*) :
1.  **Scraper :** Ajouter une méthode dans `ingestion/scraper/scraper.py` pour parser le HTML spécifique au site.
2.  **Mapping :** Mettre à jour la liste des sources dans le fichier de configuration.
3.  **Airflow :** Le DAG détectera automatiquement les nouvelles entrées si elles respectent l'interface de la classe `NewsScraper`.

---

## 🔧 6. Troubleshooting Avancé

### Problèmes fréquents :
*   **Kafka 'Connection Refused' :** Souvent dû à un manque de RAM sur l'hôte. Kafka nécessite au moins 2Go dédiés.
*   **Airflow 'Dag not found' :** Vérifiez que le volume `./airflow/dags` est correctement monté et que les permissions de lecture sont accordées.
*   **MinIO 'Bucket already exists' :** Erreur ignorée par le code, mais vérifiez les politiques d'accès (IAM) si vous changez les identifiants.

---

## 📁 7. Structure des Répertoires

```text
moroccan_news_analytics/
├── airflow/
│   ├── dags/            # Logique d'orchestration Python
│   └── Dockerfile       # Image personnalisée avec dépendances NLP
├── app_streamlit/
│   └── app.py           # Dashboard (Plotly + Streamlit)
├── ingestion/
│   ├── kafka/           # Producer Kafka
│   └── scraper/         # Logique de scraping Web
├── transformation/
│   └── processing_engine.py # Moteur de nettoyage et NLP
└── docker-compose.yml   # Orchestration globale
```


