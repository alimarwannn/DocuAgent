import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/docuagent.db")


def get_database_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection

def create_tables():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            document_type TEXT NOT NULL,
            scan_mode TEXT NOT NULL,
            raw_ocr_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_value TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            issue_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)

    connection.commit()
    connection.close()

def save_document(filename, document_type, scan_mode, raw_ocr_text):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            filename,
            document_type,
            scan_mode,
            raw_ocr_text
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            filename,
            document_type,
            scan_mode,
            raw_ocr_text,
        ),
    )

    document_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return document_id

def save_extracted_fields(document_id, fields):
    connection = get_database_connection()
    cursor = connection.cursor()

    for field_name, field_value in fields.items():
        cursor.execute(
            """
            INSERT INTO extracted_fields (
                document_id,
                field_name,
                field_value
            )
            VALUES (?, ?, ?)
            """,
            (
                document_id,
                field_name,
                None if field_value is None else str(field_value),
            ),
        )

    connection.commit()
    connection.close()

def save_validation_issues(document_id, issues):
    connection = get_database_connection()
    cursor = connection.cursor()

    for issue in issues:
        cursor.execute(
            """
            INSERT INTO validation_issues (
                document_id,
                issue_type,
                message,
                severity
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                document_id,
                issue["issue_type"],
                issue["message"],
                issue["severity"],
            ),
        )

    connection.commit()
    connection.close()    