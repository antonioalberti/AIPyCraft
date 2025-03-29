# solution_loader.py

import os
from solution import Solution
from component import Component
from colorama import Fore, Style

class SolutionLoader:
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder

    def load_solution(self, solution_name, file_path):
        solution_folder = os.path.join(self.solutions_folder, file_path)

        if not os.path.exists(solution_folder):
            print(f"{Fore.LIGHTRED_EX}\n\nThe specified solution '{solution_name}' does not exist.\n\n{Style.RESET_ALL}")
            return None

        # Read the approved solution file
        descriptor_file = os.path.join(solution_folder, "model.txt")
        if not os.path.exists(descriptor_file):
            print(f"{Fore.LIGHTYELLOW_EX}\n\nApproved solution file not found for '{solution_name}'.\n\n{Style.RESET_ALL}")
            return None

        with open(descriptor_file, "r") as file:
            descriptor_content = file.read()

        # Parse the approved solution content to extract component information
        components = []
        semantic_description = ""
        lines = descriptor_content.split("\n")
        component_name = ""
        component_description = ""
        extension = ""

        for line in lines:
            line = line.strip()
            if line.startswith("Description:"):
                semantic_description = line.split(":")[1].strip()
            elif line.startswith("Component "):
                if component_name and component_description:
                    component_code_file = os.path.join(solution_folder, f"{component_name}.{extension}")
                    if os.path.exists(component_code_file):
                        with open(component_code_file, "r") as file:
                            component_code = file.read()
                        component = Component(component_name, extension, component_code, component_description)
                        component.extension = extension
                        components.append(component)
                    else:
                        print(f"{Fore.LIGHTRED_EX}\n\nComponent code file not found for '{component_name}' in solution '{solution_name}'.\n\n{Style.RESET_ALL}")
                component_description = line.split(":")[1].strip()
            elif line.startswith("File "):
                file_info = line.split(":")[1].strip().split(".")
                component_name = file_info[0]
                extension = file_info[1] if len(file_info) > 1 else ""

        if component_name and component_description:
            component_code_file = os.path.join(solution_folder, f"{component_name}.{extension}")
            if os.path.exists(component_code_file):
                with open(component_code_file, "r") as file:
                    component_code = file.read()
                component = Component(component_name, extension, component_code, component_description)
                component.extension = extension
                components.append(component)
            else:
                print(f"{Fore.LIGHTRED_EX}\n\nComponent code file not found for '{component_name}' in solution '{solution_name}'.\n\n{Style.RESET_ALL}")

        solution = Solution(solution_name, components)
        solution.folder = solution_folder
        solution.semantic_description = semantic_description

        print(f"{Fore.LIGHTGREEN_EX}\n\nSolution '{solution_name}' loaded successfully.\n\n{Style.RESET_ALL}")
        return solution