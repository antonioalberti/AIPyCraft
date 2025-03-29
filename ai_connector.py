import os
import openai
from dotenv import load_dotenv

class AIConnector:
    def __init__(self):
        load_dotenv()  # Load environment variables from the .env file

        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found in 'OPENAI_API_KEY' environment variable.")

    def send_prompt(self, instructions: str, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",            # The underlying model
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,    # Adjust as needed
                max_tokens=8192,  # Adjust as needed
                n=1
            )

            answer = response.choices[0].message["content"]
            return answer.strip()

        except openai.OpenAIError as e:
            raise RuntimeError(f"OpenAI error: {e}") from e