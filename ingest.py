import os
import pandas as pd
from sqlalchemy import create_engine

SERVER = 'LAPTOP-8K810F6U\\SQLEXPRESS'
DATABASE = 'olist'
CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

def ingest_table(csv_path, table_name):
    print(f"Starting ingestion for {table_name}...")
    engine = create_engine(CONNECTION_STRING)
    df = pd.read_csv(csv_path, dtype={
        'customer_zip_code_prefix': str,
        'seller_zip_code_prefix': str,
        'geolocation_zip_code_prefix': str
    })
    print(df.shape)
    print(df.head())
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    print(f"Successfully ingested {len(df)} rows into {table_name}!")

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TABLE_MAPPING = {
        os.path.join(BASE_DIR, 'data', 'olist_customers_dataset.csv'): 'customers',
        os.path.join(BASE_DIR, 'data', 'olist_sellers_dataset.csv'): 'sellers',
        os.path.join(BASE_DIR, 'data', 'olist_products_dataset.csv'): 'products',
        os.path.join(BASE_DIR, 'data', 'product_category_name_translation.csv'): 'product_category_translation',
        os.path.join(BASE_DIR, 'data', 'olist_orders_dataset.csv'): 'orders',
        os.path.join(BASE_DIR, 'data', 'olist_order_items_dataset.csv'): 'order_items',
        os.path.join(BASE_DIR, 'data', 'olist_order_reviews_clean_dataset.csv'): 'order_reviews_clean',
        os.path.join(BASE_DIR, 'data', 'olist_geolocation_dataset.csv'): 'geolocation',
        os.path.join(BASE_DIR, 'data', 'olist_order_payments_dataset.csv'): 'order_payments'
    }
    for csv, table in TABLE_MAPPING.items():
        ingest_table(csv, table)

if __name__ == "__main__":
    main()