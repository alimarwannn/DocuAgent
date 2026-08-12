from datetime import datetime
from pathlib import Path
import sys
import shutil
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import src.database as database

from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
    save_validation_issues,
)


DEMO_DATABASE = Path("data/docuagent.db")
BACKUP_DIRECTORY = Path("data/backups")
DEMO_DOCUMENT_DIRECTORY = Path("data/demo_documents")


def backup_database():
    if not DEMO_DATABASE.exists():
        return None

    BACKUP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = (
        BACKUP_DIRECTORY
        / f"docuagent_demo_backup_{timestamp}.db"
    )

    shutil.copy2(
        DEMO_DATABASE,
        backup_path,
    )

    return backup_path


def reset_database_file():
    if DEMO_DATABASE.exists():
        DEMO_DATABASE.unlink()

    database.DATABASE_PATH = DEMO_DATABASE
    create_tables()


def add_document(
    filename,
    document_type,
    scan_mode,
    raw_ocr_text,
    review_status,
    fields,
    issues=None,
    review_note=None,
):
    document_id = save_document(
        filename=filename,
        document_type=document_type,
        scan_mode=scan_mode,
        raw_ocr_text=raw_ocr_text,
        review_status=review_status,
    )

    save_extracted_fields(
        document_id,
        fields,
    )

    if issues:
        save_validation_issues(
            document_id,
            issues,
        )

    if review_note:
        connection = sqlite3.connect(DEMO_DATABASE)
        connection.execute(
            "UPDATE documents SET review_note = ? WHERE id = ?",
            (review_note, document_id),
        )
        connection.commit()
        connection.close()

    return document_id


def prepare_demo_images():
    DEMO_DOCUMENT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_map = {
        "ojc-marketing-receipt.jpg": Path("img/demo_review.jpg"),
        "vodafone-egypt-invoice.jpg": Path("img/demo_approved.jpg"),
    }

    for filename, source in image_map.items():
        if source.exists():
            shutil.copy2(
                source,
                DEMO_DOCUMENT_DIRECTORY / filename,
            )


def seed_demo_documents():
    add_document(
        filename="vodafone-egypt-invoice.jpg",
        document_type="invoice",
        scan_mode="full",
        raw_ocr_text="Vodafone Egypt invoice demo",
        review_status="approved",
        fields={
            "supplier_name": "Vodafone Egypt",
            "invoice_number": "VF-DEMO-001",
            "date": "2026-08-04",
            "customer": "Al Noor Trading",
            "subtotal": 1000,
            "tax": 140,
            "total": 1140,
            "currency": "EGP",
        },
    )

    add_document(
        filename="metro-receipt.jpg",
        document_type="receipt",
        scan_mode="full",
        raw_ocr_text="Metro Market receipt demo",
        review_status="approved",
        fields={
            "merchant_name": "Metro Market",
            "receipt_number": "MR-DEMO-002",
            "date": "2026-08-06",
            "subtotal": 420,
            "tax": 0,
            "total": 420,
            "payment_method": "VISA CARD",
            "currency": "EGP",
        },
    )

    add_document(
        filename="openai-usd-invoice.jpg",
        document_type="invoice",
        scan_mode="full",
        raw_ocr_text="OpenAI USD invoice demo",
        review_status="approved",
        fields={
            "supplier_name": "OpenAI",
            "invoice_number": "OA-DEMO-003",
            "date": "2026-08-08",
            "customer": "Vodafone Egypt AI Team",
            "subtotal": 120,
            "tax": 20,
            "total": 140,
            "currency": "USD",
        },
    )

    add_document(
        filename="ojc-marketing-receipt.jpg",
        document_type="receipt",
        scan_mode="full",
        raw_ocr_text="OJC MARKETING SDN BHD demo receipt",
        review_status="pending_review",
        fields={
            "merchant_name": "OJC MARKETING SDN BHD",
            "receipt_number": "PEGIV-1030765",
            "date": "2019-01-15",
            "subtotal": 193,
            "tax": 0,
            "total": 193,
            "payment_method": "VISA CARD",
            "currency": None,
        },
        issues=[
            {
                "issue_type": "missing_field",
                "message": "Currency is missing.",
                "severity": "error",
            },
            {
                "issue_type": "missing_currency",
                "message": "Currency could not be verified from the document.",
                "severity": "error",
            },
        ],
        review_note="Demo review item: add the verified currency before approval.",
    )

    add_document(
        filename="duplicate-invoice-demo.jpg",
        document_type="invoice",
        scan_mode="full",
        raw_ocr_text="Duplicate invoice demo",
        review_status="rejected",
        fields={
            "supplier_name": "Vodafone Egypt",
            "invoice_number": "VF-DEMO-001",
            "date": "2026-08-09",
            "customer": "Archive Copy",
            "subtotal": 1000,
            "tax": 140,
            "total": 1140,
            "currency": "EGP",
        },
        issues=[
            {
                "issue_type": "duplicate_invoice",
                "message": "Invoice number VF-DEMO-001 already exists.",
                "severity": "warning",
            },
        ],
        review_note="Rejected in the demo dataset to show the review lifecycle.",
    )


def summarize():
    connection = sqlite3.connect(DEMO_DATABASE)
    cursor = connection.cursor()
    counts = dict(
        cursor.execute(
            """
            SELECT review_status, COUNT(*)
            FROM documents
            GROUP BY review_status
            """
        ).fetchall()
    )
    connection.close()
    return counts


def main():
    backup_path = backup_database()
    reset_database_file()
    prepare_demo_images()
    seed_demo_documents()
    counts = summarize()

    print("Demo database prepared.")

    if backup_path is not None:
        print(f"Backup created at: {backup_path}")
    else:
        print("No existing database was present, so no backup was needed.")

    print(f"Approved: {counts.get('approved', 0)}")
    print(f"Pending review: {counts.get('pending_review', 0)}")
    print(f"Rejected: {counts.get('rejected', 0)}")


if __name__ == "__main__":
    main()
