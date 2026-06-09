import pandas as pd
from sqlalchemy import create_engine

SERVER = 'LAPTOP-8K810F6U\\SQLEXPRESS'
DATABASE = 'olist'
CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

def clean_orders():
    print("Starting Data Quality Audit for Orders...")
    engine = create_engine(CONNECTION_STRING)
    df = pd.read_sql("SELECT * FROM orders;", engine)
    initial_count = len(df)
    print(f"Initial row count: {initial_count}")
    df_clean = df[
        (df['order_status'] != 'delivered') |
        (df['order_delivered_customer_date'].notna())
    ]
    final_count = len(df_clean)
    print(f"Dropped {initial_count - final_count} corrupted rows.")
    print(f"Final clean row count: {final_count}")
    df_clean.to_sql(name='clean_orders', con=engine, if_exists='replace', index=False)
    print("Orders cleaned and saved as 'clean_orders'!")

def main():
    clean_orders()

if __name__ == "__main__":
    main()