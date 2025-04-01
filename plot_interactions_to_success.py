import os
import re
import argparse
import statistics
import matplotlib.pyplot as plt
import glob
from collections import Counter
import numpy as np # Import numpy
from scipy import stats # Import scipy.stats

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
        tuple[int, str | None]: A tuple containing:
            - int: Number of iterations if success was found, -1 otherwise.
            - str | None: An error message if failure occurred, None otherwise.
    """
    last_iteration = -1
    success_found = False
    toml_error_details = [] # Store unique TOML error details
    runtime_error_details = [] # Store unique Runtime error details
    state = "searching" # State machine: searching, found_after, found_blank, found_output

    # Regex patterns
    loop_pattern = re.compile(r"--- Starting Correction Loop Iteration (\d+)/(\d+) ---")
    success_pattern = re.compile(rf"--- Solution '{re.escape(solution_name)}' completed successfully\. Stopping loop\. ---")
    toml_error_pattern = re.compile(r"Failed to parse TOML file:(.*)") # Regex for TOML error

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
                    return (last_iteration, None) # Success

                # Check for TOML error
                toml_match = toml_error_pattern.search(line)
                if toml_match:
                    current_detail = toml_match.group(1).strip()
                    # Add the detail if it's not a placeholder and not already collected
                    if current_detail and current_detail not in ('{e}")', '{e}') and current_detail not in toml_error_details:
                        toml_error_details.append(current_detail)

                # State machine for runtime errors
                line_strip = line.strip()
                if state == "searching" and line_strip == "After trying to run the solution, the results was:":
                    state = "found_after"
                elif state == "found_after" and line_strip == "":
                    state = "found_blank" # Expecting blank line
                elif state == "found_blank" and line_strip == "Output:":
                    state = "found_output" # Expecting "Output:"
                elif state == "found_output" and line.startswith("Error: "):
                    runtime_error = line[len("Error: "):].strip()
                    if runtime_error and runtime_error not in runtime_error_details:
                        runtime_error_details.append(runtime_error)
                    state = "searching" # Reset after finding the error line
                elif state != "searching":
                    # If the sequence breaks, reset the state
                    state = "searching"


    except FileNotFoundError:
        # Return error message
        return (-1, f"Log file not found: {log_filepath}") # Indicate file not found / error
    except Exception as e:
        # Return error message instead of just printing warning here
        return (-1, f"Error parsing log file {log_filepath}: {e}") # Indicate parsing error

    # After checking the whole file, determine the failure reason
    if not success_found:
        if runtime_error_details:
            # Prioritize reporting runtime errors if found
            error_summary = "; ".join(runtime_error_details)
            return (-1, f"Runtime errors found: {error_summary}")
        elif toml_error_details:
            # Report TOML errors if no runtime errors were found
            error_summary = "; ".join(toml_error_details)
            return (-1, f"TOML parse errors found: {error_summary}")
        else:
            # Otherwise, report generic failure
            return (-1, "Success message not found within max loops")

    # Fallback in case logic is flawed (should not be reached if success_found is True)
    return (-1, "Unknown parsing state")

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
            # --- Modified to handle tuple return ---
            iterations, error_msg = parse_log_file(log_filepath, solution_name, loops_value)
            if iterations > 0:
                print(f"  -> Trial {i} Result: SUCCESS (Iterations: {iterations})")
            else:
                # Print the specific error message returned by parse_log_file
                error_reason = f" ({error_msg})" if error_msg else ""
                print(f"  -> Trial {i} Result: FAILURE/ERROR{error_reason}")
            # --- End of modification ---
            trial_results[i] = iterations # Store iteration count (-1 for failure/error)
        else:
            # Handle missing log file case directly here as well
            print(f"Warning: Log file for Trial {i} not found.")
            parse_errors += 1 # Count missing files as errors
            trial_results[i] = -1 # Store -1 for missing log file
            parse_errors += 1 # Count missing files as errors

    # --- Statistics ---
    successful_iterations_overall = [iters for iters in trial_results.values() if iters > 0]
    # Failures are trials processed where result is <= 0
    failed_trials = len([res for res in trial_results.values() if res <= 0])
    num_successful = len(successful_iterations_overall)
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

    # --- Calculate Cumulative Statistics ---
    trial_numbers_processed = sorted(trial_results.keys())
    cumulative_trial_numbers_for_plot = []
    cumulative_means = []
    cumulative_ci_lowers = []
    cumulative_ci_uppers = []
    current_successful_iterations = []

    for k in trial_numbers_processed: # Iterate through the processed trials in order
        if trial_results[k] > 0: # Consider only successful trials for cumulative stats
            current_successful_iterations.append(trial_results[k])

        if len(current_successful_iterations) >= 2: # Need at least 2 successful points for CI
            mean_k = np.mean(current_successful_iterations)
            sem_k = stats.sem(current_successful_iterations)
            df_k = len(current_successful_iterations) - 1
            confidence_level = 0.95
            # Calculate confidence interval using t-distribution
            # Handle potential division by zero or invalid df if sem is 0
            if sem_k > 0 and df_k > 0:
                 ci_margin_k = sem_k * stats.t.ppf((1 + confidence_level) / 2., df_k)
                 ci_lower_k = mean_k - ci_margin_k
                 ci_upper_k = mean_k + ci_margin_k
            else: # If SEM is 0 (all values identical), CI is just the mean
                 ci_lower_k = mean_k
                 ci_upper_k = mean_k

            cumulative_trial_numbers_for_plot.append(k)
            cumulative_means.append(mean_k)
            cumulative_ci_lowers.append(ci_lower_k)
            cumulative_ci_uppers.append(ci_upper_k)
        elif len(current_successful_iterations) == 1: # Can plot mean but not CI yet
             mean_k = current_successful_iterations[0]
             cumulative_trial_numbers_for_plot.append(k)
             cumulative_means.append(mean_k)
             # Append NaN for CI bounds when not calculable
             cumulative_ci_lowers.append(np.nan)
             cumulative_ci_uppers.append(np.nan)

    # --- Plotting ---
    plt.figure(figsize=(max(10, len(trial_numbers_processed) * 0.5), 6)) # Adjust width based on number of trials

    # Plot individual successful points
    successful_trial_numbers = [t for t in trial_numbers_processed if trial_results[t] > 0]
    successful_iteration_values = [trial_results[t] for t in successful_trial_numbers]
    if successful_trial_numbers:
        plt.scatter(successful_trial_numbers, successful_iteration_values, color='skyblue', label='Successful Trial Iterations', zorder=5, alpha=0.7) # Use scatter

    # Plot cumulative mean line
    if cumulative_trial_numbers_for_plot:
        plt.plot(cumulative_trial_numbers_for_plot, cumulative_means, marker='.', linestyle='-', color='orange', label='Cumulative Mean', zorder=10)

        # Shade the cumulative confidence interval band
        # Ensure CI bounds are numpy arrays for potential NaN handling if needed by fill_between
        ci_lowers_np = np.array(cumulative_ci_lowers)
        ci_uppers_np = np.array(cumulative_ci_uppers)
        plt.fill_between(cumulative_trial_numbers_for_plot, ci_lowers_np, ci_uppers_np, color='palegreen', alpha=0.4, label='Cumulative 95% CI', zorder=0)

    plt.xlabel("Trial Number")
    plt.ylabel("Number of Correction Iterations")
    #plt.title(f"Cumulative Mean Iterations to Success for Solution '{solution_name}'\n({num_successful} Successful, {failed_trials} Failed out of {num_processed} Processed)")
    plt.xticks(trial_numbers_processed) # Ensure a tick for each processed trial
    plt.grid(axis='y', alpha=0.75)
    plt.ylim(bottom=0) # Ensure y-axis starts at 0
    plt.legend() # Show legend

    # Add text for failure count
    plt.text(0.95, 0.95, f'Failed Trials: {failed_trials}',
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=10, color='red')

    # Ensure the plot directory exists
    os.makedirs(PLOT_DIR, exist_ok=True)
    plot_filename = f"cumulative_iterations_plot_{solution_name}.png" # New filename
    plot_filepath = os.path.join(PLOT_DIR, plot_filename) # Construct full path

    plt.savefig(plot_filepath) # Save to the plots directory
    print(f"\nCumulative iterations plot saved to: {plot_filepath}")
    # plt.show() # Uncomment to display the plot interactively

    # Also print overall summary stats if there were successes
    if num_successful > 0:
        min_iters = min(successful_iterations_overall)
        max_iters = max(successful_iterations_overall)
        mean_iters = statistics.mean(successful_iterations_overall)
        median_iters = statistics.median(successful_iterations_overall)
        print(f"\nOverall Statistics for {num_successful} Successful Trials:")
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
