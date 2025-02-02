# solution_importer.py

import os
from colorama import init, Fore, Style
from ai_connector import AIConnector
from solution import Solution
from component import Component

class SolutionImporter:
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder
        self.ai_connector = AIConnector()

    def import_solution_from_folder(self, solution_name, folder_path):
        print(f"\nImporting solution from folder: {folder_path}\n")

        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(Fore.RED + f"Folder '{folder_path}' does not exist.")
            return None

        # Get the list of script files in the folder
        script_extensions = ['.py', '.sh', '.bat', '.js']  # Add more extensions if needed
        script_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and os.path.splitext(file)[1].lower() in script_extensions]

        components = []

        instructions = """Context:
        
        You are going to determine the Components of a Solution. 
        Each Component will be designed as a piece of code that solves a specific problem. 
        Therefeore, the main.py program must be able to import all the required classes. 
        The last Component will always named as main.py program. 
        Therefore, always put a if __name__ == "__main__": at the end of the main.py program, 
        inializing and running the all the solution.

        Expected answer format:

        File: The file name with extension.

        Description: A brief description of the functionality and purpose of the script.
        
        """

        # Generate prompts for each script file
        for file_name in script_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r") as file:
                code = file.read()

                prompt = "Follow your instructions to describe the following code:\n\n"
                prompt += f"File: {file_name}\n"
                prompt += f"Code:\n{code}\n\n"
                prompt += ""

                # Send the prompt to the AI using the AIConnector and get the response
                response = self.ai_connector.send_prompt(instructions, prompt)

                # Extract the component name and extension from the file name
                component_name, component_extension = os.path.splitext(file_name)
                component_extension = component_extension[1:]  # Remove the leading dot

                # Create a Component object using the extracted information
                component = Component(component_name, component_extension, code, response.strip())
                components.append(component)

                print(f"\n\nParsed from AI response:\n\n")

                print(Fore.BLUE + f"\n\nName: {component.name}\n")
                print(Fore.BLUE + f"Extension: {component.extension}\n")
                print(Fore.BLUE + f"Code: {component.code}\n")
                print(Fore.BLUE + f"Description: {component.semantic_description}\n")

        instructions1 = """Context:
        
        You are going to determine the overall description of a Solution. 
        Each Component will be designed as a piece of code that solves a specific problem. 

        Expected answer format:

        Overall description of the solution. Include the purpose and how the components interact with each other.
        
        """

        # Generate a final prompt for the AI to provide an overall solution description
        final_prompt = Fore.WHITE + f"Based on the analysis of the following components:\n\n"
        for component in components:
            final_prompt += f"Component: {component.name}{component.extension}\n"
            final_prompt += f"Description: {component.semantic_description}\n\n"
        final_prompt += "Provide an overall description of the solution. Include the purpose and how the components interact with each other."

        # Send the final prompt to the AI using the AIConnector and get the response
        final_response = self.ai_connector.send_prompt(instructions1, final_prompt)

        solution_description = final_response.strip()

        print(f"\nSolutions folder: {self.solutions_folder}\n")

        # Create a Solution object using the extracted information
        solution = Solution(solution_name, components)

        # Create the solution folder and save the solution description
        solution_folder = os.path.join(self.solutions_folder, solution_name)
        os.makedirs(solution_folder, exist_ok=True)

        print(f"\nSolution folder to save the files: {solution_folder}\n")

        # Set solution folder at the new solution object
        solution.folder = solution_folder

        #with open(os.path.join(solution_folder, "solution_description.txt"), "w") as file:
        #    file.write(solution_description)

        # Generate the content for the descriptor.txt file
        descriptor_content = f"Description: {solution_description}\n\n"

        solution.semantic_description = solution_description

        # Generate the content for the descriptor.txt file
        descriptor_content = f"Description: {solution_description}\n\n"

        for i, component in enumerate(components, start=1):
            descriptor_content += f"Component {i}: {component.semantic_description}\n\n"
            descriptor_content += f"File {i}: {component.name}.{component.extension}\n\n"

        # Save the descriptor.txt file
        with open(os.path.join(solution_folder, "descriptor.txt"), "w") as file:
            file.write(descriptor_content)

        # Save the components' code files in the solution folder
        for component in components:
            component_file_path = os.path.join(solution_folder, f"{component.name}.{component.extension}")
            with open(component_file_path, "w") as file:
                file.write(component.code)

        print(Fore.GREEN + f"\nSolution '{solution_name}' imported successfully.")

        return solution
