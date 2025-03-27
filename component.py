# component.py

class Component:
    def __init__(self, name, extension, content, semantic_description, language="python"):
        self.name = name
        self.extension = extension
        self.content = content
        self.semantic_description = semantic_description
        self.language = language
        self.status = 'PENDING'
        self.result_description = ''

    def execute(self):
        try:
            if self.language != "python":
                # Skip execution for non-Python components
                self.status = 'SKIPPED'
                self.result_description = self._color_text(f"Execution skipped for non-Python component: {self.language}.", 'yellow')
                return

            # Execute Python code
            exec(self.content, globals())

            # Check if the component code has a main function
            if 'main' in globals():
                # Call the main function if it exists
                main_func = globals()['main']
                main_func()

            # Update the component status and result description
            self.status = 'SUCCESS'
            self.result_description = self._color_text('Python component executed successfully.', 'green')
        except Exception as e:
            # Handle any exceptions that occur during component execution
            self.status = 'ERROR'
            self.result_description = self._color_text(f"An error occurred during component execution: {str(e)}", 'orange')

    def to_dict(self):
        # Convert the component object to a dictionary
        return {
            'name': self.name,
            'extension': self.extension,
            'content': self.content,
            'semantic_description': self.semantic_description,
            'language': self.language,
            'status': self.status,
            'result_description': self.result_description,
        }

    @classmethod
    def from_dict(cls, component_dict):
        # Create a component object from a dictionary
        component = cls(
            component_dict['name'],
            component_dict['extension'],
            component_dict['content'],
            component_dict['semantic_description'],
            component_dict['language']
        )
        component.status = component_dict['status']
        component.result_description = component_dict['result_description']
        return component

    @staticmethod
    def _color_text(text, color):
        colors = {
            'green': '\033[92m',
            'orange': '\033[93m',
            'end': '\033[0m',
        }
        return f"{colors.get(color, '')}{text}{colors['end']}"