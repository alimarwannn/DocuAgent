import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/docuagent.db")


def get_database_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection