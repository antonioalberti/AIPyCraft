<#
.SYNOPSIS
Runs the tester.py script multiple times with a specified loop count for each run.

.DESCRIPTION
This script executes the Python script 'tester.py' located in the same directory
a specified number of times (-N). For each execution, it passes the specified
loop count (-LoopsValue) to the '--loops' argument of tester.py.

.PARAMETER N
The total number of times to execute tester.py. Must be a positive integer.

.PARAMETER LoopsValue
The value to pass to the '--loops' argument of tester.py for each execution.
Must be a positive integer.

.EXAMPLE
.\run_tester_multiple.ps1 -N 5 -LoopsValue 3
Runs tester.py 5 times, and each time passes '--loops 3' to it.

.EXAMPLE
.\run_tester_multiple.ps1 -N 1 -LoopsValue 10
Runs tester.py 1 time, passing '--loops 10' to it.
#>
param(
    [Parameter(Mandatory=$true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$N,

    [Parameter(Mandatory=$true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$LoopsValue
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
Write-Host "Total runs (N): $N"
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

# Loop N times
for ($i = 1; $i -le $N; $i++) {
    Write-Host "Starting Run $i of $N..."

    # --- Run Initialization Script ---
    Write-Host "Executing initialization script: $InitializationScriptPath"
    try {
        # Execute the initialization script
        & $InitializationScriptPath
        Write-Host "Initialization script completed for Run $i."
    } catch {
        $InitErrorMessage = $_.Exception.Message
        # Use ${} to explicitly delimit both variable names for the linter
        Write-Error "An error occurred during initialization for Run ${i}: ${InitErrorMessage}"
        Write-Warning "Skipping tester.py execution for Run $i due to initialization error."
        continue # Skip to the next iteration of the loop
    }
    # --- End Initialization Script ---

    # --- Run Tester Script ---
    # Pass the current loop iteration number ($i) as the --run-id
    $Command = "python ""$TesterScriptPath"" --loops $LoopsValue --run-id $i"
    Write-Host "Executing: $Command"
    try {
        # Execute the tester command. Output will go to the console.
        Invoke-Expression -Command $Command
        $ExitCode = $LASTEXITCODE
        Write-Host "Run $i finished with exit code: $ExitCode"
    } catch {
        # Access the specific error message from the error record ($_)
        $ErrorMessage = $_.Exception.Message
        # Use ${} to explicitly delimit both variable names for the linter
        Write-Error "An error occurred during Run ${i}: ${ErrorMessage}"
        # Optionally decide if you want to stop on error or continue
        # exit 1 # Uncomment to stop the entire script on error
    }
    Write-Host "-----------------------------------------"
}

Write-Host "All $N runs completed."
