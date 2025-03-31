import pexpect
import pexpect.popen_spawn
import sys
import time
import os
import argparse # Import argparse
import datetime # Import datetime
from colorama import init, Fore, Style # Import colorama
init(autoreset=True) # Initialize colorama

# Constants
TIMEOUT_SECONDS = 60  # General timeout for expect operations
AI_PROCESSING_WAIT_TIME = 20 # Increased wait time after sending feature description
INSTALLATION_WAIT_TIME = 15 # Increased wait time after selecting install method
EXECUTION_WAIT_TIME = 10 # Increased wait time after selecting run

# Inputs based on the provided log
solutions_folder_path = r"C:\Users\Scalifax\workspace"
correction_instructions = r"""The config.toml file should define a Chainlink job that creates an external price oracle. The job listens for oracle requests on contract 0xc970705401D0D61A05d49C33ab2A39A5C49b2f94 on chain ID 1337, with external ID ca98366c-c731-4957-b8c0-12c72f05aeea. When triggered, it performs a GET request to the CoinGecko API to fetch the price of Ethereum in USD, parses the result, multiplies it by 100 (to handle decimals), and sends the result back to the blockchain via a transaction that calls the fulfillOracleRequest2 method. The data pipeline includes decoding the request log, HTTP fetch, JSON parsing, value multiplication, and data encoding for the response transaction. The job includes all essential Job Configuration properties at the top of the file. These include: type (defines the job type, e.g., "directrequest"), schemaVersion (typically set to 1), name (a human-readable identifier), externalJobID (a unique UUID for external reference), contractAddress (address of the triggering smart contract, required for job types like directrequest), evmChainID (identifies the EVM chain, e.g., 1 for Ethereum mainnet or 1337 for local testnets), forwardingAllowed (boolean, often false for direct requests), minIncomingConfirmations (minimum block confirmations before processing, e.g., 0), minContractPaymentLinkJuels (minimum LINK payment in juels, e.g., "0"), and maxTaskDuration (maximum time a task may run, e.g., "30s"). When generating or validating a job spec, include these fields with appropriate formatting and values based on the job type, and follow with the observationSource block for defining the task pipeline (e.g., http -> jsonparse -> multiply -> ethtx)."""
inputs = [
    solutions_folder_path,          # 0: Solutions folder path
    "1",                            # 1: Load a solution
    "toml1",                        # 2: Solution name to load
    "4",                            # 3: Run solution (first run)
    "1",                            # 4: Select solution 'toml1' to run
    "10",                           # 5: Correct a single component (first correction)
    "1",                            # 6: Select solution 'toml1' to correct
    "config.toml",                  # 7: Component name to correct
    correction_instructions,        # 8: Correction instructions
    "4",                            # 9: Run solution (second run)
    "1",                            # 10: Select solution 'toml1' to run
    "10",                           # 11: Correct a single component (second correction)
    "1",                            # 12: Select solution 'toml1' to correct
    "config.toml",                  # 13: Component name to correct
    "",                             # 14: Empty correction instructions
    "4",                            # 15: Run solution (third run)
    "1",                            # 16: Select solution 'toml1' to run
    "15"                            # 17: Exit
]

# Prompts to expect (using more specific regex where helpful)
PROMPT_FOLDER = r"Enter the solutions folder path:\s*"
PROMPT_CHOICE = r"Enter your choice \(1-15\):\s*" # Updated range
PROMPT_LOAD_NAME = r"Enter the name of the solution to be loaded:\s*"
PROMPT_RUN_SELECT = r"Enter the number of the solution to run \(or 'q' to quit\):\s*"
PROMPT_CORRECT_SELECT_SOLUTION = r"Enter the number of the solution containing the component to correct \(or 'q' to quit\):\s*"
PROMPT_CORRECT_COMPONENT_NAME = r"Enter the name of the component to correct in '.*?' \(e.g., main.py\):\s*"
PROMPT_CORRECT_INSTRUCTIONS = r"Enter any specific instructions for the AI \(or leave blank\):\s*"
# Removed unused prompts like FEATURE_SELECT, FEATURE_DESC, INSTALL_SELECT, INSTALL_METHOD

def main(loop_count, run_id): # Add run_id parameter
    # --- Log File Setup ---
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True) # Ensure log directory exists
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Incorporate run_id into the filename if provided
    run_id_str = f"_run{run_id}" if run_id is not None else ""
    log_filename = f"tester_run_{timestamp_str}{run_id_str}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    print(Fore.LIGHTBLACK_EX + f"Logging output to: {log_filepath}")
    # --- End Log File Setup ---

    print(Fore.LIGHTBLACK_EX + "Starting AIPyCraft test with pexpect...")
    python_executable = sys.executable # Use the same python that runs this script
    command = f"{python_executable} main.py"
    print(Fore.LIGHTBLACK_EX + f"Running command: {command}")
    print(Fore.LIGHTBLACK_EX + f"Looping correction/run steps {loop_count} times.") # Indicate loop count

    log_file = None # Initialize log_file to None
    try:
        # Open the log file for writing
        log_file = open(log_filepath, 'w', encoding='utf-8')

        # Spawn the process using PopenSpawn for Windows compatibility
        # Use encoding='utf-8' and logfile parameter to write to the log file
        child = pexpect.popen_spawn.PopenSpawn(command, encoding='utf-8', timeout=TIMEOUT_SECONDS, logfile=log_file)

        # --- Interaction Sequence ---
        # Note: The print statements below will still go to the console,
        # but the pexpect interactions and child process output go to the log file.

        # 0: Send solutions folder path
        print(Fore.CYAN + "\nEXPECT: Folder Path Prompt")
        child.expect(PROMPT_FOLDER)
        print(Fore.YELLOW + f"SEND: {inputs[0]}")
        child.sendline(inputs[0])

        # 1: Choose "Load a solution"
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice")
        child.expect(PROMPT_CHOICE)
        print(Fore.YELLOW + f"SEND: {inputs[1]}")
        child.sendline(inputs[1])

        # 2: Send solution name to load
        print(Fore.CYAN + "\nEXPECT: Solution Load Name Prompt")
        child.expect(PROMPT_LOAD_NAME)
        print(Fore.YELLOW + f"SEND: {inputs[2]}")
        child.sendline(inputs[2])

        # --- First Run ---
        # 3: Choose "Run solution"
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (Run 1)")
        child.expect(PROMPT_CHOICE)
        print(Fore.YELLOW + f"SEND: {inputs[3]}")
        child.sendline(inputs[3])

        # 4: Select solution 'toml1' to run
        print(Fore.CYAN + "\nEXPECT: Run Solution Select Prompt (Run 1)")
        child.expect(PROMPT_RUN_SELECT)
        print(Fore.YELLOW + f"SEND: {inputs[4]}")
        child.sendline(inputs[4])
        print(Fore.MAGENTA + f"WAIT: Waiting {EXECUTION_WAIT_TIME}s for execution (Run 1)...")
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (after Run 1)")
        child.expect(PROMPT_CHOICE, timeout=EXECUTION_WAIT_TIME + TIMEOUT_SECONDS)

        # --- First Correction ---
        # 5: Choose "Correct a single component"
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (Correct 1)")
        # Removed redundant child.expect(PROMPT_CHOICE) here
        print(Fore.YELLOW + f"SEND: {inputs[5]}")
        child.sendline(inputs[5])

        # 6: Select solution 'toml1' to correct
        print(Fore.CYAN + "\nEXPECT: Correct Solution Select Prompt (Correct 1)")
        child.expect(PROMPT_CORRECT_SELECT_SOLUTION)
        print(Fore.YELLOW + f"SEND: {inputs[6]}")
        child.sendline(inputs[6])

        # 7: Enter component name
        print(Fore.CYAN + "\nEXPECT: Correct Component Name Prompt (Correct 1)")
        child.expect(PROMPT_CORRECT_COMPONENT_NAME)
        print(Fore.YELLOW + f"SEND: {inputs[7]}")
        child.sendline(inputs[7])

        # 8: Send correction instructions
        print(Fore.CYAN + "\nEXPECT: Correct Instructions Prompt (Correct 1)")
        child.expect(PROMPT_CORRECT_INSTRUCTIONS)
        print(Fore.YELLOW + f"SEND: [Correction Instructions - Length: {len(inputs[8])}]")
        child.sendline(inputs[8])
        print(Fore.MAGENTA + f"WAIT: Waiting {AI_PROCESSING_WAIT_TIME}s for AI processing (Correct 1)...")
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (after Correct 1)")
        child.expect(PROMPT_CHOICE, timeout=AI_PROCESSING_WAIT_TIME + TIMEOUT_SECONDS)

        # --- Second Run ---
        # 9: Choose "Run solution"
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (Run 2)")
        # Removed redundant child.expect(PROMPT_CHOICE) here
        print(Fore.YELLOW + f"SEND: {inputs[9]}")
        child.sendline(inputs[9])

        # 10: Select solution 'toml1' to run
        print(Fore.CYAN + "\nEXPECT: Run Solution Select Prompt (Run 2)")
        child.expect(PROMPT_RUN_SELECT)
        print(Fore.YELLOW + f"SEND: {inputs[10]}")
        child.sendline(inputs[10])
        print(Fore.MAGENTA + f"WAIT: Waiting {EXECUTION_WAIT_TIME}s for execution (Run 2)...")
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (after Run 2)")
        child.expect(PROMPT_CHOICE, timeout=EXECUTION_WAIT_TIME + TIMEOUT_SECONDS)

        # --- Loop for Correction and Run ---
        for i in range(loop_count):
            loop_num = i + 1
            log_file.write(f"\n--- Starting Correction Loop Iteration {loop_num}/{loop_count} ---\n") # Log loop start
            print(Fore.BLUE + f"\n--- Starting Loop Iteration {loop_num}/{loop_count} ---")

            # --- Correction (Loop Iteration {loop_num}) ---
            # 11: Choose "Correct a single component"
            print(Fore.CYAN + f"\nEXPECT: Main Menu Choice (Correct Loop {loop_num})")
            # Removed redundant child.expect(PROMPT_CHOICE) here
            print(Fore.YELLOW + f"SEND: {inputs[11]}")
            child.sendline(inputs[11])

            # 12: Select solution 'toml1' to correct
            print(Fore.CYAN + f"\nEXPECT: Correct Solution Select Prompt (Correct Loop {loop_num})")
            child.expect(PROMPT_CORRECT_SELECT_SOLUTION)
            print(Fore.YELLOW + f"SEND: {inputs[12]}")
            child.sendline(inputs[12])

            # 13: Enter component name
            print(Fore.CYAN + f"\nEXPECT: Correct Component Name Prompt (Correct Loop {loop_num})")
            child.expect(PROMPT_CORRECT_COMPONENT_NAME)
            print(Fore.YELLOW + f"SEND: {inputs[13]}")
            child.sendline(inputs[13])

            # 14: Send empty correction instructions
            print(Fore.CYAN + f"\nEXPECT: Correct Instructions Prompt (Correct Loop {loop_num})")
            child.expect(PROMPT_CORRECT_INSTRUCTIONS)
            print(Fore.YELLOW + f"SEND: [Empty Instructions]")
            child.sendline(inputs[14])
            print(Fore.MAGENTA + f"WAIT: Waiting {AI_PROCESSING_WAIT_TIME}s for AI processing (Correct Loop {loop_num})...")
            print(Fore.CYAN + f"\nEXPECT: Main Menu Choice (after Correct Loop {loop_num})")
            child.expect(PROMPT_CHOICE, timeout=AI_PROCESSING_WAIT_TIME + TIMEOUT_SECONDS)

            # --- Run (Loop Iteration {loop_num}) ---
            # 15: Choose "Run solution"
            print(Fore.CYAN + f"\nEXPECT: Main Menu Choice (Run Loop {loop_num})")
            # Removed redundant child.expect(PROMPT_CHOICE) here
            print(Fore.YELLOW + f"SEND: {inputs[15]}")
            child.sendline(inputs[15])

            # 16: Select solution 'toml1' to run
            print(Fore.CYAN + f"\nEXPECT: Run Solution Select Prompt (Run Loop {loop_num})")
            child.expect(PROMPT_RUN_SELECT)
            print(Fore.YELLOW + f"SEND: {inputs[16]}")
            child.sendline(inputs[16])
            print(Fore.MAGENTA + f"WAIT: Waiting {EXECUTION_WAIT_TIME}s for execution (Run Loop {loop_num})...")

            # --- Check for Success or Next Prompt ---
            solution_name = inputs[2] # Get the solution name being tested
            success_pattern = rf"Solution '{solution_name}' completed with status: SUCCESS"
            print(Fore.CYAN + f"\nEXPECT: Success Message ('{success_pattern}') OR Main Menu Choice (after Run Loop {loop_num})")

            try:
                # Expect either the success message or the main menu prompt
                index = child.expect([success_pattern, PROMPT_CHOICE], timeout=EXECUTION_WAIT_TIME + TIMEOUT_SECONDS)

                if index == 0: # Success pattern matched
                    print(Fore.GREEN + f"\nSUCCESS: Solution '{solution_name}' completed successfully. Stopping loop.")
                    log_file.write(f"\n--- Solution '{solution_name}' completed successfully. Stopping loop. ---\n") # Log success and stop
                    break # Exit the loop
                elif index == 1: # Main menu prompt matched
                    print(Fore.CYAN + f"INFO: Solution run finished (not SUCCESS). Continuing loop.")
                    # No action needed, loop continues
            except pexpect.TIMEOUT:
                 print(Fore.YELLOW + f"\nTIMEOUT: Waiting for success message or main menu after run in loop {loop_num}. Continuing loop.")
                 # Log timeout but continue loop as per requirement (stop only on SUCCESS)
                 log_file.write(f"\n--- TIMEOUT waiting for run result in loop {loop_num}. Continuing loop. ---\n")
            except pexpect.EOF:
                 print(Fore.RED + f"\nEOF: Process ended unexpectedly after run in loop {loop_num}.")
                 raise # Re-raise EOF to be caught by the main handler

            print(Fore.BLUE + f"\n--- Finished Loop Iteration {loop_num}/{loop_count} ---")
        # --- End Loop ---

        # --- Exit --- (Only reached if loop completes fully or breaks due to SUCCESS)
        # 17: Choose "Exit"
        print(Fore.CYAN + "\nEXPECT: Main Menu Choice (Exit)")
        # Removed redundant child.expect(PROMPT_CHOICE) here
        print(Fore.YELLOW + f"SEND: {inputs[17]}")
        child.sendline(inputs[17])

        # Wait for the process to finish
        print(Fore.CYAN + "\nEXPECT: Process termination (EOF)")
        # Use the base pexpect EOF exception
        child.expect(pexpect.EOF)
        print(Fore.GREEN + "\nProcess finished.")

    # Use the base pexpect TIMEOUT exception
    except pexpect.TIMEOUT:
        print(Fore.RED + "\nError: Timeout waiting for expected output.")
        print(Fore.RED + "------- Last 500 characters of output: -------")
        print(Fore.RED + child.before[-500:])
        print(Fore.RED + "---------------------------------------------")
        return 1 # Indicate error
    # Use the base pexpect EOF exception
    except pexpect.EOF:
        print(Fore.RED + "\nError: Process ended unexpectedly.")
        print(Fore.RED + "------- Output before EOF: -------")
        print(Fore.RED + child.before)
        print(Fore.RED + "----------------------------------")
        return 1 # Indicate error
    except Exception as e:
        print(Fore.RED + f"\nAn unexpected error occurred: {e}")
        # Check if process is alive using poll() on the underlying Popen object
        if 'child' in locals() and hasattr(child, 'proc') and child.proc.poll() is None:
            print(Fore.RED + "------- Last 500 characters of output: -------")
            print(Fore.RED + child.before[-500:])
            print(Fore.RED + "---------------------------------------------")
        return 1 # Indicate error
    finally:
        # Check if process is alive using poll() on the underlying Popen object
        if 'child' in locals() and hasattr(child, 'proc') and child.proc.poll() is None:
            print(Fore.LIGHTBLACK_EX + "\nTerminating child process...")
            child.proc.terminate() # Call terminate on the underlying Popen object
            print(Fore.LIGHTBLACK_EX + "Child process terminated.")
        if log_file:
            log_file.close() # Ensure log file is closed

    print(Fore.GREEN + f"\nTester finished successfully. Log saved to: {log_filepath}")
    return 0 # Indicate success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AIPyCraft tester with optional looping and run ID.")
    parser.add_argument("--loops", type=int, default=1, help="Number of times to loop the correction/run sequence within a single tester execution.")
    parser.add_argument("--run-id", type=int, default=None, help="Optional unique ID for this specific tester run (used for log filename).")
    args = parser.parse_args()

    if args.loops < 1:
        print(Fore.RED + "Error: Number of loops must be at least 1.")
        sys.exit(1)

    # Pass loop count and run_id to main
    sys.exit(main(args.loops, args.run_id))
