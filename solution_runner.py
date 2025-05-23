# solution_runner.py

import subprocess
import traceback
import os
from colorama import init, Fore, Style

class SolutionRunner:
    def run_solution(self, solution):
        if solution is None:
            print(Fore.LIGHTRED_EX + "No solution selected." + Style.RESET_ALL)
            return

        print(Fore.LIGHTBLUE_EX + f"\n\nRunning solution: {solution.name}" + Style.RESET_ALL)

        main_component = None
        for component in solution.components:
            if component.name.lower() == "main" and component.language == "python":
                main_component = component
                break

        if main_component is None:
            print(Fore.LIGHTRED_EX + "No 'main.py' Python component found in the solution." + Style.RESET_ALL)
            return

        print(Fore.LIGHTCYAN_EX + f"\n\nExecuting component: {main_component.name}.{main_component.extension}\n\n" + Style.RESET_ALL)

        execution_log = ""

        try:
            # Get the file path of the main component
            main_file_path = os.path.join(solution.folder, f"{main_component.name}.{main_component.extension}")

            # Check if the virtual environment exists
            venv_path = os.path.join(solution.folder, "venv")
            if not os.path.exists(venv_path):
                print(Fore.LIGHTRED_EX + "Virtual environment not found. Please run the installation script first." + Style.RESET_ALL)
                solution.status = 'ERROR'
                execution_log += "Virtual environment not found. Please run the installation script first.\n"
                return

            if os.name == 'nt':  # Windows
                # Directly execute the python interpreter from the venv
                python_exe = os.path.join(venv_path, "Scripts", "python.exe")
                if not os.path.exists(python_exe):
                     print(Fore.LIGHTRED_EX + f"Python executable not found in venv: {python_exe}" + Style.RESET_ALL)
                     solution.status = 'ERROR'
                     execution_log += f"Python executable not found in venv: {python_exe}\n"
                     return
                command = [python_exe, main_file_path]
                # No need for shell=True when executing directly
                result = subprocess.run(command, capture_output=True, text=True, check=False) # check=False to handle non-zero exit codes manually
            else:  # Unix-based systems (keep existing logic, though direct execution is also an option here)
                activate_script = os.path.join(venv_path, "bin", "activate")
                command = f'source "{activate_script}" && python "{main_file_path}"'
                result = subprocess.run(command, capture_output=True, text=True, shell=True, executable="/bin/bash")

            # Print the captured output and error streams
            print(Fore.GREEN + "This is the output of the solution main.py run:" + Style.RESET_ALL)
            print(Fore.WHITE + result.stdout + Style.RESET_ALL)
            execution_log += f"Output:\n{result.stdout}\n"

            if result.stderr:
                print(Fore.LIGHTRED_EX + "Error:" + Style.RESET_ALL)
                print(Fore.LIGHTRED_EX + "Error:" + Style.RESET_ALL)
                print(Fore.LIGHTRED_EX + result.stderr + Style.RESET_ALL)
                execution_log += f"Error:\n{result.stderr}\n"
                # Don't set status here yet, check return code below

            # Check return code AND stderr to determine status
            if result.returncode != 0 or result.stderr:
                solution.status = 'ERROR'
                if result.returncode != 0 and not result.stderr: # Add note if only return code indicated error
                     error_msg = f"Process exited with non-zero status code: {result.returncode}"
                     print(Fore.LIGHTRED_EX + error_msg + Style.RESET_ALL)
                     execution_log += f"Error: {error_msg}\n"
            else:
                solution.status = 'SUCCESS'
        except Exception as e:
            solution.status = 'ERROR'
            error_traceback = traceback.format_exc()
            print(Fore.LIGHTRED_EX + "Error:" + Style.RESET_ALL)
            print(Fore.LIGHTRED_EX + error_traceback + Style.RESET_ALL)
            execution_log += f"Error:\n{error_traceback}\n"

        print(Fore.LIGHTMAGENTA_EX + f"\nSolution completed with status: {solution.status}\n" + Style.RESET_ALL)
        execution_log += f"\nSolution '{solution.name}' completed with status: {solution.status}\n"

        solution.result_description = execution_log

        print(Fore.LIGHTBLUE_EX + "\nSolution execution completed.\n" + Style.RESET_ALL)
