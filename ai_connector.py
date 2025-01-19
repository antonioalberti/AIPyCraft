import openai
import os
from dotenv import load_dotenv

class AIConnector:
    def __init__(self):
        load_dotenv()  # Loads environment variables from the .env file
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Sets the OpenAI API key

        if not openai.api_key:
            raise ValueError("OpenAI API key not found in 'OPENAI_API_KEY' environment variable.")

    def send_prompt(self, instructions: str, assistant_pre_identifier: str, prompt: str) -> str:
        """
        Sends a chat request to the assistant identified by 'assistant_pre_identifier'
        using the standard ChatCompletion endpoint.

        Args:
            assistant_pre_identifier (str): The model name or ID you want to call (e.g. "gpt-3.5-turbo", "gpt-4").
            prompt (str): The user prompt or question.

        Returns:
            str: The assistant's response text.
        """

        try:
            # Make a single ChatCompletion call
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # e.g., "gpt-3.5-turbo" or "gpt-4"
                messages=[
                    {
                        "role": "system",
                        "content": instructions
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=1,   # Adjust to your preference
                max_tokens=1024,   # Adjust as needed
                n=1
            )

            # Extract the text from the assistant's reply
            answer = response.choices[0].message["content"]
            
            # (Optional) Print which model was used
            print(f"[INFO] The API call used the model/assistant: '{assistant_pre_identifier}'")

            return answer.strip()

        except openai.error.AuthenticationError as e:
            raise RuntimeError(f"Authentication error: {e}") from e
        except openai.error.OpenAIError as e:
            raise RuntimeError(f"OpenAI error: {e}") from e
