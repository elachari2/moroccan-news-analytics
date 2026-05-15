-- Schéma du Data Warehouse pour les données Gold
CREATE TABLE IF NOT EXISTS gold_news_analytics (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50),
    title TEXT,
    content TEXT,
    category VARCHAR(50),
    published_date TIMESTAMP,
    cleaned_text TEXT,
    word_count INT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_stats (
    stat_date DATE PRIMARY KEY,
    article_count INT,
    top_source VARCHAR(50),
    most_common_category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS quality_logs (
    id SERIAL PRIMARY KEY,
    check_name VARCHAR(100),
    status VARCHAR(20),
    error_count INT,
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
