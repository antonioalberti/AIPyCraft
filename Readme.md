# AI-Powered Solution Creator

This project is an AI-powered solution creator that assists users in generating, managing, and running code solutions. It leverages the power of AI to create code components based on user-provided descriptions and seamlessly integrates them into a complete solution.

The program was cocreated with Cody using Claude 3 Opus.

## Features

- Create new solutions by providing a name and description
- Generate code components using AI based on user requirements
- Load existing solutions from a folder
- Install dependencies for a solution using virtual environments
- Run solutions and execute the main component
- Display detailed information about a solution and its components
- Remove solutions and their associated files
- Correct and improve existing solutions using AI
- Add new features to solutions using AI
- Import solutions from external folders
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
   - Enter `4` to run a solution and execute the main component
   - Enter `5` to display detailed information about a solution and its components
   - Enter `6` to remove a solution and its associated files
   - Enter `7` to correct and improve an existing solution using AI
   - Enter `8` to apply alternative solution correction using AI
   - Enter `9` to manually improve or correct a solution
   - Enter `10` to import a solution from an external folder
   - Enter `11` to delete a solution from the program (files will be preserved)
   - Enter `12` to exit the program

3. Follow the prompts and provide the necessary information as requested by the program.

## Folder Structure

- main.py: The main entry point of the program
- ai_connector.py: Handles the connection and communication with the OpenAI API
- ai_code_parser.py: Parses code from AI-generated responses
- component.py: Defines the structure and behavior of a code component
- solution.py: Defines the structure and behavior of a solution
- solution_creator.py: Handles the creation of new solutions
- solution_loader.py: Loads existing solutions from a folder
- solution_runner.py: Executes a solution and its main component
- solution_shower.py: Displays detailed information about a solution and its components
- installation_script_generator.py: Generates installation scripts for a solution
- solution_correcting.py: Corrects and improves existing solutions using AI
- solution_feature_adding.py: Adds new features to solutions using AI
- solution_importer.py: Imports solutions from external folders
- solution_updater.py: Applies alternative solution correction using AI
- `prompt_to_create_a_solution.py`: Generates prompts for creating solutions and components

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.