import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib

server = 'LAPTOP-8K810F6U\\SQLEXPRESS'
database = 'olist'
driver = 'ODBC Driver 17 for SQL Server'
params = urllib.parse.quote_plus(
    f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

def score_customers():
    print("Extracting Features and Timestamps from SQL Server...")
    query = """
    WITH CustomerLifespan AS (
        SELECT
            c.customer_unique_id,
            MIN(o.order_purchase_timestamp) AS First_order,
            MAX(o.order_purchase_timestamp) AS Last_order
        FROM customers AS c
        INNER JOIN clean_orders AS o ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
    )
    SELECT
        f.*,
        l.First_order,
        l.Last_order
    FROM customer_features AS f
    INNER JOIN CustomerLifespan AS l ON f.customer_unique_id = l.customer_unique_id;
    """
    df = pd.read_sql(query, engine)
    print(f"Extraction Successful! Total Rows: {len(df)}")

    print("Calculating Historical CLV Metrics...")
    df['R_Score'] = pd.to_numeric(df['R_Score'], errors='coerce')
    df['F_Score'] = pd.to_numeric(df['F_Score'], errors='coerce')
    df['M_Score'] = pd.to_numeric(df['M_Score'], errors='coerce')
    df['Churn_flag'] = pd.to_numeric(df['Churn_flag'], errors='coerce')

    df['AOV'] = df['Monetary_value'] / df['Frequency']
    df['First_order'] = pd.to_datetime(df['First_order'])
    df['Last_order'] = pd.to_datetime(df['Last_order'])
    df['Lifespan_Days'] = (df['Last_order'] - df['First_order']).dt.days
    df['Lifespan_Years'] = df['Lifespan_Days'] / 365.0
    df['Lifespan_Years'] = np.where(df['Lifespan_Years'] == 0, 0.083, df['Lifespan_Years'])
    df['CLV'] = df['AOV'] * df['Frequency'] * df['Lifespan_Years']

    print("Assigning Business Segments...")
    conditions = [
        (df['Churn_flag'] == 1) & (df['M_Score'] >= 4),
        (df['Churn_flag'] == 1),
        (df['R_Score'] >= 4) & (df['F_Score'] >= 3) & (df['M_Score'] >= 4),
        (df['R_Score'] >= 3) & (df['F_Score'] >= 3),
        (df['R_Score'] >= 4) & (df['Frequency'] == 1),
        (df['R_Score'] <= 2) & (df['F_Score'] >= 3)
    ]
    choices = ['Lost Champion', 'Lost', 'Champions', 'Loyal', 'New', 'At-Risk']
    df['Segment'] = np.select(conditions, choices, default='Standard')

    df['CLV'] = df['CLV'].round(2)
    print("\nScoring Complete! Top 5 Customers by CLV:")
    print(df[['customer_unique_id', 'CLV', 'Segment']].sort_values(by='CLV', ascending=False).head())

    print("\nWriting customer_scores table to SQL Server...")
    df.to_sql('customer_scores', engine, if_exists='replace', index=False)
    print("Phase 4 Complete!")

    # Return row count for main.py pipeline summary
    return len(df)

def main():
    return score_customers()

if __name__ == "__main__":
    main()