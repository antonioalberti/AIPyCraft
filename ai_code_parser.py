import re
import os

class AICodeParser:
    def parse_content(self, ai_response):
        """
        Extracts the code block from the AI response, regardless of the language.
        Handles cases with or without a language specifier (e.g., ```json, ```python, etc.).
        """
        # Try both patterns: with and without language specifier
        patterns = [
            r'```(?:python|json|javascript|bash|batch|toml)?\s*\n(.*?)\n\s*```',  # With language
            r'```\s*(.*?)\s*```'  # Without language
        ]
        
        for pattern in patterns:
            code_match = re.search(pattern, ai_response, re.DOTALL)
            if code_match:
                # Clean up the extracted code
                code = code_match.group(1).strip()
                # Remove any leading/trailing whitespace from each line while preserving indentation
                return '\n'.join(line.rstrip() for line in code.splitlines())
        
        return None

    def save_content_to_file(self, code, file_path):
        """
        Saves the extracted code to the specified file path.
        """
        if code is not None:
            with open(file_path, 'w') as file:
                file.write(code)
            return True
        return False

    def detect_language_from_code_block(self, ai_response):
        """
        Detects the language of the code block from the AI response based on the code block's language specifier.
        """
        # Match the language specifier in the code block
        language_match = re.search(r'```(python|json|javascript|bash|batch|toml)\s*\n', ai_response, re.IGNORECASE)
        if language_match:
            return language_match.group(1).lower()
        return "unknown"