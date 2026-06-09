# Olist Customer Lifetime Value(CLV) Engine

## The Problem
Olist knows how much revenue they make.
They don't know which customers are worth fighting to keep
— and which ones they've already lost forever.

This project answers that question.

## What I Built
A production-style Python/SQL pipeline that processes 
100,000+ real Brazilian e-commerce orders from scratch 
— no drag and drop, no pre-built templates.

It ingests raw messy data, cleans it, engineers customer 
behavior features, scores every single customer on 
Customer Lifetime Value, and segments them into tiers 
a CEO can actually act on.

The output isn't a one-time analysis.
It's a system. Run it on new data and it produces 
new scores automatically.

## What the Data Actually Revealed
- 70.9% of Olist's customer base has churned
- 27,000 Lost Champions — high-value customers who 
  went silent — represent $748K in recoverable revenue
- São Paulo, Rio, and Minas Gerais alone generate 
  62% of total lifetime value
- Champions are worth 25x more on average than 
  Lost customers
- Olist has a powerful acquisition engine 
  and a broken retention engine

## System Architecture
main.py
├── ingest.py      → Raw CSVs to SQL Server
├── cleaner.py     → Data quality audit and cleaning
├── features.py    → RFM feature engineering
├── scorer.py      → CLV scoring and segmentation
└── olist_clv.pbix → Power BI dashboard

## Tech Stack
Python, Pandas, NumPy, SQL Server, SSMS, 
Power BI, SQLAlchemy, DAX

## How to Run
1. Clone the repo
2. Add Olist CSVs to /data folder
3. Set your SQL Server connection in config
4. Run main.py
5. Open olist_clv.pbix in Power BI Desktop

## Dataset
Olist Brazilian E-Commerce — Kaggle
9 relational tables, 100,000+ orders, 2016–2018
Real data. Real mess. Real insights.
Dataset Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Note: olist_order_reviews_clean_dataset.csv is a cleaned version 
of the original reviews file with 814 duplicate review_ids removed. 
Run cleaner.py before features.py to generate this file.
