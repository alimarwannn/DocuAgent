import cv2
from src.logger import logger
import easyocr


reciept_path = r"samples/receipt_1.jpg"

image = cv2.imread(reciept_path)

if image is None: 
    logger.error("The image could not be loaded.")
else:
    logger.info("Image loaded successfully.")
    print(image.shape)

gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print(gray_image.shape)
logger.info("Grayscale conversion succeeded.")

reader = easyocr.Reader(["en"])
ocr_results = reader.readtext(gray_image)
print(ocr_results)

text_lines = []
for result in ocr_results:
    bounding_box, text, confidence = result
    text_lines.append(text)
raw_text = "\n".join(text_lines)
print(raw_text)


ocr_output = {
    "raw_text": raw_text,
    "detections": ocr_results,
    "line_count": len(text_lines)
}

print("Detected lines:", ocr_output["line_count"])
print("\nRaw text:")
print(ocr_output["raw_text"])



