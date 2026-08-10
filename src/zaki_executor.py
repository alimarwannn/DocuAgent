from src.business_tools import (
    average_document_value,
    detect_contradictions,
    duplicate_invoices,
    highest_value_documents,
    invalid_documents,
    supplier_summary,
    total_spend,
    total_tax,
)
from src.database import (
    filter_documents_by_amount,
    filter_documents_by_date,
    filter_documents_by_party,
    filter_documents_by_type,
    find_document_by_number,
    list_documents,
)


TOOL_FUNCTIONS = {
    "list_documents": list_documents,
    "filter_documents_by_type": filter_documents_by_type,
    "filter_documents_by_date": filter_documents_by_date,
    "filter_documents_by_party": filter_documents_by_party,
    "find_document_by_number": find_document_by_number,
    "filter_documents_by_amount": filter_documents_by_amount,
    "total_spend": total_spend,
    "total_tax": total_tax,
    "average_document_value": average_document_value,
    "highest_value_documents": highest_value_documents,
    "supplier_summary": supplier_summary,
    "invalid_documents": invalid_documents,
    "duplicate_invoices": duplicate_invoices,
    "detect_contradictions": detect_contradictions,
}


def clean_arguments(arguments):
    if not isinstance(arguments, dict):
        return {}

    return {
        key: value
        for key, value in arguments.items()
        if value is not None
    }


def execute_zaki_tool(tool_name, arguments=None):
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "tool_name": tool_name,
            "result": None,
            "error": "unknown_tool",
        }

    function = TOOL_FUNCTIONS[tool_name]
    safe_arguments = clean_arguments(arguments)

    try:
        result = function(**safe_arguments)

        return {
            "success": True,
            "tool_name": tool_name,
            "arguments": safe_arguments,
            "result": result,
            "error": None,
        }

    except TypeError as error:
        return {
            "success": False,
            "tool_name": tool_name,
            "arguments": safe_arguments,
            "result": None,
            "error": "invalid_arguments",
            "message": str(error),
        }

    except Exception as error:
        return {
            "success": False,
            "tool_name": tool_name,
            "arguments": safe_arguments,
            "result": None,
            "error": "tool_execution_failed",
            "message": str(error),
        }