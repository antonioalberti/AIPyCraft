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
        print(f"Warning: Error parsing log file {log_filepath}: {e}")
        return -1.0 # Indicate general parsing error

def main(trials, solution_name):
    """
    Main function to analyze logs and generate plot for total test time.
    """
    print(f"Analyzing total test time from logs for solution '{solution_name}' across {trials} trials.")

    # Store results per trial: {trial_num: duration_in_seconds_or_error_code}
    # Use -1.0 for failure/error
    trial_results = {}
    parse_errors = 0

    # Find relevant log files (AIPyCraft_main logs)
    log_pattern = os.path.join(LOG_DIR, f"AIPyCraft_main_*_run*.log")
    all_log_files = glob.glob(log_pattern)

    run_id_to_log = {}
    # Extract run_id and find the latest log for each run_id
    for log_file in all_log_files:
        match = re.search(r"_run(\d+)\.log$", log_file)
        if match:
            run_id = int(match.group(1))
            if run_id not in run_id_to_log or log_file > run_id_to_log[run_id]:
                 run_id_to_log[run_id] = log_file

    # Process logs for the requested number of trials
    processed_trials_count = 0
    for i in range(1, trials + 1):
        log_filepath = run_id_to_log.get(i)
        if log_filepath:
            processed_trials_count += 1
            print(f"Processing Trial {i}: {log_filepath}")
            duration = parse_log_for_duration(log_filepath)
            trial_results[i] = duration # Store duration or -1.0 for error
            if duration < 0:
                parse_errors += 1
        else:
            print(f"Warning: Log file for Trial {i} not found.")
            # Count missing files towards parse_errors for consistency
            parse_errors += 1

    # --- Statistics ---
    valid_durations = [d for d in trial_results.values() if d >= 0] # Durations >= 0 are valid
    num_valid_trials = len(valid_durations)
    num_processed = len(trial_results) # Number of trials where logs were found and processed

    print("\n--- Analysis Results ---")
    print(f"Total trials requested: {trials}")
    print(f"Trials processed (logs found): {num_processed}")
    print(f"Trials with valid duration calculated: {num_valid_trials}")
    print(f"Trials with errors (missing/empty/parse error): {parse_errors}")

    if num_valid_trials == 0:
         print("\nNo trials with valid durations found. Cannot generate plot.")
         return # Exit if no data

    # --- Calculate Cumulative Statistics ---
    trial_numbers_processed = sorted(trial_results.keys())
    cumulative_trial_numbers_for_plot = []
    cumulative_means = []
    cumulative_ci_lowers = []
    cumulative_ci_uppers = []
    current_valid_durations = []

    for k in trial_numbers_processed: # Iterate through the processed trials in order
        if trial_results[k] >= 0: # Consider only trials with valid durations
            current_valid_durations.append(trial_results[k])

            if len(current_valid_durations) >= 2: # Need at least 2 points for CI
                mean_k = np.mean(current_valid_durations)
                sem_k = stats.sem(current_valid_durations)
                df_k = len(current_valid_durations) - 1
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
            elif len(current_valid_durations) == 1: # Can plot mean but not CI yet
                 mean_k = current_valid_durations[0]
                 cumulative_trial_numbers_for_plot.append(k)
                 cumulative_means.append(mean_k)
                 cumulative_ci_lowers.append(np.nan) # Append NaN for CI bounds
                 cumulative_ci_uppers.append(np.nan)

    # --- Plotting ---
    # Filter processed trial numbers to only include those with valid results for plotting
    valid_trial_numbers = [t for t in trial_numbers_processed if trial_results[t] >= 0]
    valid_duration_values = [trial_results[t] for t in valid_trial_numbers]

    if not valid_trial_numbers:
        print("\nNo valid trial durations to plot.")
        return # Exit if no valid data points

    plt.figure(figsize=(max(10, len(valid_trial_numbers) * 0.5), 6)) # Adjust size based on valid trials

    # Plot individual valid trial durations
    plt.scatter(valid_trial_numbers, valid_duration_values, color='skyblue', label='Trial Duration (s)', zorder=5, alpha=0.7)

    # Plot cumulative mean line
    if cumulative_trial_numbers_for_plot:
        plt.plot(cumulative_trial_numbers_for_plot, cumulative_means, marker='.', linestyle='-', color='orange', label='Cumulative Mean Duration (s)', zorder=10)

        # Shade the cumulative confidence interval band
        ci_lowers_np = np.array(cumulative_ci_lowers)
        ci_uppers_np = np.array(cumulative_ci_uppers)
        plt.fill_between(cumulative_trial_numbers_for_plot, ci_lowers_np, ci_uppers_np, color='palegreen', alpha=0.4, label='Cumulative 95% CI', zorder=0)

    plt.xlabel("Trial Number") # Updated label
    plt.ylabel("Total Test Duration (seconds)")
    # Removed the subtitle line with counts
    #plt.title(f"Cumulative Mean Total Test Duration for Solution '{solution_name}'")
    plt.xticks(valid_trial_numbers) # Set x-ticks to only valid trial numbers
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

    # Also print overall summary stats if there were valid durations
    if num_valid_trials > 0:
        min_dur = min(valid_durations)
        max_dur = max(valid_durations)
        mean_dur = statistics.mean(valid_durations)
        median_dur = statistics.median(valid_durations)
        print(f"\nOverall Statistics for {num_valid_trials} Valid Trials:")
        print(f"  Min duration: {min_dur:.2f} s")
        print(f"  Max duration: {max_dur:.2f} s")
        print(f"  Mean duration: {mean_dur:.2f} s")
        print(f"  Median duration: {median_dur:.2f} s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze AIPyCraft main logs and plot total test duration.")
    # Re-use Trials and SolutionName, LoopsValue is not needed here
    parser.add_argument("-Trials", type=int, required=True, help="The total number of trials (log files) to analyze.")
    parser.add_argument("-SolutionName", type=str, required=True, help="The name of the solution analyzed (used for plot title/filename).")
    args = parser.parse_args()

    main(args.Trials, args.SolutionName)
