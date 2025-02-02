# solution_correcting.py

import os
import re
from colorama import init, Fore, Style
from ai_connector import AIConnector

class SolutionCorrecting:
    def __init__(self):
        self.ai_connector = AIConnector()

    def correct_solution(self, solution):
        print(f"\nCorrecting solution: {solution.name}\n")

        if solution.status == 'ERROR':
            # Get the error message from the solution's result description
            error_message = solution.result_description

            instructions = """Context:
        
        You are going to correct Python codes for Components of a Solution developed in Python. 
        The Solution has a descriptor that is going to be provided to you in the prompts.
        Each Component is a Python file that solves a specific problem. 
        

        Instructions:

        You need to correct the code of the Component that is causing a certain error.
        In addtion, you need to adjust the other components correspondingly to keep consistency. 
        The main.py program must be able to import all the required classes. 
        The last Component will always named as main.py program. Therefore, always put a if __name__ == "__main__": at the end of the main.py program, 
        initializing and running the all the solution.
        Whenever you correct components, check the consistency of attributes. This is one of the main problems in the code. 
        Keep the code of each Component coherent and compatible with the others on the same solution.
        Check consistency of naming and number of parameters in the components. 

        Expected answer format:

        1. If SOME corrections are required, send ONLY the corrected Python code of this Component.
        In addtion, do not rename the file name. Do nothing else. 

        2. If NO corrections are required in some Component, do not send any code. Send just a word saying "NO".
        
        
        """

            for component in solution.components:
                # Generate a prompt for the AI to analyze the component for possible errors
                prompt = f"The Solution {solution.name} created from the following Solution description encountered an error during execution and you need to correct it.\n\n"
                prompt += f"The solution aim is to: {solution.semantic_description}\n\n"
                prompt += f"{error_message}\n\nPlease analyze the following Component:\n\n"
                prompt += f"{component.name}\n\nCode:\n{component.code}\n\n"
                prompt += "IMPORTANT 1: If some corrections are required, send ONLY the corrected Python code of this Component. In addtion, do not rename the file name. Do nothing else.\n"
                prompt += "IMPORTANT 2: Do not remove the function if __name__ == \"__main__\" from the main.py file."

                print("\nThis is the prompt being sent to the AI:\n")
                print(prompt)

                # Send the prompt to the AI using the AIConnector and get the response
                response = self.ai_connector.send_prompt(instructions,prompt)

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

                    #print(Fore.YELLOW + f"\nComponent '{component.name}' has been improved by the AI.\n")
                    #print(Fore.YELLOW + "Updated Component Details:")
                    #print(Fore.YELLOW + f"Name: {component.name}\n")
                    #print(Fore.YELLOW + f"Code:\n{component.code}\n")
                else:
                    print(Fore.BLUE + f"\nNo code blocks found in the AI's response for component '{component.name}'.\n")
        else:
            print("The solution does not have an 'ERROR' status. No correction needed.")

    def improve_component(self, component, solutions_folder):
        # This method is no longer needed since we analyze all components in improve_solution()
        pass
