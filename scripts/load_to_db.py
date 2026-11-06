import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Подключение к PostgreSQL
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Пути к данным
DATA_DIR = Path(__file__).resolve().parent.parent / 'data' / 'processed'
TABLES = {
    'transactions': DATA_DIR / 'transactions_clean.csv',
    'rfm_segments': DATA_DIR / 'rfm_segments.csv',
    'clusters': DATA_DIR / 'clusters.csv',
}

# Загрузка таблиц
for table_name, csv_path in TABLES.items():
    print(f"Загрузка {table_name}...")
    df = pd.read_csv(csv_path)
    # chunksize и method='multi' сильно ускоряют загрузку
    df.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=5000, method='multi')
    print(f"Таблица '{table_name}' загружена: {len(df):,} строк")

# Создание индексов
print("Создание индексов...")
with engine.connect() as conn:
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_transactions_party ON transactions(party_rk);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_dttm);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_rfm_party ON rfm_segments(party_rk);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_rfm_segment ON rfm_segments(segment);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_clusters_party ON clusters(party_rk);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_clusters_cluster ON clusters(cluster);'))
    conn.commit()

print("Готово!")