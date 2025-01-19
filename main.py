# main.py

import json
import threading
import os
import shutil
from dotenv import load_dotenv
from colorama import init, Fore, Style
from ai_connector import AIConnector
from solution import Solution
from solution_creator import SolutionCreator
from solution_loader import SolutionLoader
from solution_runner import SolutionRunner
from solution_shower import SolutionShower
from installation_script_generator import InstallationScriptGenerator
from solution_correcting import SolutionCorrecting
from solution_feature_adding import SolutionFeatureAdding
from solution_importer import SolutionImporter

# Load environment variables from .env file
load_dotenv()

# Initialize colorama
init()

class Dispatcher:
    """
    The `Dispatcher` class is responsible for managing the lifecycle of solutions, including loading, creating, saving, and running solutions.
    
    The `Dispatcher` class has the following methods:
    
    - `__init__()`: Initializes the `Dispatcher` instance, setting up the necessary dependencies such as `SolutionLoader`, `SolutionSaver`, and `SolutionRunner`.
    - `run()`: Enters a command-line loop, allowing the user to interact with the `Dispatcher` by selecting options to load, create, save, and run solutions.
    """
    
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder
        self.solutions = []
        self.current_solution = None
        self.solution_loader = SolutionLoader(solutions_folder)
        self.solution_runner = SolutionRunner()
        self.solution_shower = SolutionShower(self.solutions)
        self.script_generator = InstallationScriptGenerator(solutions_folder)
        self.solution_correcting = SolutionCorrecting()
        self.solution_feature_adding = SolutionFeatureAdding()
        self.solution_importer = SolutionImporter(solutions_folder)

    def run(self):
        while True:
            print(Fore.GREEN + "\n\n1. Load a solution from a folder")
            print(Fore.GREEN + "2. Create a new solution")
            print(Fore.GREEN + "3. Install a solution environment")
            print(Fore.GREEN + "4. Run a solution")
            print(Fore.GREEN + "5. Show a solution details")
            print(Fore.GREEN + "6. Remove a solution folder (all files will be deleted)")
            print(Fore.GREEN + "7. Self-correct a solution")
            print(Fore.GREEN + "8. Manually improve a solution")
            print(Fore.GREEN + "9. Import a folder as a solution")
            print(Fore.GREEN + "10. Delete a solution (files will be preserved)")
            print(Fore.GREEN + "11. Exit")
            choice = input("Enter your choice (1-11): ")

            if choice == '1':
                solution_to_be_loaded = input("Enter the name of the solution to be loaded: ")
                file_path = os.path.join(self.solutions_folder, solution_to_be_loaded)
                solution = self.solution_loader.load_solution(solution_to_be_loaded, file_path)
                if solution:
                    self.solutions.append(solution)
                    self.current_solution = solution
                else:
                    print("Failed to load the solution.")

            elif choice == '2':
                solution_creator = SolutionCreator(self.solutions_folder)
                solution = solution_creator.create_new_solution()
                self.solutions.append(solution)
                self.current_solution = solution

            elif choice == '3':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    print(Fore.BLUE + "\nAvailable solutions:")
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")

                    while True:
                        choice = input(Fore.YELLOW + "\nEnter the number of the solution to install the environment for (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break

                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                self.script_generator.generate_installation_scripts(selected_solution)
                                break
                            else:
                                print(Fore.RED + "Invalid solution number. Please try again.")
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter a valid number.")

            elif choice == '4':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    print(Fore.BLUE + "\nAvailable solutions:")
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")

                    while True:
                        choice = input(Fore.YELLOW + "\nEnter the number of the solution to run (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break

                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                self.solution_runner.run_solution(selected_solution)
                                break
                            else:
                                print(Fore.RED + "Invalid solution number. Please try again.")
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter a valid number.")

            elif choice == '5':
                self.solution_shower.show_solution()

            elif choice == '6':
                solution_name = input("Enter the name of the solution to remove: ")
                solution_folder = os.path.join(self.solutions_folder, solution_name)
                if os.path.exists(solution_folder):
                    shutil.rmtree(solution_folder)
                    print(f"\nSolution '{solution_name}' removed successfully.\n")
                    
                    # Remove the Solution object from the solutions list
                    for solution in self.solutions:
                        if solution.name == solution_name:
                            self.solutions.remove(solution)
                            break
                else:
                    print(f"\nSolution '{solution_name}' not found.\n")

            elif choice == '7':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    print(Fore.BLUE + "\nAvailable solutions:")
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")

                    while True:
                        choice = input(Fore.YELLOW + "\nEnter the number of the solution to improve (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break

                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                self.solution_correcting.correct_solution(selected_solution)
                                break
                            else:
                                print(Fore.RED + "Invalid solution number. Please try again.")
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter a valid number.")

            elif choice == '8':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    print(Fore.BLUE + "\nAvailable solutions:")
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")

                    while True:
                        choice = input(Fore.YELLOW + "\nEnter the number of the solution to add a feature to (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break

                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                self.solution_feature_adding.add_feature_to_solution(selected_solution)
                                break
                            else:
                                print(Fore.RED + "Invalid solution number. Please try again.")
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter a valid number.")

            elif choice == '9':
                solution_to_be_imported = input("Enter the name of the solution to be imported: ")
                folder_path = input("Enter the path to the folder to import as a solution: ")
                solution = self.solution_importer.import_solution_from_folder(solution_to_be_imported,folder_path)
                if solution:
                    self.solutions.append(solution)
                    self.current_solution = solution

            elif choice == '10':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    print(Fore.BLUE + "\nAvailable solutions:")
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")

                    while True:
                        choice = input(Fore.YELLOW + "\nEnter the number of the solution to delete (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break

                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                self.solutions.remove(selected_solution)
                                print(Fore.GREEN + f"\nSolution '{selected_solution.name}' deleted successfully from the program.")
                                break
                            else:
                                print(Fore.RED + "Invalid solution number. Please try again.")
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter a valid number.")

                
            elif choice == '11':
                break

            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    api_config = {
        # API configuration settings
        #
    }

    solutions_folder = input("Enter the solutions folder path: ")
    os.makedirs(solutions_folder, exist_ok=True)

    dispatcher = Dispatcher(solutions_folder)
    dispatcher.run()