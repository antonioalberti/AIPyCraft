# solution_feature_adding.py

import os
from colorama import init, Fore, Style
from ai_connector import AIConnector
from ai_code_parser import AICodeParser

class SolutionFeatureAdding:
    def __init__(self):
        self.ai_connector = AIConnector()
        self.content_parser = AICodeParser()

    def add_feature_to_solution(self, solution):
        print(f"\nAdding a new feature to solution: {solution.name}\n")

        # Get the new feature description from the user
        feature_description = input("Enter the description of what to you want to do with the solution: ")

        instructions = """Context:
        
        You are going to improve the Components of a Solution with a new feature. 

        Expected answer format:

        Check if the new feature demands a change in the Solution's Component. 
        If the answer is YES, send ONLY the new code of this Component and do not rename the file name. 
        If the answer is NO, do not send any code. You will analyze the other Components of the Solution instead.
        Keep the code of a Component coherent and compatible with other Components of the same Solution. 
        All the Solution must have a if __name__ == "__main__": function in the main.py file.
        
        """

        for component in solution.components:
            # Generate a prompt for the AI to add the new feature to the component
            prompt = f"The following solution needs a new feature or improvement:\n\n"
            prompt += f"Solution: {solution.name}\n"
            prompt += f"Component: {component.name}.{component.extension}\n"
            prompt += f"Language: {component.language}\n"
            prompt += f"Content:\n{component.content}\n\n"
            prompt += f"Improvement or issue: {feature_description}\n\n"
            prompt += f"Please improve this component. Provide the updated code for the component, keeping the original file name and language."

            print(Fore.CYAN + "\nAnalyzing component:")
            print(Fore.CYAN + f"Name: {component.name}.{component.extension}")
            print(Fore.CYAN + f"Language: {component.language}")

            # Send the prompt to the AI using the AIConnector and get the response
            response = self.ai_connector.send_prompt(instructions, prompt)

            print(Fore.WHITE + "\nAI's response:\n")
            print(response)

            # Use AICodeParser to extract code from the AI's response
            updated_content = self.content_parser.parse_content(response)

            if updated_content:
                # Save the updated content to the component file
                component_file_path = os.path.join(solution.folder, f"{component.name}.{component.extension}")
                
                print(Fore.YELLOW + f"\nUpdating component file:")
                print(Fore.YELLOW + f"Path: {component_file_path}")
                
                try:
                    # Use AICodeParser to save the code
                    if self.content_parser.save_content_to_file(updated_content, component_file_path):
                        # Update the component content with the AI-generated content
                        component.content = updated_content
                        print(Fore.GREEN + f"\nComponent '{component.name}.{component.extension}' successfully updated.")
                    else:
                        print(Fore.RED + f"\nFailed to save updated content for component '{component.name}.{component.extension}'.")
                except Exception as e:
                    print(Fore.RED + f"\nError updating component file:")
                    print(Fore.RED + str(e))
            else:
                print(Fore.BLUE + f"\nNo changes required for component '{component.name}.{component.extension}'.")

        print(Fore.GREEN + "\nFeature addition process completed.")