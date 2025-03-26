import os
from colorama import Fore
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

        # Supported file extensions
        supported_extensions = [
            '.py', '.sh', '.bat', '.ps1', '.js', '.txt', '.toml', '.json', '.md', '.html', '.css', '.yaml', '.yml'
        ]

        # Get the list of files in the folder with supported extensions
        script_files = [
            file for file in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, file)) and os.path.splitext(file)[1].lower() in supported_extensions
        ]

        if not script_files:
            print(Fore.YELLOW + f"No supported files found in {folder_path}")
            return None

        components = []

        instructions = """Context:
        
        You are going to determine the Components of a Solution. 
        Each Component is a file in the operating system. 
        The main.py program must be able to import all the required Python classes and use one or more components in other languages. 
        The last Component will always be named as main.py program. 
        Therefore, always consider a if __name__ == "__main__": at the end of the main.py program, 
        initializing and running the entire solution.

        Expected answer format:

        File 1: The file name with extension.

        Description 1: A brief description of the functionality and purpose of the script.

        File 2: The file name with extension.

        Description 2: A brief description of the functionality and purpose of the script.
        
        """

        # Generate prompts for each file in the Solution folder
        for file_name in script_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                prompt = "Follow your instructions to describe the following content:\n\n"
                prompt += f"File: {file_name}\n"
                prompt += f"Content:\n{content}\n\n"

                # Send the prompt to the AI using the AIConnector and get the response
                response = self.ai_connector.send_prompt(instructions, prompt)

                # Extract the component name and extension from the file name
                component_name, component_extension = os.path.splitext(file_name)
                component_extension = component_extension[1:]  # Remove the leading dot

                # Determine the language based on the file extension
                language = self.detect_language(component_extension)

                # Create a Component object using the extracted information
                component = Component(
                    name=component_name,
                    extension=component_extension,
                    content=content,
                    semantic_description=response.strip(),
                    language=language
                )
                components.append(component)

                print(f"\n\nParsed from AI response:\n\n")
                print(Fore.BLUE + f"\n\nName: {component.name}\n")
                print(Fore.BLUE + f"Extension: {component.extension}\n")
                print(Fore.BLUE + f"Language: {component.language}\n")
                print(Fore.BLUE + f"Content: {component.content}\n")
                print(Fore.BLUE + f"Description: {component.semantic_description}\n")

        instructions1 = """Context:
        
        You are going to determine the overall description of a Solution. 
        Each Component is a file that contains code or text. 

        Expected answer format:

        Overall description of the solution. Include the purpose and how the components interact with each other.
        
        """

        # Generate a final prompt for the AI to provide an overall solution description
        final_prompt = Fore.WHITE + f"Based on the analysis of the following components:\n\n"
        for component in components:
            final_prompt += f"Component: {component.name}.{component.extension}\n"
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

        # Generate the content for the descriptor.txt file
        descriptor_content = f"Description: {solution_description}\n\n"

        solution.semantic_description = solution_description

        for i, component in enumerate(components, start=1):
            descriptor_content += f"Component {i}: {component.semantic_description}\n\n"
            descriptor_content += f"File {i}: {component.name}.{component.extension}\n\n"

        # Save the descriptor.txt file
        with open(os.path.join(solution_folder, "descriptor.txt"), "w") as file:
            file.write(descriptor_content)

        # Save the components' content files in the solution folder
        for component in components:
            component_file_path = os.path.join(solution_folder, f"{component.name}.{component.extension}")
            with open(component_file_path, "w", encoding="utf-8") as file:
                file.write(component.content)

        print(Fore.GREEN + f"\nSolution '{solution_name}' imported successfully.")

        return solution

    def detect_language(self, extension):
        """
        Detect a component file content language based on the file extension.
        """
        language_map = {
            "py": "python",
            "sh": "bash",
            "bat": "batch",
            "ps1": "powershell",
            "js": "javascript",
            "txt": "text",
            "json": "json",
            "md": "markdown",
            "html": "html",
            "css": "css",
            "yaml": "yaml",
            "yml": "yaml",
            "toml": "toml"
        }
        return language_map.get(extension, "unknown")