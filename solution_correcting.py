# solution_correcting.py

import os
import re
from colorama import init, Fore, Style
from ai_connector import AIConnector

init(autoreset=True)

class SolutionCorrecting:
    def __init__(self):
        self.ai_connector = AIConnector()

    def correct_solution(self, solution):
        print(Fore.CYAN + f"\nCorrecting solution: {solution.name}\n")

        if solution.status == 'ERROR':
            error_message = solution.result_description

            instructions = """Context:

        You are going to correct Components of a Solution.
        The Solution has a descriptor that is going to be provided to you in the prompts.
        Each Component is a Python file or other language code that solves a specific problem.
        Please, do not change the programming language of Components.

        Instructions:

        You need to correct the content of the Component that is causing a certain error.
        In addition, you need to adjust the other components correspondingly to keep consistency.
        The main.py program must be able to import all the required Python classes, as well as to input (read from file) other language code.
        The last Component will always be the main.py program. Therefore, always put a if __name__ == "__main__": at the end of the main.py program,
        initializing and running the all the solution.
        Whenever you correct components, check the consistency of attributes. This is one of the main problems in the code.
        Keep the content of each Component coherent and compatible with the others on the same solution.
        Check consistency of naming and number of parameters in the components.

        Expected answer format:

        1. If SOME corrections are required, send ONLY the corrected code of this Component.
        In addition, do not rename the file name. Do nothing else.

        2. If NO corrections are required in some Component, do not send any code. Send just a word saying "NO".


        """

            for component in solution.components:
                prompt = (
                    f"The Solution {solution.name} created from the following Solution description encountered an error during execution and you need to correct it.\n\n"
                    f"The solution aim is to: {solution.semantic_description}\n\n"
                    f"{error_message}\n\nPlease analyze the following Component:\n\n"
                    f"{component.name}\n\Content:\n{component.content}\n\n"
                    "IMPORTANT 1: If some corrections are required, send ONLY the complete corrected code of this Component.\n"
                    "In addition, do not rename the file name. Do nothing else.\n"
                    "IMPORTANT 2: Do not remove the function if __name__ == \"__main__\" from the main.py file."
                )

                print(Style.BRIGHT + Fore.GREEN + "\nThis is the prompt being sent to the AI:\n")
                print(Style.NORMAL + prompt)

                response = self.ai_connector.send_prompt_ensemble(instructions, prompt)

                print(Style.BRIGHT + Fore.GREEN + "\n\nAI's response:\n")
                print(Style.NORMAL + response)

                # Check if the response is exactly "NO" (case-insensitive check after stripping)
                cleaned_response = response.strip()
                if cleaned_response.upper() == "NO":
                    print(Style.BRIGHT + Fore.CYAN + f"\nNo changes needed for component '{component.name}'.\n")
                else:
                    # Try to extract code block only if response is not "NO"
                    # Use a more general pattern to catch ```python, ```, etc.
                    content_match = re.search(r"```(?:[a-zA-Z0-9]*)?\s*\n(.*?)\n```", cleaned_response, re.DOTALL)
                    if content_match:
                        updated_content = content_match.group(1).strip() # Strip whitespace from extracted code
                        component_file_path = os.path.join(solution.folder, f"{component.name}.{component.extension}")

                        print(Style.BRIGHT + Fore.CYAN + f"\nSolution Folder: {solution.folder}")
                        print(Style.BRIGHT + Fore.CYAN + f"Component File Path: {component_file_path}")

                        try:
                            with open(component_file_path, 'w') as file:
                                file.write(updated_content)
                            print(Style.BRIGHT + Fore.CYAN + f"\nComponent '{component.name}' file updated successfully.")
                            component.content = updated_content # Update component content in memory
                        except Exception as e:
                            print(Style.BRIGHT + Fore.RED + f"\nError occurred while updating component '{component.name}' file:")
                            print(Style.NORMAL + str(e))
                    else:
                        # If it wasn't "NO" but also not a valid code block
                        print(Style.BRIGHT + Fore.YELLOW + f"\nNo valid correction code block found in the AI's response for component '{component.name}'.\n")
        else:
            print(Fore.CYAN + "The solution does not have an 'ERROR' status. No correction needed.")

    def improve_component(self, component, solutions_folder):
        pass
