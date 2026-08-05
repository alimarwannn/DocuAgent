from src.schemas import INVOICE_TEMPLATE, RECEIPT_TEMPLATE


def create_empty_result(document_type, scan_mode):
    if document_type == "invoice":
        fields = INVOICE_TEMPLATE.copy()
    elif document_type == "receipt":
        fields = RECEIPT_TEMPLATE.copy()
    else:
        fields = {}

    return {
        "document_type": document_type,
        "scan_mode": scan_mode,
        "fields": fields,
    }