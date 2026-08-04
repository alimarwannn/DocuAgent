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

    try:
        reader = easyocr.Reader(["en"])
        ocr_results = reader.readtext(gray_image)
        logger.info("OCR completed successfully.")

    except Exception as error:
        logger.error(f"OCR failed: {error}")
        return None

    text_lines = []
    for result in ocr_results:
        bounding_box, text, confidence = result
        text_lines.append(text)
    raw_text = "\n".join(text_lines)

    confidence_scores = []
    high_confidence_lines = []

    minimum_confidence = 0.50

    for detection in ocr_results:
        confidence = detection[2]
        confidence_scores.append(confidence)
        if confidence >= minimum_confidence:
            high_confidence_lines.append(detection[1])    
    high_confidence_text = "\n".join(high_confidence_lines)

    if confidence_scores:
        average_confidence = sum(confidence_scores) / len(confidence_scores)
    else:
        average_confidence = 0.0

    ocr_output = {
        "raw_text": raw_text,
        "detections": ocr_results,
        "line_count": len(text_lines),
        "image_path": image_path,
        "average_confidence": average_confidence,
        "high_confidence_text": high_confidence_text
    }


    



    return ocr_output

