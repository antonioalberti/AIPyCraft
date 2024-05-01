import os
from solution import Solution
from component import Component
from ai_connector import AIConnector
from prompt_to_create_a_solution import get_prompt
from colorama import init, Fore, Style
from ai_code_parser import AICodeParser


class SolutionCreator:
    def __init__(self, solutions_folder):
        self.solutions_folder = solutions_folder
        self.solution = None
        self.ai_connector = AIConnector()
        self.code_parser = AICodeParser()

    def create_new_solution(self):
        solution_name = input(Fore.BLUE + "\n\nEnter a name for the new solution: ")
        solution_description = input("Enter a high-level description of the solution: ")

        self.solution = Solution(solution_name, [])
        

        solution_directory = os.path.join(self.solutions_folder, solution_name)
        os.makedirs(solution_directory, exist_ok=True)

        self.solution.folder = solution_directory
        
        self.solution.semantic_description = solution_description

        interaction_count = 1
        while True:
            print(f"\nSolution Creator - Interaction {interaction_count}:")
            
            # Generate a prompt for the AI to create the solution and components
            prompt = get_prompt(solution_name, solution_description)

            # Send the prompt to the AI and get the response
            response = self.ai_connector.send_prompt(prompt)

            print("\nAI-generated solution and components:")
            print(response)

            # Ask the human operator for approval
            approval = input("\nDo you approve the solution and components? (yes/no): \n\n")

            if approval.lower() == "yes":
                # Save the approved solution description to a file
                with open(os.path.join(solution_directory, f"descriptor.txt"), "w") as file:
                    file.write(response)
                break
            else:
                # Ask the user for feedback on why they rejected the solution
                feedback = input("Please provide feedback on why you rejected the solution: ")

                # Save the rejected solution description and feedback to a file
                with open(os.path.join(solution_directory, f"rejected_solution_interaction_{interaction_count}.txt"), "w") as file:
                    file.write(f"Rejected Solution:\n{response}\n\nFeedback:\n{feedback}")

                # Update the solution description with the user's feedback
                solution_description += f"\n\nUser Feedback (Interaction {interaction_count}):\n{feedback}"

            interaction_count += 1

        # Create components recursively
        self.create_components(response, solution_directory, interaction_count)

        return self.solution

    def create_components(self, solution_description, solution_directory, interaction_count):
        components = self.extract_component_descriptions(solution_description)

        for component_info in components:
            component_description = component_info['component_description']
            file_name = component_info['file_name']
            extension = component_info['extension']
            print(f"\nComponent Interaction {interaction_count}:")

            while True:
                # Generate a prompt for the AI to create the component implementation
                prompt = f"Component: {component_description}\n\nPlease provide a Python implementation for the component {file_name}.{extension}.\n"

                # Send the prompt to the AI and get the response
                response = self.ai_connector.send_prompt(prompt)

                #print("\nAI-generated component implementation\n")
                #print(response)

                # Parse the code from the AI-generated component implementation
                code = self.code_parser.parse_code(response)

                if code:
                    # Ask the human operator for approval
                    ##approval = input("Do you approve the component implementation? (yes/no): ")

                    approval = "yes"

                    if approval.lower() == "yes":
                        # Save the approved component implementation to a file
                        file_path = os.path.join(solution_directory, f"{file_name}.{extension}")
                        self.code_parser.save_code_to_file(code, file_path)

                        # Create a Component object with the file name, extension, and component description
                        component = Component(file_name, extension, code, component_description)
                        component.extension = extension
                        self.solution.add_component(component)
                        break
                    else:
                        # Ask the user for feedback on why they rejected the component implementation
                        feedback = input("Please provide feedback on why you rejected the component implementation: ")

                        # Save the rejected component implementation and feedback to a file
                        with open(os.path.join(solution_directory, f"rejected_component_interaction_{interaction_count}.txt"), "w") as file:
                            file.write(f"Component Description:\n{component_description}\n\nRejected Implementation:\n{response}\n\nFeedback:\n{feedback}")

                        # Update the prompt with the user's feedback
                        prompt += f"\n\nUser Feedback:\n{feedback}"
                else:
                    print("Failed to parse the component implementation from the AI response.")

                interaction_count += 1

        return interaction_count

    def extract_component_descriptions(self, solution_description):
        components = []
        lines = solution_description.split("\n")
        component_description = ""
        file_name = ""
        extension = ""

        for line in lines:
            line = line.strip()
            if line.startswith("Component "):
                if component_description:  # If moving to next component, save the previous one
                    components.append({
                        "component_description": component_description,
                        "file_name": file_name,
                        "extension": extension
                    })
                    print(f"\nAdded component: {component_description}, File: {file_name}.{extension}\n")
                component_description = line.split(":")[1].strip()
                file_name = ""
                extension = ""
            elif line.startswith("File "):
                file_info = line.split(":")[1].strip().split(".")
                file_name = file_info[0]
                extension = file_info[1] if len(file_info) > 1 else ""

        # Append the last component if any
        if component_description:
            components.append({
                "component_description": component_description,
                "file_name": file_name,
                "extension": extension
            })
            print(f"\nAdded component: {component_description}, File: {file_name}.{extension}\n")

        return components