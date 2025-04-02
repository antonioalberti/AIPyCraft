import re
import os

class AICodeParser:
    def parse_content(self, ai_response):
        """
        Extracts the first code block from the AI response.
        Handles optional language specifiers (e.g., ```json, ```python, ```toml).
        """
        # Pattern explanation:
        # ```                  - Match the opening fence
        # (?:[a-zA-Z0-9]+)?   - Optionally match (non-capturing) a language specifier (alphanumeric)
        # \s*                  - Match zero or more whitespace characters
        # \n                   - Match a newline *after* the opening fence/language
        # (.*?)                - Capture the content (non-greedy)
        # \n\s*                - Match a newline and optional whitespace *before* the closing fence
        # ```                  - Match the closing fence
        # Try the stricter pattern first (requiring newlines around content)
        pattern_strict = r'```(?:[a-zA-Z0-9]+)?\s*\n(.*?)\n\s*```'
        code_match = re.search(pattern_strict, ai_response, re.DOTALL)

        # If strict pattern fails, try a more lenient one (optional newlines)
        # This helps catch cases where the AI might format fences differently
        if not code_match:
            pattern_lenient = r'```(?:[a-zA-Z0-9]+)?\s*\n?(.*?)\n?\s*```'
            code_match = re.search(pattern_lenient, ai_response, re.DOTALL)

        if code_match:
            # Extract the captured content (group 1) and strip whitespace
            code = code_match.group(1).strip()
            
            # POST-PROCESSING STEP: Check for and remove potential nested fences at the beginning
            # This looks for ``` followed by optional language, optional space/newline
            nested_fence_pattern = r'^\s*```(?:[a-zA-Z0-9]+)?\s*\n?'
            nested_fence_match = re.match(nested_fence_pattern, code)
            
            if nested_fence_match:
                 # If a nested fence is found at the start, remove it from the code
                 # .end() gives the index after the matched nested fence pattern
                 code = code[nested_fence_match.end():].strip()

            # Return the potentially cleaned code
            return code
        
        # If no code block found using either pattern, return None
        return None

    def save_content_to_file(self, code, file_path):
        """
        Saves the extracted code to the specified file path.
        Ensures the directory exists and uses UTF-8 encoding.
        """
        if code is not None:
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as file: # Added encoding
                    file.write(code)
                return True
            except OSError as e:
                # Handle potential errors during directory creation or file writing
                print(f"Error saving file {file_path}: {e}")
                return False
        return False

    def detect_language_from_code_block(self, ai_response):
        """
        Detects the language of the code block from the AI response based on the code block's language specifier.
        """
        # Pattern explanation:
        # ```                  - Match the opening fence
        # ([a-zA-Z0-9]+)      - Capture the language specifier (alphanumeric)
        # \s*                  - Match zero or more whitespace characters
        # \n?                  - Optionally match a newline
        # .*?                  - Match the content (non-greedy)
        # \n?                  - Optionally match a newline before the closing fence
        # ```                  - Match the closing fence
        pattern = r'```([a-zA-Z0-9]+)\s*\n?.*?\n?```'
        
        language_match = re.search(pattern, ai_response, re.DOTALL)
        if language_match:
            return language_match.group(1).lower()
            
        return "unknown"
