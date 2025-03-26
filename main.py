# main.py

import json
import threading
import os
import shutil
from dotenv import load_dotenv
from colorama import init, Fore, Style
from logger import logger
from ai_connector import AIConnector
from solution import Solution
from solution_creator import SolutionCreator
from solution_loader import SolutionLoader
from solution_runner import SolutionRunner
from solution_displayer import SolutionDisplayer
from installation_script_generator import InstallationScriptGenerator
from solution_correcting import SolutionCorrecting
from solution_feature_adding import SolutionFeatureAdding
from solution_importer import SolutionImporter
from solution_updater import SolutionUpdater  

# Load environment variables from .env file
load_dotenv()

# Initialize colorama
init()

logger.info("AIPyCraft program started.")

class Dispatcher:
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder
        self.solutions = []
        self.current_solution = None
        self.solution_loader = SolutionLoader(solutions_folder)
        self.solution_runner = SolutionRunner()
        self.solution_displayer = SolutionDisplayer(self.solutions)
        self.script_generator = InstallationScriptGenerator(solutions_folder)
        self.solution_correcting = SolutionCorrecting()
        self.solution_feature_adding = SolutionFeatureAdding()
        self.solution_importer = SolutionImporter(solutions_folder)
        self.solution_updater = SolutionUpdater()

    def run(self):
        logger.info("Main menu started.")
        while True:
            print(Fore.GREEN + "\n\n1. Load a solution from a folder")
            print(Fore.GREEN + "2. Create a new solution")
            print(Fore.GREEN + "3. Install a solution environment")
            print(Fore.GREEN + "4. Run a solution")
            print(Fore.GREEN + "5. Show a solution details")
            print(Fore.GREEN + "6. Remove a solution folder (all files will be deleted)")
            print(Fore.GREEN + "7. Correct a solution")
            print(Fore.GREEN + "8. Alternative solution correction")
            print(Fore.GREEN + "9. Manually improve or correct a solution")
            print(Fore.GREEN + "10. Import a folder as a solution")
            print(Fore.GREEN + "11. Delete a solution (files will be preserved)")
            print(Fore.GREEN + "12. Export current solution to TOML")
            print(Fore.GREEN + "13. Exit")
            choice = input("Enter your choice (1-13): ")

            logger.info(f"User selected option: {choice}")

            if choice == '1':
                solution_to_be_loaded = input("Enter the name of the solution to be loaded: ")
                file_path = os.path.join(self.solutions_folder, solution_to_be_loaded)
                solution = self.solution_loader.load_solution(solution_to_be_loaded, file_path)
                if solution:
                    logger.info(f"Solution loaded: {solution_to_be_loaded}")
                    self.solutions.append(solution)
                    self.current_solution = solution
                else:
                    logger.warning(f"Failed to load solution: {solution_to_be_loaded}")

            elif choice == '2':
                solution_creator = SolutionCreator(self.solutions_folder)
                solution = solution_creator.create_new_solution()
                self.solutions.append(solution)
                self.current_solution = solution
                logger.info(f"New solution created: {solution.name}")

            elif choice == '3':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")
                    while True:
                        choice = input("Enter the number of the solution to install the environment for (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break
                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                logger.info(f"Installing environment for: {selected_solution.name}")
                                self.script_generator.generate_installation_scripts(selected_solution)
                                break
                        except ValueError:
                            pass

            elif choice == '4':
                if not self.solutions:
                    print("No solutions available. Please load or create a solution first.")
                else:
                    for i, solution in enumerate(self.solutions, start=1):
                        print(f"{i}. {solution.name}")
                    while True:
                        choice = input("Enter the number of the solution to run (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break
                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(self.solutions):
                                selected_solution = self.solutions[index]
                                logger.info(f"Running solution: {selected_solution.name}")
                                self.solution_runner.run_solution(selected_solution)
                                break
                        except ValueError:
                            pass

            elif choice == '5':

                logger.info("Showing details of the current solution")
                self.solution_displayer.show_solution()

            elif choice == '6':
                solution_name = input("Enter the name of the solution to remove: ")
                solution_folder = os.path.join(self.solutions_folder, solution_name)
                if os.path.exists(solution_folder):
                    shutil.rmtree(solution_folder)
                    logger.info(f"Solution removed: {solution_name}")
                    for solution in self.solutions:
                        if solution.name == solution_name:
                            self.solutions.remove(solution)
                            break

            elif choice == '7':
                for i, solution in enumerate(self.solutions, start=1):
                    print(f"{i}. {solution.name}")
                while True:
                    opt = input("Enter the number of the solution to correct (or 'q' to quit): ")
                    if opt.lower() == 'q':
                        break
                    try:
                        index = int(opt) - 1
                        if 0 <= index < len(self.solutions):
                            selected_solution = self.solutions[index]
                            logger.info(f"Correcting solution: {selected_solution.name}")
                            self.solution_correcting.correct_solution(selected_solution)
                            break
                    except ValueError:
                        pass

            elif choice == '8':
                for i, solution in enumerate(self.solutions, start=1):
                    print(f"{i}. {solution.name}")
                while True:
                    opt = input("Enter the number of the solution to apply alternative correction (or 'q' to quit): ")
                    if opt.lower() == 'q':
                        break
                    try:
                        index = int(opt) - 1
                        if 0 <= index < len(self.solutions):
                            selected_solution = self.solutions[index]
                            logger.info(f"Applying alternative correction: {selected_solution.name}")
                            self.solution_updater.update_solution(selected_solution)
                            break
                    except ValueError:
                        pass

            elif choice == '9':
                for i, solution in enumerate(self.solutions, start=1):
                    print(f"{i}. {solution.name}")
                while True:
                    choice = input("Enter the number of the solution to add a feature to (or 'q' to quit): ")
                    if choice.lower() == 'q':
                        break
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(self.solutions):
                            selected_solution = self.solutions[index]
                            logger.info(f"Adding feature to solution: {selected_solution.name}")
                            self.solution_feature_adding.add_feature_to_solution(selected_solution)
                            break
                    except ValueError:
                        pass

            elif choice == '10':
                solution_to_be_imported = input("Enter the name of the solution to be imported: ")
                folder_path = input("Enter the path to the folder to import as a solution: ")
                solution = self.solution_importer.import_solution_from_folder(solution_to_be_imported, folder_path)
                if solution:
                    logger.info(f"Solution imported: {solution.name}")
                    self.solutions.append(solution)
                    self.current_solution = solution

            elif choice == '11':
                for i, solution in enumerate(self.solutions, start=1):
                    print(f"{i}. {solution.name}")
                while True:
                    opt = input("Enter the number of the solution to delete (or 'q' to quit): ")
                    if opt.lower() == 'q':
                        break
                    try:
                        index = int(opt) - 1
                        if 0 <= index < len(self.solutions):
                            selected_solution = self.solutions[index]
                            logger.info(f"Deleting solution from program: {selected_solution.name}")
                            self.solutions.remove(selected_solution)
                            break
                    except ValueError:
                        pass

            elif choice == '12':
                if self.current_solution:
                    path = self.current_solution.export_solution_to_toml()
                    logger.info(f"Solution exported to TOML at: {path}")
                    print(Fore.GREEN + f"TOML file saved: {path}")
                else:
                    logger.warning("No solution currently selected.")
                    print(Fore.RED + "No solution currently selected.")

            elif choice == '13':
                logger.info("Exiting program.")
                break

            else:
                logger.warning(f"Invalid option: {choice}")


if __name__ == '__main__':
    api_config = {}
    solutions_folder = input("Enter the solutions folder path: ")
    os.makedirs(solutions_folder, exist_ok=True)
    logger.info(f"Solutions folder set: {solutions_folder}")
    dispatcher = Dispatcher(solutions_folder)
    dispatcher.run()
    logger.info("Program ended.")
