def ask_groq(prompt):
    from src.config import GROQ_API_KEY
    from src.logger import logger
    import groq
    import time

    groq_client = groq.Client(api_key=GROQ_API_KEY)
    max_attempts = 3

    user_message = {
        "role": "user",
        "content": prompt
    }

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Attempt {attempt}: Sending request to Groq API...")

            response = groq_client.chat.completions.create(
                messages=[user_message],
                #model="invalid-model",
                model="llama-3.1-8b-instant",
                max_tokens=200,
            )            
            logger.info("Received response from Groq API.")
            return response.choices[0].message.content                      
        except Exception as error: 
            logger.error(f"Attempt {attempt}: An error occurred while sending the request to Groq API: {error}")
            
            if attempt < max_attempts:
                logger.info("Waiting 2 seconds before retrying...")
                time.sleep(2)                
            else:
                logger.error("All Groq requests failed.")
                raise RuntimeError("All Groq request attempts failed.")