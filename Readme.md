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
    - Generate code components using an AI ensemble (OpenAI GPT-4o and Anthropic Claude 3.5 Sonnet for initial generation, Google Gemini 1.5 Pro for evaluation) based on user requirements.
    - Correct and improve entire solutions using the AI ensemble.
    - Apply alternative AI-driven correction strategies (using the ensemble).
    - Correct individual components using AI (`component_corrector.py`).
    - Add new features to solutions using AI.
- **Code Execution & Handling:**
    - Support multiple component languages (Python, JS, Bash, JSON, Text, MD, YAML, TOML, etc.).
    - Run solutions: Executes Python components, skips others.
    - Install Python dependencies using virtual environments (`install.bat`, `installation_script_generator.py`).
- **Utilities:**
    - Logging mechanism (`logger.py`) records operations, creating separate log files for each run when using batch testing (logs stored in `logs/`).
    - Testing capabilities (`tester.py`) for automated workflow testing.
    - Batch testing scripts (`run_tester_multiple.ps1`, `initialization.ps1`) for running tests multiple times with initialization.

## Prerequisites

- Python 3.x
- OpenAI API key (required for OpenAI generation)
- Anthropic API key (required for Claude generation)
- Google Gemini API key (required for evaluation)

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
      OPENAI_API_KEY=YOUR_OPENAI_API_KEY
      ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY
      GEMINI_API_KEY=YOUR_GEMINI_API_KEY
      ```

## Usage

1. Run the main.py script:
   ```bash
   python main.py
   ```

2. Follow the on-screen menu to interact with the AI-powered solution creator:
   - Enter `1` to load an existing solution from a folder
   - Enter `2` to create a new solution
   - Enter `3` to install a solution environment
   - Enter `4` to run a solution
   - Enter `5` to show solution details
   - Enter `6` to remove a solution folder (deletes files)
   - Enter `7` to correct a solution using AI
   - Enter `8` to apply alternative solution correction using AI
   - Enter `9` to manually improve or correct a solution (adds features)
   - Enter `10` to correct a single component using AI
   - Enter `11` to import a folder as a solution
   - Enter `12` to delete a solution reference (preserves files)
   - Enter `13` to export current solution to TOML
   - Enter `14` to list existing projects (folders with `model.txt`)
   - Enter `15` to exit the program

*(Note: The exact mapping of menu options 7, 8, 9, 10 to the specific correction/improvement modules (`solution_correcting.py`, `solution_updater.py`, `solution_feature_adding.py`, `component_corrector.py`) might need verification by running the application.)*

## Typical Workflow

A common workflow using AIPyCraft might look like this:

1.  **Start:** Run `python main.py`.
2.  **Set Folder:** Provide the path to your desired solutions folder when prompted.
3.  **Create/Load:**
    *   Use option `2` to create a new solution by providing a name and description. The AI will generate initial components.
    *   Or, use option `1` to load an existing solution from the solutions folder.
    *   Or, use option `11` to import an external folder as a new solution.
4.  **Install (if needed):** If the solution contains Python components with dependencies, use option `3` to generate and run an installation script (`install.bat`) within a virtual environment (`venv`).
5.  **Run:** Use option `4` to execute the solution (runs Python components). Check the output for errors or unexpected behavior.
6.  **Refine/Correct:**
    *   If errors occur or improvements are needed, use AI correction options:
        *   Option `7` (`solution_correcting.py`) for whole-solution correction based on errors.
        *   Option `8` (`solution_updater.py`) for alternative AI correction.
        *   Option `10` (`component_corrector.py`) to target a specific component with optional instructions.
        *   Use option `9` (`solution_feature_adding.py`) to add new features or manually guide improvements with AI.
7.  **Iterate:** Repeat steps 5 (Run) and 6 (Refine/Correct) until the solution functions as desired.
8.  **Manage:**
    *   Use option `5` to view details of the loaded solutions.
    *   Use option `13` to export the current solution structure to a TOML file in the `exports/` directory.
    *   Use option `14` to list all recognized projects in the solutions folder.
    *   Use option `6` to permanently delete a solution's folder and files.
    *   Use option `12` to remove a solution reference from the program's memory but keep the files.
9.  **Exit:** Use option `15` to close the application.

## Testing (`tester.py`)

The `tester.py` script provides automated integration testing for the main application flow. It now accepts a `--run-id` argument to help generate unique log filenames when run multiple times.

**How it Works:**

*   It uses the `pexpect` library to launch `main.py` as a subprocess.
*   It simulates user interaction by sending predefined inputs (like menu choices, folder paths, solution names, correction instructions) based on a sequence defined within the script.
*   It expects specific prompts from `main.py` at each step to verify the application is responding correctly.
*   It includes timeouts and waits to handle potentially long-running operations like AI processing or script execution.
*   It focuses on a specific workflow: loading a solution, running it, correcting a component using AI, and running it again. This correction/run cycle can be repeated multiple times.

**Running the Tester:**

While `tester.py` is primarily designed to be run via `run_tester_multiple.ps1` (which handles path setup), you can run it directly if needed:

```bash
python tester.py --solution-name <SolutionName> --solutions-base-path "<path_to_solutions_folder>" --correction-prompt "<Prompt Text>" [--loops N] [--run-id ID]
```

*   `--solution-name <SolutionName>`: (Required) The name of the solution to load and test.
*   `--solutions-base-path "<path_to_solutions_folder>"`: (Required) The absolute path to the directory containing the solution folders.
*   `--correction-prompt "<Prompt Text>"`: (Required) The correction instructions to provide to the AI. Enclose in quotes if it contains spaces.
*   `--loops N`: (Optional) Specify the number of times (`N`) to repeat the core correction/run cycle *within a single execution of `tester.py`*. Defaults to 1.
*   `--run-id ID`: (Optional) A unique integer ID for this specific run, used to create distinct log filenames (e.g., `tester_run_..._runID.log` and `AIPyCraft_main_..._runID.log`).

The script will print its actions (EXPECT/SEND/WAIT) and the output from `main.py`. It will exit with code 0 on success or 1 on failure (e.g., timeout, unexpected output, crash).

**Batch Testing with PowerShell:**

For running multiple independent test cycles with initialization, use the provided PowerShell scripts:

1.  **`initialization.ps1`**: (Optional, customizable) Prepares the test environment before each run. By default, it clears the `config.toml` file of the `toml1` solution.
2.  **`run_tester_multiple.ps1`**: Executes `initialization.ps1` and then `tester.py` a specified number of times.

**Running Batch Tests:**

Open PowerShell in the project directory and run:

```powershell
.\run_tester_multiple.ps1 -Trials <number_of_trials> -LoopsValue <loops_per_tester_run> -SolutionName <name_of_solution> -SolutionsBasePath "<path_to_solutions_folder>" -CorrectionPrompt "<Prompt Text>"
```

*   `-Trials <number_of_trials>`: (Required) The total number of times (trials) to execute the initialization + tester sequence.
*   `-LoopsValue <loops_per_tester_run>`: (Required) The value passed to the `--loops` argument of `tester.py` for *each* of the trials.
*   `-SolutionName <name_of_solution>`: (Required) The name of the solution folder (e.g., `toml1`, `my_solution`) to test and initialize.
*   `-SolutionsBasePath "<path_to_solutions_folder>"`: (Required) The absolute path to the directory containing the solution folders (e.g., `"C:\Users\YourUser\workspace"`). Enclose in quotes if the path contains spaces.
*   `-CorrectionPrompt "<Prompt Text>"`: (Required) The correction instructions to pass to the AI during the test. Enclose in quotes.

This setup ensures that:
*   The environment is reset via `initialization.ps1` before each trial, using the correct solutions base path.
*   `tester.py` receives the correct solutions base path and generates a unique log file for its interaction during each trial (e.g., `tester_run_..._run1.log`, `tester_run_..._run2.log`).
*   `main.py` (when called by `tester.py`) also generates a unique log file for its internal operations during each trial (e.g., `AIPyCraft_main_..._run1.log`, `AIPyCraft_main_..._run2.log`).

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
- `ai_connector.py`: Manages interaction with AI APIs (OpenAI, Anthropic Claude, Google Gemini) and implements the ensemble method.
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
- `logger.py`: Configures and provides logging functionality, supporting unique run IDs.
- `tester.py`: Contains the main integration testing script (accepts `--solutions-base-path`).
- `run_tester_multiple.ps1`: PowerShell script for batch execution of tests (requires `-SolutionsBasePath`).
- `initialization.ps1`: PowerShell script for initializing the environment before each test run in a batch (accepts `-SolutionsBasePath`).
- `plot_interactions_to_success.py`: Python script to analyze `tester_run` logs and plot iterations to success.
- `plot_total_test_time.py`: Python script to analyze `AIPyCraft_main` logs and plot total test duration.
- `requirements.txt`: Lists Python package dependencies.
- `install.bat`: Batch script for easy installation on Windows.
- `.env`: (User-created) Stores API keys and potentially other secrets.
- `model.txt`: Likely stores metadata or the core description for a solution within its folder.
- `Readme.md`: This file.
- `Copyright.txt`: Contains copyright information.
- `todo.txt`: Tracks pending tasks or ideas for the project.
- `.gitignore`: Specifies intentionally untracked files for Git.
- `exports/`: Default directory for exported solutions (e.g., in TOML format).
- `logs/`: Directory where log files are stored (both from `tester.py` and `main.py`).
- `plots/`: Directory where analysis plots are saved.
- `utils/`: (Potentially deprecated if logger moved to root) Directory for utility modules.

## Log Analysis and Plotting

After running batch tests using `run_tester_multiple.ps1`, you can analyze the results using the provided plotting scripts.

### Iterations to Success (`plot_interactions_to_success.py`)

This script analyzes the `tester_run_..._runX.log` files to determine how many correction loop iterations were needed to achieve success for each trial.

**Functionality:**

*   Parses the `tester_run_..._runX.log` files.
*   Determines the number of correction loop iterations required to reach the "SUCCESS" state for the specified solution in each trial.
*   Calculates overall statistics for successful trials (min, max, mean, median iterations).
*   Counts failed trials (where the success message wasn't found within the log).
*   Generates a cumulative line plot showing the mean iterations to success over trials, with a 95% confidence interval band.
*   Saves the plot to `plots/cumulative_iterations_plot_SolutionName.png`.

**Usage:**

```bash
python plot_interactions_to_success.py -Trials <number_of_trials> -LoopsValue <max_loops_per_trial> -SolutionName <name_of_solution>
```

*   `-Trials`: Number of trials to analyze (match the batch run).
*   `-LoopsValue`: Max loops per trial configured in `tester.py` (match the batch run).
*   `-SolutionName`: Name of the tested solution (match the batch run).

### Total Test Time (`plot_total_test_time.py`)

This script analyzes the `AIPyCraft_main_..._runX.log` files to determine the total time elapsed for each test run.

**Functionality:**

*   Parses the `AIPyCraft_main_..._runX.log` files.
*   Calculates the duration for each trial by subtracting the timestamp of the first log entry from the timestamp of the last log entry.
*   Calculates overall statistics for valid trial durations (min, max, mean, median time).
*   Counts trials where duration couldn't be calculated (e.g., missing logs, parse errors).
*   Generates a cumulative line plot showing the mean total test duration over trials, with a 95% confidence interval band.
*   Saves the plot to `plots/cumulative_total_time_plot_SolutionName.png`.

**Usage:**

```bash
python plot_total_test_time.py -Trials <number_of_trials> -SolutionName <name_of_solution>
```

*   `-Trials`: Number of trials to analyze (match the batch run).
*   `-SolutionName`: Name of the tested solution (match the batch run).

The script will print overall statistics and save the cumulative time plot image in the `plots/` directory.

**Dependencies:**

Requires `matplotlib`, `numpy`, and `scipy`. Ensure they are installed (they should be if you updated `requirements.txt` and re-ran `pip install -r requirements.txt` or `install.bat`).

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

**MIT License**

Copyright (c) Antonio Alberti and Alexis Leal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
