import os
import openai
import google.generativeai as genai
import anthropic
from dotenv import load_dotenv

class AIConnector:
    def __init__(self):
        load_dotenv()  # Load environment variables from the .env file

        # Configure OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            print("Warning: OpenAI API key not found in 'OPENAI_API_KEY' environment variable. OpenAI calls will fail.")
            # Decide if you want to raise an error or just warn:
            # raise ValueError("OpenAI API key not found in 'OPENAI_API_KEY' environment variable.")

        # Configure Gemini
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("Warning: Gemini API key not found in 'GEMINI_API_KEY' environment variable. Gemini calls will fail.")
            # Decide if you want to raise an error or just warn:
            # raise ValueError("Gemini API key not found in 'GEMINI_API_KEY' environment variable.")
        else:
            try:
                genai.configure(api_key=gemini_api_key)
                # Optional: Test connection or model availability here if needed
            except Exception as e:
                 print(f"Warning: Failed to configure Gemini API: {e}. Gemini calls may fail.")
                 # Decide if you want to raise an error or just warn:
                 # raise RuntimeError(f"Failed to configure Gemini API: {e}") from e

        # Configure Anthropic
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            print("Warning: Anthropic API key not found in 'ANTHROPIC_API_KEY' environment variable. Claude calls will fail.")
            self.anthropic_client = None
        else:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            except Exception as e:
                print(f"Warning: Failed to configure Anthropic API: {e}. Claude calls may fail.")
                self.anthropic_client = None


    def send_prompt_openai(self, instructions: str, prompt: str) -> str:
        if not openai.api_key:
             raise RuntimeError("OpenAI API key is not configured.")
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

    def send_prompt_gemini(self, instructions: str, prompt: str) -> str:
        """Sends a prompt to the Google Gemini API."""
        if not os.getenv("GEMINI_API_KEY"):
             raise RuntimeError("Gemini API key is not configured.")

        try:
            # Combine instructions and prompt. Gemini often works well with a single input.
            # You might adjust this based on how you structure prompts for Gemini.
            full_prompt = f"{instructions}\n\n{prompt}"

            # Select the Gemini model
            # Use 'gemini-1.5-pro-latest' or a specific version like 'gemini-1.5-pro-001'
            model = genai.GenerativeModel('gemini-1.5-pro-latest')

            # Generation configuration (optional, adjust as needed)
            generation_config = genai.types.GenerationConfig(
                # candidate_count=1, # Default is 1
                # stop_sequences=['...'],
                # max_output_tokens=8192, # Adjust based on model limits and needs
                temperature=1.0, # Adjust for creativity vs predictability
                # top_p=1.0,
                # top_k=1
            )

            # Safety settings (optional, adjust as needed)
            # See https://ai.google.dev/docs/safety_setting_gemini
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]

            response = model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
                # stream=False # Set to True for streaming responses
            )

            # Handle potential blocks or lack of content
            if not response.candidates:
                 # Check safety ratings if available
                 safety_feedback = getattr(response, 'prompt_feedback', None)
                 block_reason = getattr(safety_feedback, 'block_reason', 'Unknown')
                 raise RuntimeError(f"Gemini response blocked or empty. Reason: {block_reason}")

            # Accessing the text content
            # Gemini API might return multiple candidates, usually the first is the primary one.
            answer = response.text # Accessing .text directly is common for non-streaming
            return answer.strip()

        except Exception as e:
            # Catch specific Gemini exceptions if known, otherwise general Exception
            raise RuntimeError(f"Gemini API error: {e}") from e

    def _send_prompt_claude(self, instructions: str, prompt: str) -> str:
        """Internal method to send a prompt to the Anthropic Claude API."""
        if not self.anthropic_client:
             raise RuntimeError("Anthropic client is not configured.")

        try:
            # Claude uses a 'system' prompt and a list of 'messages'
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,  # Adjust as needed
                temperature=1.0, # Adjust as needed
                system=instructions,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            # Extract the text content from the response
            if message.content and isinstance(message.content, list) and hasattr(message.content[0], 'text'):
                 return message.content[0].text.strip()
            else:
                 # Handle cases where the response might be empty or structured differently
                 raise RuntimeError("Claude response format unexpected or empty.")

        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e
        except Exception as e:
            # Catch other potential exceptions
            raise RuntimeError(f"Error during Claude call: {e}") from e

    def send_prompt_ensemble(self, instructions: str, prompt: str) -> str:
        """
        Sends the prompt to OpenAI and Claude, then uses Gemini to evaluate
        and select/synthesize the best response.
        """
        response_openai = None
        response_claude = None # Renamed from response_gemini
        openai_error = None
        claude_error = None # Renamed from gemini_error

        # --- Call OpenAI ---
        if openai.api_key:
            try:
                print("Attempting OpenAI call...")
                response_openai = self.send_prompt_openai(instructions, prompt)
                print("OpenAI call successful.")
            except Exception as e:
                openai_error = e
                print(f"Warning: OpenAI call failed in ensemble: {e}")
        else:
            print("Warning: OpenAI API key not configured, skipping OpenAI call in ensemble.")
            openai_error = RuntimeError("OpenAI API key not configured.")

        # --- Call Claude --- Changed from Gemini
        if self.anthropic_client:
            try:
                print("Attempting Claude call...")
                response_claude = self._send_prompt_claude(instructions, prompt) # Use internal method
                print("Claude call successful.")
            except Exception as e:
                claude_error = e
                print(f"Warning: Claude call failed in ensemble: {e}")
        else:
            print("Warning: Anthropic client not configured, skipping Claude call in ensemble.")
            claude_error = RuntimeError("Anthropic client not configured.")

        # --- Handle API call failures --- Updated variable names
        if response_openai is None and response_claude is None:
            raise RuntimeError(f"Both OpenAI and Claude calls failed or were skipped. OpenAI Error: {openai_error}, Claude Error: {claude_error}")
        elif response_openai is None:
            print("Warning: OpenAI failed or skipped, returning Claude response directly.")
            # Ensure response_claude is not None before returning
            if response_claude is None:
                 raise RuntimeError(f"OpenAI failed/skipped, and Claude also failed. Claude Error: {claude_error}")
            # Wrap Claude's direct response for the parser if OpenAI failed
            clean_claude_response = response_claude.strip()
            return f"```\n{clean_claude_response}\n```"
        elif response_claude is None:
            print("Warning: Claude failed or skipped, returning OpenAI response directly.")
             # Ensure response_openai is not None before returning
            if response_openai is None:
                 raise RuntimeError(f"Claude failed/skipped, and OpenAI also failed. OpenAI Error: {openai_error}")
            # Wrap OpenAI's direct response for the parser if Claude failed
            clean_openai_response = response_openai.strip()
            return f"```\n{clean_openai_response}\n```"

        # --- If both succeeded, proceed to evaluation ---
        print("Both models succeeded, proceeding to Gemini evaluation.")
        evaluation_instructions = "You are an expert evaluator. Analyze the two provided responses based on the original instructions and prompt. Choose the best response OR synthesize a new, improved response that best fulfills the original request. Output ONLY the final chosen or synthesized response, without any explanation, preamble, or markdown formatting like ```."
        evaluation_prompt = f"""Original Instructions:
```
{instructions}
```

Original Prompt:
```
{prompt}
```

Response from Model A (OpenAI):
---
{response_openai}
---

Response from Model B (Claude):
---
{response_claude}
---

Evaluate both responses (A and B) based *only* on the 'Original Instructions' and 'Original Prompt'. Provide *only* the single best response text (either A, B, or a synthesized improvement). Do not add any explanation, commentary, or markdown formatting. Your output should be the raw text of the final chosen/synthesized response."""

        try:
            print("Attempting Gemini evaluation call...")
            # Use the standard send_prompt_gemini for the evaluation
            final_response = self.send_prompt_gemini(evaluation_instructions, evaluation_prompt)
            print("Gemini evaluation successful.")
            # Ensure the final response is wrapped in ``` for the parser, removing any existing ones first.
            clean_response = final_response.strip()
            if clean_response.startswith("```") and clean_response.endswith("```"):
                 # Strip existing markers if present (handle nested cases potentially)
                 clean_response = clean_response[3:-3].strip()
                 # Further strip if language specifier was present, e.g., ```python\n...```
                 if '\n' in clean_response:
                     first_line, rest = clean_response.split('\n', 1)
                     if first_line.isalnum(): # Simple check for language specifier
                         clean_response = rest

            # Wrap the cleaned response in plain backticks for the parser
            formatted_response = f"```\n{clean_response}\n```"
            return formatted_response
        except Exception as e:
            # If evaluation fails, maybe fall back to one of the original responses? Or raise error?
            # Let's raise an error for now, but could consider returning response_gemini as a fallback.
            print(f"Error during Gemini evaluation: {e}. Raising error.")
            raise RuntimeError(f"Gemini evaluation call failed in ensemble: {e}") from e
