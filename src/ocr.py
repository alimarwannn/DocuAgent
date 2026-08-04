import cv2
from src.logger import logger
import easyocr

easyocr.Reader(["en"])
reader.readtext(gray_image)




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