from typing import TypedDict, Optional


class DocumentState(TypedDict, total=False):
    image_path: str
    raw_ocr_text: str
    document_type: str
    scan_mode: str
    requested_fields: list[str]
    scan_result: dict
    validation_issues: list[dict]
    document_id: int
    error: Optional[str]