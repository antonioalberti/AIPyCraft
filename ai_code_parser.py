# ai_code_parser.py

import re
import os

class AICodeParser:
    def parse_code(self, ai_response):
        code_match = re.search(r'```(?:python)?\n(.*?)\n```', ai_response, re.DOTALL)
        if code_match:
            return code_match.group(1)
        else:
            return None

    def save_code_to_file(self, code, file_path):
        with open(file_path, 'w') as file:
            file.write(code)