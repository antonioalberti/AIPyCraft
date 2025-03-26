# solution_updater.py

import os
import re
from colorama import Fore
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
                "If no changes are necessary, reply with 'NO'."
            )

            print(f"\nPrompt for {comp.name}.{comp.extension}:\n{prompt}\n\n")
            response = self.ai_connector.send_prompt("", prompt)
            print(f"AI response for {comp.name}.{comp.extension}:\n{response}\n")

            # Try to extract a Python content block.
            content_match = re.search(r"```(?:python)?\n(.*?)\n```", response, re.DOTALL)
            if content_match:
                updated_content = content_match.group(1)
                file_path = os.path.join(solution.folder, f"{comp.name}.{comp.extension}")
                try:
                    with open(file_path, "w") as file:
                        file.write(updated_content)
                    comp.content = updated_content
                    print(Fore.GREEN + f"Updated {comp.name}.{comp.extension} successfully.")
                except Exception as e:
                    print(Fore.RED + f"Error updating {comp.name}.{comp.extension}: {e}")
            elif response.strip() == "NO":
                print(Fore.YELLOW + f"No changes needed for {comp.name}.{comp.extension}.")
            else:
                print(Fore.BLUE + f"No valid correction provided for {comp.name}.{comp.extension}.")
