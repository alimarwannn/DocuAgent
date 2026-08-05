from src.database import DATABASE_PATH, get_database_connection

connection = get_database_connection()

assert connection is not None
assert DATABASE_PATH.exists()

connection.close()

print("Database connection test passed.")
print(f"Database path: {DATABASE_PATH}")