def initialize_state(session_state):
    defaults = {
        "page": "Home",
        "scan_output": None,
        "last_image_path": None,
        "last_uploaded_name": None,
        "last_upload_signature": None,
        "last_scan_config": None,
        "current_scan_options": None,
        "uploader_version": 0,
        "review_message": None,
        "navigation_notice": None,
        "home_zaki_answer": None,
        "zaki_messages": [
            {
                "role": "assistant",
                "content": (
                    "Hi, I'm Zaki. "
                    "Ask me anything about "
                    "your saved documents."
                ),
            }
        ],
    }

    for key, value in defaults.items():
        if key not in session_state:
            session_state[key] = value


def set_page(
    session_state,
    page,
    document_id=None,
):
    session_state["page"] = page

    if (
        page == "Review"
        and document_id is not None
    ):
        session_state[
            "review_document_select"
        ] = document_id

    if (
        page == "Documents"
        and document_id is not None
    ):
        session_state[
            "document_select"
        ] = document_id


def clear_document_workspace(
    session_state,
):
    session_state["scan_output"] = None
    session_state["last_image_path"] = None
    session_state["last_uploaded_name"] = None
    session_state["last_upload_signature"] = None
    session_state["last_scan_config"] = None
    session_state["current_scan_options"] = None
    session_state["uploader_version"] += 1


def prepare_uploaded_document(
    session_state,
    uploaded_name,
    signature,
):
    if (
        session_state.get(
            "last_upload_signature"
        )
        == signature
    ):
        return False

    session_state["scan_output"] = None
    session_state["last_image_path"] = None
    session_state["last_scan_config"] = None
    session_state[
        "last_upload_signature"
    ] = signature
    session_state[
        "last_uploaded_name"
    ] = uploaded_name

    return True


def build_scan_options(
    scan_mode,
    user_request,
    document_type_override,
):
    return {
        "scan_mode": scan_mode,
        "user_request": user_request,
        "document_type_override": document_type_override,
    }


def should_enable_processing(
    has_uploaded_file,
    scan_mode,
    user_request,
):
    if not has_uploaded_file:
        return False

    if (
        scan_mode == "partial"
        and not user_request.strip()
    ):
        return False

    return True
