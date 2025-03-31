<#
.SYNOPSIS
Initializes the test environment by clearing the config.toml file for a specified solution.

.DESCRIPTION
This script prepares a specified solution for testing by ensuring its 'config.toml'
file is empty. This is intended to be run before executing batch tests using
run_tester_multiple.ps1 to establish a known starting state.

.PARAMETER SolutionName
The name of the solution folder (e.g., 'toml1', 'toml2') whose config.toml should be cleared.

.NOTES
The script assumes the solutions folder is located at 'C:\Users\Scalifax\workspace'.
Modify the $SolutionsBasePath variable if needed.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$SolutionName,

    [Parameter(Mandatory=$true)]
    [string]$SolutionsBasePath # Added parameter
)

# Path to the solutions folder is now provided as a parameter
# $SolutionsBasePath = "C:\Users\Scalifax\workspace" # Removed hardcoded path
$ConfigFileName = "config.toml"

# Construct the full path to the config.toml file using the provided SolutionName
$ConfigFilePath = Join-Path -Path $SolutionsBasePath -ChildPath $SolutionName | Join-Path -ChildPath $ConfigFileName

Write-Host "Initialization script started for solution: $SolutionName"
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

Write-Host "Initialization script finished for solution: $SolutionName"
