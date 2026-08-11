from src.ui.state import (
    build_scan_options,
    clear_document_workspace,
    initialize_state,
    prepare_uploaded_document,
    set_page,
    should_enable_processing,
)


session_state = {}

initialize_state(session_state)

assert session_state["page"] == "Home"
assert session_state["scan_output"] is None
assert session_state["uploader_version"] == 0


session_state["scan_output"] = {"status": "failed"}
session_state["last_image_path"] = "data/uploads/original.jpg"
session_state["last_scan_config"] = {"scan_mode": "full"}

changed = prepare_uploaded_document(
    session_state=session_state,
    uploaded_name="receipt.jpg",
    signature="sig-001",
)

assert changed is True
assert session_state["scan_output"] is None
assert session_state["last_image_path"] is None
assert session_state["last_uploaded_name"] == "receipt.jpg"
assert session_state["last_upload_signature"] == "sig-001"


unchanged = prepare_uploaded_document(
    session_state=session_state,
    uploaded_name="receipt.jpg",
    signature="sig-001",
)

assert unchanged is False


session_state["scan_output"] = {"status": "saved"}
clear_document_workspace(session_state)

assert session_state["scan_output"] is None
assert session_state["last_upload_signature"] is None
assert session_state["uploader_version"] == 1


assert should_enable_processing(
    has_uploaded_file=False,
    scan_mode="full",
    user_request="",
) is False

assert should_enable_processing(
    has_uploaded_file=True,
    scan_mode="partial",
    user_request="",
) is False

assert should_enable_processing(
    has_uploaded_file=True,
    scan_mode="partial",
    user_request="merchant name and total",
) is True


options = build_scan_options(
    scan_mode="quick",
    user_request="",
    document_type_override="receipt",
)

assert options == {
    "scan_mode": "quick",
    "user_request": "",
    "document_type_override": "receipt",
}


set_page(
    session_state,
    page="Review",
    document_id=7,
)

assert session_state["page"] == "Review"
assert session_state["review_document_select"] == 7


set_page(
    session_state,
    page="Documents",
    document_id=9,
)

assert session_state["page"] == "Documents"
assert session_state["document_select"] == 9


print("UI state helper tests passed.")
