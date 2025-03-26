import os
import toml
from datetime import datetime
from component import Component

class Solution:
    def __init__(self, name, components=None, execution_time=0):
        self.name = name
        self.description = ""
        self.semantic_description = ""
        self.components = components or []
        self.execution_time = execution_time
        self.status = 'PENDING'
        self.result_description = ""
        self.folder = ""

    def execute(self):
        """
        Executes all Python components in the solution.
        Non-Python components are skipped automatically.
        """
        try:
            start_time = datetime.now()
            for component in self.components:
                component.execute()
            
            # Update solution status based on component statuses
            if all(component.status == 'SUCCESS' for component in self.components if component.language == "python"):
                self.status = 'SUCCESS'
                self.result_description = 'All Python components executed successfully.'
            elif any(component.status == 'ERROR' for component in self.components):
                self.status = 'ERROR'
                self.result_description = 'One or more components failed during execution.'
            else:
                self.status = 'PARTIAL'
                self.result_description = 'Some components were skipped or not executed.'
            
            self.execution_time = (datetime.now() - start_time).total_seconds()
        except Exception as e:
            self.status = 'ERROR'
            self.result_description = f"An error occurred during solution execution: {str(e)}"

    def to_dict(self):
        """
        Converts the solution object to a dictionary representation.
        """
        return {
            'name': self.name,
            'description': self.description,
            'semantic_description': self.semantic_description,
            'components': [component.to_dict() for component in self.components],
            'execution_time': self.execution_time,
            'status': self.status,
            'result_description': self.result_description,
            'folder': self.folder
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a solution object from a dictionary representation.
        """
        name = data['name']
        components = [Component.from_dict(component_data) for component_data in data.get('components', [])]
        execution_time = data.get('execution_time', 0)
        
        solution = cls(name, components, execution_time)
        solution.description = data.get('description', '')
        solution.semantic_description = data.get('semantic_description', '')
        solution.status = data.get('status', 'PENDING')
        solution.result_description = data.get('result_description', '')
        solution.folder = data.get('folder', '')
        return solution

    def add_component(self, component):
        """
        Adds a component to the solution.
        """
        self.components.append(component)

    def export_solution_to_toml(self, output_dir="exports"):
        """
        Exports the solution to a TOML file.
        """
        os.makedirs(output_dir, exist_ok=True)
        data = {
            "solution": self.to_dict(),
            "created_at": datetime.now().isoformat()
        }
        file_path = os.path.join(output_dir, f"{self.name}.toml")
        with open(file_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
        return file_path

    def __str__(self):
        return (f"Solution: {self.name}, Execution Time: {self.execution_time}, "
                f"Components: {len(self.components)}, Status: {self.status}")