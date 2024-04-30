# component.py

class Component:
    def __init__(self, name, extension, code, semantic_description):
        self.name = name
        self.extension = extension
        self.code = code
        self.semantic_description = semantic_description

    def execute(self):
        try:
            # Execute the component code
            exec(self.code, globals())
            
            # Check if the component code has a main function
            if 'main' in globals():
                # Call the main function if it exists
                main_func = globals()['main']
                main_func()
            
            # Update the component status and result description
            self.status = 'SUCCESS'
            self.result_description = 'Component executed successfully'
        except Exception as e:
            # Handle any exceptions that occur during component execution
            self.status = 'ERROR'
            self.result_description = f"An error occurred during component execution: {str(e)}"

    def to_dict(self):
        # Convert the component object to a dictionary
        return {
            'name': self.name,
            'extension': self.extension,
            'code': self.code,
            'status': self.status,
            'result_description': self.result_description,
        }

    @classmethod
    def from_dict(cls, component_dict):
        # Create a component object from a dictionary
        component = cls(
            component_dict['name'],
            component_dict['extension'],
            component_dict['code'],
            component_dict['semantic_description']
        )
        component.status = component_dict['status']
        component.result_description = component_dict['result_description']
        return component
