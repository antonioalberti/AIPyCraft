# solution_updater.py

import os
import re
from colorama import Fore, Style
from ai_connector import AIConnector

class ComponentCorrector:
    def __init__(self):
        self.ai_connector = AIConnector()

    def update_solution(self, solution, component_name, user_prompt=""):
        """
        Corrects a single specified component of the solution using AI, optionally guided by a user prompt.

        Args:
            solution: The solution object containing components and metadata.
            component_name: The name of the component file to correct (e.g., "main.py").
            user_prompt (str, optional): Additional instructions from the user. Defaults to "".
        """
        # Create a context string with all components' content.
        context = "Solution Components:\n"
        for comp in solution.components:
            context += f"{comp.name}.{comp.extension}:\n{comp.content}\n\n"

        # Get the error message from the solution's result description
        error_message = solution.result_description

        # Find the component to correct.
        comp_to_correct = next((c for c in solution.components if f"{c.name}.{c.extension}" == component_name), None)

        if not comp_to_correct:
            print(Fore.RED + f"Error: Component '{component_name}' not found in the solution." + Style.RESET_ALL)
            return

        # Use the found component
        comp = comp_to_correct

        # Base prompt
        base_prompt = (
            f"Solution: {solution.name}\n"
            f"Description: {solution.semantic_description}\n\n"
                f"{context}\n\n"
                f"After trying to run the solution, the results was: \n\n{error_message}\n\n"
                f"Review the component '{comp.name}.{comp.extension}'. If any improvements are needed, "
                "return ONLY the complete code corrected inside a code block. It must be complete, not a partial fix."
                "If no changes are necessary, reply with 'NO'."
        )

        # Add user prompt if provided
        full_prompt = base_prompt
        if user_prompt and user_prompt.strip():
            full_prompt += f"\n\nUser Instructions:\n{user_prompt.strip()}"

        print(f"\nPrompt for {comp.name}.{comp.extension}:\n{full_prompt}\n\n")
        response = self.ai_connector.send_prompt("", full_prompt)
        print(Fore.BLUE + Style.BRIGHT + f"AI response for {comp.name}.{comp.extension}:\n{response}\n" + Style.RESET_ALL)

        # Try to extract any code block, regardless of language specifier.
        # Pattern breakdown:
        # ```          - Matches the opening backticks
        # [a-zA-Z0-9]* - Matches an optional language specifier (letters/numbers)
        # \s*          - Matches optional whitespace
        # \n           - Matches the newline after the opening tag
        # (.*?)        - Captures the code content (non-greedy)
        # \n```        - Matches the newline before the closing backticks and the closing backticks
        content_match = re.search(r"```[a-zA-Z0-9]*\s*\n(.*?)\n```", response, re.DOTALL)
        if content_match:
            # Strip leading/trailing whitespace from the captured block, but preserve internal indentation
            updated_content = content_match.group(1).strip()
            file_path = os.path.join(solution.folder, f"{comp.name}.{comp.extension}")
            try:
                with open(file_path, "w") as file:
                    file.write(updated_content)
                comp.content = updated_content
                print(Fore.GREEN + Style.BRIGHT + f"Updated {comp.name}.{comp.extension} successfully." + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Error updating {comp.name}.{comp.extension}: {e}" + Style.RESET_ALL)
        elif response.strip() == "NO":
            print(Fore.CYAN + f"No changes needed for {comp.name}.{comp.extension}." + Style.RESET_ALL)
        else:
            print(Fore.MAGENTA + Style.DIM + f"No valid correction provided for {comp.name}.{comp.extension}." + Style.RESET_ALL)
