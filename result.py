import os
import re
import argparse
import glob

LOG_DIR = "logs"
OUTPUT_FILE = "results.txt"

def extract_errors_from_log(log_filepath, solution_name):
    """
    Parses a log file to extract the first line immediately following the
    start_marker for all blocks that end with the end_marker.

    Args:
        log_filepath (str): Path to the tester log file.
        solution_name (str): The name of the solution being checked.

    Returns:
        list[tuple[str, int]]: A list of tuples, where each tuple contains:
                                (the first non-blank line (stripped) after the start marker,
                                 the line number of that line in the log file).
                                Returns an empty list if no such blocks are found.
    """
    start_marker = "This is the output of the solution main.py run:"
    end_marker = f"Solution '{solution_name}' completed with status: ERROR"

    collected_errors = [] # Store tuples of (line_content, line_number)
    potential_first_line = None
    potential_line_number = -1
    # state: 0=searching start, 1=found start (searching first non-blank), 2=found first non-blank (searching end)
    state = 0

    try:
        with open(log_filepath, 'r', encoding='utf-8') as f:
            # Use enumerate to get line numbers (starting from 1)
            for line_num, line in enumerate(f, 1):
                line_strip = line.strip()

                if state == 0: # Searching for start marker
                    if line_strip == start_marker:
                        state = 1 # Found start, now look for first non-blank line
                        potential_first_line = None # Reset
                        potential_line_number = -1
                elif state == 1: # Found start, looking for first non-blank line
                    if line_strip: # Found the first non-blank line
                        potential_first_line = line_strip # Store the stripped line
                        potential_line_number = line_num # Store the line number
                        state = 2 # Now search for the end marker
                    # else: it's a blank line, stay in state 1 and keep looking
                elif state == 2: # Found first non-blank, searching for end marker
                    if line_strip == end_marker:
                        # Found end marker. This block is valid. Add its stored data to the results.
                        if potential_first_line is not None and potential_line_number != -1:
                            collected_errors.append((potential_first_line, potential_line_number))
                        # Reset to search for the next block starting from scratch
                        state = 0
                        potential_first_line = None
                        potential_line_number = -1
                    elif line_strip == start_marker:
                         # Found a new start marker before the current block ended with ERROR.
                         # Discard the stored potential data and start over for the new block.
                         state = 1
                         potential_first_line = None # Reset potential line
                         potential_line_number = -1
                    # else: continue searching for end_marker within this block (stay in state 2)

        # After checking all lines, return all the collected errors (tuples)
        return collected_errors

    except FileNotFoundError:
        print(f"Warning: Log file not found: {log_filepath}")
        return [] # Return empty list if file not found
    except Exception as e:
        print(f"Warning: Error parsing log file {log_filepath}: {e}")
        return [] # Return empty list on other errors

    # No need for the extra return statement here anymore

def main(trials, loops_value, solution_name):
    """
    Main function to find logs, extract errors, and write to results file.
    """
    print(f"Searching for runtime errors in logs for solution '{solution_name}' across {trials} trials.")
    print(f"(LoopsValue: {loops_value} - not directly used for error extraction but kept for consistency)")

    all_formatted_errors = [] # Store formatted strings including line numbers
    processed_files_count = 0
    log_files_not_found = 0

    # Find relevant log files using glob and then filter by run_id
    log_pattern = os.path.join(LOG_DIR, f"tester_run_*_run*.log")
    all_log_files = glob.glob(log_pattern)

    run_id_to_log = {}
    # Extract run_id and find the latest log for each run_id
    for log_file in all_log_files:
        match = re.search(r"_run(\d+)\.log$", log_file)
        if match:
            run_id = int(match.group(1))
            # Keep only the latest log file if multiple exist for the same run_id
            if run_id not in run_id_to_log or log_file > run_id_to_log[run_id]:
                 run_id_to_log[run_id] = log_file

    # Process logs for the requested number of trials
    for i in range(1, trials + 1):
        log_filepath = run_id_to_log.get(i)
        if log_filepath:
            print(f"Processing Trial {i}: {log_filepath}")
            # errors_list now contains tuples of (line_content, line_number)
            errors_list = extract_errors_from_log(log_filepath, solution_name)
            if errors_list:
                print(f"  -> Found {len(errors_list)} relevant error line(s) in Trial {i}.")
                # Add context and line number to each error before adding to the main list
                for error_line, line_num in errors_list:
                     all_formatted_errors.append(f"Trial {i} ({os.path.basename(log_filepath)} - Line {line_num}): {error_line}")
            else:
                 print(f"  -> No relevant error lines found in Trial {i}.")
            processed_files_count += 1
        else:
            print(f"Warning: Log file for Trial {i} not found.")
            log_files_not_found += 1

    print(f"\n--- Extraction Summary ---")
    print(f"Total trials requested: {trials}")
    print(f"Log files processed: {processed_files_count}")
    print(f"Log files not found: {log_files_not_found}")
    print(f"Total error messages extracted: {len(all_formatted_errors)}")

    # Write formatted errors to the output file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            if not all_formatted_errors:
                outfile.write("No relevant error lines found in logs from blocks ending with status ERROR.\n")
            else:
                # Write each formatted error line (which now includes context and line number)
                for formatted_error in all_formatted_errors:
                    outfile.write(formatted_error + '\n') # Add newline after each entry
        print(f"\nResults successfully written to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"\nError writing results to {OUTPUT_FILE}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract specific runtime errors from tester logs.")
    parser.add_argument("-Trials", type=int, required=True, help="The total number of trials (log files) to analyze.")
    parser.add_argument("-LoopsValue", type=int, required=True, help="The max number of loops per trial (parameter consistency).")
    parser.add_argument("-SolutionName", type=str, required=True, help="The name of the solution analyzed (parameter consistency).")
    args = parser.parse_args()

    main(args.Trials, args.LoopsValue, args.SolutionName)
