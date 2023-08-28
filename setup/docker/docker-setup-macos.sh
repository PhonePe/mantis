#!/bin/bash

# Regular Colors
Black='\033[0;30m'        # Black
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
Purple='\033[0;35m'       # Purple
Cyan='\033[0;36m'         # Cyan
White='\033[0;37m'        # White
NC='\033[0m' # No Color

# Bold
BBlack='\033[1;30m'       # Black
BRed='\033[1;31m'         # Red
BGreen='\033[1;32m'       # Green
BYellow='\033[1;33m'      # Yellow
BBlue='\033[1;34m'        # Blue
BPurple='\033[1;35m'      # Purple
BCyan='\033[1;36m'        # Cyan
BWhite='\033[1;37m'       # White

# High Intensity
IBlack='\033[0;90m'       # Black
IRed='\033[0;91m'         # Red
IGreen='\033[0;92m'       # Green
IYellow='\033[0;93m'      # Yellow
IBlue='\033[0;94m'        # Blue
IPurple='\033[0;95m'      # Purple
ICyan='\033[0;96m'        # Cyan
IWhite='\033[0;97m'       # White

# Bold High Intensity
BIBlack='\033[1;90m'      # Black
BIRed='\033[1;91m'        # Red
BIGreen='\033[1;92m'      # Green
BIYellow='\033[1;93m'     # Yellow
BIBlue='\033[1;94m'       # Blue
BIPurple='\033[1;95m'     # Purple
BICyan='\033[1;96m'       # Cyan
BIWhite='\033[1;97m'      # White


echo -e -n "
${BIYellow}
MANDATORY PREREQUISITES 

Please ensure your system meets them before proceeding.

1. Docker >= v19.0.0
   - Check with 'docker --version'
2. Docker compose >= v2.0.0
   - Check with 'docker compose version'
3. Docker configured to work without sudo 
4. Homebrew installed
5. sudo access on the machine
6. Port 1337 & 13337 available on host machine (for appsmith dashboard)
    - If these ports can't be freed then modify the port mapping in docker-compose-mantis.yml 
      to any available ports
${NC}
"

echo -e -n "[?] ${BICyan}Does your system meet the above prerequisites? (y/n) ${NC}"
read is_installed_answer

if [ "$is_installed_answer" != "${is_installed_answer#[Yy]}" ] ;then 
    echo -e "[+] ${Green}Proceeding with mantis installation on docker${NC}"
else 
    echo -e "[+] ${BYellow}Please ensure that the prerequisites are met${NC}"
    exit -1
fi

echo -e -n "[?] ${BICyan}Have you tried setting up Mantis using this script previously?   
    Selecting yes means, we will remove & recreate all the resources including MongoDB (y/n)?
    ${Red}(It is recommended to backup MongoDB before proceeding) ${NC}"
read remove_answer
if [ "$remove_answer" != "${remove_answer#[Yy]}" ] ;then 
    echo -e "[-] ${Red}Removing the existing containers${NC}"
    docker-compose down
fi

## Setup aliases

COMMAND_NAME="mantis-activate"
COMMAND_PATH="/usr/local/bin/mantis-activate"
COMMAND_CONTENT="docker exec -it mantis bash"


# Check if the command already exists

echo -e "[*] ${BPurple}Sudo is only required to provide a seamless user experience by adding aliases on host system ${NC}"
echo -e -n "[?] ${BICyan} Do you have sudo access on the machine? (y/n)? ${NC}"
    read sudo_answer
    if [ "$sudo_answer" != "${sudo_answer#[Yy]}" ] ;then 
        sudo rm -f /usr/local/bin/mantis-activate
        echo "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"  >/dev/null
        sudo chmod +x "$COMMAND_PATH"
        echo "Command '$COMMAND_NAME' added to system."
    fi

# Install packages

brew install jq

docker-compose up --remove-orphans -d --build
#docker network connect mantis-network appsmith

echo -e "${BIYellow}\n\nSETUP SUMMARY${NC}\n"

docker-compose ps --format json | jq -r \
'["Service","Status"], ["--------","------------"], (.[] | [.Service, .State]) | @tsv' | column -ts $'\t'

sudo  sed -i "" "/mantis/d" /etc/hosts
sudo -- sh -c -e "echo '10.10.0.3  mantis.db' >> /etc/hosts";
sudo -- sh -c -e "echo '127.0.0.1  mantis.dashboard' >> /etc/hosts";

echo -e -n "
${BIGreen}
    Mantis has been setup successfully on docker!

    1. You can access Mantis container using: ${BICyan}docker exec -it mantis bash${BIGreen}
        - For ease of use, run ${BICyan}mantis-activate${BIGreen} command anywhere on the system to exec into Mantis docker
   
    2. Appsmith dashboard application is accessible on the host's localhost port 1337
        - For ease of use, you can access dashboard from your system at ${BICyan}http://mantis.dashboard:1337${BIGreen}
        - You can access Appsmith container using - ${BICyan}docker exec -it appsmith bash${BIGreen}
        - Configure your dashboard using instructions at https://

    3. You can access MongoDB container using: ${BICyan}docker exec -it mantis bash${BIGreen}

    4. Command "mantis-activate" is added to your local system. Run this from anywhere to drop into Mantis shell
    5. Mantis documentation is available at https://phonepe.github.io/mantis
    6. Get help and give feedback at https://slack.com
    ${NC}
"

docker exec -it mantis bash