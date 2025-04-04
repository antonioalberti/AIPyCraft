import os
import re
import argparse
import statistics
import matplotlib.pyplot as plt
import glob
from datetime import datetime
import numpy as np
from scipy import stats

LOG_DIR = "logs"
PLOT_DIR = "plots" # Define the output directory for plots
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S,%f" # Format including milliseconds

# --- Removed old check_trial_success function ---

# --- Added parse_log_file function from plot_interactions_to_success.py ---
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
# --- End of added parse_log_file function ---


def parse_log_for_duration(log_filepath):
    """
    Parses a single AIPyCraft main log file to find the total duration.

    Args:
        log_filepath (str): Path to the AIPyCraft main log file.

    Returns:
        float: Total duration in seconds if successful, -1.0 otherwise.
    """
    first_timestamp = None
    last_timestamp = None

    try:
        with open(log_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                print(f"Warning: Log file is empty: {log_filepath}")
                return -1.0

            # Extract timestamp from the first line
            first_line = lines[0]
            match_first = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", first_line)
            if match_first:
                try:
                    first_timestamp = datetime.strptime(match_first.group(1), TIMESTAMP_FORMAT)
                except ValueError as e:
                    print(f"Warning: Could not parse timestamp in first line of {log_filepath}: {e}")
                    return -1.0
            else:
                print(f"Warning: Could not find timestamp in first line of {log_filepath}")
                return -1.0

            # Extract timestamp from the last line
            last_line = lines[-1]
            match_last = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", last_line)
            if match_last:
                 try:
                    # Handle potential trailing newline characters before parsing
                    timestamp_str = match_last.group(1).strip()
                    last_timestamp = datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)
                 except ValueError as e:
                    print(f"Warning: Could not parse timestamp in last line of {log_filepath}: {e}")
                    return -1.0 # Indicate parsing error
            else:
                # Fallback: search backwards if the last line doesn't match immediately
                for line in reversed(lines):
                    match_last_fallback = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", line)
                    if match_last_fallback:
                        try:
                            last_timestamp = datetime.strptime(match_last_fallback.group(1), TIMESTAMP_FORMAT)
                            break # Found the last timestamp
                        except ValueError as e:
                            continue # Try previous line if parse error
                if not last_timestamp:
                    print(f"Warning: Could not find timestamp in last lines of {log_filepath}")
                    return -1.0 # Indicate failure to find last timestamp

            # Calculate duration
            if first_timestamp and last_timestamp:
                duration = last_timestamp - first_timestamp
                return duration.total_seconds()
            else:
                # This case should ideally not be reached due to earlier checks
                return -1.0

    except FileNotFoundError:
        print(f"Warning: Log file not found: {log_filepath}")
        return -1.0 # Indicate file not found
    except Exception as e:
        print(f"Warning: Error parsing duration log file {log_filepath}: {e}")
        return -1.0 # Indicate general parsing error

def main(trials, loops_value, solution_name):
    """
    Main function to analyze logs and generate plot for total test time,
    considering only successful trials.
    """
    print(f"Analyzing total test time from logs for solution '{solution_name}' across {trials} trials (max loops: {loops_value}).")

    # Store results per trial: {trial_num: duration_in_seconds_or_error_code}
    # Use -1.0 for error, -2.0 for skipped due to failure
    trial_durations = {}
    duration_parse_errors = 0
    skipped_failed_trials = 0
    processed_trials_count = 0

    # Find relevant log files (AIPyCraft_main and tester logs)
    main_log_pattern = os.path.join(LOG_DIR, f"AIPyCraft_main_*_run*.log")
    tester_log_pattern = os.path.join(LOG_DIR, f"tester_run_*_run*.log")
    all_main_logs = glob.glob(main_log_pattern)
    all_tester_logs = glob.glob(tester_log_pattern)

    main_run_id_to_log = {}
    tester_run_id_to_log = {}

    # Map run IDs to latest main logs
    for log_file in all_main_logs:
        match = re.search(r"_run(\d+)\.log$", log_file)
        if match:
            run_id = int(match.group(1))
            if run_id not in main_run_id_to_log or log_file > main_run_id_to_log[run_id]:
                 main_run_id_to_log[run_id] = log_file

    # Map run IDs to latest tester logs
    for log_file in all_tester_logs:
        match = re.search(r"_run(\d+)\.log$", log_file)
        if match:
            run_id = int(match.group(1))
            if run_id not in tester_run_id_to_log or log_file > tester_run_id_to_log[run_id]:
                 tester_run_id_to_log[run_id] = log_file

    # Process logs for the requested number of trials
    for i in range(1, trials + 1):
        tester_log_filepath = tester_run_id_to_log.get(i)
        main_log_filepath = main_run_id_to_log.get(i)

        if not tester_log_filepath:
            print(f"Warning: Tester log for Trial {i} not found. Skipping duration calculation.")
            skipped_failed_trials += 1 # Count as skipped/failed
            continue # Skip this trial

        # Check if the trial was successful using the tester log (using parse_log_file now)
        iterations, error_msg = parse_log_file(tester_log_filepath, solution_name, loops_value)

        # Determine success based on iterations >= 0
        if iterations < 0:
            error_reason = f" ({error_msg})" if error_msg else ""
            print(f"Info: Trial {i} failed or error{error_reason} (based on tester log). Skipping duration calculation.")
            skipped_failed_trials += 1
            continue # Skip this trial

        # If successful (iterations >= 0), proceed to calculate duration from the main log
        processed_trials_count += 1 # Count only trials checked for duration
        if main_log_filepath:
            print(f"Processing Successful Trial {i} for duration: {main_log_filepath}")
            duration = parse_log_for_duration(main_log_filepath)
            trial_durations[i] = duration # Store duration or -1.0 for error
            if duration < 0:
                duration_parse_errors += 1
        else:
            print(f"Warning: Main log for successful Trial {i} not found. Cannot calculate duration.")
            trial_durations[i] = -1.0 # Mark as error if main log is missing for a successful trial
            duration_parse_errors += 1

    # --- Statistics ---
    # Filter results to include only successful trials with valid durations
    valid_durations = {k: v for k, v in trial_durations.items() if v >= 0}
    num_valid_duration_trials = len(valid_durations)

    print("\n--- Analysis Results ---")
    print(f"Total trials requested: {trials}")
    print(f"Trials processed for duration (successful & main log found): {processed_trials_count}")
    print(f"Trials skipped due to failure or missing tester log: {skipped_failed_trials}")
    print(f"Successful trials with valid duration calculated: {num_valid_duration_trials}")
    print(f"Successful trials with duration errors (missing main log/parse error): {duration_parse_errors}")

    if num_valid_duration_trials == 0:
         print("\nNo successful trials with valid durations found. Cannot generate plot.")
         return # Exit if no data # Corrected indentation

    # --- Calculate Cumulative Statistics (based on successful trials with valid durations) ---
    valid_trial_numbers_sorted = sorted(valid_durations.keys())
    cumulative_trial_numbers_for_plot = []
    cumulative_means = []
    cumulative_ci_lowers = []
    cumulative_ci_uppers = []
    current_successful_valid_durations = []

    for k in valid_trial_numbers_sorted: # Iterate through the successful trials with valid durations
        current_successful_valid_durations.append(valid_durations[k])

        # Calculate mean regardless of CI calculation
        mean_k = np.mean(current_successful_valid_durations)
        cumulative_trial_numbers_for_plot.append(k)
        cumulative_means.append(mean_k)

        # Calculate CI only if we have at least 2 points
        if len(current_successful_valid_durations) >= 2:
            sem_k = stats.sem(current_successful_valid_durations)
            df_k = len(current_successful_valid_durations) - 1
            confidence_level = 0.95
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

    # --- Plotting ---
    # Make figure square
    plt.figure(figsize=(5, 5)) # Square figure

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
                         label='Cumulative Mean Duration (95% CI, s)')
        else:
             print("No valid data points with confidence intervals to plot.")

    # Configure plot appearance
    plt.xlabel("Successful Trial Number", fontsize=12) # Reduced font size
    plt.ylabel("Cumulative Mean Total Test Duration (seconds)", fontsize=12) # Reduced font size, Adjusted label
    # Set x-ticks to only successful, valid trial numbers used in the cumulative plot
    plt.xticks(cumulative_trial_numbers_for_plot)
    plt.tick_params(axis='x', labelsize=11, rotation=45) # Reduced font size
    plt.tick_params(axis='y', labelsize=11) # Reduced font size
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(bottom=0)
    if cumulative_trial_numbers_for_plot and len(x_values_valid) > 0:
        plt.legend(fontsize=11) # Reduced font size

    # Add text for skipped/failed trial count
    plt.text(0.15, 0.85, f'Failed Trials: {skipped_failed_trials}',
             horizontalalignment='left', verticalalignment='top',
              transform=plt.gca().transAxes, fontsize=11, color='red')

    # Adjust layout
    plt.tight_layout(pad=1.5)

    # Ensure the plot directory exists
    os.makedirs(PLOT_DIR, exist_ok=True)
    plot_filename = f"time-{solution_name}.pdf" # Changed filename format (already done in previous step, confirming)
    plot_filepath = os.path.join(PLOT_DIR, plot_filename)

    plt.savefig(plot_filepath, format='pdf') # Save as PDF
    print(f"\nCumulative total time plot saved to: {plot_filepath}")
    # plt.show()

    # Also print overall summary stats for successful trials with valid durations
    if num_valid_duration_trials > 0:
        valid_duration_list = list(valid_durations.values())
        min_dur = min(valid_duration_list)
        max_dur = max(valid_duration_list)
        mean_dur = statistics.mean(valid_duration_list)
        median_dur = statistics.median(valid_duration_list)
        print(f"\nOverall Statistics for {num_valid_duration_trials} Successful Trials with Valid Durations:")
        print(f"  Min duration: {min_dur:.2f} s")
        print(f"  Max duration: {max_dur:.2f} s")
        print(f"  Mean duration: {mean_dur:.2f} s")
        print(f"  Median duration: {median_dur:.2f} s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze AIPyCraft main logs for successful trials and plot total test duration.")
    parser.add_argument("-Trials", type=int, required=True, help="The total number of trials to check.")
    # Add LoopsValue argument needed for success check
    parser.add_argument("-LoopsValue", type=int, required=True, help="The max number of loops per trial (used for success check).")
    parser.add_argument("-SolutionName", type=str, required=True, help="The name of the solution analyzed.")
    args = parser.parse_args()

    main(args.Trials, args.LoopsValue, args.SolutionName)
