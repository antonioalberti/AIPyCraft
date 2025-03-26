# solution_runner.py

import subprocess
import traceback
import os
from colorama import init, Fore, Style

class SolutionRunner:
    def run_solution(self, solution):
        if solution is None:
            print(Fore.RED + "No solution selected.")
            return

        print(f"\n\nRunning solution: {solution.name}")

        main_component = None
        for component in solution.components:
            if component.name.lower() == "main" and component.language == "python":
                main_component = component
                break

        if main_component is None:
            print(Fore.RED + "No 'main.py' Python component found in the solution.")
            return

        print(Fore.RED + f"\n\nExecuting component: {main_component.name}.{main_component.extension}\n\n")

        execution_log = ""

        try:
            # Get the file path of the main component
            main_file_path = os.path.join(solution.folder, f"{main_component.name}.{main_component.extension}")

            # Check if the virtual environment exists
            venv_path = os.path.join(solution.folder, "venv")
            if not os.path.exists(venv_path):
                print(Fore.RED + "Virtual environment not found. Please run the installation script first.")
                solution.status = 'ERROR'
                execution_log += "Virtual environment not found. Please run the installation script first.\n"
                return

            if os.name == 'nt':  # Windows
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                command = f'cmd /c "{activate_script} && python "{main_file_path}""'
                result = subprocess.run(command, capture_output=True, text=True, shell=True)
            else:  # Unix-based systems
                activate_script = os.path.join(venv_path, "bin", "activate")
                command = f'source "{activate_script}" && python "{main_file_path}"'
                result = subprocess.run(command, capture_output=True, text=True, shell=True, executable="/bin/bash")            

            # Print the captured output and error streams
            print(Fore.GREEN + "Output:")
            print(result.stdout)
            execution_log += f"Output:\n{result.stdout}\n"

            if result.stderr:
                print(Fore.RED + "Error:")
                print(result.stderr)
                execution_log += f"Error:\n{result.stderr}\n"
                solution.status = 'ERROR'
            else:
                solution.status = 'SUCCESS'
        except Exception as e:
            solution.status = 'ERROR'
            error_traceback = traceback.format_exc()
            print(Fore.RED + "Error:")
            print(error_traceback)
            execution_log += f"Error:\n{error_traceback}\n"

        print(Fore.RED + f"\nSolution '{solution.name}' completed with status: {solution.status}\n")
        execution_log += f"\nSolution '{solution.name}' completed with status: {solution.status}\n"

        solution.result_description = execution_log

        print("\nSolution execution completed.\n")