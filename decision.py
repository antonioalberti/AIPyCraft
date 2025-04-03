# decision.py
from typing import TYPE_CHECKING, Optional, Dict # Import Dict

if TYPE_CHECKING:
    from ai_connector import AIConnector # Avoid circular import for type hinting

class Decision:
    def __init__(self, ai_connector: 'AIConnector'):
        """
        Initializes the Decision class with an AIConnector instance.

        Args:
            ai_connector: An instance of the AIConnector class to access its methods (e.g., send_prompt_gemini).
        """
        self.ai_connector = ai_connector

    def evaluate_and_select(
        self,
        instructions: str,
        prompt: str,
        # Accept a dictionary of responses: {model_name: response_text_or_None}
        responses: Dict[str, Optional[str]]
    ) -> str:
        """
        Uses Gemini 1.5 Pro to evaluate available responses or generate one if none exist.

        Args:
            instructions: The original system instructions.
            prompt: The original user prompt.
            responses: A dictionary where keys are model names and values are their
                       responses (str) or None if the call failed.

        Returns:
            The selected or synthesized best response.

        Raises:
            RuntimeError: If the Gemini call fails.
        """
        # --- Filter out failed responses and build dynamic parts ---
        valid_responses = {name: text for name, text in responses.items() if text is not None}
        num_valid_responses = len(valid_responses)
        models_involved = list(valid_responses.keys())

        # Define the Gemini model used for decision making/generation
        decision_model_name = "Gemini (gemini-2.5-pro-exp-03-25)" # Match the one in ai_connector.py

        # --- Case 1: No valid responses, use Gemini as generator ---
        if num_valid_responses == 0:
            print(f"{' ' * 20}No valid initial responses received. Using {decision_model_name} to generate directly.")
            try:
                # Call Gemini with original instructions and prompt
                # The send_prompt_gemini function itself now logs the model being called
                final_response = self.ai_connector.send_prompt_gemini(instructions, prompt)
                print(f"{' ' * 20}{decision_model_name} direct generation successful.")
                return final_response
            except Exception as e:
                print(f"{' ' * 20}Error during {decision_model_name} direct generation: {e}. Raising error.")
                raise RuntimeError(f"Gemini direct generation call failed: {e}") from e

        # --- Case 2: One or more valid responses, use Gemini as evaluator/synthesizer ---
        # decision_model_name is already defined above
        print(f"{' ' * 20}Received {num_valid_responses} valid response(s) from: {', '.join(models_involved)}. Proceeding to {decision_model_name} evaluation.")

        available_responses_text = ""
        for name, text in valid_responses.items():
            available_responses_text += f"Response from {name}:\n---\n{text}\n---\n\n"

        # Adjust evaluation instructions and task based on number of valid responses
        if num_valid_responses == 1:
            single_model_name = models_involved[0]
            evaluation_instructions = f"You are an expert evaluator. Analyze the provided response from {single_model_name} based on the original instructions and prompt. If the response is good, return it as is. If it can be improved, synthesize a new, improved response that best fulfills the original request. Output ONLY the final chosen or synthesized response, without any explanation, preamble, or markdown formatting like ```."
            evaluation_task = f"Evaluate the response from {single_model_name}. If it accurately and completely addresses the 'Original Prompt' according to the 'Original Instructions', return it directly. Otherwise, generate a new response that does satisfy the requirements. Output only the final response text."
        else: # 2 or more responses
            model_list_str = " and ".join([", ".join(models_involved[:-1]), models_involved[-1]]) if len(models_involved) > 1 else models_involved[0] # Handles 2+ names nicely
            evaluation_instructions = f"You are an expert evaluator. Analyze the {num_valid_responses} provided responses ({model_list_str}) based on the original instructions and prompt. Choose the single best response OR synthesize a new, improved response that incorporates the best elements and best fulfills the original request. Output ONLY the final chosen or synthesized response, without any explanation, preamble, or markdown formatting like ```."
            evaluation_task = f"Evaluate the responses from {model_list_str}. Choose the one that best addresses the 'Original Prompt' according to the 'Original Instructions', or synthesize a new, better response based on them. Output only the final response text."

        # Construct the final prompt for Gemini evaluation
        evaluation_prompt = f"""Original Instructions:
```
{instructions}
```

Original Prompt:
```
{prompt}
```

Available Responses:
{available_responses_text.strip()}

{evaluation_task}"""

        try:
            # decision_model_name is already defined above
            print(f"{' ' * 20}Attempting {decision_model_name} evaluation call with {num_valid_responses} response(s)...")
            # Use the AIConnector's send_prompt_gemini for the evaluation
            # The send_prompt_gemini function itself now logs the model being called
            final_response = self.ai_connector.send_prompt_gemini(evaluation_instructions, evaluation_prompt)
            print(f"{' ' * 20}{decision_model_name} evaluation successful.")
            # Return the raw response from Gemini evaluation directly.

            #print(f"{' ' * 20}Available responses provided to {decision_model_name}: {available_responses_text.strip()}")
            #print(f"{' ' * 20}Final response chosen/synthesized by {decision_model_name}: {final_response}")

            return final_response
        except Exception as e:
            # If evaluation fails, raise an error.
            # decision_model_name is already defined above
            print(f"{' ' * 20}Error during {decision_model_name} evaluation: {e}. Raising error.")
            raise RuntimeError(f"Gemini evaluation call failed in ensemble: {e}") from e
