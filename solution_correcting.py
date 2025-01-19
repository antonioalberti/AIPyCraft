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

            instructions = """Context:
        
        You are going to correct Python codes for Components of a Solution. 
        Each Component will be designed as a piece of code that solves a specific problem. 
        Therefeore, the main.py program must be able to import all the required classes. 
        The last Component will always named as main.py program. 
        Therefore, always put a if __name__ == "__main__": at the end of the main.py program, 
        inializing and running the all the solution.

        Expected answer format:

        Check if the error is caused by a certain Solution's Component. 
        If the answer is YES, send ONLY the corrected code of this Component and do not rename the file name. 
        If the answer is NO, do not send any code. You will analyze the other Components of the Solution instead.
        Keep the code of a Component coherent and compatible with other components of the same solution. 
        All the Solution must have a if __name__ == "__main__": function in the main.py file.
        
        """

            for component in solution.components:
                # Generate a prompt for the AI to analyze the component for possible errors
                prompt = f"The following Solution encountered an error during execution and you need to correct it:\n\n"
                prompt += f"Error message: {error_message}\n\nPlease analyze the following Component. "
                prompt += f"Component: {component.name}\nCode:\n{component.code}\n\n"

                print("\n\nAI's prompt:\n")
                print(prompt)

                # Send the prompt to the AI using the AIConnector and get the response
                response = self.ai_connector.send_prompt(instructions,"asst_YiljxNBLxlvdPiGiKINWHOB6",prompt)

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
