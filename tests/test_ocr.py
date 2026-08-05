from src.ocr import extract_text



result = extract_text("samples/receipt_1.jpg")

assert result is not None, "OCR returned None for a valid image"
assert "raw_text" in result
assert result["line_count"] > 0
assert "detections" in result
assert "average_confidence" in result
assert "high_confidence_text" in result


invalid_result = extract_text("src/bolbol.png")

assert invalid_result is None

print("Average confidence:", result["average_confidence"])
print("\nHigh-confidence text:")
print(result["high_confidence_text"])
if result is not None:
    print("Detected lines:", result["line_count"])
    print("\nRaw text:")
    print(result["raw_text"])

