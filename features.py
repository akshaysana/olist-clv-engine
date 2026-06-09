import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib

# ---------------------------------------------------------
# Step 1: Database Connection
# ---------------------------------------------------------
server = 'LAPTOP-8K810F6U\\SQLEXPRESS' 
database = 'olist'
driver = 'ODBC Driver 17 for SQL Server'
# We use urllib to safely encode the connection string for SQLAlchemy
params = urllib.parse.quote_plus(f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

def engineer_features():
    print("Extracting Base RFM Metrics from SQL Server...")
    
    # ---------------------------------------------------------
    # YOUR TASK: Paste your final Mega-Join query inside the triple quotes
    # ---------------------------------------------------------
    query = """ 

    SELECT
    c.customer_unique_id,
    DATEDIFF(day, MAX(o.order_purchase_timestamp), '2018-10-17 17:30:18.000') AS Recency,
    COUNT (DISTINCT o.order_id) AS Frequency,
    SUM(oi.price + oi.freight_value) AS Monetary_value,
    AVG(DATEDIFF(day, order_estimated_delivery_date, order_delivered_customer_date)) AS Delivery_delta,
    AVG(r.review_score * 1.0) AS Avg_review_score,
    CASE
        WHEN DATEDIFF(day, MAX(order_purchase_timestamp), '2018-10-17 17:30:18.000') > 180 THEN 1
        ELSE 0
        END AS Churn_flag
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.customer_id = o.customer_id
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    LEFT JOIN order_reviews_clean AS r
        ON o.order_id = r.order_id
    GROUP BY c.customer_unique_id
    ORDER BY Monetary_value DESC;
    
    """
    
    df = pd.read_sql(query, engine)
    print(f"Extraction Successful! Total Rows: {len(df)}")
    
    # ---------------------------------------------------------
    # Step 2: Handle NULL values from the LEFT JOIN
    # ---------------------------------------------------------
    # If a customer didn't leave a review, we impute the global average to avoid breaking the math
    global_avg_review = df['Avg_review_score'].mean()
    df['Avg_review_score'] = df['Avg_review_score'].fillna(global_avg_review)
    
    # Same for delivery delta - if it's missing, we assume it arrived exactly on time (0 days late)
    df['Delivery_delta'] = df['Delivery_delta'].fillna(0)
    
    # ---------------------------------------------------------
    # Step 3: NumPy Percentile Bins (Quintiles 1-5)
    # ---------------------------------------------------------
    print("Calculating RFM Quintile Bins...")
    # Monetary (5 is best, highest spend)
    df['M_Score'] = pd.qcut(df['Monetary_value'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Recency (5 is best, lowest number of days)
    df['R_Score'] = pd.qcut(df['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    
    # Frequency (Most people only bought once, so qcut breaks. We use custom bins)
    # 1 purchase = Score 1. 2 purchases = Score 3. 3+ purchases = Score 5.
    df['F_Score'] = np.where(df['Frequency'] == 1, 1, 
                    np.where(df['Frequency'] == 2, 3, 5))
                    
    # ---------------------------------------------------------
    # Step 4: Normalization (0-to-1 Scale)
    # ---------------------------------------------------------
    print("Normalizing Metrics to 0-1 scale...")
    # Min-Max Normalization Formula: (x - min) / (max - min)
    
    # Normalize Monetary Value
    min_m = df['Monetary_value'].min()
    max_m = df['Monetary_value'].max()
    df['Monetary_Normalized'] = (df['Monetary_value'] - min_m) / (max_m - min_m)
    
    # Normalize Recency (Inverted, because lower days = higher score)
    min_r = df['Recency'].min()
    max_r = df['Recency'].max()
    df['Recency_Normalized'] = 1 - ((df['Recency'] - min_r) / (max_r - min_r))
    
    print("\nFeature Engineering Complete! Here is the final dataset preview:")
    print(df[['customer_unique_id', 'R_Score', 'F_Score', 'M_Score', 'Monetary_Normalized']].head())
    
    # ---------------------------------------------------------
    # Step 5: Write the final features back to SQL Server
    # ---------------------------------------------------------
    print("\nWriting customer_features table to SQL Server...")
    df.to_sql('customer_features', engine, if_exists='replace', index=False)
    print("Write complete! Phase 3 is finished.")

if __name__ == "__main__":
    engineer_features()