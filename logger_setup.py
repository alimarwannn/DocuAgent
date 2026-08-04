import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('docuagent')

logger.info("API key loaded successfully.")
logger.info("Groq request sent successfully.")
logger.error("Test error occurred.")