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
    Parses a single tester log file to find the number of iterations to success,
    based *only* on the last occurrence of "Solution completed with status: SUCCESS"
    or "Solution completed with status: ERROR".

    Args:
        log_filepath (str): Path to the tester log file.
        solution_name (str): The name of the solution being tested (unused in this logic).
        max_loops (int): The maximum number of loops configured for the test run (unused).

    Returns:
        tuple[int, str | None]: A tuple containing:
            - int: Number of iterations if success was found (>=0), -1 otherwise.
            - str | None: Error message "Completed with status: ERROR" if that specific
                          status line is found and success wasn't, otherwise None or
                          another error message (file not found, parse error, status unknown).
    """
    # Compile patterns
    loop_pattern = re.compile(r"--- Starting Correction Loop Iteration (\d+)/(\d+) ---")
    success_pattern_string = "Solution completed with status: SUCCESS"
    error_pattern_string = "Solution completed with status: ERROR"
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    last_success_index = -1
    last_error_index = -1

    try:
        with open(log_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find the index of the LAST relevant status line using endswith
        for idx, line in enumerate(lines):
            cleaned_line = ansi_escape.sub('', line).strip()
            if cleaned_line.endswith(success_pattern_string):
                last_success_index = idx
            elif cleaned_line.endswith(error_pattern_string):
                last_error_index = idx

        # Determine outcome based on which status appeared last
        if last_success_index > last_error_index:
            # Success is the final status. Find the iteration number before this line.
            final_success_iter = -1
            # Search backwards starting strictly *before* the success line index
            for i in range(last_success_index - 1, -1, -1):
                # Match loop pattern on the raw line content
                loop_match = loop_pattern.search(lines[i]) # Search raw line for loop marker
                if loop_match:
                    final_success_iter = int(loop_match.group(1))
                    break
            # If success happened before loop 1 (or no loop marker found before it), iteration is 0
            return (max(0, final_success_iter), None)

        elif last_error_index > last_success_index:
            # Error is the final status
            return (-1, "Completed with status: ERROR")
        elif last_error_index != -1:
             # Only error was found, and it wasn't preceded by a later success
             return (-1, "Completed with status: ERROR")
        else:
            # Neither SUCCESS nor ERROR status found in the log
            return (-1, "SUCCESS/ERROR status not found")

    except FileNotFoundError:
        return (-1, f"Log file not found: {log_filepath}")
    except Exception as e:
        return (-1, f"Error parsing log file {log_filepath}: {e}")

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
            # Treat iteration 0 as success as well
            if iterations >= 0:
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
    # Success is now iterations >= 0
    successful_iterations_overall = [iters for iters in trial_results.values() if iters >= 0]
    # Failures are trials processed where result is < 0
    failed_trials = len([res for res in trial_results.values() if res < 0])
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
        # CORRECTED: Include trials succeeding at iteration 0 (>= 0)
        if trial_results[k] >= 0: # Consider successful trials (including 0 iterations)
            current_successful_iterations.append(trial_results[k])

        # Calculate stats if we have successful iterations
        if current_successful_iterations:
             mean_k = np.mean(current_successful_iterations)
             cumulative_trial_numbers_for_plot.append(k) # Add trial number regardless of CI calc
             cumulative_means.append(mean_k)

             # Calculate CI only if we have at least 2 points
             if len(current_successful_iterations) >= 2:
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
                 cumulative_ci_lowers.append(ci_lower_k)
                 cumulative_ci_uppers.append(ci_upper_k)
             else: # Only 1 point, append NaN for CI
                 cumulative_ci_lowers.append(np.nan)
                 cumulative_ci_uppers.append(np.nan)
        # If trial_results[k] was < 0, we don't add to cumulative stats for this k,
        # but the loop continues to the next trial number k.

    # --- Plotting ---
    plt.figure(figsize=(max(10, len(trial_numbers_processed) * 0.5), 6)) # Adjust width based on number of trials

    # Plot individual successful points (iters >= 0)
    successful_trial_numbers = [t for t in trial_numbers_processed if trial_results[t] >= 0]
    successful_iteration_values = [trial_results[t] for t in successful_trial_numbers]
    if successful_trial_numbers:
        plt.scatter(successful_trial_numbers, successful_iteration_values, color='skyblue', label='Successful Trial Iterations', zorder=5, alpha=0.7) # Use scatter

    # Plot cumulative mean line
    if cumulative_trial_numbers_for_plot:
        plt.plot(cumulative_trial_numbers_for_plot, cumulative_means, marker='.', linestyle='-', color='orange', label='Cumulative Mean (Successful Trials)', zorder=10) # Updated label

        # Shade the cumulative confidence interval band
        # Ensure CI bounds are numpy arrays for potential NaN handling if needed by fill_between
        ci_lowers_np = np.array(cumulative_ci_lowers)
        ci_uppers_np = np.array(cumulative_ci_uppers)
        # Filter out NaN values before plotting CI band to avoid warnings/errors
        valid_ci_indices = ~np.isnan(ci_lowers_np) & ~np.isnan(ci_uppers_np)
        if np.any(valid_ci_indices):
             plt.fill_between(np.array(cumulative_trial_numbers_for_plot)[valid_ci_indices],
                              ci_lowers_np[valid_ci_indices],
                              ci_uppers_np[valid_ci_indices],
                              color='palegreen', alpha=0.4, label='Cumulative 95% CI (Successful Trials)', zorder=0) # Updated label

    plt.xlabel("Trial Number")
    plt.ylabel("Number of Correction Iterations to Success") # Updated label
    plt.title(f"Cumulative Mean Iterations to Success for Solution '{solution_name}'\n({num_successful} Successful, {failed_trials} Failed out of {num_processed} Processed)")
    plt.xticks(trial_numbers_processed) # Ensure a tick for each processed trial
    plt.grid(axis='y', alpha=0.75)
    # Ensure y-axis starts at 0 or slightly below if CI dips below
    # Corrected calculation of min_y based on potentially empty or all-NaN CI arrays
    min_ci_lower_val = np.nanmin(cumulative_ci_lowers) if cumulative_ci_lowers and not all(np.isnan(x) for x in cumulative_ci_lowers) else 0
    min_y = min(0, min_ci_lower_val)
    plt.ylim(bottom=min_y)
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
