import os
from dotenv import load_dotenv

load_dotenv('.env')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in the .env file.")