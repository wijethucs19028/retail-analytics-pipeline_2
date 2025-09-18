import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Connect to Postgres
engine = create_engine("postgresql+psycopg2://retail_user:retail_pass@localhost:5432/retail_db")

# Load customer sales table into pandas
df = pd.read_sql("SELECT * FROM customer_sales ORDER BY total_spent DESC;", engine)

# Plot bar chart
plt.figure(figsize=(8, 5))
plt.bar(df["customer_name"], df["total_spent"], color="orange")
plt.title("Customer Sales (Total Spent)")
plt.xlabel("Customer")
plt.ylabel("Total Spent")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

# Save as image
plt.savefig("customer_sales.png")
print("✅ Chart saved as customer_sales.png")
