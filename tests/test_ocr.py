from src.ocr import extract_text


result = extract_text("samples/receipt_1.jpg")
print("Average confidence:", result["average_confidence"])
print("\nHigh-confidence text:")
print(result["high_confidence_text"])
if result is not None:
    print("Detected lines:", result["line_count"])
    print("\nRaw text:")
    print(result["raw_text"])

