import os
import re
import queue
import threading
from colorama import init, Fore, Style
from ai_connector import AIConnector

class ThreadedSolutionCorrector:
    """
    This class uses a threaded approach to correct the components of a solution 
    in parallel, sending prompts to an AI model and writing back updated code 
    (if required) to the component files.

    Usage:
        1. Instantiate ThreadedSolutionCorrector().
        2. Call threaded_correct_solution(solution).

    Where 'solution' has:
        - name (str)
        - folder (str) : path where components are stored
        - status (str) : e.g. 'ERROR'
        - result_description (str) : error message
        - semantic_description (str) : text describing solution purpose
        - components (list of objects), each with attributes:
            - name (str)
            - extension (str)
            - code (str)
    """

    def __init__(self):
        self.ai_connector = AIConnector()

    def _worker_correct_component(
        self, 
        component,
        instructions,
        solution_name,
        solution_description,
        error_message,
        return_queue
    ):
        """
        Thread worker function to correct the code of one component.
        Builds a prompt, calls the AI, and puts the AI response in a queue.
        """
        prompt = (
            f"The Solution {solution_name} created from the following Solution description "
            f"encountered an error during execution and you need to correct it.\n\n"
            f"The solution aim is to: {solution_description}\n\n"
            f"{error_message}\n\n"
            f"Please analyze the following Component:\n\n"
            f"{component.name}\n\nCode:\n{component.code}\n\n"
            "IMPORTANT 1: If SOME corrections are required, send ONLY the corrected Python code of this Component. "
            "In addition, do not rename the file name. Do nothing else.\n"
            "IMPORTANT 2: If NO corrections are required, do not send any code. Send just a word saying \"NO\".\n"
            "IMPORTANT 3: Do not remove the function if __name__ == \"__main__\" from the main.py file."
        )

        # Make the request to the AI, removing assistant_id usage
        response = self.ai_connector.send_prompt(
            instructions=instructions,
            prompt=prompt
        )

        # Put the result into a queue so the main thread can process it
        return_queue.put((component.name, response))

    def threaded_correct_solution(self, solution):
        """
        Corrects a solution using multithreading: 
        one thread per component in 'ERROR' mode.
        """
        if solution.status != 'ERROR':
            print("The solution does not have an 'ERROR' status. No correction needed.")
            return

        print(f"\nCorrecting solution: {solution.name}\n")

        # The error message from the solution (why it's in 'ERROR')
        error_message = solution.result_description

        instructions = """Context:

You are going to correct Python codes for Components of a Solution developed in Python.
The Solution has a descriptor that is going to be provided to you in the prompts.
Each Component is a Python file that solves a specific problem.

Instructions:

You need to correct the code of the Component that is causing a certain error.
In addition, you need to adjust the other components correspondingly to keep consistency.
The main.py program must be able to import all the required classes.
The last Component will always be named as main.py program. Therefore, always put a if __name__ == "__main__":
at the end of the main.py program, initializing and running the solution.
Whenever you correct components, check the consistency of attributes. This is one of the main problems in the code.
Keep the code of each Component coherent and compatible with the others in the same solution.
Check consistency of naming and number of parameters in the components.

Expected answer format:

1. If SOME corrections are required, send ONLY the corrected Python code of this Component.
In addition, do not rename the file name. Do nothing else.

2. If NO corrections are required, do not send any code. Send just a word saying "NO".
"""

        # The queue collects results from each worker thread
        return_queue = queue.Queue()
        threads = []

        # Create and start a thread for each component
        for component in solution.components:
            t = threading.Thread(
                target=self._worker_correct_component,
                args=(component, instructions, solution.name, solution.semantic_description, error_message, return_queue)
            )
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for t in threads:
            t.join()

        # Process responses from each component
        while not return_queue.empty():
            component_name, response = return_queue.get()

            print(Fore.YELLOW + f"\n--- AI Response for component '{component_name}' ---")
            print(Style.RESET_ALL + response + "\n")

            # Extract code blocks
            code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
            if not code_blocks:
                print(Fore.BLUE + f"No code blocks found for '{component_name}'.")
                print(Style.RESET_ALL)
                continue

            # Use the first code block
            updated_code = code_blocks[0]

            # Find the matching component to update code on disk
            for comp in solution.components:
                if comp.name == component_name:
                    component_file_path = os.path.join(solution.folder, f"{comp.name}.{comp.extension}")
                    try:
                        with open(component_file_path, 'w', encoding='utf-8') as file:
                            file.write(updated_code)
                        comp.code = updated_code
                        print(Fore.GREEN + f"Component '{comp.name}' file updated successfully.")
                    except Exception as e:
                        print(Fore.RED + f"Error updating component '{comp.name}': {str(e)}")
                    finally:
                        print(Style.RESET_ALL)
                    break
