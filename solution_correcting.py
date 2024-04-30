# solution_correcting.py

import os
import re
from colorama import init, Fore, Style
from ai_connector import AIConnector

class SolutionCorrecting:
    def __init__(self):
        self.ai_connector = AIConnector()

    def correct_solution(self, solution):
        print(f"\nImproving solution: {solution.name}\n")

        if solution.status == 'ERROR':
            # Get the error message from the solution's result description
            error_message = solution.result_description

            for component in solution.components:
                # Generate a prompt for the AI to analyze the component for possible errors
                prompt = f"The following solution encountered an error during execution:\n\n"
                prompt += f"Component: {component.name}\nCode:\n{component.code}\n\n"
                prompt += f"Error message: {error_message}\n\nPlease analyze this Component. Check if the error is caused by this code. If the answer is YES, resend the code and do not rename the file name. If the answer is NO, do not send any code. We are going to analyze the other components."

                print("\n\nAI's prompt:\n")
                print(prompt)

                # Send the prompt to the AI using the AIConnector and get the response
                response = self.ai_connector.send_prompt(prompt)

                print("\n\nAI's response:\n")
                print(response)

                # Extract code blocks from the AI's response
                code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)

                if code_blocks:
                    updated_code = code_blocks[0]
                    # Save the updated code to the component file
                    component_file_path = os.path.join(solution.folder, f"{component.name}.{component.extension}")
                    
                    print(Fore.YELLOW + f"\nSolution Folder: {solution.folder}")
                    print(Fore.YELLOW + f"Component File Path: {component_file_path}")
                    
                    try:
                        with open(component_file_path, 'w') as file:
                            file.write(updated_code)
                        print(Fore.GREEN + f"\nComponent '{component.name}' file updated successfully.")
                    except Exception as e:
                        print(Fore.RED + f"\nError occurred while updating component '{component.name}' file:")
                        print(Fore.RED + str(e))

                    # Update the component code with the AI-generated code
                    component.code = updated_code

                    print(Fore.YELLOW + f"\nComponent '{component.name}' has been improved by the AI.\n")
                    print(Fore.YELLOW + "Updated Component Details:")
                    print(Fore.YELLOW + f"Name: {component.name}\n")
                    print(Fore.YELLOW + f"Code:\n{component.code}\n")
                else:
                    print(Fore.BLUE + f"\nNo code blocks found in the AI's response for component '{component.name}'.\n")
        else:
            print("The solution does not have an 'ERROR' status. No correction needed.")

    def improve_component(self, component, solutions_folder):
        # This method is no longer needed since we analyze all components in improve_solution()
        pass
