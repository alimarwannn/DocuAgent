import cv2
from src.logger import logger
import easyocr

def extract_text(image_path):
    
    image = cv2.imread(image_path)

    if image is None: 
        logger.error("The image could not be loaded.")
        return None

    logger.info("Image loaded successfully.")
    print(image.shape)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(gray_image.shape)
    logger.info("Grayscale conversion succeeded.")

    reader = easyocr.Reader(["en"])
    ocr_results = reader.readtext(gray_image)

    text_lines = []
    for result in ocr_results:
        bounding_box, text, confidence = result
        text_lines.append(text)
    raw_text = "\n".join(text_lines)



    ocr_output = {
        "raw_text": raw_text,
        "detections": ocr_results,
        "line_count": len(text_lines)
    }

    print("Detected lines:", ocr_output["line_count"])
    print("\nRaw text:")
    print(ocr_output["raw_text"])



    return ocr_output

