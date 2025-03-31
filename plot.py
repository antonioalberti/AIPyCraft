import os
import re
import argparse
import statistics
import matplotlib.pyplot as plt
import glob
from collections import Counter

LOG_DIR = "logs"
PLOT_DIR = "plots" # Define the output directory for plots

def parse_log_file(log_filepath, solution_name, max_loops):
    """
    Parses a single tester log file to find the number of iterations to success.

    Args:
        log_filepath (str): Path to the tester log file.
        solution_name (str): The name of the solution being tested.
        max_loops (int): The maximum number of loops configured for the test run.

    Returns:
        int: Number of iterations if success was found, -1 otherwise.
    """
    last_iteration = -1
    success_found = False
    # Regex to find the loop iteration start line
    loop_pattern = re.compile(r"--- Starting Correction Loop Iteration (\d+)/(\d+) ---")
    # Regex to find the success line
    success_pattern = re.compile(rf"--- Solution '{re.escape(solution_name)}' completed successfully\. Stopping loop\. ---")

    try:
        with open(log_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                loop_match = loop_pattern.search(line)
                if loop_match:
                    last_iteration = int(loop_match.group(1)) # Capture the current iteration number

                success_match = success_pattern.search(line)
                if success_match:
                    success_found = True
                    # If success is found, the result is the last recorded iteration number
                    # If success happens before the first loop log (unlikely), last_iteration remains -1,
                    # which needs handling, but the logic implies success happens *after* a loop.
                    # If success happens *during* iteration X, last_iteration will be X.
                    return last_iteration

    except FileNotFoundError:
        print(f"Warning: Log file not found: {log_filepath}")
        return -1 # Indicate file not found / error
    except Exception as e:
        print(f"Warning: Error parsing log file {log_filepath}: {e}")
        return -1 # Indicate parsing error

    # If the loop finishes without finding the success line
    if not success_found:
        return -1 # Indicate failure to reach success

def main(trials, loops_value, solution_name):
    """
    Main function to analyze logs and generate plot.
    """
    print(f"Analyzing logs for solution '{solution_name}' across {trials} trials (max loops per trial: {loops_value}).")

    # Store results per trial: {trial_num: iterations_or_failure_code}
    # Use -1 for failure/error, 0 for success in 0 iterations (unlikely but handled)
    trial_results = {}
    parse_errors = 0

    # Find relevant log files
    log_pattern = os.path.join(LOG_DIR, f"tester_run_*_run*.log")
    all_log_files = glob.glob(log_pattern)

    run_id_to_log = {}
    # Extract run_id and find the latest log for each run_id (if multiple exist)
    for log_file in all_log_files:
        match = re.search(r"_run(\d+)\.log$", log_file)
        if match:
            run_id = int(match.group(1))
            # Keep only the latest log file if multiple exist for the same run_id
            # (based on filename timestamp implicitly)
            if run_id not in run_id_to_log or log_file > run_id_to_log[run_id]:
                 run_id_to_log[run_id] = log_file

    # Process logs for the requested number of trials
    processed_trials_count = 0
    for i in range(1, trials + 1):
        log_filepath = run_id_to_log.get(i)
        if log_filepath:
            processed_trials_count += 1
            print(f"Processing Trial {i}: {log_filepath}")
            iterations = parse_log_file(log_filepath, solution_name, loops_value)
            trial_results[i] = iterations # Store result (-1 for failure/error)
        else:
            print(f"Warning: Log file for Trial {i} not found.")
            parse_errors += 1 # Count missing files as errors
            # Optionally store a different code for missing logs if needed
            # trial_results[i] = -2 # Example: -2 for missing log

    # --- Statistics ---
    successful_iterations = [iters for iters in trial_results.values() if iters > 0]
    # Failures are trials processed where result is <= 0
    failed_trials = len([res for res in trial_results.values() if res <= 0])
    num_successful = len(successful_iterations)
    num_processed = len(trial_results) # Number of trials where logs were found

    print("\n--- Analysis Results ---")
    print(f"Total trials requested: {trials}")
    print(f"Trials processed (logs found): {num_processed}")
    print(f"Successful trials: {num_successful}")
    print(f"Failed trials (no success msg / error / 0 iters): {failed_trials}")
    print(f"Log files not found: {parse_errors}")

    if num_processed == 0:
         print("\nNo trials processed (no relevant log files found). Cannot generate plot.")
         return # Exit if no data

    # --- Plotting ---
    trial_numbers = sorted(trial_results.keys())
    # Replace -1 (failure) with 0 for plotting purposes on the bar chart
    iteration_values = [trial_results[t] if trial_results[t] > 0 else 0 for t in trial_numbers]

    plt.figure(figsize=(max(10, len(trial_numbers) * 0.5), 6)) # Adjust width based on number of trials

    colors = ['red' if trial_results[t] <= 0 else 'skyblue' for t in trial_numbers]
    plt.bar(trial_numbers, iteration_values, color=colors, edgecolor='black')

    plt.xlabel("Trial Number")
    plt.ylabel("Number of Correction Iterations to Success (0 = Failed)")
    plt.title(f"Iterations to Success per Trial for Solution '{solution_name}'\n({num_successful} Successful, {failed_trials} Failed out of {num_processed} Processed)")
    plt.xticks(trial_numbers) # Ensure a tick for each trial
    plt.grid(axis='y', alpha=0.75)
    plt.ylim(bottom=0) # Ensure y-axis starts at 0

    # Add overall stats text if needed
    # plt.text(...)

    # Ensure the plot directory exists
    os.makedirs(PLOT_DIR, exist_ok=True)
    plot_filename = f"iterations_per_trial_{solution_name}.png"
    plot_filepath = os.path.join(PLOT_DIR, plot_filename) # Construct full path

    plt.savefig(plot_filepath) # Save to the plots directory
    print(f"\nBar chart saved to: {plot_filepath}")
    # plt.show() # Uncomment to display the plot interactively

    # Also print summary stats if there were successes
    if num_successful > 0:
        min_iters = min(successful_iterations)
        max_iters = max(successful_iterations)
        mean_iters = statistics.mean(successful_iterations)
        median_iters = statistics.median(successful_iterations)
        print(f"\nStatistics for Successful Trials:")
        print(f"  Min iterations: {min_iters}")
        print(f"  Max iterations: {max_iters}")
        print(f"  Mean iterations: {mean_iters:.2f}")
        print(f"  Median iterations: {median_iters}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze tester logs and plot iterations to success.")
    parser.add_argument("-Trials", type=int, required=True, help="The total number of trials (log files) to analyze.")
    parser.add_argument("-LoopsValue", type=int, required=True, help="The max number of loops per trial (used to indicate failure).")
    parser.add_argument("-SolutionName", type=str, required=True, help="The name of the solution analyzed.")
    args = parser.parse_args()

    main(args.Trials, args.LoopsValue, args.SolutionName)
