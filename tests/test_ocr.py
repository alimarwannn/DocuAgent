from src.ocr import extract_text
from src.ocr import correct_rotation
import cv2
from src.ocr import extract_text, correct_rotation, reader


result = extract_text("samples/receipt_1.jpg")
result_2 = extract_text("samples/receipt_2.jpg")

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

print("receipt 2 avergae confidence:", result_2["average_confidence"])
print("receipt 2 detected lines", result_2["line_count"])
print("\n receipt 2 raw text:")
print(result_2["raw_text"]
      )

result_rotated = extract_text("samples/receipt_rotated.jpg")

assert result is not None, "OCR returned None for a valid image"
assert result["line_count"] > 0
assert "average_confidence" in result

#print("Rotated receipt average confidence:", result_rotated["average_confidence"])
#print("Rotated receipt detected lines:", result_rotated["line_count"])
print(result_rotated["raw_text"])

#rotated_image = cv2.imread("samples/receipt_rotated.jpg")
#corrected_image = correct_rotation(rotated_image)

#print("Orignal rotated shape:", rotated_image.shape)
#print("Corrected shape:", corrected_image.shape)

#corrected_detections = reader.readtext(corrected_image)

#correction_confidences = [
#    detection[2] for detection in corrected_detections
#]

#corrected_average_confidence = (
#    sum(correction_confidences) / len(correction_confidences)
#    if correction_confidences
#    else 0.0
#)

#print("Corrected detection count:", len(corrected_detections))
#print("Corrected average confidence:", corrected_average_confidence)
