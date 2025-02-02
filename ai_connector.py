import os
import openai
from dotenv import load_dotenv

# Import exceptions directly from openai
from openai import OpenAIError, AuthenticationError

class AIConnector:
    def __init__(self):
        load_dotenv()  # Loads environment variables from the .env file

        # Set the OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found in 'OPENAI_API_KEY' environment variable.")
        
        # Set the API base URL.
        # For standard OpenAI models, this is "https://api.openai.com/v1".
        # If your custom assistant uses a nonstandard endpoint, set OPENAI_API_BASE in your .env file.
        openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
    def send_prompt(self, instructions: str, assistant_pre_identifier: str, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=assistant_pre_identifier,  # e.g., "asst_6NQycWIDfMqhXtZBC0JAfpWT"
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,     # Adjust as needed
                max_tokens=8192,   # Adjust as needed (ensure it fits the model's limits)
                n=1
            )
            
            # Extract and return the assistant's reply text
            answer = response.choices[0].message["content"]
            print(f"[INFO] The API call used the model/assistant: '{assistant_pre_identifier}'")
            return answer.strip()
        
        except AuthenticationError as e:
            raise RuntimeError(f"Authentication error: {e}") from e
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI error: {e}") from e

# Example usage:
if __name__ == "__main__":
    connector = AIConnector()
    instructions = "You are a helpful assistant."
    assistant_id = "asst_6NQycWIDfMqhXtZBC0JAfpWT"
    prompt = "Plot a Mandelbrot fractal on the screen"
    
    try:
        result = connector.send_prompt(instructions, assistant_id, prompt)
        print("Result:", result)
    except RuntimeError as err:
        print(err)