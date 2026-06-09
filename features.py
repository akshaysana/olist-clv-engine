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

def engineer_features():
    print("Extracting Base RFM Metrics from SQL Server...")
    query = """
    SELECT
        c.customer_unique_id,
        DATEDIFF(day, MAX(o.order_purchase_timestamp), '2018-10-17 17:30:18.000') AS Recency,
        COUNT(DISTINCT o.order_id) AS Frequency,
        SUM(oi.price + oi.freight_value) AS Monetary_value,
        AVG(DATEDIFF(day, order_estimated_delivery_date, order_delivered_customer_date)) AS Delivery_delta,
        AVG(r.review_score * 1.0) AS Avg_review_score,
        CASE
            WHEN DATEDIFF(day, MAX(order_purchase_timestamp), '2018-10-17 17:30:18.000') > 180 THEN 1
            ELSE 0
        END AS Churn_flag
    FROM customers AS c
    INNER JOIN orders AS o ON c.customer_id = o.customer_id
    INNER JOIN order_items AS oi ON o.order_id = oi.order_id
    LEFT JOIN order_reviews_clean AS r ON o.order_id = r.order_id
    GROUP BY c.customer_unique_id
    ORDER BY Monetary_value DESC;
    """
    df = pd.read_sql(query, engine)
    print(f"Extraction Successful! Total Rows: {len(df)}")

    global_avg_review = df['Avg_review_score'].mean()
    df['Avg_review_score'] = df['Avg_review_score'].fillna(global_avg_review)
    df['Delivery_delta'] = df['Delivery_delta'].fillna(0)

    print("Calculating RFM Quintile Bins...")
    df['M_Score'] = pd.qcut(df['Monetary_value'], q=5, labels=[1,2,3,4,5], duplicates='drop')
    df['R_Score'] = pd.qcut(df['Recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
    df['F_Score'] = np.where(df['Frequency'] == 1, 1,
                    np.where(df['Frequency'] == 2, 3, 5))

    print("Normalizing Metrics to 0-1 scale...")
    min_m, max_m = df['Monetary_value'].min(), df['Monetary_value'].max()
    df['Monetary_Normalized'] = (df['Monetary_value'] - min_m) / (max_m - min_m)
    min_r, max_r = df['Recency'].min(), df['Recency'].max()
    df['Recency_Normalized'] = 1 - ((df['Recency'] - min_r) / (max_r - min_r))

    print("\nWriting customer_features table to SQL Server...")
    df.to_sql('customer_features', engine, if_exists='replace', index=False)
    print("Write complete! Phase 3 finished.")

def main():
    engineer_features()

if __name__ == "__main__":
    main()