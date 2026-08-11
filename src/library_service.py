from src.database import (
    get_database_connection,
)


def list_document_summaries(
    limit=None,
    review_status=None,
):
    connection = (
        get_database_connection()
    )

    cursor = connection.cursor()

    query = """
        SELECT
            d.id,
            d.filename,
            d.document_type,
            d.scan_mode,
            d.review_status,
            d.review_note,
            d.created_at,

            (
                SELECT e.field_value
                FROM extracted_fields e
                WHERE e.document_id = d.id
                  AND e.field_name IN (
                      'supplier_name',
                      'merchant_name'
                  )
                LIMIT 1
            ) AS party,

            (
                SELECT e.field_value
                FROM extracted_fields e
                WHERE e.document_id = d.id
                  AND e.field_name IN (
                      'invoice_number',
                      'receipt_number'
                  )
                LIMIT 1
            ) AS document_number,

            (
                SELECT e.field_value
                FROM extracted_fields e
                WHERE e.document_id = d.id
                  AND e.field_name = 'date'
                LIMIT 1
            ) AS document_date,

            (
                SELECT e.field_value
                FROM extracted_fields e
                WHERE e.document_id = d.id
                  AND e.field_name = 'total'
                LIMIT 1
            ) AS total,

            (
                SELECT e.field_value
                FROM extracted_fields e
                WHERE e.document_id = d.id
                  AND e.field_name = 'currency'
                LIMIT 1
            ) AS currency,

            (
                SELECT COUNT(*)
                FROM validation_issues v
                WHERE v.document_id = d.id
            ) AS issue_count

        FROM documents d
    """

    parameters = []

    if review_status is not None:
        query += """
            WHERE d.review_status = ?
        """

        parameters.append(
            review_status
        )

    query += """
        ORDER BY d.created_at DESC, d.id DESC
    """

    if limit is not None:
        query += """
            LIMIT ?
        """

        parameters.append(
            int(limit)
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


def get_library_counts():
    connection = (
        get_database_connection()
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total,

            SUM(
                CASE
                    WHEN review_status = 'approved'
                    THEN 1
                    ELSE 0
                END
            ) AS approved,

            SUM(
                CASE
                    WHEN review_status = 'pending_review'
                    THEN 1
                    ELSE 0
                END
            ) AS pending_review,

            SUM(
                CASE
                    WHEN review_status = 'rejected'
                    THEN 1
                    ELSE 0
                END
            ) AS rejected,

            SUM(
                CASE
                    WHEN document_type = 'invoice'
                    THEN 1
                    ELSE 0
                END
            ) AS invoices,

            SUM(
                CASE
                    WHEN document_type = 'receipt'
                    THEN 1
                    ELSE 0
                END
            ) AS receipts

        FROM documents
        """
    )

    row = cursor.fetchone()

    connection.close()

    return {
        "total":
            row["total"] or 0,
        "approved":
            row["approved"] or 0,
        "pending_review":
            row["pending_review"] or 0,
        "rejected":
            row["rejected"] or 0,
        "invoices":
            row["invoices"] or 0,
        "receipts":
            row["receipts"] or 0,
    }


def get_pending_review_count():
    return get_library_counts()[
        "pending_review"
    ]