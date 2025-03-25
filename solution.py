# solution.py

import os
import toml
from datetime import datetime

class Solution:
    def __init__(self, name, description, components=None):
        self.name = name
        self.description = description
        self.components = components or []

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
