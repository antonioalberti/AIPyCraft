import os
from solution import Solution
from component import Component
from ai_connector import AIConnector
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

        instructions = f"""You are going to create a componentized Solutions using Python. 

Context:

The Solutions are composed by Components.  
Each Component will be designed as a piece of code that solves a specific problem. 
Make the Solution with the minimum number of Components possible. 
The last Component will always be a main.py program. 
The previous Components are classes to be initiatized in the main.py program. 
Therefeore, the main.py program must be able to import all the required classes. 
After every Component, put the file associatated with the Component using the label File. 
All the Components should be numbered and separated by a new line.
This will make the Solution modular and each Component is self-contained.  
All files need to have different names obrigatory.

Expected answer format:

For the response parser to be possible, each Component description must be on a single line, 
starting with the word "Component N:", where N is the number of the Component. 
Do not send the code now. Add a blank line and describe the Components required to implement this Solution. 
After every Component, put the file associatated with the Component using the label File.  
All the Components should be numbered and separated by a new line. 
This will make the Solution modular and each Component is self-contained.  
All files need to have different names obrigatory. 
For the response parser to be possible, each Component description must be on a single line, 
starting with the word "Component N:", where N is the number of the Component. 
The description of a Component using a single paragraph. 

Here is just an example of a Solution with 3 Components, but you always should keep the number of Components as low as possible:

Description: Plot Mandelbrot fractal with resolution 1000x1000 and color mapping.

Component 1: Create a class MandelbrotFractal that will handle the calculations and generation of the Mandelbrot fractal. Include methods to determine the escape time for each point in the fractal, based on the Mandelbrot set formula. 
This class will be in a file named mandelbrot.py.

File 1: mandelbrot.py

Component 2: Create a class FractalPlotter that will handle the plotting of the Mandelbrot fractal. Include methods to generate the plot with customizable resolution and color mapping. 
This class will be in a file named fractal_plotter.py.

File 2: fractal_plotter.py

Component 3: Implement a main program in a file named main.py that will instantiate the MandelbrotFractal class and the FractalPlotter class. 
Use these classes to calculate the escape times and plot the Mandelbrot fractal. Allow the user to specify the resolution of the plot and the color mapping. 
Include a if __name__ == "__main__": at the end of the main.py program, inializing and running the all the Solution.

File 3: main.py
"""

        interaction_count = 1
        while True:
            print(f"\nCreating the solution {solution_name} - Interaction {interaction_count}:")
            
            # Generate a prompt for the AI to create the solution and components
            prompt = f"""We are going to create the Solution {solution_name} with the following decription: \n\n{solution_description}\n\n"""
            
            print(f"\n[DEBUG] Prompt being sent to the AI:\n{prompt}")

            print("\nThis is the propmt being sent to the AI:\n")
            print(prompt)

            # Send the prompt to the AI and get the response
            response = self.ai_connector.send_prompt(instructions,prompt)

            print("\nAI-generated solution and components:")
            print(response)

            # Ask the human operator for approval
            approval = input("\nDo you approve the solution and its components? (yes/no): \n\n")

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

            instructions = """Context for creating the code of a Solution:
        
        You are going to create the Python code for a Component of a solution. 

        Instructions:  

        A Component has exactly on file.
        All Components need to have different names obrigatory.
        The last Component will always named as main.py program. 
        Therefore, always put a if __name__ == "__main__": at the end of the main.py program, 
        inializing and running the all the solution.
        The previous Components are classes to be initiatized in the main.py program. 
        Therefeore, the main.py program must be able to import all the required classes.
        Do not take user parameters as input in the main.py.

        Expected answer format:

        A Python code for just one component (file). Keep the code coherent and compatible to other components of the same solution. 
        Use the same names of the classes and functions of the previous Components, but do not repeat code in more than one Component.
        
        """

            while True:
                # Generate a prompt for the AI to create the component implementation
                prompt = f"""We are going to create the Solution {self.solution.name} with the following decription: \n\n{solution_description}\n\n"""
                prompt += f"{component_description}\n\nPlease provide a Python implementation for the Component {file_name}.{extension}.\n"

                print("\nThis is the propmt being sent to the AI:\n")
                print(prompt)

                # Send the prompt to the AI and get the response
                response = self.ai_connector.send_prompt(instructions, prompt)

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