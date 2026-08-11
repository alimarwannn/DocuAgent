import os
import sqlite3
import sys
from pathlib import Path


def _default_database_path():
    environment_path = os.getenv(
        "DOCUAGENT_DB_PATH"
    )

    if environment_path:
        return Path(
            environment_path
        )

    argv0 = Path(
        sys.argv[0] or ""
    )

    looks_like_test_run = (
        argv0.name.startswith(
            "test_"
        )
        or "pytest"
        in argv0.name.lower()
        or bool(
            os.getenv(
                "PYTEST_CURRENT_TEST"
            )
        )
    )

    if looks_like_test_run:
        stem = (
            argv0.stem
            or "test_session"
        )

        return (
            Path("data/test_dbs")
            / f"{stem}_{os.getpid()}.db"
        )

    return Path("data/docuagent.db")


DATABASE_PATH = _default_database_path()

REVIEW_STATUSES = {
    "approved",
    "pending_review",
    "rejected",
}


def get_database_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def _column_exists(
    cursor,
    table_name,
    column_name,
):
    rows = cursor.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        row["name"] == column_name
        for row in rows
    )


def create_tables():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            document_type TEXT NOT NULL,
            scan_mode TEXT NOT NULL,
            raw_ocr_text TEXT,
            review_status TEXT NOT NULL DEFAULT 'approved',
            review_note TEXT,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS extracted_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_value TEXT,
            FOREIGN KEY (document_id)
                REFERENCES documents(id)
                ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS validation_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            issue_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            FOREIGN KEY (document_id)
                REFERENCES documents(id)
                ON DELETE CASCADE
        )
        """
    )

    if not _column_exists(
        cursor,
        "documents",
        "review_status",
    ):
        cursor.execute(
            """
            ALTER TABLE documents
            ADD COLUMN review_status TEXT
            NOT NULL DEFAULT 'approved'
            """
        )

    if not _column_exists(
        cursor,
        "documents",
        "review_note",
    ):
        cursor.execute(
            """
            ALTER TABLE documents
            ADD COLUMN review_note TEXT
            """
        )

    if not _column_exists(
        cursor,
        "documents",
        "reviewed_at",
    ):
        cursor.execute(
            """
            ALTER TABLE documents
            ADD COLUMN reviewed_at TIMESTAMP
            """
        )

    connection.commit()
    connection.close()


def save_document(
    filename,
    document_type,
    scan_mode,
    raw_ocr_text,
    review_status="approved",
):
    if review_status not in REVIEW_STATUSES:
        raise ValueError(
            "Invalid review status."
        )

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            filename,
            document_type,
            scan_mode,
            raw_ocr_text,
            review_status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            filename,
            document_type,
            scan_mode,
            raw_ocr_text,
            review_status,
        ),
    )

    document_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return document_id


def save_extracted_fields(
    document_id,
    fields,
):
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
                (
                    None
                    if field_value is None
                    else str(field_value)
                ),
            ),
        )

    connection.commit()
    connection.close()


def replace_extracted_fields(
    document_id,
    fields,
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM extracted_fields
        WHERE document_id = ?
        """,
        (document_id,),
    )

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
                (
                    None
                    if field_value is None
                    else str(field_value)
                ),
            ),
        )

    connection.commit()
    connection.close()


def save_validation_issues(
    document_id,
    issues,
):
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


def replace_validation_issues(
    document_id,
    issues,
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM validation_issues
        WHERE document_id = ?
        """,
        (document_id,),
    )

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


def invoice_number_exists(
    invoice_number,
    exclude_document_id=None,
):
    if invoice_number in (None, ""):
        return False

    connection = get_database_connection()
    cursor = connection.cursor()

    if exclude_document_id is None:
        cursor.execute(
            """
            SELECT 1
            FROM extracted_fields
            WHERE field_name = 'invoice_number'
              AND field_value = ?
            LIMIT 1
            """,
            (str(invoice_number),),
        )

    else:
        cursor.execute(
            """
            SELECT 1
            FROM extracted_fields
            WHERE field_name = 'invoice_number'
              AND field_value = ?
              AND document_id != ?
            LIMIT 1
            """,
            (
                str(invoice_number),
                exclude_document_id,
            ),
        )

    exists = (
        cursor.fetchone()
        is not None
    )

    connection.close()

    return exists


def get_document(document_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE id = ?
        """,
        (document_id,),
    )

    document = cursor.fetchone()

    connection.close()

    if document is None:
        return None

    return dict(document)


def get_document_fields(document_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            field_name,
            field_value
        FROM extracted_fields
        WHERE document_id = ?
        """,
        (document_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    return {
        row["field_name"]:
        row["field_value"]
        for row in rows
    }


def get_document_issues(document_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            issue_type,
            message,
            severity
        FROM validation_issues
        WHERE document_id = ?
        """,
        (document_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "issue_type":
                row["issue_type"],
            "message":
                row["message"],
            "severity":
                row["severity"],
        }
        for row in rows
    ]


def list_documents():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        ORDER BY created_at DESC, id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def list_documents_by_review_status(
    review_status,
):
    if review_status not in REVIEW_STATUSES:
        return []

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE review_status = ?
        ORDER BY created_at DESC, id DESC
        """,
        (review_status,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def list_review_documents():
    return list_documents_by_review_status(
        "pending_review"
    )


def set_document_review_status(
    document_id,
    review_status,
    note=None,
):
    if review_status not in REVIEW_STATUSES:
        return False

    connection = get_database_connection()
    cursor = connection.cursor()

    if review_status == "pending_review":
        cursor.execute(
            """
            UPDATE documents
            SET
                review_status = ?,
                review_note = ?,
                reviewed_at = NULL
            WHERE id = ?
            """,
            (
                review_status,
                note,
                document_id,
            ),
        )

    else:
        cursor.execute(
            """
            UPDATE documents
            SET
                review_status = ?,
                review_note = ?,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                review_status,
                note,
                document_id,
            ),
        )

    updated = (
        cursor.rowcount > 0
    )

    connection.commit()
    connection.close()

    return updated


def filter_documents_by_type(
    document_type,
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE document_type = ?
        ORDER BY created_at DESC, id DESC
        """,
        (document_type,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def filter_documents_by_date(
    start_date,
    end_date,
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT d.*
        FROM documents d
        JOIN extracted_fields e
            ON d.id = e.document_id
        WHERE e.field_name = 'date'
          AND e.field_value BETWEEN ? AND ?
        ORDER BY d.created_at DESC, d.id DESC
        """,
        (
            start_date,
            end_date,
        ),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def filter_documents_by_party(name):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT d.*
        FROM documents d
        JOIN extracted_fields e
            ON d.id = e.document_id
        WHERE e.field_name IN (
            'supplier_name',
            'merchant_name'
        )
          AND LOWER(e.field_value)
              LIKE LOWER(?)
        ORDER BY d.created_at DESC, d.id DESC
        """,
        (f"%{name}%",),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def find_document_by_number(
    document_number,
):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT d.*
        FROM documents d
        JOIN extracted_fields e
            ON d.id = e.document_id
        WHERE e.field_name IN (
            'invoice_number',
            'receipt_number'
        )
          AND e.field_value = ?
        ORDER BY d.created_at DESC, d.id DESC
        """,
        (str(document_number),),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def filter_documents_by_amount(
    minimum_amount=None,
    maximum_amount=None,
    currency=None,
    review_statuses=("approved",),
):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT DISTINCT d.*
        FROM documents d
        JOIN extracted_fields total_field
            ON d.id = total_field.document_id
        WHERE total_field.field_name = 'total'
          AND total_field.field_value IS NOT NULL
          AND TRIM(total_field.field_value) != ''
    """

    parameters = []

    if review_statuses is not None:
        placeholders = ", ".join(
            "?"
            for _ in review_statuses
        )

        query += (
            " AND d.review_status IN "
            f"({placeholders})"
        )

        parameters.extend(
            review_statuses
        )

    if minimum_amount is not None:
        query += (
            " AND "
            "CAST(total_field.field_value AS REAL) >= ?"
        )

        parameters.append(
            float(minimum_amount)
        )

    if maximum_amount is not None:
        query += (
            " AND "
            "CAST(total_field.field_value AS REAL) <= ?"
        )

        parameters.append(
            float(maximum_amount)
        )

    if currency:
        query += """
            AND EXISTS (
                SELECT 1
                FROM extracted_fields currency_field
                WHERE currency_field.document_id = d.id
                  AND currency_field.field_name = 'currency'
                  AND UPPER(TRIM(currency_field.field_value))
                      = UPPER(TRIM(?))
            )
        """

        parameters.append(
            str(currency)
        )

    query += (
        " ORDER BY "
        "d.created_at DESC, d.id DESC"
    )

    cursor.execute(
        query,
        parameters,
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]
