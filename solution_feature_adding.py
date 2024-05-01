# solution_feature_adding.py

import os
import re
from colorama import init, Fore, Style
from ai_connector import AIConnector

class SolutionFeatureAdding:
    def __init__(self):
        self.ai_connector = AIConnector()

    def add_feature_to_solution(self, solution):
        print(f"\nAdding a new feature to solution: {solution.name}\n")

        # Get the new feature description from the user
        feature_description = input("Enter the description of what to you want to do with the solution: ")

        for component in solution.components:
            # Generate a prompt for the AI to add the new feature to the component
            prompt = f"The following solution needs a new feature:\n\n"
            prompt += f"Solution: {solution.name}\n"
            prompt += f"Component: {component.name}\nCode:\n{component.code}\n\n"
            prompt += f"Issue: {feature_description}\n\nPlease improve this component. Provide the updated code for the component, keeping the original file name."

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
                    print(Fore.GREEN + f"\nComponent '{component.name}' file updated successfully with the new feature.")
                except Exception as e:
                    print(Fore.RED + f"\nError occurred while updating component '{component.name}' file:")
                    print(Fore.RED + str(e))

                # Update the component code with the AI-generated code
                component.code = updated_code

                print(Fore.YELLOW + f"\nComponent '{component.name}' has been updated with the new feature by the AI.\n")
                print(Fore.YELLOW + "Updated Component Details:")
                print(Fore.YELLOW + f"Name: {component.name}\n")
                print(Fore.YELLOW + f"Code:\n{component.code}\n")
            else:
                print(Fore.BLUE + f"\nNo code blocks found in the AI's response for component '{component.name}'.\n")