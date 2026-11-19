import sqlite3
import os

DB_PATH = "../storage/document.db"

print("DB 경로:", os.path.abspath(DB_PATH))
print("파일 존재:", os.path.exists(DB_PATH))

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
               SELECT name, sql
               FROM sqlite_master
               WHERE type='table'
               """)

print("=== TABLES ===")
for row in cursor.fetchall():
    print(row)

cursor.execute("""
               SELECT name
               FROM sqlite_master
               WHERE type='table'
               """)

tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    print(f"\n=== {table} ===")
    try:
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        print("COUNT:", cursor.fetchone()[0])
    except sqlite3.Error as e:
        print("ERROR:", e)

conn.close()