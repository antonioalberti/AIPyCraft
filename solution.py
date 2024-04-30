# solution.py

from component import Component

class Solution:
    def __init__(self, name, components, execution_time=0):
        self.name = name
        self.semantic_description = ""
        self.components = components
        self.execution_time = execution_time
        self.status = 'PENDING'
        self.result_description = ""
        self.folder = ""

    def to_dict(self):
        return {
            'name': self.name,
            'components': [component.to_dict() for component in self.components],
            'execution_time': self.execution_time
        }

    @classmethod
    def from_dict(cls, data):
        name = data['name']
        components = [Component.from_dict(component_data) for component_data in data['components']]
        execution_time = data.get('execution_time', 0)
        return cls(name, components, execution_time)

    def add_component(self, component):
        self.components.append(component)

    def remove_component(self, component):
        self.components.remove(component)

    def __str__(self):
        return f"Solution: {self.name}, Execution Time: {self.execution_time}, Components: {len(self.components)}"
