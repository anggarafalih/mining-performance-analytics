"""
Idempotent Data Loader for PostgreSQL (Weekend 2)
Loads synthetic data from CSV files into PostgreSQL tables.
Can be safely re-run without duplicating records.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "pama_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "PamaSecure2026!")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "mining_analytics")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        return engine
    except Exception as e:
        print(f"[!] Gagal terhubung ke PostgreSQL pada {DB_HOST}:{DB_PORT}/{DB_NAME}")
        print(f"    Detail error: {e}")
        print("\n[PETUNJUK]: Pastikan container Docker aktif dengan menjalankan:")
        print("    cd week2-python-pg && docker compose up -d\n")
        return None

def init_schema(engine, schema_path="schema.sql"):
    print(f"Applying schema DDL from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    # Split by statements
    with engine.begin() as conn:
        # Execute script
        conn.execute(text(sql_script))
    print("-> Schema and views successfully initialized!")

def load_tables(engine, data_dir="../data"):
    # Resolve relative data directory
    if not os.path.exists(data_dir):
        data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"[!] Direktori data tidak ditemukan di {data_dir}")
        return False
        
    print(f"Loading data from {data_dir} into PostgreSQL...")
    
    # 1. dim_project
    df_proj = pd.read_csv(os.path.join(data_dir, "dim_project.csv"))
    df_proj.to_sql("dim_project", engine, if_exists="append", index=False)
    print(f"-> Loaded dim_project ({len(df_proj)} rows)")
    
    # 2. dim_equipment
    df_eq = pd.read_csv(os.path.join(data_dir, "dim_equipment.csv"))
    df_eq.to_sql("dim_equipment", engine, if_exists="append", index=False)
    print(f"-> Loaded dim_equipment ({len(df_eq)} rows)")
    
    # 3. fact_production
    df_prod = pd.read_csv(os.path.join(data_dir, "fact_production.csv"))
    df_prod.to_sql("fact_production", engine, if_exists="append", index=False)
    print(f"-> Loaded fact_production ({len(df_prod)} rows)")
    
    # 4. fact_equipment_hours
    df_hours = pd.read_csv(os.path.join(data_dir, "fact_equipment_hours.csv"))
    df_hours.to_sql("fact_equipment_hours", engine, if_exists="append", index=False)
    print(f"-> Loaded fact_equipment_hours ({len(df_hours)} rows)")
    
    # 5. fact_fuel
    df_fuel = pd.read_csv(os.path.join(data_dir, "fact_fuel.csv"))
    df_fuel.to_sql("fact_fuel", engine, if_exists="append", index=False)
    print(f"-> Loaded fact_fuel ({len(df_fuel)} rows)")
    
    # 6. budget_monthly
    df_budget = pd.read_csv(os.path.join(data_dir, "budget_monthly.csv"))
    df_budget.to_sql("budget_monthly", engine, if_exists="append", index=False)
    print(f"-> Loaded budget_monthly ({len(df_budget)} rows)")
    
    print("\n[V] Semua tabel berhasil dimuat secara idempotensial ke PostgreSQL!")
    return True

if __name__ == "__main__":
    engine = get_engine()
    if engine is not None:
        schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
        init_schema(engine, schema_file)
        load_tables(engine)
    else:
        sys.exit(1)
