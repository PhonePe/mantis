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

echo -e "[*] ${BPurple}Mantis setup will require sudo privileges during installation${NC}"

# Create folder structure

if [ -d "/opt/mantis" ] 
then
    echo -e "[!] ${Yellow}Looks like Mantis Project was installed before${NC}"
    printf '[?] Would you like to delete old installation and reinstall (y/n)? '
    read answer
        if [ "$answer" != "${answer#[Yy]}" ] ;then 
           echo -e "[!] ${Red}Deleting older Mantis & reinstalling new Mantis${NC}"
           sudo rm -rf /opt/mantis
        else
           echo "[-] Exiting..."
           exit -1
        fi
else
    echo -e "[+] ${Purple}Installing Mantis...${NC}"
fi

sudo mkdir /opt/mantis
sudo chmod 777 -R /opt/mantis
cp -r ../../* /opt/mantis
echo -e "[*] ${BGreen}Mantis project Directory - /opt/mantis${NC}"
cd /opt/mantis

## Install Devbox
curl -fsSL https://get.jetpack.io/devbox | bash

## Install Mongo
sudo apt-get update -qq
sudo apt-get install gnupg curl ca-certificates -y -qq

curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor

sudo echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update -qq

if pgrep mongo; 
then
   echo -e "[!] ${Red}Looks like you have MongoDB service running. Either stop the service or remove mongo setup from this script${NC}"
   exit -1
else
   sudo apt-get install -y mongodb-org -qq
   sudo systemctl start mongod
   sudo -- sh -c -e "echo '127.0.0.1   mantis.db' >> /etc/hosts";
   sudo sed -i "s,\\(^[[:blank:]]*bindIp:\\) .*,\\1 127.0.0.1\,172.17.0.1," /etc/mongod.conf
   sudo systemctl restart mongod
   #sed -i "s,\\(^[[:blank:]]*bindIp:\\) .*,\\1 0.0.0.0," /etc/mongod.conf
fi

# Run devbox
devbox version update
devbox run -c /opt/mantis/setup/ubuntu setup

# Permissions for the project dir

sudo chmod 777 /usr/local/bin/devbox

#sudo chmod 755 -R /opt/mantis/.devbox
#sudo chmod 755 -R /opt/mantis/virtenv

# Install docker & docker-compose 

if [[ $(which docker) && $(docker --version) ]]; then
    echo "[*] Docker is already installed.."
else
   set -o errexit
   set -o nounset
   IFS=$(printf '\n\t')

   # Install Docker
   sudo apt remove --yes docker docker-engine docker.io containerd runc || true
   sudo apt update
   sudo apt --yes --no-install-recommends install apt-transport-https ca-certificates
   wget --quiet --output-document=- https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository --yes "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $(lsb_release --codename --short) stable"
   sudo apt update
   sudo apt --yes --no-install-recommends install docker-ce docker-ce-cli containerd.io
   sudo usermod --append --groups docker "$USER"
   sudo systemctl enable docker
   printf '\nDocker installed successfully\n\n'

   printf 'Waiting for Docker to start...\n\n'
   sleep 5
fi

# Install docker compose 

if docker-compose version
then
   echo -e "[*] ${Yellow}Docker compose is already installed${NC}"
else
   sudo apt install docker-compose
fi

# Install Appsmith

curl -L https://bit.ly/docker-compose-CE -o $PWD/docker-compose.yml
docker-compose up -d

## Setup commands

COMMAND_NAME="mantis-activate"
COMMAND_PATH="/usr/local/bin/mantis-activate"
COMMAND_CONTENT="cd /opt/mantis/; devbox shell -c /opt/mantis/setup/ubuntu"

sudo rm -f /usr/local/bin/mantis-activate
# Create the command script
echo -e "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"
sudo chmod +x "$COMMAND_PATH"
echo "Command '$COMMAND_NAME' added to system."

## Drop into devbox shell
cd /opt/mantis
devbox shell -c /opt/mantis/setup/ubuntu