from src.ocr import extract_text


result = extract_text("samples/receipt_1.jpg")
print("Average confidence:", result["average_confidence"])
if result is not None:
    print("Detected lines:", result["line_count"])
    print("\nRaw text:")
    print(result["raw_text"])

