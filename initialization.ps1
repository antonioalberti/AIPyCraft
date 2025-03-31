<#
.SYNOPSIS
Initializes the test environment by clearing the config.toml file for the 'toml1' solution.

.DESCRIPTION
This script prepares the 'toml1' solution for testing by ensuring its 'config.toml'
file is empty. This is intended to be run before executing batch tests using
run_tester_multiple.ps1 to establish a known starting state.

.NOTES
The script assumes the solutions folder is located at 'C:\Users\Scalifax\workspace'
and the solution being initialized is named 'toml1'. Modify the paths if needed.
#>

# Define the path to the solutions folder and the specific solution
$SolutionsBasePath = "C:\Users\Scalifax\workspace"
$SolutionName = "toml1"
$ConfigFileName = "config.toml"

# Construct the full path to the config.toml file
$ConfigFilePath = Join-Path -Path $SolutionsBasePath -ChildPath $SolutionName | Join-Path -ChildPath $ConfigFileName

Write-Host "Initialization script started."
Write-Host "Target configuration file: $ConfigFilePath"

# Check if the config file exists
if (Test-Path -Path $ConfigFilePath -PathType Leaf) {
    try {
        # Clear the content of the file
        Clear-Content -Path $ConfigFilePath -ErrorAction Stop
        Write-Host "Successfully cleared content of '$ConfigFilePath'."
    } catch {
        Write-Error "Error clearing content of '$ConfigFilePath': $_.Exception.Message"
        # Exit with an error code if clearing fails
        exit 1
    }
} else {
    Write-Warning "Warning: Configuration file '$ConfigFilePath' not found. Skipping clearing."
    # Depending on requirements, you might want to exit here or just continue
    # exit 1 # Uncomment if the file MUST exist
}

Write-Host "Initialization script finished."
