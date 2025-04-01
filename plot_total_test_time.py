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

# --- Helper function copied and adapted from plot_interactions_to_success.py ---
def check_trial_success(tester_log_filepath, solution_name, max_loops):
    """
    Checks if a trial was successful based on its tester log file.

    Args:
        tester_log_filepath (str): Path to the tester log file.
        solution_name (str): The name of the solution being tested.
        max_loops (int): The maximum number of loops configured for the test run.

    Returns:
        bool: True if success message was found, False otherwise.
    """
    success_found = False
    # Regex to find the success line
    success_pattern = re.compile(rf"--- Solution '{re.escape(solution_name)}' completed successfully\. Stopping loop\. ---")

    try:
        with open(tester_log_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if success_pattern.search(line):
                    success_found = True
                    break # Found success, no need to read further
        return success_found
    except FileNotFoundError:
        print(f"Warning: Tester log file not found for success check: {tester_log_filepath}")
        return False # Treat missing tester log as failure for duration calculation
    except Exception as e:
        print(f"Warning: Error reading tester log file {tester_log_filepath} for success check: {e}")
        return False # Treat errors as failure

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

        # Check if the trial was successful using the tester log
        is_success = check_trial_success(tester_log_filepath, solution_name, loops_value)

        if not is_success:
            print(f"Info: Trial {i} failed (based on tester log). Skipping duration calculation.")
            skipped_failed_trials += 1
            continue # Skip this trial

        # If successful, proceed to calculate duration from the main log
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
         return # Exit if no data

    # --- Calculate Cumulative Statistics (based on successful trials with valid durations) ---
    valid_trial_numbers_sorted = sorted(valid_durations.keys())
    cumulative_trial_numbers_for_plot = []
    cumulative_means = []
    cumulative_ci_lowers = []
    cumulative_ci_uppers = []
    current_successful_valid_durations = []

    for k in valid_trial_numbers_sorted: # Iterate through the successful trials with valid durations
        current_successful_valid_durations.append(valid_durations[k])

        if len(current_successful_valid_durations) >= 2: # Need at least 2 points for CI
            mean_k = np.mean(current_successful_valid_durations)
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

            cumulative_trial_numbers_for_plot.append(k)
            cumulative_means.append(mean_k)
            cumulative_ci_lowers.append(ci_lower_k)
            cumulative_ci_uppers.append(ci_upper_k)
        elif len(current_successful_valid_durations) == 1: # Can plot mean but not CI yet
             mean_k = current_successful_valid_durations[0]
             cumulative_trial_numbers_for_plot.append(k)
             cumulative_means.append(mean_k)
             cumulative_ci_lowers.append(np.nan) # Append NaN for CI bounds
             cumulative_ci_uppers.append(np.nan)

    # --- Plotting ---
    # Use the already filtered valid_durations dictionary
    valid_trial_numbers_plot = list(valid_durations.keys())
    valid_duration_values_plot = list(valid_durations.values())

    if not valid_trial_numbers_plot:
        print("\nNo valid trial durations to plot.")
        return # Exit if no valid data points

    plt.figure(figsize=(max(10, len(valid_trial_numbers_plot) * 0.5), 6)) # Adjust size based on valid trials

    # Plot individual valid trial durations
    plt.scatter(valid_trial_numbers_plot, valid_duration_values_plot, color='skyblue', label='Successful Trial Duration (s)', zorder=5, alpha=0.7)

    # Plot cumulative mean line (using data derived from valid trials only)
    if cumulative_trial_numbers_for_plot:
        plt.plot(cumulative_trial_numbers_for_plot, cumulative_means, marker='.', linestyle='-', color='orange', label='Cumulative Mean Duration (Successful Trials, s)', zorder=10)

        # Shade the cumulative confidence interval band
        ci_lowers_np = np.array(cumulative_ci_lowers)
        ci_uppers_np = np.array(cumulative_ci_uppers)
        plt.fill_between(cumulative_trial_numbers_for_plot, ci_lowers_np, ci_uppers_np, color='palegreen', alpha=0.4, label='Cumulative 95% CI', zorder=0)

    plt.xlabel("Successful Trial Number") # Updated label
    plt.ylabel("Total Test Duration (seconds)")
    plt.title(f"Test Duration for Successful Trials - Solution '{solution_name}'") # Updated title
    plt.xticks(valid_trial_numbers_plot) # Set x-ticks to only successful, valid trial numbers
    plt.grid(axis='y', alpha=0.75)
    plt.ylim(bottom=0) # Ensure y-axis starts at 0
    plt.legend()

    # Ensure the plot directory exists
    os.makedirs(PLOT_DIR, exist_ok=True)
    plot_filename = f"cumulative_total_time_plot_{solution_name}.png" # New filename
    plot_filepath = os.path.join(PLOT_DIR, plot_filename)

    plt.savefig(plot_filepath)
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
