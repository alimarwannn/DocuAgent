# DocuAgent One-Page Presenter Sheet

### Slide 1

- Introduce yourself and DocuAgent.
- Say this was your Vodafone Egypt AI internship project.
- Say the goal: turn invoices and receipts from raw images into structured business data.
- Say the flow of the presentation: business problem, technical solution, then business value and internship learning.

### Slide 2

- Explain the problem with manual document processing.
- Mention delays, human errors, hard tracking, and weak reporting visibility.
- Say the issue is not just reading text from images.
- Say the real problem is building a trusted workflow around business documents.

### Slide 3

- Walk through the end-to-end flow.
- Upload document.
- OCR the document.
- Extract structured fields.
- Validate and normalize values.
- Approve or send for review if uncertain.
- Store in library.
- Use Zaki for business questions later.

### Slide 4

- Explain that the app is designed around user workflows, not only OCR.
- Mention the scan modes: full, partial, quick preview.
- Mention the review workflow: approved, pending, rejected.
- Mention the searchable document library.
- Mention that Zaki answers questions using approved data only.

### Slide 5

- Explain the technical architecture briefly.
- User layer: Streamlit interface.
- Document intelligence: OpenCV, EasyOCR, extraction, normalization, validation.
- Trust and persistence: SQLite, saved fields, approval and review states.
- Analytics and Q&A: Zaki, business tools, approved-only retrieval.
- Make the key point: AI helps with understanding, but deterministic logic handles validation, storage, and calculations.
- If you mention Zaki here, use tested questions only.

### Slide 5 Zaki Questions

- What is the total spending across approved documents?
- How many approved documents are in the library?
- Which documents need review?

## Demo

Say this before demo:

- "I have shown the business problem and technical design, so now I will show the app as a short business workflow. I will use prepared demo images so the demo is reliable and fast, while the real OCR pipeline is still available for normal documents."

### Before You Start The Demo

1. In terminal, go to the project folder: `cd /mnt/c/Users/Ali_m/OneDrive/Desktop/DocuAgent`
2. Activate the environment: `source .venv/bin/activate`
3. Reset the demo data: `python scripts/prepare_demo.py`
4. Start the app: `python -m streamlit run app.py`
5. In the browser, start from the Home page.
6. Use only the prepared upload image: `img/demo_approved.jpg`

### Exact Demo Flow

1. Show the Home page.
2. Say: "This is the main workspace where a user uploads a receipt or invoice."
3. Click the document uploader and choose `img/demo_approved.jpg`.
4. Keep scan mode as `Full Document`.
5. Click `Process document`.
6. Point out the progress/status feedback.
7. When the result appears, say: "The document was converted into structured fields and saved as an approved business record."
8. Scroll to the result section.
9. Click `Open saved document`.
10. In Documents, show the saved fields and the status card.
11. Say: "This is now searchable data, not just an image."
12. Click `Review (1)` in the sidebar.
13. Show the pending review receipt and the document preview on the right.
14. Say: "If the system is not confident, it does not blindly approve the document. It sends it to human review."
15. In the Currency field, type `EGP`.
16. Click `Approve changes`.
17. Say: "Now the reviewer fixed the missing value and approved the document."
18. Click `Ask Zaki` in the sidebar.
19. Ask: `What is the total spending across approved documents?`
20. If Zaki takes too long, say: "Zaki queries the approved document library. The key point is that questions are answered from saved approved data, not random text."

### What To Say During Demo

- "The user starts with a document image."
- "The app extracts structured business fields, not only raw OCR text."
- "Validation decides whether the document can be approved or needs review."
- "The review screen keeps humans in control when data is missing or uncertain."
- "The document library turns processed images into searchable business records."
- "Zaki adds a business layer by answering questions from approved saved data."

### Safe Demo Questions

- Main: `What is the total spending across approved documents?`
- Backup: `How many approved documents are in the library?`
- Backup: `Which documents need review?`

### Demo Timing

- Home upload and processing: about 30 seconds to 1 minute.
- Saved document and library: about 1 minute.
- Review workflow: about 1.5 minutes.
- Zaki question: about 30 seconds.
- Total demo target: 3 to 4 minutes.

### Backup If Anything Feels Slow

- Do not upload a random image during the presentation.
- Use only `img/demo_approved.jpg` for the upload demo.
- If Zaki is slow, explain the concept and move on to the final business value slide.
- If the app state looks changed, stop Streamlit, run `python scripts/prepare_demo.py`, and restart.

## Slide 6

- Return to business value after the demo.
- Faster handling: less manual reading and retyping.
- Better data quality: validation and review reduce bad outputs.
- Better visibility: saved records are easier to search and analyze.
- Mention next steps briefly: stronger document coverage and more pilot-ready workflow.

### Slide 7

- Close with what you learned and gained.
- Say you gained hands-on experience building a real product end to end.
- Say you learned how OCR, extraction, validation, storage, and analytics work together.
- Mention Vodafone summer materials: notebooks, datasets, exercises, presentations, and final project requirements.
- Say you also grew in Python, data work, ML workflows, and business communication.
- End with thanking Ayman and the team, then Q&A.

## Final Closing Line

- "Thank you, and I would be happy to take any questions."
