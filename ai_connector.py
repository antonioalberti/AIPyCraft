import openai
from dotenv import load_dotenv
import os

class AIConnector:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Get the API key from the environment variable

    def send_prompt(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code assistant that  will help a user to create a solution for a problem via sucessfull interaction via a chatbot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        return response.choices[0].message['content'].strip()



