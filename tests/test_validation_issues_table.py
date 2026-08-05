import sqlite3

from src.database import DATABASE_PATH, create_tables

create_tables()

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name = 'validation_issues'
""")

table = cursor.fetchone()

assert table is not None
assert table[0] == "validation_issues"

connection.close()

print("Validation issues table test passed.")