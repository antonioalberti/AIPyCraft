# solution_shower.py

from colorama import init, Fore, Style

class SolutionDisplayer:
    def __init__(self, solutions):
        self.solutions = solutions

    def show_solution(self):
        if not self.solutions:
            print(Fore.RED + "No solutions available.")
            return

        print(Fore.BLUE + "\nAvailable solutions:")
        for i, solution in enumerate(self.solutions, start=1):
            print(f"{i}. {solution.name}")

        while True:
            choice = input(Fore.YELLOW + "\nEnter the number of the solution you want to see (or 'q' to quit): ")
            if choice.lower() == 'q':
                return

            try:
                index = int(choice) - 1
                if 0 <= index < len(self.solutions):
                    selected_solution = self.solutions[index]
                    self.display_solution_details(selected_solution)
                    break
                else:
                    print(Fore.RED + "Invalid solution number. Please try again.")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a valid number.")

    def display_solution_details(self, solution):
        print(Fore.BLUE + f"\n\nFolder: {solution.folder}")
        print(Fore.BLUE + f"Semantic Descriptor: {solution.semantic_description}")
        print(Fore.BLUE + f"Execution Time: {solution.execution_time}")
        print(Fore.BLUE + f"Status: {solution.status}")
        print(Fore.BLUE + f"Result Description: {solution.result_description}")

        print(Fore.BLUE + f"\nComponents:")
        for component in solution.components:
            print(Fore.BLUE + f"\n\nName: {component.name}")
            print(Fore.BLUE + f"Extension: {component.extension}")
            print(Fore.BLUE + f"Language: {component.language}")  # Display the language of the component
            print(Fore.BLUE + f"Code:")
            print(Fore.WHITE + f"{component.code}")
            print(Fore.BLUE + f"Semantic Description: {component.semantic_description}")

        print(Style.RESET_ALL)