import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Connect to Postgres
engine = create_engine("postgresql+psycopg2://retail_user:retail_pass@localhost:5432/retail_db")

# -----------------------------
# 1. Top Products by Revenue
# -----------------------------
df_products = pd.read_sql("SELECT * FROM top_products ORDER BY total_revenue DESC;", engine)

plt.figure(figsize=(8, 5))
plt.bar(df_products["product_name"], df_products["total_revenue"], color="skyblue")
plt.title("Top Products by Revenue")
plt.xlabel("Product")
plt.ylabel("Total Revenue")
plt.tight_layout()
plt.savefig("top_products.png")
plt.close()
print("✅ Chart saved as top_products.png")

# -----------------------------
# 2. Monthly Sales Trend
# -----------------------------
df_monthly = pd.read_sql("""
    SELECT DATE_TRUNC('month', t.transaction_date::date) AS month,
           SUM(t.total_amount) AS total_sales
    FROM transactions t
    GROUP BY month
    ORDER BY month;
""", engine)

plt.figure(figsize=(8, 5))
plt.plot(df_monthly["month"], df_monthly["total_sales"], marker="o", color="green")
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("monthly_sales.png")
plt.close()
print("✅ Chart saved as monthly_sales.png")

# -----------------------------
# 3. Revenue by Category per Month
# -----------------------------
df_category = pd.read_sql("""
    SELECT DATE_TRUNC('month', t.transaction_date::date) AS month,
           p.category,
           SUM(t.total_amount) AS total_sales
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY month, p.category
    ORDER BY month, total_sales DESC;
""", engine)

pivot = df_category.pivot(index="month", columns="category", values="total_sales")
pivot.plot(kind="bar", stacked=True, figsize=(8, 5))
plt.title("Revenue by Category per Month")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("revenue_by_category.png")
plt.close()
print("✅ Chart saved as revenue_by_category.png")

# -----------------------------
# 4. Top 5 Customers by Spending
# -----------------------------
df_customers = pd.read_sql("""
    SELECT c.first_name || ' ' || c.last_name AS customer_name,
           SUM(t.total_amount) AS total_spent
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    GROUP BY customer_name
    ORDER BY total_spent DESC
    LIMIT 5;
""", engine)

plt.figure(figsize=(8, 5))
plt.bar(df_customers["customer_name"], df_customers["total_spent"], color="orange")
plt.title("Top 5 Customers by Spending")
plt.xlabel("Customer")
plt.ylabel("Total Spent")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("top_customers.png")
plt.close()
print("✅ Chart saved as top_customers.png")
