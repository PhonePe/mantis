# Display Mandatory Prerequisites
Write-Host @"

MANDATORY PREREQUISITES 

Please ensure your system meets them before proceeding.

1. Install Docker >= v19.0.0
   - https://docs.docker.com/engine/install/ubuntu/
   - Check version with 'docker --version'
2. Install docker compose >= v2.0.0
   - Check version with 'docker compose version'
3. sudo access on the machine
4. Ports 1337, 1338, 27000 available on host machine (for Mantis dashboard and MongoDB)
    - If these ports can't be freed then modify the port mapping in docker-compose.yml 
      to any available ports

"@  -ForegroundColor "Yellow"


# Display the prompt
Write-Host -NoNewline "[?] Does your system meet the above prerequisites? (y/n)" -ForegroundColor "Cyan"
$is_installed_answer = Read-Host

# Check the answer
if ($is_installed_answer -match '^[Yy]') {
    Write-Host "[+] Proceeding with mantis installation on docker" -ForegroundColor "Green" 
}
else {
    Write-Host "[+] Please ensure that the prerequisites are met" -ForegroundColor "DarkYellow"
    exit -1
}

# Check if Docker and Docker Compose are installed
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed or not in PATH. Please install Docker." -ForegroundColor "Red"
    exit 1
}
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Compose is not installed or not in PATH. Please install Docker Compose." -ForegroundColor "Red"
    exit 1
}


# Check if any Docker Compose services are "Up"
if (docker compose ps | Select-String -Pattern "Up") {
    Write-Host "[?] Looks like this script was run previously to set up Mantis." -ForegroundColor Yellow

    # Display the services and their states in a formatted way
    $services = docker compose ps --format json | ConvertFrom-Json
    # Format each service and state into a custom object
    $services | ForEach-Object {
        [PSCustomObject]@{
            Service = $_.Service
            State   = $_.State
        }
    } | Format-Table -Property Service, State -AutoSize

    # Display options for cleanup
    Write-Host "`n[!] Previously created resources need to be cleaned up before proceeding with installation`n" -ForegroundColor Yellow
    Write-Host "Following are your options:`n" -ForegroundColor "Cyan"
}

Write-Host "1. Delete all the previously created containers" -ForegroundColor Cyan
Write-Host "    - Recommended to export the dashboard before deleting Appsmith" -ForegroundColor Yellow
Write-Host "    - Recommended to backup the database before deleting MongoDB" -ForegroundColor Yellow
Write-Host "2. Delete Mantis, Appsmith and don't delete MongoDB" -ForegroundColor Cyan
Write-Host "    - Recommended to export the dashboard before deleting Appsmith" -ForegroundColor Yellow
Write-Host "3. Delete Mantis, MongoDB and don't delete Appsmith" -ForegroundColor Cyan
Write-Host "    - Recommended to backup the database before deleting MongoDB" -ForegroundColor Yellow
Write-Host "      https://www.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/" -ForegroundColor Cyan
Write-Host "4. Delete Mantis and don't delete Appsmith, MongoDB `n" -ForegroundColor Cyan


# Cleanup options for previous setup
$cleanupChoice = Read-Host "What would you like to do? (1/2/3/4) "
switch ($cleanupChoice) {
    1 {
        Write-Host "Removing all the existing containers from Mantis setup" -ForegroundColor "Red"
        docker compose down
    }
    2 {
        Write-Host "Removing Mantis, Appsmith and retaining MongoDB" -ForegroundColor "Red"
        docker compose stop appsmith
        docker compose rm -f appsmith
        docker compose stop mantis
        docker compose rm -f mantis
    }
    3 {
        Write-Host "Removing Mantis, MongoDB and retaining Appsmith" -ForegroundColor "Red"
        docker compose stop mongodb
        docker compose rm -f mongodb
        docker compose stop mantis
        docker compose rm -f mantis
    }
    4 {
        Write-Host "Removing Mantis and retaining MongoDB, Appsmith" -ForegroundColor "Red"
        docker compose stop mantis
        docker compose rm -f mantis
    }
    default {
        Write-Host "Invalid choice. Please select a valid option (1/2/3/4)." -ForegroundColor "Red"
    }
}

# Setup aliases
$CommandName = "mantis-activate"
$CommandPath = "C:\Windows\System32\mantis-activate.bat"
$CommandContent = "docker exec -it mantis bash"

# Check if the command already exists
Write-Host "[*] Running PowerShell as Administrator is required for Docker commands and adding shortcuts/commands on the system." -ForegroundColor "DarkBlue"
$adminAccess = Read-Host "[?] Do you have Administrator access on the machine? (y/n)?"

if ($adminAccess -match "^[Yy]") {
    # Remove the existing command if it exists
    if (Test-Path $CommandPath) {
        Remove-Item $CommandPath -Force
    }

    # Write the command content to the new batch file
    Set-Content -Path $CommandPath -Value $CommandContent
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser 

    Write-Host "Command '$CommandName' added to system." -ForegroundColor "Green"
}

docker compose pull
docker compose up --remove-orphans -d mongodb 
docker compose up --remove-orphans -d mantis 
docker compose up --remove-orphans -d appsmith

Write-Host "SETUP SUMMARY" -ForegroundColor "Yellow"

$services = docker compose ps --format json | ConvertFrom-Json
$services | ForEach-Object {
    [PSCustomObject]@{
        Service = $_.Service
        State   = $_.State
    }
} | Format-Table -Property Service, State -AutoSize

# Update Hosts File
$hostEntries = "127.0.0.1 mantis.dashboard", "127.0.0.1 mantis.db"
foreach ($entry in $hostEntries) {
    if (!(Select-String -Path "C:\Windows\System32\drivers\etc\hosts" -Pattern $entry -Quiet)) {
        Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value $entry
        Write-Host "$entry added to hosts file." -ForegroundColor "Green"
    }
    else {
        Write-Host "$entry already exists in hosts file." -ForegroundColor "Yellow"
    }
}

# Check if containers are running for appsmith, mongodb, and mantis
$appsmith_exists = docker compose ps -q appsmith
$mongo_exists = docker compose ps -q mongodb
$mantis_exists = docker compose ps -q mantis

# If all containers exist
if ($appsmith_exists -and $mongo_exists -and $mantis_exists) {
    Write-Host @"
1. You can find the Mantis shell below where you can run mantis commands. Run help for further instructions.
    - You can always access Mantis container again using: 
"@  -NoNewline -ForegroundColor "Green"
    
    Write-Host "docker exec -it mantis bash" -ForegroundColor "Cyan"
    Write-Host "    - For ease of use, run " -ForegroundColor "Green" -NoNewline
    Write-Host "mantis-activate" -ForegroundColor "Cyan" -NoNewline
    Write-Host " command anywhere on the system to exec into Mantis docker" -ForegroundColor "Green"
    
    Write-Host @"
2. Mantis dashboard (appsmith) is accessible on the host's localhost port 1337
    - For ease of use, you can access the dashboard from your system at 
"@ -ForegroundColor "Green" -NoNewline
    
    Write-Host "http://mantis.dashboard:1337" -ForegroundColor "Cyan"
    Write-Host "    - You can access appsmith container using:" -ForegroundColor "Green" -NoNewline
    Write-Host " docker exec -it appsmith bash" -ForegroundColor "Cyan"
    Write-Host "    - Configure your dashboard using instructions at https://github.com/PhonePe/mantis/#dashboard-setup-" -ForegroundColor "Green"
    
    Write-Host "3. You can access MongoDB container using: docker exec -it mongodb bash" -ForegroundColor "Green"
    Write-Host "4. Mantis documentation is available at https://phonepe.github.io/mantis" -ForegroundColor "Green"
    Write-Host "5. Get help and give feedback at https://discord.gg/uJV8Y3uSGu" -ForegroundColor "Green"
    
    Write-Host "`nMantis has been set up successfully on Docker!" -ForegroundColor "Green"
    
} else {
    Write-Host "Please check the container/service status above and check for any errors to resolve this issue." -ForegroundColor "Red"
    Write-Host "Mantis has NOT been setup successfully on docker!" -ForegroundColor "Red"
}

mantis-activate