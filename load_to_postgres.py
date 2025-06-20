import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# load connection details 
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL.")
except Exception as e:
    print("❌ Connection failed:", e)
    exit(1)

# Create Tables
def create_tables():
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id INT PRIMARY KEY,
            client_name TEXT,
            lawyer TEXT,
            practice_area TEXT,
            status TEXT,
            start_date DATE,
            due_date DATE,
            end_date DATE
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS billable_hours (
            entry_id INT PRIMARY KEY,
            lawyer TEXT,
            case_id INT,
            date DATE,
            hours_logged FLOAT,
            billed TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INT PRIMARY KEY,
            case_id INT,
            task_description TEXT,
            assigned_to TEXT,
            due_date DATE,
            completed TEXT
        );
        """)
        
        conn.commit()
        print("✅ Tables created successfully.")
    except Exception as e:
        print("❌ Error creating tables:", e)

# Load data
def load_csv_to_db(file_path, table_name):
    try:
        df = pd.read_csv(file_path)
        print(f"\n📄 Loading '{file_path}' into '{table_name}'... ({len(df)} rows found)")

        if df.empty:
            print(f"⚠️ File '{file_path}' is empty. Skipping.")
            return

        
        df = df.where(pd.notnull(df), None)

        for index, row in df.iterrows():
            cols = ','.join(row.index)
            vals = ','.join(['%s'] * len(row))
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({vals}) ON CONFLICT DO NOTHING;"
            try:
                cursor.execute(sql, tuple(row))
            except Exception as row_error:
                print(f"❌ Row {index + 1} insert failed in '{table_name}':", row_error)

        conn.commit()
        print(f"✅ Finished loading '{table_name}' with {len(df)} rows.")
    except Exception as e:
        print(f"❌ Failed to load data into {table_name}:", e)


create_tables()

load_csv_to_db("C:/Users/Administrator/law_firm/cases.csv", "cases")
load_csv_to_db("C:/Users/Administrator/law_firm/billable_hours.csv", "billable_hours")
load_csv_to_db("C:/Users/Administrator/law_firm/tasks.csv", "tasks")


cursor.close()
conn.close()
print("\n🎉 All done!")
