import sqlite3

from src.database import DATABASE_PATH, create_tables

create_tables()

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name = 'documents'
""")

table = cursor.fetchone()

assert table is not None
assert table[0] == "documents"

connection.close()

print("Documents table test passed.")