# Usage:
# To create new agent
# 1. .\CreateOrRemoveAgent.ps1 {Agent-Pool} {Agent-Name} 
# To remove agent
# 2. .\CreateOrRemoveAgent.ps1 {Agent-Pool} {Agent-Name} -remove
# To remove old agent and create new agent
# 3. .\CreateOrRemoveAgent.ps1 {Agent-Pool} {Agent-Name} {New-Agent-Name} -replace

param(
    [string]$agentPool,
    [string]$serviceName,
    [string]$newServiceName,
    [switch]$Remove,
    [switch]$Replace
)

# Replace these variables with your actual values
$pat = "USER_PAT"
$url = "https://azure.devops.com"
$serviceUserName = "Username" # Replace with a user account that has necessary permissions
$servicePassword = "Password" # Replace with the user account's password

# Path to the Azure DevOps agent ZIP file
$agentZipPath = "C:\Users\defaultUser\Documents\vsts-agent-win-x64-latest.zip"

# Path to the folder where you want to extract the agent
$agentExtractPath = "E:\Agents"

if (-not (Test-Path $agentZipPath)) {
    Write-Host "Downloading agent ZIP file..."
    $agentZipUrl = "http://internal-registry/vsts-agent-win-x64-latest.zip"
    Invoke-WebRequest -Uri $agentZipUrl -OutFile $agentZipPath
}

function Extract-Agent {
    # Extract the agent ZIP file
    Expand-Archive -Path $agentZipPath -DestinationPath $agentExtractPath\$serviceName

    # Navigate to the extracted agent folder
    $agentFolder = Get-ChildItem -Path $agentExtractPath\$serviceName -Directory | Select -First 1
    Set-Location $newAgentPath
}

function Create-Agent {
    param (
        [string]$agentPool,
        [string]$serviceName
    )

    # Extract the agent
    Extract-Agent

    # Configure the agent using config.cmd
    Write-Host "Configuring agent.."
    $configureCmd = "$agentExtractPath\$serviceName\.\config.cmd"
    & $configureCmd --unattended --url $url --auth PAT --token $pat --pool $agentPool --agent $serviceName --runAsService --windowsLogonAccount $serviceUserName --windowsLogonPassword $servicePassword --acceptTeeEula
}

if (-not $agentPool -or -not $serviceName) {
    Write-Host "Please provide both Agent-Pool and Agent-Name as command-line arguments."
    exit 1
}

if ($Remove -and $Replace) {
    Write-Host "Please provide either -Remove or -Replace option, not both."
    exit 1
}

if ($Remove) {
    # Removing the agents and the extraction folder
    Write-Host "Removing the agents.."
    $configureCmd = "$agentExtractPath\$serviceName\.\config.cmd"
    & $configureCmd remove --unattended --auth PAT --token $pat
    Write-Host "Removing the existing extraction folder..."
    Remove-Item -Path "$agentExtractPath\$serviceName" -Force -Recurse
    exit 0
}

if ($Replace) {
    if (-not $newServiceName) {
        Write-Host "Please provide Agent-NewName as a command-line argument when using -Replace option."
        exit 1
    }
    # Replacing the existing agent by creating a new folder with the provided name
    if (Test-Path -Path "$agentExtractPath\$serviceName") {
        Write-Host "Removing the agents.."
        $configureCmd = "$agentExtractPath\$serviceName\.\config.cmd"
        & $configureCmd remove --unattended --auth PAT --token $pat
        Write-Host "Replacing the existing agent by creating a new folder with the name $newServiceName ..."
        Remove-Item -Path "$agentExtractPath\$serviceName" -Force -Recurse
        $serviceName = $newServiceName
    }
}

# Proceed with creating the agent
Write-Host "Creating agent.."
Create-Agent -agentPool $agentPool -serviceName $serviceName
