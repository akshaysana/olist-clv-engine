import pandas as pd
from sqlalchemy import create_engine

# Step 1: Configuration
SERVER = 'LAPTOP-8K810F6U\\SQLEXPRESS'
DATABASE = 'olist'
CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

def clean_orders():
    print("Starting Data Quality Audit for Orders...")
    engine = create_engine(CONNECTION_STRING)
    
    # Step 2: Extract from Raw Database
    # We pull the data directly from the SQL table we built in Phase 1
    query = "SELECT * FROM orders;"
    df = pd.read_sql(query, engine)
    
    initial_count = len(df)
    print(f"Initial row count: {initial_count}")

    
    
    # ---------------------------------------------------------
    # Step 3: THE SURGICAL DROP (YOUR TURN)
    # HINT: You want to KEEP rows where the status is NOT 'delivered' 
    # OR where the 'order_delivered_customer_date' is NOT null.
    # Write the Pandas filter to drop the 8 ghost orders.
    # ---------------------------------------------------------
    
    df_clean = df[(df['order_status'] != 'delivered') | (df['order_delivered_customer_date'].notna())]
    
    # ---------------------------------------------------------
    
    final_count = len(df_clean)
    dropped_count = initial_count - final_count
    
    print(f"Dropped {dropped_count} corrupted rows.")
    print(f"Final clean row count: {final_count}")
    
    # Step 4: Load to Clean Schema
    # We write this back to SQL Server as a brand new table
    print("Pushing clean data to database...")
    df_clean.to_sql(name='clean_orders', con=engine, if_exists='replace', index=False)
    print("orders table cleaned and saved as 'clean_orders'!")

if __name__ == "__main__":
    clean_orders()