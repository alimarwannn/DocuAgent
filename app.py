import hashlib
import html
import json
from pathlib import Path

import streamlit as st

from src.database import (
    create_tables,
    get_document,
    get_document_fields,
    get_document_issues,
    list_review_documents,
)

from src.document_service import (
    approve_reviewed_document,
    reject_reviewed_document,
)

from src.graph import build_document_graph

from src.library_service import (
    get_library_counts,
    list_document_summaries,
)

from src.zaki_graph import run_zaki

from src.ui.state import (
    build_scan_options as build_ui_scan_options,
    clear_document_workspace as clear_ui_document_workspace,
    initialize_state as initialize_ui_state,
    prepare_uploaded_document,
    set_page as set_ui_page,
    should_enable_processing,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="DocuAgent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# STYLING
# ---------------------------------------------------------

st.html(
    """
    <style>
    #MainMenu,
    footer,
    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }

    [data-testid="stSidebarCollapsedControl"] button {
        background: white !important;
        color: #17191d !important;
        border: 1px solid #e2e5e9 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(20, 24, 32, 0.10) !important;
    }

    [data-testid="stSidebarCollapsedControl"] button svg {
        fill: #17191d !important;
        color: #17191d !important;
    }

    .stApp {
        background: #f6f7f9;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 0.7rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #24272d;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 10px !important;
        min-height: 42px;
        font-weight: 650 !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: #1b1e24 !important;
        color: #f5f5f5 !important;
        border: 1px solid #2b3038 !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: #252a32 !important;
        color: white !important;
        border-color: #424851 !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #e60000 !important;
        color: white !important;
        border: 1px solid #e60000 !important;
    }

    [data-testid="stSidebar"] .stButton > button * {
        color: inherit !important;
    }

    .sidebar-brand {
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .sidebar-copy {
        color: #9298a3;
        font-size: 0.82rem;
        margin-bottom: 22px;
    }

    .sidebar-label {
        color: #777e89;
        text-transform: uppercase;
        font-size: 0.67rem;
        letter-spacing: 0.09em;
        font-weight: 750;
        margin-top: 19px;
        margin-bottom: 8px;
    }

    .sidebar-stat {
        background: #1b1e24;
        border: 1px solid #292d34;
        border-radius: 13px;
        padding: 12px 14px;
        margin-top: 10px;
    }

    .sidebar-stat-label {
        color: #9298a3;
        font-size: 0.72rem;
    }

    .sidebar-stat-value {
        color: white;
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 3px;
    }

    .page-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 15px;
    }

    .logo {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: #e60000;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
        font-weight: 800;
        box-shadow: 0 7px 20px rgba(230, 0, 0, 0.17);
    }

    .page-title {
        color: #15171b;
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1;
    }

    .page-copy {
        color: #777d87;
        font-size: 0.84rem;
        margin-top: 5px;
    }

    .home-intro {
        background: linear-gradient(
            135deg,
            #17191f,
            #272b33
        );
        border-radius: 20px;
        padding: 19px 25px;
        margin-bottom: 15px;
        color: white;
        box-shadow: 0 10px 30px rgba(20, 24, 32, 0.08);
    }

    .home-intro-label {
        color: #ff6666;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.67rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .home-intro-title {
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 6px;
    }

    .home-intro-copy {
        color: #c8ccd3;
        font-size: 0.87rem;
        line-height: 1.45;
    }

    .section-heading {
        color: #17191d;
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 3px;
    }

    .section-copy {
        color: #777d87;
        font-size: 0.82rem;
        margin-bottom: 10px;
    }

    .mini-card {
        background: white;
        border: 1px solid #e6e8ec;
        border-radius: 15px;
        padding: 15px 16px;
        margin-bottom: 10px;
        box-shadow: 0 3px 13px rgba(20, 24, 32, 0.025);
    }

    .mini-label {
        color: #858b95;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.66rem;
        font-weight: 750;
    }

    .mini-value {
        color: #17191d;
        font-size: 1.15rem;
        font-weight: 750;
        margin-top: 5px;
    }

    .document-row {
        background: white;
        border: 1px solid #e7e9ed;
        border-radius: 12px;
        padding: 10px 13px;
        margin-bottom: 7px;
    }

    .document-row-title {
        color: #191b20;
        font-size: 0.88rem;
        font-weight: 700;
    }

    .document-row-meta {
        color: #858b95;
        font-size: 0.74rem;
        margin-top: 3px;
    }

    .field-card {
        background: #fafafa;
        border: 1px solid #e8eaee;
        border-radius: 13px;
        padding: 13px 15px;
        min-height: 76px;
        margin-bottom: 9px;
    }

    .field-label {
        color: #838994;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.67rem;
        font-weight: 750;
    }

    .field-value {
        color: #17191d;
        font-size: 0.95rem;
        font-weight: 650;
        margin-top: 6px;
        word-break: break-word;
    }

    .success-box {
        background: #effbf4;
        border: 1px solid #b7e7c9;
        color: #126b40;
        border-radius: 12px;
        padding: 11px 14px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .warning-box {
        background: #fff9eb;
        border: 1px solid #f4d68e;
        color: #845508;
        border-radius: 12px;
        padding: 11px 14px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .error-box {
        background: #fff2f1;
        border: 1px solid #f1bbb6;
        color: #a92b22;
        border-radius: 12px;
        padding: 11px 14px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .issue {
        background: #fff9ec;
        border-left: 4px solid #f79009;
        border-radius: 8px;
        padding: 10px 13px;
        margin-bottom: 8px;
        color: #64420b;
        font-size: 0.86rem;
    }

    .issue-error {
        background: #fff5f4;
        border-left-color: #d92d20;
        color: #7b241d;
    }

    .status-approved {
        color: #087443;
    }

    .status-review {
        color: #a46305;
    }

    .status-rejected {
        color: #b42318;
    }

    .zaki-box {
        background: linear-gradient(
            135deg,
            #ffffff,
            #fff5f5
        );
        border: 1px solid #efdcdc;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .zaki-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #181a1f;
    }

    .zaki-copy {
        color: #747a85;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    div[data-testid="stFileUploader"] {
        background: white;
        border-radius: 13px;
    }

    [data-testid="stFileUploaderDropzone"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 39px;
    }

    main .stButton > button[kind="primary"] {
        background: #e60000 !important;
        border-color: #e60000 !important;
        color: white !important;
    }

    main .stButton > button[kind="primary"]:hover {
        background: #c90000 !important;
        border-color: #c90000 !important;
    }

    main .stButton > button[kind="primary"]:disabled {
        background: #e5e7eb !important;
        border-color: #e5e7eb !important;
        color: #9ca3af !important;
        opacity: 1 !important;
    }

    div[data-testid="stProgress"] > div > div {
        border-radius: 999px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 14px;
    }
    </style>
    """
)


# ---------------------------------------------------------
# STARTUP
# ---------------------------------------------------------

create_tables()


@st.cache_resource
def get_document_graph():
    return build_document_graph()


# ---------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------

def ui(content):
    st.html(content)


def safe(value):
    if value in (
        None,
        "",
    ):
        return "Not found"

    return html.escape(
        str(value)
    )


def initialize_state():
    initialize_ui_state(
        st.session_state
    )


def go_to(
    page,
    document_id=None,
):
    set_ui_page(
        st.session_state,
        page,
        document_id=document_id,
    )

    st.rerun()


def uploaded_signature(
    uploaded_file,
):
    if uploaded_file is None:
        return None

    file_bytes = (
        uploaded_file.getvalue()
    )

    return hashlib.sha256(
        file_bytes
    ).hexdigest()


def clean_filename(
    filename,
):
    name = Path(
        filename
    ).name

    cleaned = "".join(
        character
        for character in name
        if (
            character.isalnum()
            or character
            in "._-"
        )
    )

    if cleaned:
        return cleaned

    return "document.jpg"


def save_uploaded_file(
    uploaded_file,
):
    directory = Path(
        "data/uploads"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_bytes = (
        uploaded_file.getvalue()
    )

    digest = hashlib.sha256(
        file_bytes
    ).hexdigest()[:12]

    filename = clean_filename(
        uploaded_file.name
    )

    file_path = (
        directory
        / f"{digest}_{filename}"
    )

    # Do not rewrite identical files.
    # This keeps the modified time unchanged,
    # allowing OCR caching to work on retries.
    if not file_path.exists():
        with open(
            file_path,
            "wb",
        ) as file:
            file.write(
                file_bytes
            )

    return str(
        file_path
    )


def clear_document_workspace():
    clear_ui_document_workspace(
        st.session_state
    )


def build_scan_state(
    image_path,
    scan_mode,
    user_request="",
    document_type_override=None,
):
    state = {
        "image_path":
            image_path,

        "scan_mode":
            scan_mode,

        "error":
            None,
    }

    if (
        scan_mode == "partial"
        and user_request.strip()
    ):
        state[
            "user_request"
        ] = user_request.strip()

    if document_type_override:
        state[
            "document_type_override"
        ] = document_type_override

    return state


# ---------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------

def status_label(status):
    labels = {
        "approved":
            "Approved",

        "pending_review":
            "Needs review",

        "rejected":
            "Rejected",
    }

    return labels.get(
        status,
        "Saved",
    )


def status_class(status):
    classes = {
        "approved":
            "status-approved",

        "pending_review":
            "status-review",

        "rejected":
            "status-rejected",
    }

    return classes.get(
        status,
        "",
    )


def display_fields(fields):
    if not fields:
        st.info(
            "No details were found."
        )
        return

    items = list(
        fields.items()
    )

    for start in range(
        0,
        len(items),
        3,
    ):
        columns = st.columns(
            3
        )

        for column, item in zip(
            columns,
            items[
                start:
                start + 3
            ],
        ):
            name, value = item

            label = (
                name
                .replace(
                    "_",
                    " ",
                )
                .title()
            )

            with column:
                ui(
                    f"""
                    <div class="field-card">
                        <div class="field-label">
                            {safe(label)}
                        </div>

                        <div class="field-value">
                            {safe(value)}
                        </div>
                    </div>
                    """
                )


def display_issues(issues):
    if not issues:
        ui(
            """
            <div class="success-box">
                ✓ Everything looks good
            </div>
            """
        )

        return

    for issue in issues:
        severity = issue.get(
            "severity",
            "warning",
        )

        css_class = (
            "issue issue-error"
            if severity
            == "error"
            else "issue"
        )

        message = issue.get(
            "message",
            (
                "This item "
                "needs checking."
            ),
        )

        ui(
            f"""
            <div class="{css_class}">
                {safe(message)}
            </div>
            """
        )


def show_page_header(
    title,
    copy,
):
    ui(
        f"""
        <div class="page-header">
            <div class="logo">
                D
            </div>

            <div>
                <div class="page-title">
                    {safe(title)}
                </div>

                <div class="page-copy">
                    {safe(copy)}
                </div>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

def show_sidebar():
    counts = (
        get_library_counts()
    )

    with st.sidebar:
        ui(
            """
            <div class="sidebar-brand">
                ◈ DocuAgent
            </div>

            <div class="sidebar-copy">
                Your document workspace
            </div>

            <div class="sidebar-label">
                Menu
            </div>
            """
        )

        pages = [
            (
                "Home",
                "⌂ Home",
            ),

            (
                "Review",
                (
                    "✓ Review"
                    if counts[
                        "pending_review"
                    ] == 0
                    else (
                        "⚠ Review "
                        f"({counts['pending_review']})"
                    )
                ),
            ),

            (
                "Documents",
                "▤ Documents",
            ),

            (
                "Zaki",
                "✦ Ask Zaki",
            ),
        ]

        for page, label in pages:
            active = (
                st.session_state.page
                == page
            )

            if st.button(
                label,
                key=f"nav_{page}",
                type=(
                    "primary"
                    if active
                    else "secondary"
                ),
                use_container_width=True,
            ):
                if not active:
                    go_to(
                        page
                    )

        ui(
            """
            <div class="sidebar-label">
                Library
            </div>
            """
        )

        ui(
            f"""
            <div class="sidebar-stat">
                <div class="sidebar-stat-label">
                    Documents
                </div>

                <div class="sidebar-stat-value">
                    {counts["total"]}
                </div>
            </div>

            <div class="sidebar-stat">
                <div class="sidebar-stat-label">
                    Waiting for review
                </div>

                <div class="sidebar-stat-value">
                    {counts["pending_review"]}
                </div>
            </div>
            """
        )


# ---------------------------------------------------------
# GRAPH PROGRESS
# ---------------------------------------------------------

NODE_PROGRESS = {
    "load": (
        8,
        "Preparing document...",
    ),

    "ocr": (
        35,
        "Reading document...",
    ),

    "document_type": (
        48,
        "Identifying document...",
    ),

    "full_scan": (
        68,
        "Extracting details...",
    ),

    "partial_scan": (
        68,
        "Extracting requested details...",
    ),

    "quick_scan": (
        82,
        "Finding available details...",
    ),

    "normalization": (
        82,
        "Cleaning extracted data...",
    ),

    "validation": (
        92,
        "Checking details...",
    ),

    "save": (
        100,
        "Saving document...",
    ),

    "human_review": (
        100,
        "Preparing document for review...",
    ),
}


def run_scan_with_progress(
    initial_state,
):
    graph = (
        get_document_graph()
    )

    progress = st.progress(
        0
    )

    status = st.empty()

    merged_state = dict(
        initial_state
    )

    last_percent = 0

    try:
        for update in graph.stream(
            initial_state,
            stream_mode="updates",
        ):
            if not isinstance(
                update,
                dict,
            ):
                continue

            for (
                node_name,
                node_update,
            ) in update.items():

                if isinstance(
                    node_update,
                    dict,
                ):
                    merged_state.update(
                        node_update
                    )

                (
                    percent,
                    message,
                ) = NODE_PROGRESS.get(
                    node_name,
                    (
                        50,
                        "Processing document...",
                    ),
                )

                last_percent = max(
                    last_percent,
                    percent,
                )

                progress.progress(
                    last_percent
                )

                status.caption(
                    message
                )

        if merged_state.get(
            "error"
        ):
            progress.progress(
                max(
                    last_percent,
                    10,
                )
            )

            status.caption(
                (
                    "Processing stopped — "
                    "see the reason below."
                )
            )

        else:
            progress.progress(
                100
            )

            status.caption(
                "Done."
            )

        return merged_state

    except Exception as error:
        progress.progress(
            max(
                last_percent,
                10,
            )
        )

        status.caption(
            (
                "Processing stopped — "
                "see the reason below."
            )
        )

        return {
            **merged_state,

            "error":
                str(error),
        }


def process_scan(
    image_path,
    scan_mode,
    user_request="",
    document_type_override=None,
):
    config = {
        "scan_mode":
            scan_mode,

        "user_request":
            user_request,

        "document_type_override":
            document_type_override,
    }

    st.session_state[
        "last_scan_config"
    ] = config

    initial_state = (
        build_scan_state(
            image_path=(
                image_path
            ),

            scan_mode=(
                scan_mode
            ),

            user_request=(
                user_request
            ),

            document_type_override=(
                document_type_override
            ),
        )
    )

    result = (
        run_scan_with_progress(
            initial_state
        )
    )

    st.session_state[
        "scan_output"
    ] = result

    return result


# ---------------------------------------------------------
# ERROR HANDLING
# ---------------------------------------------------------

def friendly_error_message(
    error,
):
    text = str(
        error or ""
    )

    lowered = (
        text.lower()
    )

    if (
        "unsupported document type"
        in lowered
    ):
        return (
            "DocuAgent couldn't confidently tell "
            "whether this is an invoice or receipt. "
            "Choose Invoice or Receipt manually above "
            "and try again."
        )

    if (
        "ocr returned no readable text"
        in lowered
    ):
        return (
            "DocuAgent couldn't find enough readable "
            "text in this image. Try a clearer or "
            "higher-resolution image."
        )

    if (
        "ocr failed"
        in lowered
    ):
        return (
            "DocuAgent couldn't read this image. "
            "Check that the file is a valid PNG or JPG "
            "and try again."
        )

    if (
        "full scan extraction failed"
        in lowered
        or "partial scan extraction failed"
        in lowered
        or "quick scan failed"
        in lowered
    ):
        return (
            "The document was read, but its details "
            "couldn't be extracted successfully. "
            "Try again or choose another extraction mode."
        )

    if (
        "saving document failed"
        in lowered
        or "could not save"
        in lowered
    ):
        return (
            "The document was processed, but DocuAgent "
            "couldn't save the result."
        )

    if (
        "missing image path"
        in lowered
    ):
        return (
            "The uploaded document is no longer available. "
            "Choose the file again."
        )

    return (
        "DocuAgent couldn't finish processing this document. "
        "You can retry without uploading it again."
    )


def retry_current_document():
    image_path = (
        st.session_state.get(
            "last_image_path"
        )
    )

    options = (
        st.session_state.get(
            "current_scan_options"
        )
        or st.session_state.get(
            "last_scan_config"
        )
    )

    if (
        not image_path
        or not options
    ):
        st.error(
            (
                "There is no document "
                "available to retry."
            )
        )
        return

    process_scan(
        image_path=(
            image_path
        ),

        scan_mode=(
            options.get(
                "scan_mode",
                "full",
            )
        ),

        user_request=(
            options.get(
                "user_request",
                "",
            )
        ),

        document_type_override=(
            options.get(
                "document_type_override"
            )
        ),
    )


# ---------------------------------------------------------
# QUICK SCAN
# ---------------------------------------------------------

def get_quick_suggestions(
    scan_result,
):
    if not isinstance(
        scan_result,
        dict,
    ):
        return []

    candidates = (
        scan_result.get(
            "suggested_fields"
        )
        or scan_result.get(
            "available_fields"
        )
    )

    if isinstance(
        candidates,
        list,
    ):
        return [
            str(item)
            for item
            in candidates
        ]

    if isinstance(
        candidates,
        dict,
    ):
        return list(
            candidates.keys()
        )

    fields = scan_result.get(
        "fields"
    )

    if isinstance(
        fields,
        list,
    ):
        return [
            str(item)
            for item
            in fields
        ]

    if isinstance(
        fields,
        dict,
    ):
        return list(
            fields.keys()
        )

    return []


# ---------------------------------------------------------
# SCAN RESULT
# ---------------------------------------------------------

def show_scan_result(
    result,
):
    if not result:
        return

    error = result.get(
        "error"
    )

    if error:
        ui(
            f"""
            <div class="error-box">
                {safe(
                    friendly_error_message(
                        error
                    )
                )}
            </div>
            """
        )

        retry_col, clear_col = (
            st.columns(2)
        )

        with retry_col:
            if st.button(
                "↻ Try again",
                type="primary",
                use_container_width=True,
                key="retry_failed_scan",
            ):
                retry_current_document()

                st.rerun()

        with clear_col:
            if st.button(
                "Choose another document",
                use_container_width=True,
                key="clear_failed_scan",
            ):
                clear_document_workspace()

                st.rerun()

        with st.expander(
            "Why did processing stop?"
        ):
            st.write(
                friendly_error_message(
                    error
                )
            )


        return

    scan_result = result.get(
        "scan_result",
        {},
    )

    scan_mode = result.get(
        "scan_mode",
        scan_result.get(
            "scan_mode",
            "",
        ),
    )

    document_type = result.get(
        "document_type",
        scan_result.get(
            "document_type",
            "document",
        ),
    )

    document_id = result.get(
        "document_id"
    )

    needs_review = result.get(
        "needs_human_review",
        False,
    )

    if needs_review:
        ui(
            """
            <div class="warning-box">
                This document needs a quick review
                before it can be approved.
            </div>
            """
        )

        if st.button(
            "Review now",
            key="review_scanned_document",
            type="primary",
            use_container_width=True,
        ):
            go_to(
                "Review",
                document_id=(
                    document_id
                ),
            )

    elif (
        scan_mode == "quick"
    ):
        ui(
            """
            <div class="success-box">
                ✓ Preview complete
            </div>
            """
        )

    else:
        reference = (
            f" #{document_id}"
            if document_id
            else ""
        )

        ui(
            f"""
            <div class="success-box">
                ✓ {safe(
                    str(
                        document_type
                    ).title()
                )}
                ready{safe(reference)}
            </div>
            """
        )

    fields = scan_result.get(
        "fields"
    )

    if (
        isinstance(
            fields,
            dict,
        )
        and fields
        and scan_mode
        != "quick"
    ):
        st.markdown(
            "#### Details"
        )

        display_fields(
            fields
        )

    if scan_mode == "quick":
        suggestions = (
            get_quick_suggestions(
                scan_result
            )
        )

        if suggestions:
            selected = (
                st.multiselect(
                    (
                        "Choose the details "
                        "you want to extract"
                    ),

                    options=(
                        suggestions
                    ),

                    default=(
                        suggestions
                    ),

                    format_func=(
                        lambda value:
                        value
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),

                    key=(
                        "quick_selected_fields"
                    ),
                )
            )

            if st.button(
                (
                    "Extract selected "
                    "details"
                ),

                type="primary",

                use_container_width=True,

                disabled=(
                    len(selected)
                    == 0
                ),
            ):
                request = (
                    "Extract only these fields: "
                    + ", ".join(
                        selected
                    )
                )

                previous_config = (
                    st.session_state.get(
                        "last_scan_config"
                    )
                    or {}
                )

                result = (
                    process_scan(
                        image_path=(
                            st.session_state[
                                "last_image_path"
                            ]
                        ),

                        scan_mode=(
                            "partial"
                        ),

                        user_request=(
                            request
                        ),

                        document_type_override=(
                            previous_config.get(
                                "document_type_override"
                            )
                        ),
                    )
                )

                st.session_state[
                    "scan_output"
                ] = result

                st.rerun()

        else:
            st.info(
                (
                    "No suggested details were found. "
                    "Use Specific details instead."
                )
            )

    issues = result.get(
        "validation_issues",
        [],
    )

    if (
        issues
        and scan_mode
        != "quick"
    ):
        st.markdown(
            "#### Checks"
        )

        display_issues(
            issues
        )

    if (
        document_id
        and not needs_review
        and scan_mode
        != "quick"
    ):
        if st.button(
            "Open saved document",
            key="open_saved_document",
            use_container_width=True,
        ):
            go_to(
                "Documents",
                document_id=(
                    document_id
                ),
            )


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

def home_page():
    show_page_header(
        "DocuAgent",
        (
            "Process documents and get "
            "answers in one place."
        ),
    )

    ui(
        """
        <div class="home-intro">
            <div class="home-intro-label">
                Document workspace
            </div>

            <div class="home-intro-title">
                Turn paperwork into answers.
            </div>

            <div class="home-intro-copy">
                Upload an invoice or receipt,
                choose what you need, and DocuAgent
                takes care of the rest.
            </div>
        </div>
        """
    )

    main, side = st.columns(
        [
            1.55,
            0.72,
        ],
        gap="large",
    )

    with main:
        ui(
            """
            <div class="section-heading">
                Process a document
            </div>

            <div class="section-copy">
                Upload an invoice or receipt.
            </div>
            """
        )

        uploader_key = (
            "document_uploader_"
            f"{st.session_state['uploader_version']}"
        )

        uploaded_file = (
            st.file_uploader(
                "Document",

                type=[
                    "png",
                    "jpg",
                    "jpeg",
                ],

                label_visibility=(
                    "collapsed"
                ),

                key=uploader_key,
            )
        )

        if uploaded_file is not None:
            signature = (
                uploaded_signature(
                    uploaded_file
                )
            )

            prepare_uploaded_document(
                st.session_state,
                uploaded_name=(
                    uploaded_file.name
                ),
                signature=signature,
            )

            st.caption(
                f"Selected file: {uploaded_file.name}"
            )

            if st.button(
                "Remove selected file",
                key="clear_uploaded_file",
                use_container_width=True,
            ):
                clear_document_workspace()
                st.rerun()

        option_left, option_right = (
            st.columns(
                [
                    1.55,
                    0.65,
                ]
            )
        )

        with option_left:
            mode_label = st.radio(
                "What do you need?",

                [
                    "Everything",
                    "Specific details",
                    "Quick preview",
                ],

                horizontal=True,
            )

        with option_right:
            type_label = (
                st.selectbox(
                    "Document type",

                    [
                        "Auto detect",
                        "Invoice",
                        "Receipt",
                    ],
                )
            )

        mode_map = {
            "Everything":
                "full",

            "Specific details":
                "partial",

            "Quick preview":
                "quick",
        }

        type_map = {
            "Auto detect":
                None,

            "Invoice":
                "invoice",

            "Receipt":
                "receipt",
        }

        scan_mode = (
            mode_map[
                mode_label
            ]
        )

        document_type_override = (
            type_map[
                type_label
            ]
        )

        user_request = ""

        if scan_mode == "partial":
            user_request = (
                st.text_input(
                    "What should I extract?",

                    placeholder=(
                        "e.g. supplier, invoice number, "
                        "total and currency"
                    ),
                )
            )

        elif scan_mode == "full":
            st.caption(
                (
                    "Extract all supported "
                    "details."
                )
            )

        else:
            st.caption(
                (
                    "See what's available "
                    "before choosing."
                )
            )

        st.session_state[
            "current_scan_options"
        ] = build_ui_scan_options(
            scan_mode=scan_mode,
            user_request=user_request,
            document_type_override=(
                document_type_override
            ),
        )

        ready = should_enable_processing(
            has_uploaded_file=(
                uploaded_file
                is not None
            ),
            scan_mode=scan_mode,
            user_request=user_request,
        )

        if st.button(
            "Process document",
            key="process_document",
            type="primary",
            use_container_width=True,
            disabled=(
                not ready
            ),
        ):
            # Clear any previous failed result
            # before starting the new run.
            st.session_state[
                "scan_output"
            ] = None

            image_path = (
                save_uploaded_file(
                    uploaded_file
                )
            )

            st.session_state[
                "last_image_path"
            ] = image_path

            st.session_state[
                "last_uploaded_name"
            ] = (
                uploaded_file.name
            )

            result = (
                process_scan(
                    image_path=(
                        image_path
                    ),

                    scan_mode=(
                        scan_mode
                    ),

                    user_request=(
                        user_request
                    ),

                    document_type_override=(
                        document_type_override
                    ),
                )
            )

            st.session_state[
                "scan_output"
            ] = result

        if (
            st.session_state[
                "scan_output"
            ]
        ):
            st.markdown(
                "### Result"
            )

            show_scan_result(
                st.session_state[
                    "scan_output"
                ]
            )

    with side:
        counts = (
            get_library_counts()
        )

        ui(
            f"""
            <div class="mini-card">
                <div class="mini-label">
                    Waiting for you
                </div>

                <div class="mini-value">
                    {counts["pending_review"]}
                    to review
                </div>
            </div>
            """
        )

        if st.button(
            "Open review queue",
            key="open_review_queue",
            use_container_width=True,
            disabled=(
                counts[
                    "pending_review"
                ] == 0
            ),
        ):
            go_to(
                "Review"
            )

        ui(
            """
            <div class="zaki-box">
                <div class="zaki-title">
                    ✦ Ask Zaki
                </div>

                <div class="zaki-copy">
                    Get an answer from all
                    of your saved documents.
                </div>
            </div>
            """
        )

        quick_question = (
            st.text_input(
                "Quick question",

                placeholder=(
                    "How much did I spend?"
                ),

                label_visibility=(
                    "collapsed"
                ),

                key=(
                    "home_zaki_question"
                ),
            )
        )

        if st.button(
            "Ask Zaki",
            key="home_ask_zaki",
            use_container_width=True,
            disabled=(
                not quick_question.strip()
            ),
        ):
            try:
                with st.spinner(
                    (
                        "Checking your "
                        "documents..."
                    )
                ):
                    result = (
                        run_zaki(
                            quick_question.strip()
                        )
                    )

                st.session_state[
                    "home_zaki_answer"
                ] = result.get(
                    "answer"
                )
            except Exception:
                st.session_state[
                    "home_zaki_answer"
                ] = (
                    "Zaki couldn't answer that right now. "
                    "Please try again."
                )

        if st.session_state[
            "home_zaki_answer"
        ]:
            st.info(
                st.session_state[
                    "home_zaki_answer"
                ]
            )

        st.markdown(
            "#### Recent"
        )

        recent = (
            list_document_summaries(
                limit=3
            )
        )

        if not recent:
            st.caption(
                "No documents yet."
            )

        for document in recent:
            title = (
                document.get(
                    "party"
                )
                or document.get(
                    "document_number"
                )
                or (
                    f"{document['document_type'].title()} "
                    f"#{document['id']}"
                )
            )

            metadata = (
                document.get(
                    "document_number"
                )
                or document.get(
                    "document_date"
                )
                or (
                    f"Reference "
                    f"#{document['id']}"
                )
            )

            ui(
                f"""
                <div class="document-row">
                    <div class="document-row-title">
                        {safe(title)}
                    </div>

                    <div class="document-row-meta">
                        {safe(metadata)}
                    </div>
                </div>
                """
            )

            if st.button(
                "Open",
                key=(
                    f"recent_"
                    f"{document['id']}"
                ),
                use_container_width=True,
            ):
                go_to(
                    "Documents",
                    document_id=(
                        document["id"]
                    ),
                )


# ---------------------------------------------------------
# REVIEW
# ---------------------------------------------------------

def review_page():
    show_page_header(
        "Review",
        (
            "Check documents that "
            "need your attention."
        ),
    )

    if st.session_state[
        "review_message"
    ]:
        st.success(
            st.session_state[
                "review_message"
            ]
        )

        st.session_state[
            "review_message"
        ] = None

    documents = (
        list_review_documents()
    )

    if not documents:
        st.session_state.pop(
            "review_document_select",
            None,
        )

        ui(
            """
            <div class="success-box">
                ✓ You're all caught up.
                No documents are waiting
                for review.
            </div>
            """
        )

        return

    review_items = []

    for document in documents:
        fields = (
            get_document_fields(
                document[
                    "id"
                ]
            )
        )

        party = (
            fields.get(
                "supplier_name"
            )
            or fields.get(
                "merchant_name"
            )
        )

        number = (
            fields.get(
                "invoice_number"
            )
            or fields.get(
                "receipt_number"
            )
        )

        label = (
            party
            or number
            or (
                f"{document['document_type'].title()} "
                f"#{document['id']}"
            )
        )

        if (
            party
            and number
        ):
            label = (
                f"{party} · {number}"
            )

        review_items.append(
            (
                document,
                fields,
                label,
            )
        )

    ids = [
        item[0]["id"]
        for item
        in review_items
    ]

    if (
        "review_document_select"
        in st.session_state
        and st.session_state[
            "review_document_select"
        ]
        not in ids
    ):
        st.session_state[
            "review_document_select"
        ] = ids[0]

    selected_id = (
        st.selectbox(
            "Document to review",

            options=ids,

            format_func=(
                lambda document_id:
                next(
                    item[2]
                    for item
                    in review_items
                    if item[0][
                        "id"
                    ]
                    == document_id
                )
            ),

            key=(
                "review_document_select"
            ),
        )
    )

    (
        document,
        fields,
        label,
    ) = next(
        item
        for item
        in review_items
        if item[0][
            "id"
        ] == selected_id
    )

    document_id = (
        document["id"]
    )

    issues = (
        get_document_issues(
            document_id
        )
    )

    st.markdown(
        f"### {label}"
    )

    display_issues(
        issues
    )

    st.markdown(
        "#### Check and edit details"
    )

    edited_fields = {}

    items = list(
        fields.items()
    )

    for start in range(
        0,
        len(items),
        2,
    ):
        columns = (
            st.columns(
                2
            )
        )

        for column, item in zip(
            columns,
            items[
                start:
                start + 2
            ],
        ):
            (
                field_name,
                field_value,
            ) = item

            with column:
                value = (
                    st.text_input(
                        field_name
                        .replace(
                            "_",
                            " ",
                        )
                        .title(),

                        value=(
                            ""
                            if field_value
                            is None
                            else str(
                                field_value
                            )
                        ),

                        key=(
                            f"review_"
                            f"{document_id}_"
                            f"{field_name}"
                        ),
                    )
                )

                edited_fields[
                    field_name
                ] = (
                    None
                    if not value.strip()
                    else value.strip()
                )

    note = st.text_area(
        "Review note",

        placeholder=(
            "Optional note about "
            "your decision"
        ),

        key=(
            f"review_note_"
            f"{document_id}"
        ),
    )

    approve_col, reject_col = (
        st.columns(
            2
        )
    )

    with approve_col:
        approve = st.button(
            "Approve changes",
            type="primary",
            use_container_width=True,
        )

    with reject_col:
        reject = st.button(
            "Reject document",
            use_container_width=True,
        )

    if approve:
        result = (
            approve_reviewed_document(
                document_id,

                edited_fields=(
                    edited_fields
                ),

                note=(
                    note.strip()
                    or None
                ),
            )
        )

        if result.get(
            "success"
        ):
            st.session_state[
                "review_message"
            ] = (
                f"{label} "
                "was approved."
            )

            st.session_state.pop(
                "review_document_select",
                None,
            )

            st.rerun()

        else:
            st.error(
                (
                    "Some problems still "
                    "need to be fixed "
                    "before approval."
                )
            )

            display_issues(
                result.get(
                    "validation_issues",
                    [],
                )
            )

    if reject:
        result = (
            reject_reviewed_document(
                document_id,

                note=(
                    note.strip()
                    or None
                ),
            )
        )

        if result.get(
            "success"
        ):
            st.session_state[
                "review_message"
            ] = (
                f"{label} "
                "was rejected."
            )

            st.session_state.pop(
                "review_document_select",
                None,
            )

            st.rerun()

        else:
            st.error(
                (
                    "The document could "
                    "not be rejected."
                )
            )


# ---------------------------------------------------------
# DOCUMENT LIBRARY
# ---------------------------------------------------------

def documents_page():
    show_page_header(
        "Documents",
        (
            "Find and open anything "
            "you've processed."
        ),
    )

    summaries = (
        list_document_summaries()
    )

    if not summaries:
        st.info(
            (
                "Your document "
                "library is empty."
            )
        )

        return

    counts = (
        get_library_counts()
    )

    a, b, c, d = (
        st.columns(
            4
        )
    )

    with a:
        st.metric(
            "All",
            counts[
                "total"
            ],
        )

    with b:
        st.metric(
            "Approved",
            counts[
                "approved"
            ],
        )

    with c:
        st.metric(
            "Review",
            counts[
                "pending_review"
            ],
        )

    with d:
        st.metric(
            "Rejected",
            counts[
                "rejected"
            ],
        )

    (
        search_col,
        status_col,
    ) = st.columns(
        [
            1.6,
            0.6,
        ]
    )

    with search_col:
        search = (
            st.text_input(
                "Search",

                placeholder=(
                    "Supplier, document number, "
                    "date or reference"
                ),
            )
        )

    with status_col:
        status_filter = (
            st.selectbox(
                "Status",

                [
                    "All",
                    "Approved",
                    "Needs review",
                    "Rejected",
                ],
            )
        )

    status_map = {
        "Approved":
            "approved",

        "Needs review":
            "pending_review",

        "Rejected":
            "rejected",
    }

    filtered = []

    for document in summaries:
        if (
            status_filter
            != "All"
            and document.get(
                "review_status"
            )
            != status_map[
                status_filter
            ]
        ):
            continue

        searchable = " ".join(
            str(value)
            for value in [
                document.get(
                    "id"
                ),

                document.get(
                    "party"
                ),

                document.get(
                    "document_number"
                ),

                document.get(
                    "document_date"
                ),

                document.get(
                    "document_type"
                ),

                document.get(
                    "currency"
                ),
            ]
            if value
            not in (
                None,
                "",
            )
        ).lower()

        if (
            search.strip()
            and search
            .lower()
            .strip()
            not in searchable
        ):
            continue

        filtered.append(
            document
        )

    if not filtered:
        st.info(
            (
                "No documents match "
                "your search."
            )
        )

        return

    ids = [
        document["id"]
        for document
        in filtered
    ]

    if (
        "document_select"
        in st.session_state
        and st.session_state[
            "document_select"
        ]
        not in ids
    ):
        st.session_state[
            "document_select"
        ] = ids[0]

    selected_id = (
        st.selectbox(
            "Open document",

            options=ids,

            format_func=(
                lambda doc_id:
                next(
                    (
                        (
                            document.get(
                                "party"
                            )
                            or document.get(
                                "document_number"
                            )
                            or document[
                                "document_type"
                            ].title()
                        )
                        + " · "
                        + (
                            document.get(
                                "document_number"
                            )
                            or (
                                f"#{doc_id}"
                            )
                        )
                    )
                    for document
                    in filtered
                    if document[
                        "id"
                    ] == doc_id
                )
            ),

            key=(
                "document_select"
            ),
        )
    )

    document = (
        get_document(
            selected_id
        )
    )

    fields = (
        get_document_fields(
            selected_id
        )
    )

    issues = (
        get_document_issues(
            selected_id
        )
    )

    selected_summary = next(
        item
        for item
        in filtered
        if item[
            "id"
        ] == selected_id
    )

    status = document.get(
        "review_status",
        "approved",
    )

    left, right = (
        st.columns(
            [
                1.5,
                0.5,
            ]
        )
    )

    with left:
        title = (
            selected_summary.get(
                "party"
            )
            or selected_summary.get(
                "document_number"
            )
            or document[
                "document_type"
            ].title()
        )

        st.markdown(
            f"### {title}"
        )

        st.caption(
            (
                f"Reference "
                f"#{selected_id}"
            )
        )

    with right:
        ui(
            f"""
            <div class="mini-card">
                <div class="mini-label">
                    Status
                </div>

                <div class="mini-value {status_class(status)}">
                    {safe(
                        status_label(
                            status
                        )
                    )}
                </div>
            </div>
            """
        )

    st.markdown(
        "#### Details"
    )

    display_fields(
        fields
    )

    if issues:
        st.markdown(
            "#### Checks"
        )

        display_issues(
            issues
        )

    if (
        status
        == "pending_review"
    ):
        if st.button(
            "Open in Review",
            type="primary",
        ):
            go_to(
                "Review",
                document_id=(
                    selected_id
                ),
            )

    payload = {
        "reference":
            selected_id,

        "document_type":
            document.get(
                "document_type"
            ),

        "status":
            status,

        "fields":
            fields,

        "checks":
            issues,
    }

    st.download_button(
        "Download document data",

        data=json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),

        file_name=(
            f"document_"
            f"{selected_id}.json"
        ),

        mime=(
            "application/json"
        ),
    )


# ---------------------------------------------------------
# ZAKI
# ---------------------------------------------------------

def zaki_page():
    show_page_header(
        "Zaki",
        (
            "Ask questions across "
            "your saved documents."
        ),
    )

    ui(
        """
        <div class="zaki-box">
            <div class="zaki-title">
                ✦ What would you like to know?
            </div>

            <div class="zaki-copy">
                Ask about spending, tax,
                suppliers, duplicates,
                contradictions and more.
            </div>
        </div>
        """
    )

    examples = [
        "How much did I spend?",
        "What was my total tax?",
        (
            "Which supplier "
            "appears most often?"
        ),
        (
            "Do I have "
            "duplicate invoices?"
        ),
    ]

    columns = (
        st.columns(
            4
        )
    )

    selected_example = None

    for (
        column,
        example,
    ) in zip(
        columns,
        examples,
    ):
        with column:
            if st.button(
                example,

                key=(
                    "zaki_example_"
                    f"{example}"
                ),

                use_container_width=True,
            ):
                selected_example = (
                    example
                )

    for message in (
        st.session_state[
            "zaki_messages"
        ]
    ):
        avatar = (
            "✨"
            if message[
                "role"
            ] == "assistant"
            else None
        )

        with st.chat_message(
            message[
                "role"
            ],

            avatar=(
                avatar
            ),
        ):
            st.markdown(
                message[
                    "content"
                ]
            )

    typed = (
        st.chat_input(
            (
                "Ask Zaki about "
                "your documents..."
            )
        )
    )

    question = (
        selected_example
        if selected_example
        else typed
    )

    if question:
        st.session_state[
            "zaki_messages"
        ].append(
            {
                "role":
                    "user",

                "content":
                    question,
            }
        )

        with st.chat_message(
            "user"
        ):
            st.markdown(
                question
            )

        with st.chat_message(
            "assistant",
            avatar="✨",
        ):
            with st.spinner(
                (
                    "Checking your "
                    "documents..."
                )
            ):
                try:
                    result = (
                        run_zaki(
                            question
                        )
                    )

                    answer = (
                        result.get(
                            "answer"
                        )
                        or (
                            "I couldn't "
                            "find an answer."
                        )
                    )

                    st.markdown(
                        answer
                    )

                except Exception:
                    answer = (
                        "I couldn't complete "
                        "that request. "
                        "Please try again."
                    )

                    st.error(
                        answer
                    )

        st.session_state[
            "zaki_messages"
        ].append(
            {
                "role":
                    "assistant",

                "content":
                    answer,
            }
        )

    if (
        len(
            st.session_state[
                "zaki_messages"
            ]
        )
        > 1
    ):
        if st.button(
            "Clear conversation"
        ):
            st.session_state[
                "zaki_messages"
            ] = [
                {
                    "role":
                        "assistant",

                    "content": (
                        "Hi, I'm Zaki. "
                        "Ask me anything "
                        "about your saved "
                        "documents."
                    ),
                }
            ]

            st.rerun()


# ---------------------------------------------------------
# RUN APP
# ---------------------------------------------------------

initialize_state()

show_sidebar()


page = (
    st.session_state[
        "page"
    ]
)


if page == "Home":
    home_page()

elif page == "Review":
    review_page()

elif page == "Documents":
    documents_page()

elif page == "Zaki":
    zaki_page()