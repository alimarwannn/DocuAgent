import html
import json
from pathlib import Path

import streamlit as st

from src.database import (
    create_tables,
    get_document_fields,
    get_document_issues,
    list_documents,
)
from src.graph import build_document_graph
from src.zaki_graph import run_zaki


st.set_page_config(
    page_title="DocuAgent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.html(
    """
    <style>
    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: transparent;
        height: 0;
    }

    .stApp {
        background: #f6f7f9;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 0.8rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background: #111318;
        border-right: 1px solid #202329;
    }

    [data-testid="stSidebar"] * {
        color: #f5f5f5;
    }

    h1, h2, h3 {
        letter-spacing: -0.025em;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    .brand-mark {
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
        box-shadow: 0 7px 20px rgba(230, 0, 0, 0.18);
    }

    .brand-name {
        color: #17191d;
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1;
    }

    .brand-tagline {
        color: #777d87;
        font-size: 0.82rem;
        margin-top: 4px;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #17191f 0%,
            #252932 100%
        );
        border-radius: 21px;
        padding: 24px 32px;
        margin: 0 0 15px 0;
        color: white;
        box-shadow: 0 12px 32px rgba(22, 24, 29, 0.09);
    }

    .hero-eyebrow {
        color: #ff6464;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        font-size: 0.68rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-title {
        color: white;
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .hero-copy {
        color: #c9cdd5;
        max-width: 780px;
        font-size: 0.91rem;
        line-height: 1.5;
    }

    .panel {
        background: white;
        border: 1px solid #e7e9ed;
        border-radius: 17px;
        padding: 16px 20px;
        box-shadow: 0 3px 14px rgba(20, 24, 32, 0.03);
        margin-bottom: 12px;
    }

    .panel-title {
        color: #15171b;
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 3px;
    }

    .panel-copy {
        color: #737985;
        font-size: 0.84rem;
        line-height: 1.45;
    }

    .metric-card {
        background: white;
        border: 1px solid #e7e9ed;
        border-radius: 17px;
        padding: 18px 20px;
        min-height: 105px;
        box-shadow: 0 3px 15px rgba(20, 24, 32, 0.035);
    }

    .metric-label {
        color: #838994;
        text-transform: uppercase;
        font-size: 0.71rem;
        letter-spacing: 0.07em;
        font-weight: 750;
    }

    .metric-value {
        color: #17191d;
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 8px;
    }

    .field-card {
        background: #fafafa;
        border: 1px solid #ebecef;
        border-radius: 14px;
        padding: 15px 16px;
        margin-bottom: 11px;
        min-height: 82px;
    }

    .field-label {
        color: #828893;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 750;
    }

    .field-value {
        color: #17191d;
        font-size: 1rem;
        font-weight: 650;
        margin-top: 7px;
        word-break: break-word;
    }

    .success-box {
        background: #effbf4;
        border: 1px solid #b7e7c9;
        color: #126b40;
        border-radius: 13px;
        padding: 13px 15px;
        font-weight: 650;
    }

    .warning-box {
        background: #fff9eb;
        border: 1px solid #f4d68e;
        color: #8c5a07;
        border-radius: 13px;
        padding: 13px 15px;
        font-weight: 650;
    }

    .error-box {
        background: #fff2f1;
        border: 1px solid #f1bbb6;
        color: #a92b22;
        border-radius: 13px;
        padding: 13px 15px;
        font-weight: 650;
    }

    .issue-error {
        background: #fff6f5;
        border-left: 4px solid #d92d20;
        padding: 13px 15px;
        border-radius: 9px;
        margin-bottom: 10px;
        color: #5c1d18;
    }

    .issue-warning {
        background: #fff9ec;
        border-left: 4px solid #f79009;
        padding: 13px 15px;
        border-radius: 9px;
        margin-bottom: 10px;
        color: #67430b;
    }

    .zaki-card {
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #fff5f5 100%
        );
        border: 1px solid #efdada;
        border-radius: 21px;
        padding: 24px 26px;
        margin-bottom: 18px;
    }

    .zaki-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #15171b;
    }

    .zaki-copy {
        color: #6e7480;
        margin-top: 6px;
        line-height: 1.5;
    }

    .empty-preview {
        height: 265px;
        border: 1.5px dashed #d5d9df;
        border-radius: 17px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        color: #949aa5;
        text-align: center;
        padding: 30px;
    }

    .empty-preview-icon {
        font-size: 1.7rem;
        margin-bottom: 8px;
    }

    .sidebar-brand {
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .sidebar-copy {
        color: #9399a4 !important;
        font-size: 0.82rem;
        line-height: 1.5;
        margin-bottom: 26px;
    }

    .sidebar-section-label {
        color: #8b919b !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.68rem;
        font-weight: 700;
        margin-bottom: 11px;
    }

    .sidebar-card {
        background: #1b1e24;
        border: 1px solid #292d35;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .sidebar-card-label {
        color: #9197a2 !important;
        font-size: 0.74rem;
    }

    .sidebar-card-value {
        color: white !important;
        font-size: 1.6rem;
        font-weight: 750;
        margin-top: 3px;
    }

    .sidebar-tip {
        color: #a9aeb7 !important;
        line-height: 1.55;
        font-size: 0.8rem;
    }

    div[data-testid="stFileUploader"] {
        background: white;
        border-radius: 14px;
    }

    [data-testid="stFileUploaderDropzone"] {
        padding-top: 0.55rem !important;
        padding-bottom: 0.55rem !important;
    }

    div[data-testid="stRadio"] {
        margin-top: -4px;
    }

    button[kind="primary"] {
        background: #e60000 !important;
        border-color: #e60000 !important;
        color: white !important;
    }

    button[kind="primary"]:hover {
        background: #c90000 !important;
        border-color: #c90000 !important;
        color: white !important;
    }

    button[kind="primary"]:disabled {
        background: #e5e7eb !important;
        border-color: #e5e7eb !important;
        color: #9ca3af !important;
        opacity: 1 !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 40px;
    }

    div[data-baseweb="tab-list"] {
        gap: 18px;
        border-bottom: 1px solid #e1e3e7;
    }

    button[data-baseweb="tab"] {
        font-weight: 650;
        padding-top: 7px;
        padding-bottom: 7px;
        padding-left: 4px;
        padding-right: 4px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 17px;
    }
    </style>
    """
)


create_tables()


@st.cache_resource
def get_document_graph():
    return build_document_graph()


def ui(content):
    st.html(content)


def safe(value):
    if value in (None, ""):
        return "Not found"

    return html.escape(str(value))


def initialize_session_state():
    defaults = {
        "scan_output": None,
        "last_uploaded_name": None,
        "zaki_messages": [
            {
                "role": "assistant",
                "content": (
                    "Hi, I'm Zaki. Ask me anything "
                    "about your saved documents."
                ),
            }
        ],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_uploaded_file(uploaded_file):
    upload_directory = Path("data/uploads")

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = Path(uploaded_file.name).name
    file_path = upload_directory / safe_name

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(file_path)


def get_document_display_name(document, fields):
    document_type = str(
        document.get(
            "document_type",
            "document",
        )
    ).title()

    party = (
        fields.get("supplier_name")
        or fields.get("merchant_name")
    )

    number = (
        fields.get("invoice_number")
        or fields.get("receipt_number")
    )

    if party and number:
        return f"{party} · {number}"

    if number:
        return f"{document_type} · {number}"

    if party:
        return f"{party} · {document_type}"

    return f"{document_type} #{document['id']}"


def display_field_cards(fields):
    if not fields:
        st.info("No information was found.")
        return

    items = list(fields.items())

    for index in range(
        0,
        len(items),
        3,
    ):
        columns = st.columns(3)

        for column, item in zip(
            columns,
            items[index:index + 3],
        ):
            field_name, field_value = item

            label = (
                field_name
                .replace("_", " ")
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
                            {safe(field_value)}
                        </div>
                    </div>
                    """
                )


def display_validation_issues(issues):
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

        message = issue.get(
            "message",
            "This document may need attention.",
        )

        if severity == "error":
            css_class = "issue-error"
            title = "Needs attention"
        else:
            css_class = "issue-warning"
            title = "Check recommended"

        ui(
            f"""
            <div class="{css_class}">
                <strong>{title}</strong><br>
                {safe(message)}
            </div>
            """
        )


def show_sidebar():
    with st.sidebar:
        ui(
            """
            <div class="sidebar-brand">
                ◈ DocuAgent
            </div>

            <div class="sidebar-copy">
                Your smart workspace for invoices
                and receipts.
            </div>
            """
        )

        documents = list_documents()

        invoice_count = sum(
            1
            for document in documents
            if document.get("document_type")
            == "invoice"
        )

        receipt_count = sum(
            1
            for document in documents
            if document.get("document_type")
            == "receipt"
        )

        ui(
            """
            <div class="sidebar-section-label">
                Your library
            </div>
            """
        )

        ui(
            f"""
            <div class="sidebar-card">
                <div class="sidebar-card-label">
                    Total documents
                </div>

                <div class="sidebar-card-value">
                    {len(documents)}
                </div>
            </div>
            """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Invoices",
                invoice_count,
            )

        with col2:
            st.metric(
                "Receipts",
                receipt_count,
            )

        st.write("")

        ui(
            """
            <div class="sidebar-section-label">
                Zaki
            </div>

            <div class="sidebar-card">
                <div class="sidebar-tip">
                    Ask questions like:<br><br>
                    “How much did I spend?”<br>
                    “Do I have duplicates?”<br>
                    “Which supplier appears most?”
                </div>
            </div>
            """
        )


def scan_tab():
    ui(
        """
        <div class="panel">
            <div class="panel-title">
                Upload a document
            </div>

            <div class="panel-copy">
                Add an invoice or receipt and choose
                what you want DocuAgent to find.
            </div>
        </div>
        """
    )

    left, right = st.columns(
        [1, 0.9],
        gap="large",
    )

    with left:
        uploaded_file = st.file_uploader(
            "Choose invoice or receipt",
            type=[
                "png",
                "jpg",
                "jpeg",
            ],
        )

        scan_choice = st.radio(
            "What would you like to do?",
            [
                "Extract everything",
                "Choose specific details",
                "Preview available details",
            ],
            horizontal=True,
        )

        choice_map = {
            "Extract everything": "full",
            "Choose specific details": "partial",
            "Preview available details": "quick",
        }

        scan_mode = choice_map[
            scan_choice
        ]

        user_request = ""

        if scan_mode == "full":
            st.caption(
                "Get a complete structured view "
                "of the document."
            )

        elif scan_mode == "partial":
            user_request = st.text_area(
                "What information do you need?",
                placeholder=(
                    "Example: Supplier name, invoice "
                    "number, total and currency"
                ),
                height=78,
            )

        else:
            st.caption(
                "See which useful details are available "
                "before extracting them."
            )

        can_process = (
            uploaded_file is not None
        )

        if (
            scan_mode == "partial"
            and not user_request.strip()
        ):
            can_process = False

        process = st.button(
            "Process document",
            type="primary",
            use_container_width=True,
            disabled=not can_process,
        )

    with right:
        if uploaded_file is not None:
            st.image(
                uploaded_file,
                use_container_width=True,
            )

            st.caption(
                uploaded_file.name
            )

        else:
            ui(
                """
                <div class="empty-preview">
                    <div>
                        <div class="empty-preview-icon">
                            ◫
                        </div>

                        Your document preview will
                        appear here
                    </div>
                </div>
                """
            )

    if process:
        image_path = save_uploaded_file(
            uploaded_file
        )

        state = {
            "image_path": image_path,
            "scan_mode": scan_mode,
            "error": None,
        }

        if scan_mode == "partial":
            state["user_request"] = (
                user_request.strip()
            )

        graph = get_document_graph()

        with st.spinner(
            "Reading your document..."
        ):
            try:
                result = graph.invoke(
                    state
                )

                st.session_state.scan_output = (
                    result
                )

                st.session_state.last_uploaded_name = (
                    uploaded_file.name
                )

                if result.get("error"):
                    st.error(
                        "We couldn't process this "
                        "document. Please try again."
                    )

                elif result.get(
                    "needs_human_review"
                ):
                    st.warning(
                        "Document processed. "
                        "Some details need checking."
                    )

                else:
                    st.success(
                        "Document processed successfully."
                    )

            except Exception:
                st.session_state.scan_output = {
                    "error": (
                        "We couldn't process this document."
                    )
                }

                st.error(
                    "Something went wrong while "
                    "processing the document."
                )


def results_tab():
    result = st.session_state.scan_output

    if result is None:
        ui(
            """
            <div class="panel">
                <div class="panel-title">
                    Your results will appear here
                </div>

                <div class="panel-copy">
                    Upload and process a document first.
                </div>
            </div>
            """
        )
        return

    if result.get("error"):
        ui(
            """
            <div class="error-box">
                We couldn't complete this document.
                Try uploading it again or use a clearer image.
            </div>
            """
        )
        return

    scan_result = result.get(
        "scan_result",
        {},
    )

    document_type = result.get(
        "document_type",
        scan_result.get(
            "document_type",
            "Document",
        ),
    )

    scan_mode = result.get(
        "scan_mode",
        scan_result.get(
            "scan_mode",
            "",
        ),
    )

    document_id = result.get(
        "document_id"
    )

    needs_review = result.get(
        "needs_human_review",
        False,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        ui(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    Document
                </div>

                <div class="metric-value">
                    {safe(str(document_type).title())}
                </div>
            </div>
            """
        )

    with col2:
        if scan_mode == "quick":
            status = "Preview ready"
        elif needs_review:
            status = "Check required"
        else:
            status = "Ready"

        ui(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    Status
                </div>

                <div class="metric-value">
                    {safe(status)}
                </div>
            </div>
            """
        )

    with col3:
        if document_id is not None:
            display_id = f"#{document_id}"
        elif scan_mode == "quick":
            display_id = "Preview"
        else:
            display_id = "Not saved"

        ui(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    Reference
                </div>

                <div class="metric-value">
                    {safe(display_id)}
                </div>
            </div>
            """
        )

    st.write("")

    if needs_review:
        ui(
            """
            <div class="warning-box">
                Some details need your attention before
                relying on this document.
            </div>
            """
        )

    elif scan_mode == "quick":
        ui(
            """
            <div class="success-box">
                ✓ Preview completed
            </div>
            """
        )

    else:
        ui(
            """
            <div class="success-box">
                ✓ Your document is ready
            </div>
            """
        )

    st.write("")

    fields = scan_result.get(
        "fields",
        {},
    )

    if fields:
        st.subheader(
            "Document details"
        )

        display_field_cards(
            fields
        )

    suggested_fields = (
        scan_result.get(
            "suggested_fields"
        )
        or scan_result.get(
            "available_fields"
        )
    )

    if suggested_fields:
        st.subheader(
            "Available details"
        )

        if isinstance(
            suggested_fields,
            dict,
        ):
            display_field_cards(
                suggested_fields
            )

        elif isinstance(
            suggested_fields,
            list,
        ):
            for field in suggested_fields:
                st.write(
                    f"✓ {str(field).replace('_', ' ').title()}"
                )

        else:
            st.write(
                suggested_fields
            )

    issues = result.get(
        "validation_issues",
        [],
    )

    if scan_mode != "quick":
        st.subheader(
            "Checks"
        )

        display_validation_issues(
            issues
        )

    payload = {
        "document_type": document_type,
        "fields": fields,
        "checks": issues,
    }

    st.download_button(
        "Download document data",
        data=json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        file_name="document_data.json",
        mime="application/json",
    )


def library_tab():
    ui(
        """
        <div class="panel">
            <div class="panel-title">
                Your documents
            </div>

            <div class="panel-copy">
                Browse and review documents you've
                already processed.
            </div>
        </div>
        """
    )

    documents = list_documents()

    if not documents:
        st.info(
            "Your document library is empty."
        )
        return

    document_records = []

    for document in documents:
        fields = get_document_fields(
            document["id"]
        )

        issues = get_document_issues(
            document["id"]
        )

        document_records.append(
            {
                "document": document,
                "fields": fields,
                "issues": issues,
            }
        )

    search_query = st.text_input(
        "Search",
        placeholder=(
            "Search supplier, document number, "
            "date, type or reference"
        ),
    )

    if search_query.strip():
        query = (
            search_query
            .strip()
            .lower()
        )

        filtered_records = []

        for record in document_records:
            document = record["document"]
            fields = record["fields"]

            searchable_values = [
                document.get("id"),
                document.get(
                    "document_type"
                ),
                fields.get(
                    "supplier_name"
                ),
                fields.get(
                    "merchant_name"
                ),
                fields.get(
                    "invoice_number"
                ),
                fields.get(
                    "receipt_number"
                ),
                fields.get("date"),
                fields.get("currency"),
            ]

            searchable_text = " ".join(
                str(value)
                for value in searchable_values
                if value not in (None, "")
            ).lower()

            if query in searchable_text:
                filtered_records.append(
                    record
                )

    else:
        filtered_records = (
            document_records
        )

    st.caption(
        f"{len(filtered_records)} documents"
    )

    for record in filtered_records:
        document = record["document"]
        fields = record["fields"]
        issues = record["issues"]

        document_id = document["id"]

        display_name = (
            get_document_display_name(
                document,
                fields,
            )
        )

        with st.expander(
            display_name
        ):
            top1, top2, top3 = (
                st.columns(3)
            )

            with top1:
                st.caption(
                    "Reference"
                )

                st.write(
                    f"#{document_id}"
                )

            with top2:
                st.caption(
                    "Type"
                )

                st.write(
                    str(
                        document.get(
                            "document_type",
                            "Document",
                        )
                    ).title()
                )

            with top3:
                st.caption(
                    "Added"
                )

                st.write(
                    document.get(
                        "created_at",
                        "Unknown",
                    )
                )

            st.markdown(
                "#### Details"
            )

            display_field_cards(
                fields
            )

            st.markdown(
                "#### Checks"
            )

            display_validation_issues(
                issues
            )

            payload = {
                "reference": document_id,
                "type": document.get(
                    "document_type"
                ),
                "fields": fields,
                "checks": issues,
            }

            st.download_button(
                "Download data",
                data=json.dumps(
                    payload,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                ),
                file_name=(
                    f"document_{document_id}.json"
                ),
                mime="application/json",
                key=(
                    f"download_{document_id}"
                ),
            )


def zaki_tab():
    ui(
        """
        <div class="zaki-card">
            <div class="zaki-title">
                ✦ Meet Zaki
            </div>

            <div class="zaki-copy">
                Ask questions about your saved invoices
                and receipts in plain language.
            </div>
        </div>
        """
    )

    st.markdown(
        "##### Suggestions"
    )

    examples = [
        "How much did I spend?",
        "What was my total tax?",
        "Which supplier appears most often?",
        "Do I have duplicate invoices?",
    ]

    columns = st.columns(4)

    selected_example = None

    for column, example in zip(
        columns,
        examples,
    ):
        with column:
            if st.button(
                example,
                key=(
                    f"example_{example}"
                ),
                use_container_width=True,
            ):
                selected_example = (
                    example
                )

    for message in (
        st.session_state.zaki_messages
    ):
        avatar = (
            "✨"
            if message["role"]
            == "assistant"
            else None
        )

        with st.chat_message(
            message["role"],
            avatar=avatar,
        ):
            st.markdown(
                message["content"]
            )

    typed_question = st.chat_input(
        "Ask Zaki about your documents..."
    )

    question = (
        selected_example
        if selected_example
        else typed_question
    )

    if question:
        st.session_state.zaki_messages.append(
            {
                "role": "user",
                "content": question,
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
                "Zaki is checking your documents..."
            ):
                try:
                    result = run_zaki(
                        question
                    )

                    answer = result.get(
                        "answer",
                        (
                            "I couldn't find an answer "
                            "for that question."
                        ),
                    )

                    st.markdown(
                        answer
                    )

                except Exception:
                    answer = (
                        "I couldn't complete that request. "
                        "Please try again."
                    )

                    st.error(
                        answer
                    )

        st.session_state.zaki_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    if len(
        st.session_state.zaki_messages
    ) > 1:
        if st.button(
            "Clear conversation"
        ):
            st.session_state.zaki_messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Hi, I'm Zaki. Ask me anything "
                        "about your saved documents."
                    ),
                }
            ]

            st.rerun()


initialize_session_state()
show_sidebar()


ui(
    """
    <div class="brand">
        <div class="brand-mark">
            D
        </div>

        <div>
            <div class="brand-name">
                DocuAgent
            </div>

            <div class="brand-tagline">
                Smarter document management
            </div>
        </div>
    </div>
    """
)


ui(
    """
    <div class="hero">
        <div class="hero-eyebrow">
            Your document workspace
        </div>

        <div class="hero-title">
            Turn paperwork into answers.
        </div>

        <div class="hero-copy">
            Upload invoices and receipts, capture the
            information you need, keep everything organised,
            and ask Zaki questions across your documents.
        </div>
    </div>
    """
)


tab_upload, tab_results, tab_documents, tab_zaki = st.tabs(
    [
        "Upload",
        "Results",
        "Documents",
        "✦ Ask Zaki",
    ]
)


with tab_upload:
    scan_tab()


with tab_results:
    results_tab()


with tab_documents:
    library_tab()


with tab_zaki:
    zaki_tab()