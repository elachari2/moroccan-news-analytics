# 🇲🇦 Moroccan News Analytics Platform

Une plateforme Big Data moderne pour la collecte, le traitement et la visualisation en temps réel de l'actualité marocaine (Hespress, Akhbarona).



##  Architecture du Système (Médaillon)

Le projet implémente une architecture de type Data Lakehouse organisée en trois couches (Médaillon) pour garantir la qualité et la traçabilité des données :

*    Couche Bronze (Raw) : Ingestion des articles bruts via des scrapers Python. Les données sont envoyées dans un topic Kafka puis archivées au format JSON dans MinIO.
*    Couche Silver (Cleaned) : Processus de nettoyage des données (suppression du HTML, déduplication, validation de format) et conversion au format optimisé Parquet.
*    Couche Gold (Analytics) : Agrégations métier et enrichissement des données (catégorisation, sentiments) stockées dans PostgreSQL pour une consommation rapide par le dashboard.

---

##  Stack Technologique

| Composant       | Technologie      |                         Rôle                              |
|                 |                  |                                                           |
| Orchestration   | Apache Airflow   | Gestion des pipelines ETL et planification des tâches.    |
| Streaming       | Apache Kafka     | Ingestion temps réel et découplage des services.          |
| Stockage S3     | MinIO            | Data Lake pour le stockage des fichiers Bronze et Silver. |
| Base de Données | PostgreSQL       | Data Warehouse pour les données structurées Gold.         |
| Visualisation   | Streamlit        | Dashboard interactif pour l'analyse des tendances.        |
| Conteneurisation| Docker & Compose | Isolation et déploiement simplifié de l'infrastructure.   |


##  Installation et Lancement

### 1. Prérequis
   Docker & Docker Compose installés.
   Minimum 8 Go de RAM alloués à Docker.

### 2. Démarrage
Clonez le dépôt et lancez l'infrastructure complète avec une seule commande :
```bash
docker-compose up --build -d
```

### 3. Accès aux Services
Une fois les services démarrés, accédez aux outils suivants :
    Airflow : [http://localhost:8080](http://localhost:8080) (admin / admin)
    Dashboard Streamlit : [http://localhost:8501](http://localhost:8501)
    MinIO (S3 Console) : [http://localhost:9001](http://localhost:9001) (minioadmin / minioadmin)
    PostgreSQL : `localhost:5432` (admin / adminpassword)

---

##  Flux de Travail (Workflow)

1.  Déclenchement : Le pipeline est piloté par Airflow (`news_pipeline_dag`).
2.  Ingestion : Les scrapers récupèrent les derniers articles et les poussent dans Kafka.
3.  Traitement : Le `ProcessingEngine` récupère les données de MinIO Bronze, les nettoie, et les dépose dans Silver.
4.  Chargement : Les données Silver sont agrégées et chargées dans Postgres (Gold).
5.  Analyse : Le Dashboard Streamlit se connecte à Postgres pour afficher les indicateurs clés.

---

##  Qualité des Données (DQ)

Le système intègre des contrôles automatiques pour garantir l'intégrité des analyses :
   Validation de la présence obligatoire du titre et de l'URL.
   Nettoyage automatique des balises HTML et des espaces superflus.
   Filtrage des articles dont le contenu est trop court (< 20 caractères).
   Détection et suppression des doublons basés sur l'URL de l'article.

---

##  Structure du Projet

```text
moroccan_news_analytics/
├── airflow/             # DAGs et configuration Airflow
├── app_streamlit/       # Interface de visualisation (Dashboard)
├── ingestion/           # Scrapers et Producers Kafka
├── transformation/      # Moteur de traitement (Bronze -> Silver -> Gold)
├── postgres/            # Scripts d'initialisation de la base de données
└── docker-compose.yml   # Définition de l'infrastructure multi-container
```
