import os
import re
import argparse
import statistics
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker # Import ticker
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
    # Make figure square
    plt.figure(figsize=(5, 3)) # Square figure

    # Prepare data for error bar plot
    if cumulative_trial_numbers_for_plot:
        x_values = np.array(cumulative_trial_numbers_for_plot)
        means_np = np.array(cumulative_means)
        ci_lowers_np = np.array(cumulative_ci_lowers)
        ci_uppers_np = np.array(cumulative_ci_uppers)

        # Calculate asymmetric error bars
        lower_error = np.where(np.isnan(ci_lowers_np), np.nan, means_np - ci_lowers_np)
        upper_error = np.where(np.isnan(ci_uppers_np), np.nan, ci_uppers_np - means_np)
        lower_error = np.maximum(0, lower_error)
        upper_error = np.maximum(0, upper_error)
        y_err = np.array([lower_error, upper_error])

        # Filter out entries where mean or error is NaN
        valid_indices = ~np.isnan(means_np) & ~np.isnan(y_err[0,:]) & ~np.isnan(y_err[1,:])
        x_values_valid = x_values[valid_indices]
        means_valid = means_np[valid_indices]
        y_err_valid = y_err[:, valid_indices]

        if len(x_values_valid) > 0:
            # Use plt.errorbar to plot mean markers and error bars (no connecting line)
            plt.errorbar(x_values_valid, means_valid, yerr=y_err_valid,
                         fmt='o', color='dodgerblue', # Circle markers only, blue color
                         ecolor='black', capsize=5, # Black error bars with caps
                         markersize=4, # Reduced marker size
                         label='Mean Iterations (95% CI)') # Adjusted label for this script
        else:
             print("No valid data points with confidence intervals to plot.")

    # Configure plot appearance (Applying settings from plot_total_test_time.py)
    plt.xlabel("Trial Number", fontsize=12) # Font size from plot_total_test_time.py
    plt.ylabel("Iterations to Success", fontsize=12) # Font size from plot_total_test_time.py
    # Set x-ticks to only successful, valid trial numbers used in the cumulative plot
    plt.xticks(cumulative_trial_numbers_for_plot)
    plt.tick_params(axis='x', labelsize=11, rotation=45) # Font size from plot_total_test_time.py
    plt.tick_params(axis='y', labelsize=11) # Font size from plot_total_test_time.py
    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f')) # Format Y-axis to 1 decimal place
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(bottom=0)
    if cumulative_trial_numbers_for_plot and len(x_values_valid) > 0:
        plt.legend(fontsize=11) # Font size from plot_total_test_time.py

    # Add text for failure count
    plt.text(0.05, 0.9, f'Failed Trials: {failed_trials}', # Using correct variable for this script & standard top-left coordinates
             horizontalalignment='left', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=11, color='red') # Font size from plot_total_test_time.py & removed leading space before transform

    # Adjust layout
    plt.tight_layout(pad=1.5)

    # Ensure the plot directory exists
    os.makedirs(PLOT_DIR, exist_ok=True)
    plot_filename = f"cumulativeinteractions-{solution_name}.pdf" # Changed filename format
    plot_filepath = os.path.join(PLOT_DIR, plot_filename) # Construct full path

    plt.savefig(plot_filepath, format='pdf') # Save as PDF
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
