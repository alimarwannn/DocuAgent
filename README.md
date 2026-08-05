# DocuAgent

DocuAgent is an agentic computer-vision document platform for invoices, receipts, and other business documents.

The user uploads a document and chooses either a full scan or a partial scan. The document is preprocessed using OpenCV, read using EasyOCR, converted into structured data, validated, stored, and made available for chat-based questions.

## Planned Workflow

Upload document  
→ Choose full or partial scan  
→ OpenCV preprocessing  
→ EasyOCR  
→ Structured extraction  
→ Validation  
→ SQLite storage  
→ Chat and tools  

## Current Features

- OpenCV image loading
- Invalid image handling
- Grayscale conversion
- Image resizing using cubic interpolation
- EasyOCR text extraction
- OCR confidence score collection
- Average confidence calculation
- High-confidence text filtering
- Structured OCR result dictionary
- Reusable OCR functions
- Logging for successful and failed operations
- Tests for valid and invalid image paths
- Groq API client configuration
- Environment-variable loading using `.env`

## Planned Features

- Full document scanning
- Partial scanning by natural-language request
- Quick scan with suggested fields
- Invoice and receipt structured schemas
- Field validation
- SQLite document storage
- Document retrieval
- Calculations across stored documents
- Contradiction detection
- LangGraph workflow orchestration
- Human review for uncertain results
- Streamlit user interface
- Chat after both full and partial scans

## Project Structure

```text
DocuAgent/
├── app.py
├── README.md
├── logger_setup.py
├── test_env.py
├── samples/
│   └── receipt_1.jpg
├── src/
│   ├── config.py
│   ├── groq_client.py
│   ├── logger.py
│   └── ocr.py
└── tests/
    ├── test_ocr.py
    └── test_packages.py
src/ contains the main project logic.
tests/ contains the project test modules.
samples/ contains example documents used for testing.
Installation
1. Clone the repository
git clone https://github.com/alimarwannn/DocuAgent.git
cd DocuAgent
2. Create a virtual environment
python -m venv .venv
3. Activate the environment in WSL Ubuntu
source .venv/bin/activate
4. Install the required packages
pip install -r requirements.txt
Environment Configuration

Create a .env file in the project root:

GROQ_API_KEY=your_api_key_here

The .env file must not be committed to GitHub.

Make sure .gitignore includes:

.env
.venv/
__pycache__/
*.pyc
Running the OCR Test

Run commands from the project root:

python -m tests.test_ocr

The test checks that:

A valid receipt image is loaded.
OCR returns detected text.
The result contains raw text and original detections.
Average OCR confidence is returned.
High-confidence text is returned.
A missing image path returns None.
Invalid input logs an error without crashing.
Current OCR Preprocessing

The current default preprocessing pipeline is:

Image loading
→ Grayscale conversion
→ Resize by 1.5 using cubic interpolation
→ EasyOCR

Current receipt test result:

Original image shape: (894, 463, 3)
Processed image shape: (1341, 694)
Detected lines: approximately 51
Average confidence: approximately 0.75

Grayscale and resizing currently perform better than the tested blur and adaptive-thresholding alternatives.

## Limitations
OCR accuracy depends on image quality, lighting, rotation, and document layout.
The current pipeline has been tested mainly on one receipt sample.
Some words and field names may be recognized incorrectly.
Structured invoice and receipt extraction is not yet implemented.
SQLite storage is not yet implemented.
Full scan, partial scan, chat, and LangGraph routing are not yet implemented.
EasyOCR currently runs on the CPU and may be slower than GPU execution.
Preprocessing that helps one document may reduce accuracy on another document.
Security
API keys must be stored only in the local .env file.
API keys must never be written directly inside Python files.
The .env file must remain excluded from Git.
No private document data or credentials should be committed to the repository.

## Rotation Test

A known upright receipt was rotated by 90 degrees to measure how orientation affects OCR.

Results:

- Upright receipt average confidence: `0.7999`
- Rotated receipt average confidence: `0.4053`
- Corrected receipt average confidence: `0.6829`

Rotation correction significantly improved OCR confidence and recovered important fields such as the receipt number, date, subtotal, tax, and total.

However, the corrected result did not fully match the original upright image quality.

Automatic orientation detection is not implemented yet, so rotation correction currently requires the correct direction to be known.

## Structured Scanning

DocuAgent supports invoice and receipt extraction through three scan modes.

### Full Scan

Extracts every supported field for the detected document type.

Invoice fields:

- supplier name
- invoice number
- date
- customer
- subtotal
- tax
- total
- currency

Receipt fields:

- merchant name
- receipt number
- date
- subtotal
- tax
- total
- payment method
- currency

### Partial Scan

Extracts only selected fields.

Users can provide:

- an explicit field list;
- a natural-language request, such as:
  `Extract the invoice number, total, and currency.`

Unsupported fields are ignored, and missing values remain `null`.

### Quick Scan

Checks the OCR text and suggests likely available fields before detailed extraction.

### Standard Result Structure

```json
{
  "document_type": "invoice",
  "scan_mode": "full",
  "fields": {
    "supplier_name": "Vodafone Egypt",
    "invoice_number": "INV-123",
    "date": "2026-08-05",
    "customer": null,
    "subtotal": 1000,
    "tax": 140,
    "total": 1140,
    "currency": "EGP"
  }
}