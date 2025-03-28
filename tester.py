import pexpect
import pexpect.popen_spawn
import sys
import time
import os

# Constants
TIMEOUT_SECONDS = 60  # General timeout for expect operations
AI_PROCESSING_WAIT_TIME = 20 # Increased wait time after sending feature description
INSTALLATION_WAIT_TIME = 15 # Increased wait time after selecting install method
EXECUTION_WAIT_TIME = 10 # Increased wait time after selecting run

# Inputs (same as before)
solutions_folder_path = r"C:\Users\Scalifax\workspace"
feature_description = r"""Modify the solution’s TOML file. The TOML configuration file should define a Chainlink job that creates an external price oracle. The job listens for oracle requests on contract 0xc970705401D0D61A05d49C33ab2A39A5C49b2f94 on chain ID 1337, with external ID ca98366c-c731-4957-b8c0-12c72f05aeea. When triggered, it performs a GET request to the CoinGecko API to fetch the price of Ethereum in USD, parses the result, multiplies it by 100 (to handle decimals), and sends the result back to the blockchain via a transaction that calls the fulfillOracleRequest2 method. The data pipeline includes decoding the request log, HTTP fetch, JSON parsing, value multiplication, and data encoding for the response transaction."""
inputs = [
    solutions_folder_path,  # 0: Solutions folder path
    "1",  # 1: Load a solution
    "toml1",  # 2: Solution name
    "9",  # 3: Manually improve or correct
    "1",  # 4: Select solution 'toml1' for feature
    feature_description,  # 5: Feature description
    "4",  # 5: Run solution
    "1",  # 6: Select solution 'toml1' for run
    "14"  # 7: Exit
]

# Prompts to expect (using more specific regex where helpful)
PROMPT_FOLDER = r"Enter the solutions folder path:\s*"
PROMPT_CHOICE = r"Enter your choice \(1-14\):\s*"
PROMPT_LOAD_NAME = r"Enter the name of the solution to be loaded:\s*"
PROMPT_FEATURE_SELECT = r"Enter the number of the solution to add a feature to \(or 'q' to quit\):\s*"
PROMPT_FEATURE_DESC = r"Enter the description of what to you want to do with the solution:\s*"
PROMPT_INSTALL_SELECT = r"Enter the number of the solution to install the environment for \(or 'q' to quit\):\s*"
PROMPT_INSTALL_METHOD = r"Select the installation method \(pip/conda/quit\):\s*"
PROMPT_RUN_SELECT = r"Enter the number of the solution to run \(or 'q' to quit\):\s*"

def main():
    print("Starting AIPyCraft test with pexpect...")
    python_executable = sys.executable # Use the same python that runs this script
    command = f"{python_executable} main.py"
    print(f"Running command: {command}")

    try:
        # Spawn the process using PopenSpawn for Windows compatibility
        # Use encoding='utf-8' and logfile for debugging output
        child = pexpect.popen_spawn.PopenSpawn(command, encoding='utf-8', timeout=TIMEOUT_SECONDS, logfile=sys.stdout)

        # --- Interaction Sequence ---

        # 0: Send solutions folder path
        print("\nEXPECT: Folder Path Prompt")
        child.expect(PROMPT_FOLDER)
        print(f"SEND: {inputs[0]}")
        child.sendline(inputs[0])

        # 1: Choose "Load a solution"
        print("\nEXPECT: Main Menu Choice")
        child.expect(PROMPT_CHOICE)
        print(f"SEND: {inputs[1]}")
        child.sendline(inputs[1])

        # 2: Send solution name to load
        print("\nEXPECT: Solution Load Name Prompt")
        child.expect(PROMPT_LOAD_NAME)
        print(f"SEND: {inputs[2]}")
        child.sendline(inputs[2])

        # 3: Choose "Manually improve or correct"
        print("\nEXPECT: Main Menu Choice")
        child.expect(PROMPT_CHOICE)
        print(f"SEND: {inputs[3]}")
        child.sendline(inputs[3])

        # 4: Select solution for feature
        print("\nEXPECT: Feature Solution Select Prompt")
        child.expect(PROMPT_FEATURE_SELECT)
        print(f"SEND: {inputs[4]}")
        child.sendline(inputs[4])

        # 5: Send feature description
        print("\nEXPECT: Feature Description Prompt")
        child.expect(PROMPT_FEATURE_DESC)
        print(f"SEND: [Feature Description - Length: {len(inputs[5])}]")
        child.sendline(inputs[5])
        print(f"WAIT: Waiting {AI_PROCESSING_WAIT_TIME}s for AI processing...")
        # Expect the next prompt *after* the AI response and file updates
        # We need to wait longer here, potentially consuming intermediate output
        # Let's expect the menu prompt again, but with a longer timeout specifically for this step
        print("\nEXPECT: Main Menu Choice (after AI)")
        child.expect(PROMPT_CHOICE, timeout=AI_PROCESSING_WAIT_TIME + TIMEOUT_SECONDS) # Add AI time to base timeout

        # 6: Choose "Run solution" (was index 9)
        print(f"SEND: {inputs[6]}")
        child.sendline(inputs[6])

        # 7: Select solution to run (was index 10)
        print("\nEXPECT: Run Solution Select Prompt")
        child.expect(PROMPT_RUN_SELECT)
        print(f"SEND: {inputs[7]}")
        child.sendline(inputs[7])
        print(f"WAIT: Waiting {EXECUTION_WAIT_TIME}s for execution...")
        # Expect the menu prompt again after execution
        print("\nEXPECT: Main Menu Choice (after Run)")
        child.expect(PROMPT_CHOICE, timeout=EXECUTION_WAIT_TIME + TIMEOUT_SECONDS)

        # 8: Choose "Exit" (was index 11)
        print(f"SEND: {inputs[8]}")
        child.sendline(inputs[8])

        # Wait for the process to finish
        print("\nEXPECT: Process termination (EOF)")
        # Use the base pexpect EOF exception
        child.expect(pexpect.EOF)
        print("\nProcess finished.")

    # Use the base pexpect TIMEOUT exception
    except pexpect.TIMEOUT:
        print("\nError: Timeout waiting for expected output.")
        print("------- Last 500 characters of output: -------")
        print(child.before[-500:])
        print("---------------------------------------------")
        return 1 # Indicate error
    # Use the base pexpect EOF exception
    except pexpect.EOF:
        print("\nError: Process ended unexpectedly.")
        print("------- Output before EOF: -------")
        print(child.before)
        print("----------------------------------")
        return 1 # Indicate error
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        # Check if process is alive using poll() on the underlying Popen object
        if 'child' in locals() and hasattr(child, 'proc') and child.proc.poll() is None:
            print("------- Last 500 characters of output: -------")
            print(child.before[-500:])
            print("---------------------------------------------")
        return 1 # Indicate error
    finally:
        # Check if process is alive using poll() on the underlying Popen object
        if 'child' in locals() and hasattr(child, 'proc') and child.proc.poll() is None:
            print("\nTerminating child process...")
            child.proc.terminate() # Call terminate on the underlying Popen object
            print("Child process terminated.")

    print("\nTester finished successfully.")
    return 0 # Indicate success

if __name__ == "__main__":
    sys.exit(main())
