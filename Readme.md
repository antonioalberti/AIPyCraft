# AI-Powered Solution Creator

This project is an AI-powered solution creator that assists users in generating, managing, and running code solutions. It leverages the power of AI to create code components based on user-provided descriptions and seamlessly integrates them into a complete solution.

The program was cocreated with GitHub Copilot using Claude 3.5 Sonnet.

## Features

- Create new solutions by providing a name and description
- Generate code components using AI based on user requirements
- Support multiple programming languages (Python, JavaScript, Bash, JSON, etc.)
- Load existing solutions from a folder
- Install dependencies for Python components using virtual environments
- Run solutions (Python components are executed, other languages are skipped)
- Display detailed information about a solution and its components
- Remove solutions and their associated files
- Correct and improve existing solutions using AI
- Add new features to solutions using AI
- Import solutions from external folders
- Export solutions to TOML format
- Delete solutions from the program (files will be preserved)

## Prerequisites

- Python 3.x
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/antonioalberti/AIPyCraft.git
   ```

2. Navigate to the project directory:
   ```bash
   cd AIPyCraft
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or in Windows, just double-click on:
   ```bash
   install.bat
   ```

4. Set up the OpenAI API key:
   - Create a file named .env in the project root directory
   - Add the following line to the .env file, replacing `YOUR_API_KEY` with your actual OpenAI API key:
     ```plaintext
     OPENAI_API_KEY=YOUR_API_KEY
     ```

## Usage

1. Run the main.py script:
   ```bash
   python main.py
   ```

2. Follow the on-screen menu to interact with the AI-powered solution creator:
   - Enter `1` to load an existing solution from a folder
   - Enter `2` to create a new solution by providing a name and description
   - Enter `3` to install dependencies for a solution using a virtual environment
   - Enter `4` to run a solution (executes Python components, skips others)
   - Enter `5` to display detailed information about a solution and its components
   - Enter `6` to remove a solution and its associated files
   - Enter `7` to correct and improve an existing solution using AI
   - Enter `8` to apply alternative solution correction using AI
   - Enter `9` to manually improve or correct a solution
   - Enter `10` to import a solution from an external folder
   - Enter `11` to delete a solution from the program (files will be preserved)
   - Enter `12` to export current solution to TOML
   - Enter `13` to exit the program

## Component Languages

The project supports various file types and programming languages:
- Python (.py)
- JavaScript (.js)
- Bash scripts (.sh)
- Batch files (.bat)
- JSON (.json)
- Text files (.txt)
- Markdown (.md)
- YAML (.yml, .yaml)
- TOML (.toml)

Note: Only Python components are executed when running a solution. Other components are automatically skipped but remain part of the solution structure.

## Folder Structure

- main.py: The main entry point of the program
- ai_connector.py: Handles the connection and communication with the OpenAI API
- ai_code_parser.py: Parses code from AI-generated responses with language detection
- component.py: Defines the structure and behavior of a multilanguage code component
- solution.py: Defines the structure and behavior of a solution
- solution_creator.py: Handles the creation of new solutions with multilanguage support
- solution_loader.py: Loads existing solutions from a folder
- solution_runner.py: Executes Python components and skips non-Python components
- solution_shower.py: Displays detailed information about solutions and their components
- installation_script_generator.py: Generates installation scripts for Python dependencies
- solution_correcting.py: Corrects and improves existing solutions using AI
- solution_feature_adding.py: Adds new features to solutions using AI
- solution_importer.py: Imports solutions from external folders with language detection
- solution_updater.py: Applies alternative solution correction using AI

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.