import os
import openai
import google.generativeai as genai
# Removed: import anthropic
from dotenv import load_dotenv
from decision import Decision # Import the new Decision class
import concurrent.futures # For parallel API calls
from typing import Callable, Tuple, Optional, Dict # For type hinting

class AIConnector:
    def __init__(self):
        load_dotenv()  # Load environment variables from the .env file

        # Configure OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            print(f"{' ' * 20}Warning: OpenAI API key not found in 'OPENAI_API_KEY' environment variable. OpenAI calls will fail.")
            # Decide if you want to raise an error or just warn:
            # raise ValueError("OpenAI API key not found in 'OPENAI_API_KEY' environment variable.")

        # Configure Gemini
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print(f"{' ' * 20}Warning: Gemini API key not found in 'GEMINI_API_KEY' environment variable. Gemini calls will fail.")
            # Decide if you want to raise an error or just warn:
            # raise ValueError("Gemini API key not found in 'GEMINI_API_KEY' environment variable.")
        else:
            try:
                genai.configure(api_key=gemini_api_key)
                # Optional: Test connection or model availability here if needed
            except Exception as e:
                 print(f"{' ' * 20}Warning: Failed to configure Gemini API: {e}. Gemini calls may fail.")
                 # Decide if you want to raise an error or just warn:
                 # raise RuntimeError(f"Failed to configure Gemini API: {e}") from e

        # Removed Anthropic configuration

        # Instantiate the Decision maker
        self.decision_maker = Decision(self)

    def send_prompt_openai(self, instructions: str, prompt: str) -> str:
        model_name = "gpt-4o" # Define model name
        if not openai.api_key:
             raise RuntimeError("OpenAI API key is not configured.")
        try:
            print(f"{' ' * 20}Calling OpenAI model: {model_name}") # Log model name
            response = openai.ChatCompletion.create(
                model=model_name,            # Use variable
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
            # Updated model name as requested:
            model_identifier = 'gemini-2.5-pro-exp-03-25'
            model = genai.GenerativeModel(model_identifier)
            print(f"{' ' * 20}Calling Gemini model: {model_identifier}") # Log model name

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

    def _send_prompt_openai_gpt35(self, instructions: str, prompt: str) -> str:
        """Internal method to send a prompt to OpenAI GPT-3.5 Turbo."""
        model_name = "gpt-3.5-turbo" # Define model name
        if not openai.api_key:
             raise RuntimeError("OpenAI API key is not configured.")
        try:
            print(f"{' ' * 20}Calling OpenAI model: {model_name}") # Log model name
            response = openai.ChatCompletion.create(
                model=model_name, # Use variable
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_tokens=4096, # Adjust if needed for GPT-3.5
                n=1
            )
            answer = response.choices[0].message["content"]
            return answer.strip()
        except openai.OpenAIError as e:
            raise RuntimeError(f"OpenAI GPT-3.5 error: {e}") from e
        except Exception as e:
            # Catch other potential exceptions
            raise RuntimeError(f"Error during OpenAI GPT-3.5 call: {e}") from e

    def _call_api_wrapper(self, api_func: Callable[[str, str], str], model_name: str, instructions: str, prompt: str) -> Tuple[str, Optional[str]]:
        """
        Wrapper function to call an API, handle errors, and return result tuple.
        Needed for use with ThreadPoolExecutor.
        """
        # Model name is already passed in, use it in prints
        try:
            # The actual call inside api_func will print the specific model now
            print(f"{' ' * 20}Attempting call via wrapper for: {model_name}")
            response = api_func(instructions, prompt)
            print(f"{' ' * 20}Call successful via wrapper for: {model_name}")
            return model_name, response
        except Exception as e:
            print(f"{' ' * 20}Warning: Call failed via wrapper for {model_name}: {e}")
            return model_name, None # Return None on failure

    def send_prompt_ensemble(self, instructions: str, prompt: str) -> str:
        """
        Sends the prompt to configured models (OpenAI, Claude) in parallel,
        then uses the Decision class (Gemini) to evaluate available responses
        or generate one if all others fail.
        """
        api_calls_to_make = []

        # --- Define potential API calls ---
        # Pass more specific names to the wrapper
        if openai.api_key:
            api_calls_to_make.append((self.send_prompt_openai, "OpenAI (gpt-4o)"))
        else:
            print(f"{' ' * 20}Skipping OpenAI (gpt-4o) call (no API key).")

        # Add call to GPT-3.5 if API key is present
        if openai.api_key:
            api_calls_to_make.append((self._send_prompt_openai_gpt35, "OpenAI (gpt-3.5-turbo)"))
        else:
            # This condition might be redundant if the first check already skipped OpenAI entirely,
            # but it's safe to leave for clarity or future changes.
            print(f"{' ' * 20}Skipping OpenAI (gpt-3.5-turbo) call (no API key).")

        # Removed Claude call section

        # --- Execute calls in parallel ---
        results_dict: Dict[str, Optional[str]] = {}
        if not api_calls_to_make:
             print(f"{' ' * 20}Warning: No APIs configured or available to call in ensemble.")
             # Proceed directly to decision maker which will use Gemini as generator
        else:
            # Use max_workers=len(api_calls_to_make) to run all in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_calls_to_make)) as executor:
                # Prepare futures
                futures = [
                    executor.submit(self._call_api_wrapper, api_func, model_name, instructions, prompt)
                    for api_func, model_name in api_calls_to_make
                ]
                # Collect results as they complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        model_name, response = future.result()
                        results_dict[model_name] = response
                    except Exception as exc:
                        # This shouldn't happen often as _call_api_wrapper catches errors,
                        # but good practice to handle future exceptions.
                        print(f"{' ' * 20}Error retrieving result from future: {exc}")
                        # We don't know which model failed here easily without more complex tracking,
                        # but results_dict will simply lack an entry or have None.

        # --- Proceed to evaluation using Decision class (Gemini) ---
        # The decision maker now expects a dictionary and handles None values or empty dict.
        print(f"{' ' * 20}Proceeding to Gemini evaluation/generation with results: { {k: ('<response>' if v else None) for k, v in results_dict.items()} }") # Avoid printing full responses
        try:
            final_response = self.decision_maker.evaluate_and_select(
                instructions=instructions,
                prompt=prompt,
                responses=results_dict # Pass the dictionary
            )
            # Return the response selected/synthesized/generated by the Decision maker (Gemini)
            return final_response
        except Exception as e:
            # The evaluate_and_select method already prints its specific error.
            # Re-raise the exception caught from the decision maker.
            raise RuntimeError(f"Decision evaluation/generation failed in ensemble: {e}") from e
