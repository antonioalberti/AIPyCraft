import subprocess
import os
import sys
import tempfile

def test_main_menu():
    # Create a temporary folder for solutions
    with tempfile.TemporaryDirectory() as solutions_folder:
        print(f"[INFO] Testing with temporary solutions folder: {solutions_folder}")

        # Prepare the inputs for the menu options
        inputs = [
            f"{solutions_folder}\n",  # Enter solutions folder path
            "2\n",  # Create a new solution
            "pong\n",  # Enter a name for the new solution
            "This is a test solution for a Pong game.\n",  # Enter a description for the solution
            "yes\n",  # Approve the solution and its components
            "3\n",  # Install a solution environment
            "q\n",  # Quit the submenu
            "4\n",  # Run a solution
            "q\n",  # Quit the submenu
            "2\n",  # Create another solution
            "pink\n",  # Enter a name for the new solution
            "Plot a house with pink color.\n",  # Enter a description for the solution
            "yes\n",  # Approve the solution and its components
            "3\n",  # Install a solution environment
            "q\n",  # Quit the submenu
            "4\n",  # Run the solution
            "7\n",  # Correct the solution
            "q\n",  # Quit the submenu
            "8\n",  # Apply alternative correction
            "q\n",  # Quit the submenu
            "4\n",  # Run the solution again
            "3\n",  # Reinstall the environment
            "q\n",  # Quit the submenu
            "4\n",  # Run the solution again
            "8\n",  # Apply another alternative correction
            "q\n",  # Quit the submenu
            "12\n",  # Export the solution to TOML
            "9\n",  # Add a feature to the solution
            "Check imports on my solution.\n",  # Enter the feature description
            "13\n"  # Exit the program
        ]

        # Combine all inputs into a single string
        input_sequence = "".join(inputs)
        print("[INFO] Input sequence prepared for testing.")

        # Run the main.py script and provide the inputs
        print("[INFO] Starting the main.py script...")
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            # Send the inputs to the program
            print("[INFO] Sending inputs to the program...")
            stdout, stderr = process.communicate(input=input_sequence, timeout=60)

            # Save the outputs for verification
            print("[INFO] Writing outputs to 'test_output.log'...")
            with open("test_output.log", "w") as log_file:
                log_file.write("Program Output:\n")
                log_file.write(stdout)
                if stderr:
                    log_file.write("\nProgram Errors:\n")
                    log_file.write(stderr)

            # Print a summary
            print("[INFO] Test completed. Check 'test_output.log' for details.")
            print("[INFO] Program Output:")
            print(stdout)
            if stderr:
                print("[ERROR] Program Errors:")
                print(stderr)

        except subprocess.TimeoutExpired:
            process.kill()
            print("[ERROR] The program took too long to respond and was terminated.")

if __name__ == "__main__":
    print("[INFO] Starting the test_main_menu function...")
    test_main_menu()
    print("[INFO] Test execution finished.")