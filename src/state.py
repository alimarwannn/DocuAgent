from typing import TypedDict, Optional


class DocumentState(TypedDict, total=False):
    image_path: str
    raw_ocr_text: str
    document_type: str
    scan_mode: str
    requested_fields: list[str]
    user_request: str
    scan_result: dict
    validation_issues: list[dict]
    document_id: int
    needs_human_review: bool
    error: Optional[str]