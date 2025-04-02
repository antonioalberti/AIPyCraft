# solution_updater.py

import os
import re
from colorama import Fore, Style
from ai_connector import AIConnector

class SolutionUpdater:
    def __init__(self):
        self.ai_connector = AIConnector()

    def update_solution(self, solution):
        # Create a context string with all components' content.
        context = "Solution Components:\n"
        for comp in solution.components:
            context += f"{comp.name}.{comp.extension}:\n{comp.content}\n\n"

        # Get the error message from the solution's result description
        error_message = solution.result_description

        # Loop over each component and ask for improvements.
        for comp in solution.components:
            prompt = (
                f"Solution: {solution.name}\n"
                f"Description: {solution.semantic_description}\n\n"
                f"{context}\n\n"
                f"After trying to run the solution, the results was: \n\n{error_message}\n\n"
                f"Review the component '{comp.name}.{comp.extension}'. If any improvements are needed, "
                "return ONLY the complete code corrected inside a code block. It must be complete, not a partial fix."
                "If no changes are necessary, reply with 'NO'. This indicates that the code is correct and does not require any replacement in the OS."
            )

            print(f"\nPrompt for {comp.name}.{comp.extension}:\n{prompt}\n\n")
            response = self.ai_connector.send_prompt_ensemble("", prompt)
            print(Fore.BLUE + Style.BRIGHT + f"AI response for {comp.name}.{comp.extension}:\n{response}\n" + Style.RESET_ALL)

            # Check if the response is exactly "NO" (case-insensitive check after stripping)
            cleaned_response = response.strip()
            if cleaned_response.upper() == "NO":
                print(Fore.CYAN + f"No changes needed for {comp.name}.{comp.extension}." + Style.RESET_ALL)
            else:
                # Try to extract code block only if response is not "NO"
                # Use a more general pattern to catch ```python, ```, etc.
                content_match = re.search(r"```(?:[a-zA-Z0-9]*)?\s*\n(.*?)\n```", cleaned_response, re.DOTALL)
                if content_match:
                    updated_content = content_match.group(1).strip() # Strip whitespace from extracted code
                    file_path = os.path.join(solution.folder, f"{comp.name}.{comp.extension}")
                    try:
                        with open(file_path, "w") as file:
                            file.write(updated_content)
                        comp.content = updated_content # Update component content in memory
                        print(Fore.GREEN + Style.BRIGHT + f"Updated {comp.name}.{comp.extension} successfully." + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Error updating {comp.name}.{comp.extension}: {e}" + Style.RESET_ALL)
                else:
                    # If it wasn't "NO" but also not a valid code block
                    print(Fore.MAGENTA + Style.DIM + f"No valid correction code block provided for {comp.name}.{comp.extension}." + Style.RESET_ALL)

            # --- This block below is now handled by the logic above ---
            # if content_match:
            #     updated_content = content_match.group(1)
            #     file_path = os.path.join(solution.folder, f"{comp.name}.{comp.extension}")
