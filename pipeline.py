import subprocess
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import os

# Make sure charts folder exists
os.makedirs("charts", exist_ok=True)

# Database connection
engine = create_engine("postgresql+psycopg2://retail_user:retail_pass@localhost:5432/retail_db")

# 1. Load raw CSVs into Postgres
print("📥 Step 1: Loading data...")
subprocess.run(["python", "src/load_data.py"], check=True)

# 2. Run analytics SQL
print("📊 Step 2: Running SQL transformations...")
queries = {
    "customer_sales": """
        DROP TABLE IF EXISTS customer_sales CASCADE;
        CREATE TABLE customer_sales AS
        SELECT c.customer_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               SUM(t.total_amount) AS total_spent,
               COUNT(t.transaction_id) AS num_transactions
        FROM customers c
        JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name;
    """,
    "top_products": """
        DROP TABLE IF EXISTS top_products CASCADE;
        CREATE TABLE top_products AS
        SELECT p.product_id,
               p.product_name,
               SUM(t.total_amount) AS total_revenue,
               COUNT(t.transaction_id) AS num_transactions
        FROM products p
        JOIN transactions t ON p.product_id = t.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_revenue DESC;
    """,
    "monthly_sales": """
        DROP TABLE IF EXISTS monthly_sales CASCADE;
        CREATE TABLE monthly_sales AS
        SELECT DATE_TRUNC('month', t.transaction_date::date) AS month,
               SUM(t.total_amount) AS total_sales
        FROM transactions t
        GROUP BY month
        ORDER BY month;
    """,
    "top_customers": """
        DROP TABLE IF EXISTS top_customers CASCADE;
        CREATE TABLE top_customers AS
        SELECT c.customer_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               SUM(t.total_amount) AS total_spent
        FROM customers c
        JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        ORDER BY total_spent DESC
        LIMIT 5;
    """,
    "category_sales": """
        DROP TABLE IF EXISTS category_sales CASCADE;
        CREATE TABLE category_sales AS
        SELECT p.category,
               SUM(t.total_amount) AS total_sales
        FROM products p
        JOIN transactions t ON p.product_id = t.product_id
        GROUP BY p.category
        ORDER BY total_sales DESC;
    """
}

with engine.begin() as conn:
    for name, sql in queries.items():
        print(f"   ▶ Creating table {name}...")
        conn.execute(text(sql))

# 3. Generate charts
print("📈 Step 3: Generating charts...")

# Top products chart
df = pd.read_sql("SELECT * FROM top_products ORDER BY total_revenue DESC;", engine)
plt.figure(figsize=(8,5))
plt.bar(df["product_name"], df["total_revenue"], color="skyblue")
plt.title("Top Products by Revenue")
plt.xlabel("Product")
plt.ylabel("Total Revenue")
plt.tight_layout()
plt.savefig("charts/top_products.png")
print("✅ Saved charts/top_products.png")

# Top Customers chart
df_customers = pd.read_sql("SELECT * FROM top_customers;", engine)
plt.figure(figsize=(8,5))
plt.bar(df_customers["customer_name"], df_customers["total_spent"], color="orange")
plt.title("Top Customers by Spending")
plt.xlabel("Customer")
plt.ylabel("Total Spent")
plt.tight_layout()
plt.savefig("charts/top_customers.png")
print("✅ Saved charts/top_customers.png")

# Category Sales chart
df_category = pd.read_sql("SELECT * FROM category_sales;", engine)
plt.figure(figsize=(8,5))
plt.pie(df_category["total_sales"], labels=df_category["category"], autopct="%1.1f%%")
plt.title("Sales by Product Category")
plt.savefig("charts/category_sales.png")
print("✅ Saved charts/category_sales.png")

print("🎉 Pipeline completed successfully!")
