import os
import pandas as pd
from sqlalchemy import create_engine

# Step 1: Configure your SQL Server connection string
SERVER = 'LAPTOP-8K810F6U\\SQLEXPRESS' # e.g., 'localhost' or 'DESKTOP-XXXX'
DATABASE = 'olist' # e.g., 'olist_db'

# Standard SQLAlchemy connection string for Windows Authentication
CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

def ingest_table(csv_path, table_name):
    print(f"Starting ingestion for {table_name}...")
    
    # Step 2: Create the database engine
    engine = create_engine(CONNECTION_STRING)
    
    # Step 3: Read the CSV using Pandas
    # HINT: How do you force Pandas to read 'customer_zip_code_prefix' as a string so we don't lose the leading zeros?
    df = pd.read_csv(csv_path, dtype={'customer_zip_code_prefix': str, 'seller_zip_code_prefix': str, 'geolocation_zip_code_prefix': str})
    
    print(df.shape)
    print(df.head())

    # Step 4: Push the dataframe to SQL Server
    # HINT: We want to insert into the existing table you built in SSMS. 
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    
    print(f"Successfully ingested {len(df)} rows into {table_name}!")

if __name__ == "__main__":
    # Define the absolute path to the directory containing ingest.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # The ordered hierarchy of ingestion with dynamic pathing
    TABLE_MAPPING = {
        # 1. Parents
        os.path.join(BASE_DIR, 'data', 'olist_customers_dataset.csv'): 'customers',
        os.path.join(BASE_DIR, 'data', 'olist_sellers_dataset.csv'): 'sellers',
        os.path.join(BASE_DIR, 'data', 'olist_products_dataset.csv'): 'products',
        os.path.join(BASE_DIR, 'data', 'product_category_name_translation.csv'): 'product_category_translation',
        
        # 2. Hub
        os.path.join(BASE_DIR, 'data', 'olist_orders_dataset.csv'): 'orders',
        
        # 3. Bridge
        os.path.join(BASE_DIR, 'data', 'olist_order_items_dataset.csv'): 'order_items',
        os.path.join(BASE_DIR, 'data', 'olist_order_reviews_clean_dataset.csv'): 'order_reviews_clean',
        os.path.join(BASE_DIR, 'data', 'olist_order_reviews_dataset.csv'): 'reviews',
        os.path.join(BASE_DIR, 'data', 'olist_geolocation_dataset.csv'): 'geolocation',
        os.path.join(BASE_DIR, 'data', 'olist_order_payments_dataset.csv'): 'order_payments'
    }   
    
    for csv, table in TABLE_MAPPING.items():
        ingest_table(csv, table)