# solution.py

import os
import toml
from datetime import datetime

class Solution:
    def __init__(self, name, description, components=None):
        self.name = name
        self.description = description
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
        except Exception as e:
            self.status = 'ERROR'
            self.result_description = f"An error occurred during solution execution: {str(e)}"

    def to_dict(self):
        return {
            'name': self.name,
            'components': [component.to_dict() for component in self.components],
            'execution_time': self.execution_time,
            'status': self.status,
            'result_description': self.result_description
        }

    @classmethod
    def from_dict(cls, data):
        name = data['name']
        components = [Component.from_dict(component_data) for component_data in data['components']]
        execution_time = data.get('execution_time', 0)
        solution = cls(name, components, execution_time)
        solution.status = data.get('status', 'PENDING')
        solution.result_description = data.get('result_description', "")
        return solution

    def add_component(self, component):
        self.components.append(component)

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "components": [c.to_dict() for c in self.components]
        }


def export_solution_to_toml(solution, output_dir="exports"):
    os.makedirs(output_dir, exist_ok=True)
    data = {
        "solution": {
            "name": solution.name,
            "description": solution.description,
            "created_at": datetime.now().isoformat()
        }
    }
    file_path = os.path.join(output_dir, f"{solution.name}.toml")
    with open(file_path, "w", encoding="utf-8") as f:
        toml.dump(data, f)
    return file_path

    def __str__(self):
        return (f"Solution: {self.name}, Execution Time: {self.execution_time}, "
                f"Components: {len(self.components)}, Status: {self.status}")

