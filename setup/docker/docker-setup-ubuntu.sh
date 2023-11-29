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

1. Install Docker >= v19.0.0
   - https://docs.docker.com/engine/install/ubuntu/
   - Check version with 'docker --version'
2. Install Docker compose >= v2.0.0
   - Check version with 'docker compose version'
4. sudo access on the machine
5. Ports 1337, 1338, 27000 available on host machine (for Mantis dashboard and MongoDB)
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

sudo apt update && sudo apt install jq -y

if docker compose ps | grep -q "Up"; then
    echo -e "[?] ${BIYellow}Looks like this script was run previously to setup Mantis.${NC}\n"

sudo docker compose ps --format json | jq -r '(. | [.Service, .State]) | @tsv' | column -ts $'\t'

echo -e -n "
[!] ${Yellow}Previously created resources need to be cleaned up before proceeding with installation \n

Following are your options:

"

echo -e "${BICyan}
1. Delete all the previously created containers${BYellow}
    - Recommended to export the dashboard before deleting Appsmith
    - ${BYellow}Recommended to backup the database before deleting MongoDB${BICyan}
2. Delete Mantis, Appsmith and don't delete MongoDB
    - ${BYellow}Recommended to export the dashboard before deleting Appsmith${BICyan}
3. Delete Mantis, MongoDB and don't delete Appsmith
    - ${BYellow}Recommended to backup the database before deleting MongoDB 
      https://www.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/${BICyan}
4. Delete Mantis and don't delete Appsmith, MongoDB
${NC}
"

read -p "What would you like to do? (1/2/3/4): " choice

case $choice in
    1)
        echo -e "[-] ${Red}Removing all the existing containers from Mantis setup${NC}"
        sudo docker compose down
        ;;
    2)
        echo -e "[-] ${Red}Removing Mantis, Appsmith and retaining MongoDB${NC}"
        sudo docker compose down appsmith
        sudo docker compose down mantis
        ;;
    3)
        echo -e "[-] ${Red}Removing Mantis, MongoDB and retaining Appsmith${NC}"
        sudo docker compose down mongodb
        sudo docker compose down mantis
        ;;

    4)
        echo -e "[-] ${Red}Removing Mantis and retaining MongoDB, Appsmith${NC}"
        sudo docker compose down mantis
        ;;
    *)
        echo -e "\nInvalid choice. Please select a valid option (1/2/3/4)."
        ;;
esac

fi

## Setup aliases

COMMAND_NAME="mantis-activate"
COMMAND_PATH="/usr/local/bin/mantis-activate"
COMMAND_CONTENT="docker exec -it mantis bash"


# Check if the command already exists

echo -e "[*] ${BPurple}Sudo is required for running docker and adding aliases/commands on host system${NC}"
echo -e -n "[?] ${BICyan}Do you have sudo access on the machine? (y/n)? ${NC}"
    read sudo_answer
    if [ "$sudo_answer" != "${sudo_answer#[Yy]}" ] ;then 
        sudo rm -f /usr/local/bin/mantis-activate
        echo "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"  >/dev/null
        sudo chmod +x "$COMMAND_PATH"
        echo "Command '$COMMAND_NAME' added to system."
    fi

# Install packages


sudo docker compose up --remove-orphans -d --build

echo -e "${BIYellow}\n\nSETUP SUMMARY${NC}\n"

sudo docker compose ps --format json | jq -r '(. | [.Service, .State]) | @tsv' | column -ts $'\t'

sudo  sed -i "/mantis/d" /etc/hosts
sudo -- sh -c -e "echo '10.10.0.3  mantis.db' >> /etc/hosts";
sudo -- sh -c -e "echo '127.0.0.1  mantis.dashboard' >> /etc/hosts";

appsmith_exists=$(docker compose ps appsmith --quiet)
mongo_exists=$(docker compose ps mongodb --quiet)
mantis_exists=$(docker compose ps mantis --quiet)

if [ -n "$appsmith_exists" ] && [ -n "$mongo_exists" ] && [ -n "$mantis_exists" ]; then
echo -e -n "
${BIGreen}
    

    1. You can find the Mantis shell below where you can run mantis commands. Run help for further instructions.
        - You can always access Mantis container again using: ${BICyan}docker exec -it mantis bash${BIGreen}
        - For ease of use, run ${BICyan}mantis-activate${BIGreen} command anywhere on the system to exec into Mantis docker

    2. Mantis dashboard (appsmith) is accessible on the host's localhost port 1337
        - For ease of use, you can access dashboard from your system at ${BICyan}http://mantis.dashboard:1337${BIGreen}
        - You can access appsmith container using - ${BICyan}docker exec -it appsmith bash${BIGreen}
        - Configure your dashboard using instructions at https://github.com/PhonePe/mantis/#dashboard-setup-

    3. You can access MongoDB container using: ${BICyan}docker exec -it mongodb bash${BIGreen}

    4. Mantis documentation is available at https://phonepe.github.io/mantis
    5. Get help and give feedback at https://discord.gg/uJV8Y3uSGu

    Mantis has been setup successfully on docker!
    ${NC}
"
else
    echo -e -n "
${BIRed}
Please check the container/service status above and check for any errors to resolve this issue.

Mantis has NOT been setup successfully on docker!
${NC}
"
fi

mantis-activate
