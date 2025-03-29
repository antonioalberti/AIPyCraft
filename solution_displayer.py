# solution_shower.py

from colorama import init, Fore, Style

class SolutionDisplayer:
    def __init__(self, solutions):
        self.solutions = solutions

    def show_solution(self):
        if not self.solutions:
            print(Fore.RED + "No solutions available." + Style.RESET_ALL)
            return

        print(Fore.BLUE + "\nAvailable solutions:" + Style.RESET_ALL)
        for i, solution in enumerate(self.solutions, start=1):
            print(Fore.GREEN + f"{i}. {solution.name}" + Style.RESET_ALL)

        while True:
            choice = input(Fore.YELLOW + "\nEnter the number of the solution you want to see (or 'q' to quit): " + Style.RESET_ALL)
            if choice.lower() == 'q':
                return

            try:
                index = int(choice) - 1
                if 0 <= index < len(self.solutions):
                    selected_solution = self.solutions[index]
                    self.display_solution_details(selected_solution)
                    break
                else:
                    print(Fore.RED + Style.DIM + "Invalid solution number. Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + Style.DIM + "Invalid input. Please enter a valid number." + Style.RESET_ALL)

    def display_solution_details(self, solution):
        print(Fore.BLUE + f"\n\nFolder: {solution.folder}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Semantic Descriptor: {solution.semantic_description}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Execution Time: {solution.execution_time}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Status: {solution.status}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Result Description: {solution.result_description}" + Style.RESET_ALL)

        print(Fore.BLUE + f"\nComponents:" + Style.RESET_ALL)
        for component in solution.components:
            print(Fore.BLUE + f"\n\nName: {component.name}" + Style.RESET_ALL)
            print(Fore.BLUE + f"Extension: {component.extension}" + Style.RESET_ALL)
            print(Fore.BLUE + f"Language: {component.language}" + Style.RESET_ALL)
            print(Fore.BLUE + f"Content:" + Style.RESET_ALL)
            print(Fore.WHITE + f"{component.content}" + Style.RESET_ALL)
            print(Fore.BLUE + f"Semantic Description: {component.semantic_description}" + Style.RESET_ALL)

        print(Style.RESET_ALL)