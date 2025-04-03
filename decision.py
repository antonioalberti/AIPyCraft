# decision.py
from typing import TYPE_CHECKING, Optional

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
        response_openai: str
    ) -> str:
        """
        Uses an evaluation model (Gemini) to evaluate or refine a response from OpenAI.

        Args:
            instructions: The original system instructions.
            prompt: The original user prompt.
            response_openai: The response from the OpenAI model.

        Returns:
            The evaluated or synthesized best response from Gemini.

        Raises:
            RuntimeError: If the evaluation call fails.
        """
        print(f"{' ' * 20}Received OpenAI response, proceeding to Gemini evaluation/refinement.")
        # Updated instructions for Gemini: Evaluate/refine the single OpenAI response
        evaluation_instructions = "You are an expert evaluator. Analyze the provided response from OpenAI based on the original instructions and prompt. If the response is good, return it as is. If it can be improved, synthesize a new, improved response that best fulfills the original request. Output ONLY the final chosen or synthesized response, without any explanation, preamble, or markdown formatting like ```."
        # Updated prompt for Gemini: Include only the OpenAI response
        evaluation_prompt = f"""Original Instructions:
```
{instructions}
```

Original Prompt:
```
{prompt}
```

Response from OpenAI:
---
{response_openai}
---

Evaluate the 'Response from OpenAI'. If it accurately and completely addresses the 'Original Prompt' according to the 'Original Instructions', return it directly. Otherwise, generate a new response that does satisfy the requirements. Output only the final response text."""

        try:
            print(f"{' ' * 20}Attempting Gemini evaluation/refinement call...")
            # Use the AIConnector's send_prompt_gemini for the evaluation/refinement
            final_response = self.ai_connector.send_prompt_gemini(evaluation_instructions, evaluation_prompt)
            print(f"{' ' * 20}Gemini evaluation/refinement successful.\n")
            # Return the raw response from Gemini evaluation/refinement directly.
            return final_response
        except Exception as e:
            # If evaluation fails, raise an error.
            print(f"{' ' * 20}Error during Gemini evaluation/refinement: {e}. Raising error.")
            raise RuntimeError(f"Gemini evaluation/refinement call failed: {e}") from e
