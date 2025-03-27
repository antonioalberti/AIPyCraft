# installation_script_generator.py

import os
import subprocess
from ai_connector import AIConnector
from colorama import Fore, Style, init

init(autoreset=True)

class InstallationScriptGenerator:
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder
        self.ai_connector = AIConnector()

    def generate_installation_scripts(self, solution):
        solution_directory = os.path.join(self.solutions_folder, solution.name)
        print(f"{Fore.BLUE}This is the solution directory: {solution_directory}")
        os.makedirs(solution_directory, exist_ok=True)

        requirements_file_path = os.path.join(solution_directory, "requirements.txt")

        instructions = """Context:

        You are going to determine the required Python packages for a Solution.

        Expected answer format:

        Provide only the required package names, one per line, without any additional text or explanations.
        Be careful to provide packages that are mutually compatible. Deal with versions to avoid incompatibilities.

        Example of answer (a list of package names, one per line):

        aiohttp==3.9.4
        aiosignal==1.3.1
        async-timeout==4.0.3
        attrs==23.2.0
        """

        # Filter Python components
        python_components = [component for component in solution.components if component.language == "python"]
        non_python_components = [component for component in solution.components if component.language != "python"]

        # Notify about non-Python components
        if non_python_components:
            print(f"{Fore.YELLOW}\nThe following non-Python components are part of the solution and must be handled manually:")
            for component in non_python_components:
                print(f"{Fore.YELLOW}- {component.name}.{component.extension} ({component.language})")

        # Generate the prompt for the AI to determine the necessary packages
        prompt = f"Given the following Python solution components:\n\n"
        for component in python_components:
            prompt += f"Component: {component.name}\n\Content:\n{component.content}\n\n"
        prompt += f"Solution Result Description:\n{solution.result_description}\n\n"
        prompt += "Please provide a list of the necessary Python packages that need to be installed via pip in order to run this Solution.\n"
        prompt += "IMPORTANT 1: Provide only the required package names, one per line, without any additional text or explanations. \n"
        prompt += "IMPORTANT 2: Do not forget to include the version of all packages.\n"
        prompt += "IMPORTANT 3: Be careful to provide packages that are mutually compatible. Deal with versions to avoid incompatibilities.\n\n"
        prompt += "Example of answer (a list of package names, one per line):\n\n"
        prompt += "aiohttp==3.9.4\n"
        prompt += "aiosignal==1.3.1\n"
        prompt += "async-timeout==4.0.3\n"
        prompt += "attrs==23.2.0\n"

        # Send the prompt to the AI using the AIConnector and get the response
        response = self.ai_connector.send_prompt(instructions, prompt)

        print(f"{Fore.CYAN}\n\nAI's response:\n")
        print(f"{response}")

        # Parse the AI's response to extract the package names
        packages = response.strip().split("\n")
        print(f"{Fore.GREEN}\n\nThese are the required packages: {packages}")

        # Remove markers, duplicates, and invalid package names from the package list
        packages = [package.strip() for package in packages if "==" in package]
        packages = list(set(packages))

        # Write the packages to the requirements.txt file
        with open(requirements_file_path, 'w') as req_file:
            for package in packages:
                req_file.write(package + '\n')

        # Ask the user to select the installation method
        while True:
            installation_method = input(f"{Fore.BLUE}Select the installation method (pip/conda/quit): ")
            if installation_method.lower() in ['pip', 'conda', 'quit']:
                break
            else:
                print(f"{Fore.RED}Invalid installation method. Please enter 'pip', 'conda', or 'quit'.")

        if installation_method.lower() == 'quit':
            print(f"{Fore.RED}Installation process aborted.")
            return

        if installation_method.lower() == 'pip':
            # Create a virtual environment within the solution directory
            venv_directory = os.path.join(solution_directory, "venv")
            subprocess.run(["python", "-m", "venv", venv_directory])

            # Install the packages using pip within the virtual environment
            if os.name == 'nt':  # Windows
                pip_executable = os.path.join(venv_directory, "Scripts", "pip.exe")
                subprocess.run([pip_executable, "install", "-r", requirements_file_path])
                print(f"{Fore.GREEN}\n\nPackages installed using pip in {venv_directory}\n\n")
            else:  # Unix-based systems
                activate_script = os.path.join(venv_directory, "bin", "activate")
                pip_executable = os.path.join(venv_directory, "bin", "pip")

                # Activate the virtual environment and install the packages using pip
                subprocess.run(f"source {activate_script} && {pip_executable} install -r {requirements_file_path}", shell=True, executable="/bin/bash")

                print(f"{Fore.GREEN}\n\nPackages installed using pip in {venv_directory}\n\n")
        else:
            # Check if conda is installed
            try:
                subprocess.run(["conda", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Create a Conda environment within the solution directory
                subprocess.run(["conda", "create", "--prefix", os.path.join(solution_directory, "conda_env"), "--file", requirements_file_path, "-y"])
                print(f"{Fore.GREEN}\n\nConda environment created and packages installed in {os.path.join(solution_directory, 'conda_env')}\n\n")
            except FileNotFoundError:
                print(f"{Fore.RED}Conda is not installed. Falling back to using pip.")
                # Create a virtual environment within the solution directory
                venv_directory = os.path.join(solution_directory, "venv")
                subprocess.run(["python", "-m", "venv", venv_directory])

                # Install the packages using pip within the virtual environment
                subprocess.run([os.path.join(venv_directory, "bin", "pip"), "install", "-r", requirements_file_path])
                print(f"{Fore.GREEN}\n\nPackages installed using pip in {venv_directory}\n\n")