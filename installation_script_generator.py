import os
import subprocess
from ai_connector import AIConnector

class InstallationScriptGenerator:
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder
        self.ai_connector = AIConnector()

    def generate_installation_scripts(self, solution):
        solution_directory = os.path.join(self.solutions_folder, solution.name)
        print(f"This is the solution directory: {solution_directory}")
        os.makedirs(solution_directory, exist_ok=True)

        requirements_file_path = os.path.join(solution_directory, "requirements.txt")

        # Generate the prompt for the AI to determine the necessary packages
        prompt = f"Given the following solution components:\n\n"
        for component in solution.components:
            prompt += f"Component: {component.name}\nCode:\n{component.code}\n\n"
        prompt += "Please provide a list of the necessary Python packages with compatible versions that need to be installed via pip in order to run this solution.\n"
        prompt += "Provide only the package names, one per line, without any additional text or explanations.\n"
        prompt += "For instance, colorama==0.4.6, numpy==1.19.5, etc. Be careful to provide packages that are mutually compatible.\n"

        # Send the prompt to the AI using the AIConnector and get the response
        response = self.ai_connector.send_prompt(prompt)

        # Parse the AI's response to extract the package names
        packages = response.strip().split("\n")
        print(f"These are the required packages: {packages}")

        # Remove markers, duplicates, and invalid package names from the package list
        packages = [package.split("==")[0] for package in packages if "==" in package]
        packages = list(set(packages))

        # Write the packages to the requirements.txt file
        with open(requirements_file_path, 'w') as req_file:
            for package in packages:
                req_file.write(package.strip() + '\n')

        # Ask the user to select the installation method
        while True:
            installation_method = input("Select the installation method (pip/conda/quit): ")
            if installation_method.lower() in ['pip', 'conda', 'quit']:
                break
            else:
                print("Invalid installation method. Please enter 'pip', 'conda', or 'quit'.")

        if installation_method.lower() == 'quit':
            print("Installation process aborted.")
            return

        if installation_method.lower() == 'pip':
            # Create a virtual environment within the solution directory
            venv_directory = os.path.join(solution_directory, "venv")
            subprocess.run(["python", "-m", "venv", venv_directory])

            # Install the packages using pip within the virtual environment
            subprocess.run([os.path.join(venv_directory, "bin", "pip"), "install", "-r", requirements_file_path])
            print(f"\n\nPackages installed using pip in {venv_directory}\n\n")
        else:
            # Check if conda is installed
            try:
                subprocess.run(["conda", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Create a Conda environment within the solution directory
                subprocess.run(["conda", "create", "--prefix", os.path.join(solution_directory, "conda_env"), "--file", requirements_file_path, "-y"])
                print(f"\n\nConda environment created and packages installed in {os.path.join(solution_directory, 'conda_env')}\n\n")
            except FileNotFoundError:
                print("Conda is not installed. Falling back to using pip.")
                # Create a virtual environment within the solution directory
                venv_directory = os.path.join(solution_directory, "venv")
                subprocess.run(["python", "-m", "venv", venv_directory])

                # Install the packages using pip within the virtual environment
                subprocess.run([os.path.join(venv_directory, "bin", "pip"), "install", "-r", requirements_file_path])
                print(f"\n\nPackages installed using pip in {venv_directory}\n\n")
