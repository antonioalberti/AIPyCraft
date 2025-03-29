# AI-Powered Solution Creator

This project is an AI-powered solution creator that assists users in generating, managing, and running code solutions. It leverages the power of AI to create code components based on user-provided descriptions and seamlessly integrates them into a complete solution.

The program was cocreated with GitHub Copilot using Claude 3.5 Sonnet.

## Features

- **Solution Management:**
    - Create new solutions with a name and description.
    - Load existing solutions from folders.
    - List loaded solutions and display detailed information.
    - Import solutions from external folders (detects component languages).
    - Export solutions to TOML format (stored in `exports/`).
    - Remove solutions and their associated files.
    - Delete solution references from the program while preserving files.
    - List existing project folders containing `model.txt`.
- **AI-Powered Development:**
    - Generate code components using AI based on user requirements.
    - Correct and improve entire solutions using AI.
    - Apply alternative AI-driven correction strategies.
    - Correct individual components using AI (`component_corrector.py`).
    - Add new features to solutions using AI.
- **Code Execution & Handling:**
    - Support multiple component languages (Python, JS, Bash, JSON, Text, MD, YAML, TOML, etc.).
    - Run solutions: Executes Python components, skips others.
    - Install Python dependencies using virtual environments (`install.bat`, `installation_script_generator.py`).
- **Utilities:**
    - Logging mechanism (`utils/logger.py`) records operations (logs stored in `logs/`).
    - Testing capabilities (`tester.py`).

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
   - Enter `5` to list loaded solutions and display detailed information about a selected solution
   - Enter `6` to remove a solution and its associated files
   - Enter `7` to correct and improve an existing solution using AI
   - Enter `8` to apply alternative solution correction using AI
   - Enter `9` to manually improve or correct a solution
   - Enter `10` to import a solution from an external folder
   - Enter `11` to delete a solution from the program (files will be preserved)
   - Enter `12` to export current solution to TOML
- Enter `13` to list existing project folders (containing model.txt)
- Enter `14` to exit the program

*(Note: The exact mapping of menu options 7, 8, 9 to the correction modules might need verification by running the application.)*

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

- `main.py`: Main entry point and user interface handler.
- `ai_connector.py`: Manages interaction with the AI API (e.g., OpenAI).
- `ai_code_parser.py`: Parses code blocks from AI responses and detects language.
- `component.py`: Defines the `Component` class representing a single code file.
- `solution.py`: Defines the `Solution` class, managing a collection of components.
- `solution_creator.py`: Handles the creation of new solutions.
- `solution_loader.py`: Loads existing solutions from disk.
- `solution_runner.py`: Executes runnable components (currently Python).
- `solution_displayer.py`: Formats and displays solution information to the user.
- `installation_script_generator.py`: Creates scripts (`install.bat`) for Python dependencies.
- `solution_correcting.py`: Implements AI-based correction for entire solutions.
- `solution_updater.py`: Provides alternative AI-based correction mechanisms.
- `component_corrector.py`: Handles AI-based correction for individual components.
- `solution_feature_adding.py`: Uses AI to add new features (components) to a solution.
- `solution_importer.py`: Imports solutions from external directories.
- `utils/logger.py`: Configures and provides logging functionality. (`logger.py` in root might be deprecated).
- `tester.py`: Contains testing scripts or utilities for the project.
- `requirements.txt`: Lists Python package dependencies.
- `install.bat`: Batch script for easy installation on Windows.
- `.env`: (User-created) Stores API keys and potentially other secrets.
- `model.txt`: Likely stores metadata or the core description for a solution within its folder.
- `Readme.md`: This file.
- `Copyright.txt`: Contains copyright information.
- `todo.txt`: Tracks pending tasks or ideas for the project.
- `.gitignore`: Specifies intentionally untracked files for Git.
- `exports/`: Default directory for exported solutions (e.g., in TOML format).
- `logs/`: Directory where log files are stored.
- `test_solutions/`: Contains example or test solutions.
- `utils/`: Directory for utility modules like the logger.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
