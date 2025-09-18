from sqlalchemy import create_engine
import pandas as pd

# ✅ Connect to local Postgres (change host to "postgres" if using Docker Compose)
engine = create_engine(
    "postgresql+psycopg2://retail_user:retail_pass@localhost:5432/retail_db"
)

def load_csv_to_db(table_name, file_path):
    print(f"📥 Loading {file_path} into {table_name}...")
    df = pd.read_csv(file_path)
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"✅ Loaded {len(df)} rows into {table_name}")

if __name__ == "__main__":
    tables = {
        "customers": "data/raw/customers.csv",
        "products": "data/raw/products.csv",
        "transactions": "data/raw/transactions.csv"
    }

    for table, path in tables.items():
        load_csv_to_db(table, path)
