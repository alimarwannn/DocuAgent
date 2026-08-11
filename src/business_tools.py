from collections import defaultdict
from datetime import datetime

from src.database import (
    get_database_connection,
    get_document_fields,
    get_document_issues,
    list_documents,
)


def _to_float(value):
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_text(value):
    if value in (None, ""):
        return None

    return " ".join(str(value).strip().lower().split())


def _normalize_amount(value):
    amount = _to_float(value)

    if amount is None:
        return None

    return round(amount, 2)


def _currency_code(value):
    if value in (None, ""):
        return None

    text = " ".join(
        str(value).strip().upper().split()
    )

    return text or None


def _normalize_date(value):
    if value in (None, ""):
        return None

    text = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %I:%M.%S %p",
    ]

    for date_format in formats:
        try:
            parsed = datetime.strptime(text, date_format)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return text


def get_documents_with_fields(
    review_statuses=("approved",),
):
    documents = list_documents()

    if review_statuses is not None:
        allowed_statuses = set(
            review_statuses
        )

        documents = [
            document
            for document in documents
            if document.get(
                "review_status"
            )
            in allowed_statuses
        ]

    results = []

    for document in documents:
        document_data = dict(document)
        document_data["fields"] = get_document_fields(document["id"])
        results.append(document_data)

    return results


def _documents_by_currency(
    amount_field,
    start_date=None,
    end_date=None,
    review_statuses=("approved",),
):
    documents = get_documents_with_fields(
        review_statuses=review_statuses
    )

    grouped_totals = defaultdict(float)
    matched_documents = []

    for document in documents:
        fields = document["fields"]

        document_date = _normalize_date(
            fields.get("date")
        )

        amount = _to_float(
            fields.get(amount_field)
        )

        if amount is None:
            continue

        if start_date is not None:
            if (
                document_date is None
                or document_date < start_date
            ):
                continue

        if end_date is not None:
            if (
                document_date is None
                or document_date > end_date
            ):
                continue

        currency = (
            _currency_code(
                fields.get("currency")
            )
            or "UNKNOWN"
        )

        grouped_totals[currency] += amount
        matched_documents.append(document)

    totals_by_currency = {
        currency: round(total, 2)
        for currency, total in sorted(
            grouped_totals.items()
        )
    }

    single_currency = None
    single_total = None

    if len(totals_by_currency) == 1:
        (
            single_currency,
            single_total,
        ) = next(
            iter(
                totals_by_currency.items()
            )
        )

    return {
        "currency": single_currency,
        "total": single_total,
        "totals_by_currency": totals_by_currency,
        "document_count": len(matched_documents),
        "documents": matched_documents,
    }


def total_spend(start_date=None, end_date=None):
    return _documents_by_currency(
        "total",
        start_date=start_date,
        end_date=end_date,
    )


def total_tax(start_date=None, end_date=None):
    summary = _documents_by_currency(
        "tax",
        start_date=start_date,
        end_date=end_date,
    )

    summary["total_tax"] = summary[
        "total"
    ]

    return summary


def average_document_value(start_date=None, end_date=None):
    spend_result = total_spend(start_date, end_date)

    count = spend_result["document_count"]

    if count == 0:
        average = 0.0
    else:
        total = spend_result.get(
            "total"
        )

        average = (
            0.0
            if total is None
            else total / count
        )

    averages_by_currency = {}

    if count > 0:
        grouped_counts = defaultdict(int)

        for document in spend_result[
            "documents"
        ]:
            currency = (
                _currency_code(
                    document[
                        "fields"
                    ].get("currency")
                )
                or "UNKNOWN"
            )

            grouped_counts[currency] += 1

        for (
            currency,
            total,
        ) in spend_result[
            "totals_by_currency"
        ].items():
            averages_by_currency[
                currency
            ] = round(
                total
                / grouped_counts[currency],
                2,
            )

    return {
        "average": average,
        "currency": spend_result.get(
            "currency"
        ),
        "averages_by_currency": averages_by_currency,
        "document_count": count,
        "total": spend_result.get(
            "total"
        ),
        "totals_by_currency": spend_result.get(
            "totals_by_currency",
            {},
        ),
    }


def highest_value_documents(limit=5):
    documents = get_documents_with_fields()

    valued_documents = []

    for document in documents:
        amount = _to_float(document["fields"].get("total"))

        if amount is None:
            continue

        document_data = dict(document)
        document_data["total"] = amount
        document_data["currency"] = _currency_code(
            document["fields"].get(
                "currency"
            )
        )

        valued_documents.append(document_data)

    valued_documents.sort(
        key=lambda document: document["total"],
        reverse=True,
    )

    return valued_documents[:limit]


def supplier_summary():
    documents = get_documents_with_fields()

    summaries = defaultdict(
        lambda: {
            "document_count": 0,
            "total_value": None,
            "total_value_by_currency": defaultdict(float),
        }
    )

    supplier_names = {}

    for document in documents:
        fields = document["fields"]

        supplier = (
            fields.get("supplier_name")
            or fields.get("merchant_name")
        )

        if not supplier:
            continue

        normalized_supplier = _normalize_text(supplier)

        if normalized_supplier not in supplier_names:
            supplier_names[normalized_supplier] = supplier

        amount = _to_float(
            fields.get("total")
        )
        currency = _currency_code(
            fields.get("currency")
        )

        summaries[normalized_supplier]["document_count"] += 1

        if (
            amount is not None
            and currency is not None
        ):
            summaries[normalized_supplier][
                "total_value_by_currency"
            ][currency] += amount

    results = []

    for normalized_supplier, data in summaries.items():
        grouped_totals = {
            currency: round(total, 2)
            for currency, total in sorted(
                data[
                    "total_value_by_currency"
                ].items()
            )
        }

        total_value = None

        if len(grouped_totals) == 1:
            total_value = next(
                iter(
                    grouped_totals.values()
                )
            )

        results.append(
            {
                "supplier": supplier_names[normalized_supplier],
                "document_count": data["document_count"],
                "total_value": total_value,
                "total_value_by_currency": grouped_totals,
            }
        )

    results.sort(
        key=lambda item: item["document_count"],
        reverse=True,
    )

    return results


def invalid_documents():
    documents = list_documents()

    results = []

    for document in documents:
        issues = get_document_issues(document["id"])

        if not issues:
            continue

        document_data = dict(document)
        document_data["issues"] = issues

        results.append(document_data)

    return results


def duplicate_invoices():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            field_value AS invoice_number,
            COUNT(*) AS occurrence_count
        FROM extracted_fields
        WHERE field_name = 'invoice_number'
          AND field_value IS NOT NULL
          AND TRIM(field_value) != ''
        GROUP BY field_value
        HAVING COUNT(*) > 1
        ORDER BY occurrence_count DESC
        """
    )

    duplicates = cursor.fetchall()

    results = []

    for duplicate in duplicates:
        invoice_number = duplicate["invoice_number"]

        cursor.execute(
            """
            SELECT DISTINCT d.*
            FROM documents d
            JOIN extracted_fields e
                ON d.id = e.document_id
            WHERE e.field_name = 'invoice_number'
              AND e.field_value = ?
            ORDER BY d.id
            """,
            (invoice_number,),
        )

        documents = [
            dict(row)
            for row in cursor.fetchall()
        ]

        results.append(
            {
                "invoice_number": invoice_number,
                "occurrence_count": duplicate["occurrence_count"],
                "documents": documents,
            }
        )

    connection.close()

    return results


def detect_contradictions():
    documents = get_documents_with_fields(
        review_statuses=None
    )

    invoice_groups = defaultdict(list)

    for document in documents:
        fields = document["fields"]

        invoice_number = fields.get("invoice_number")

        if not invoice_number:
            continue

        invoice_groups[str(invoice_number).strip()].append(document)

    contradictions = []

    for invoice_number, grouped_documents in invoice_groups.items():
        if len(grouped_documents) < 2:
            continue

        totals = {}
        suppliers = {}
        dates = {}

        for document in grouped_documents:
            fields = document["fields"]

            raw_total = fields.get("total")
            raw_supplier = fields.get("supplier_name")
            raw_date = fields.get("date")

            normalized_total = _normalize_amount(raw_total)
            normalized_supplier = _normalize_text(raw_supplier)
            normalized_date = _normalize_date(raw_date)

            if normalized_total is not None:
                totals[normalized_total] = raw_total

            if normalized_supplier is not None:
                suppliers[normalized_supplier] = raw_supplier

            if normalized_date is not None:
                dates[normalized_date] = raw_date

        document_ids = [
            document["id"]
            for document in grouped_documents
        ]

        if len(totals) > 1:
            contradictions.append(
                {
                    "invoice_number": invoice_number,
                    "type": "conflicting_total",
                    "values": sorted(totals.keys()),
                    "document_ids": document_ids,
                }
            )

        if len(suppliers) > 1:
            contradictions.append(
                {
                    "invoice_number": invoice_number,
                    "type": "conflicting_supplier",
                    "values": sorted(suppliers.values()),
                    "document_ids": document_ids,
                }
            )

        if len(dates) > 1:
            contradictions.append(
                {
                    "invoice_number": invoice_number,
                    "type": "conflicting_date",
                    "values": sorted(dates.keys()),
                    "document_ids": document_ids,
                }
            )

    return contradictions
