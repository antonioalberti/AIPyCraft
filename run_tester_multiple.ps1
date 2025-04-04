<#
.SYNOPSIS
Runs the tester.py script multiple times for a specific solution, with initialization.

.DESCRIPTION
This script executes the Python script 'tester.py' located in the same directory
a specified number of times (-N) for a given solution (-SolutionName).
For each execution, it first runs 'initialization.ps1' (passing the SolutionName)
and then runs 'tester.py', passing the specified loop count (-LoopsValue),
the run ID, and the solution name (--solution-name).

.PARAMETER Trials
The total number of times (trials) to execute the initialization + tester sequence. Must be a positive integer.

.PARAMETER LoopsValue
The value to pass to the '--loops' argument of tester.py for each execution.
Must be a positive integer.

.PARAMETER SolutionName
The name of the solution folder (e.g., 'toml1', 'toml2') to test and initialize.

.PARAMETER SolutionsBasePath
The absolute path to the directory containing the solution folders.

.PARAMETER CorrectionPrompt
The specific correction instructions to pass to the AI during the test.

.EXAMPLE
.\run_tester_multiple.ps1 -Trials 5 -LoopsValue 3 -SolutionName toml1 -SolutionsBasePath "C:\Users\Scalifax\workspace" -CorrectionPrompt "Ensure the TOML file has observationSource."
Runs the sequence 5 times for 'toml1' located in 'C:\Users\Scalifax\workspace', passing '--loops 3', the base path, and the correction prompt to tester.py.

.EXAMPLE
.\run_tester_multiple.ps1 -Trials 1 -LoopsValue 10 -SolutionName my_other_solution -SolutionsBasePath "D:\projects\aipycraft_solutions" -CorrectionPrompt "Fix the main function logic."
Runs the sequence 1 time for 'my_other_solution' located in 'D:\projects\aipycraft_solutions', passing '--loops 10', the base path, and the prompt.
#>
param(
    [Parameter(Mandatory=$true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$Trials, # Renamed from N

    [Parameter(Mandatory=$true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$LoopsValue,

    [Parameter(Mandatory=$true)]
    [string]$SolutionName,

    [Parameter(Mandatory=$true)]
    [string]$CorrectionPrompt,

    [Parameter(Mandatory=$true)]
    [string]$SolutionsBasePath # Added parameter
)

# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TesterScriptPath = Join-Path -Path $ScriptDir -ChildPath "tester.py"

# Check if tester.py exists
if (-not (Test-Path -Path $TesterScriptPath -PathType Leaf)) {
    Write-Error "Error: tester.py not found in the script directory '$ScriptDir'."
    exit 1
}

Write-Host "Starting multi-run execution of tester.py..."
Write-Host "Target Solution: $SolutionName"
Write-Host "Total trials: $Trials" # Updated text and variable
Write-Host "Loops per run (--loops): $LoopsValue"
Write-Host "Tester script path: $TesterScriptPath"
Write-Host "-----------------------------------------"

# Define the path to the initialization script (assuming it's in the same directory)
$InitializationScriptPath = Join-Path -Path $ScriptDir -ChildPath "initialization.ps1"

# Check if initialization.ps1 exists
if (-not (Test-Path -Path $InitializationScriptPath -PathType Leaf)) {
    Write-Error "Error: initialization.ps1 not found in the script directory '$ScriptDir'."
    exit 1
}

# Loop Trials times
for ($i = 1; $i -le $Trials; $i++) { # Use $Trials in loop condition
    Write-Host "Starting Trial $i of $Trials..." # Updated text and variable

    # --- Run Initialization Script ---
    Write-Host "Executing initialization script for solution '$SolutionName' (Trial $i): $InitializationScriptPath" # Added Trial context
    try {
        # Execute the initialization script, passing the SolutionName and SolutionsBasePath
        & $InitializationScriptPath -SolutionName $SolutionName -SolutionsBasePath $SolutionsBasePath # Pass the new parameter
        Write-Host "Initialization script completed for Trial $i." # Updated text
    } catch {
        $InitErrorMessage = $_.Exception.Message
        # Use ${} to explicitly delimit both variable names for the linter
        Write-Error "An error occurred during initialization for Trial ${i}: ${InitErrorMessage}" # Updated text
        Write-Warning "Skipping tester.py execution for Trial $i due to initialization error." # Updated text
        continue # Skip to the next iteration of the loop
    }
    # --- End Initialization Script ---

    # --- Run Tester Script ---
    # Pass run-id, solution-name, solutions-base-path and correction-prompt. Quote the prompt carefully.
    # Escape any double quotes within the prompt itself for the command line
    $EscapedCorrectionPrompt = $CorrectionPrompt -replace '"','`"'
    # Added --solutions-base-path argument
    $Command = "python ""$TesterScriptPath"" --loops $LoopsValue --run-id $i --solution-name ""$SolutionName"" --solutions-base-path ""$SolutionsBasePath"" --correction-prompt ""$EscapedCorrectionPrompt"""
    Write-Host "Executing: $Command"
    try {
        # Execute the tester command. Output will go to the console.
        Invoke-Expression -Command $Command
        $ExitCode = $LASTEXITCODE
        Write-Host "Trial $i finished with exit code: $ExitCode" # Updated text
    } catch {
        # Access the specific error message from the error record ($_)
        $ErrorMessage = $_.Exception.Message
        # Use ${} to explicitly delimit both variable names for the linter
        Write-Error "An error occurred during Trial ${i}: ${ErrorMessage}" # Updated text
        # Optionally decide if you want to stop on error or continue
        # exit 1 # Uncomment to stop the entire script on error
    }
    Write-Host "-----------------------------------------"
}

Write-Host "All $Trials trials completed." # Updated text and variable
