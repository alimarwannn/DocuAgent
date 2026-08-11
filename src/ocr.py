from functools import lru_cache
from pathlib import Path

import cv2
import easyocr

from src.logger import logger


@lru_cache(maxsize=1)
def get_ocr_reader():
    logger.info(
        "Loading EasyOCR model."
    )

    return easyocr.Reader(
        ["en"],
        gpu=False,
        verbose=False,
    )


class LazyOCRReader:
    def readtext(self, *args, **kwargs):
        return get_ocr_reader().readtext(
            *args,
            **kwargs,
        )


reader = LazyOCRReader()


def correct_rotation(image):
    return cv2.rotate(
        image,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
    )


def preprocess_image(image):
    gray_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    height, width = (
        gray_image.shape[:2]
    )

    shortest_side = min(
        height,
        width,
    )

    if shortest_side < 1000:
        gray_image = cv2.resize(
            gray_image,
            None,
            fx=1.5,
            fy=1.5,
            interpolation=cv2.INTER_CUBIC,
        )

    return gray_image


@lru_cache(maxsize=32)
def _extract_text_cached(
    image_path,
    modified_time,
):
    image = cv2.imread(
        image_path
    )

    if image is None:
        logger.error(
            "The image could not be loaded."
        )

        return None

    logger.info(
        "Image loaded successfully."
    )

    processed_image = preprocess_image(
        image
    )

    try:
        ocr_results = reader.readtext(
            processed_image,
            detail=1,
            paragraph=False,
        )

        logger.info(
            "OCR completed successfully."
        )

    except Exception as error:
        logger.error(
            f"OCR failed: {error}"
        )

        return None

    text_lines = [
        detection[1]
        for detection in ocr_results
    ]

    raw_text = "\n".join(
        text_lines
    )

    confidence_scores = [
        detection[2]
        for detection in ocr_results
    ]

    minimum_confidence = 0.50

    high_confidence_lines = [
        detection[1]
        for detection in ocr_results
        if detection[2]
        >= minimum_confidence
    ]

    high_confidence_text = "\n".join(
        high_confidence_lines
    )

    if confidence_scores:
        average_confidence = (
            sum(confidence_scores)
            / len(confidence_scores)
        )
    else:
        average_confidence = 0.0

    return {
        "raw_text": raw_text,
        "detections": ocr_results,
        "line_count": len(text_lines),
        "image_path": image_path,
        "average_confidence": average_confidence,
        "high_confidence_text": high_confidence_text,
    }


def extract_text(image_path):
    path = Path(
        image_path
    )

    if not path.exists():
        logger.error(
            "The image path does not exist."
        )

        return None

    try:
        modified_time = (
            path.stat().st_mtime_ns
        )

    except OSError as error:
        logger.error(
            f"Could not inspect image: {error}"
        )

        return None

    return _extract_text_cached(
        str(path),
        modified_time,
    )