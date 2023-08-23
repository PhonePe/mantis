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

# Checking the OS

# os_type="$(uname -s)"

# case "${os_type}" in
#     Linux*)     machine=Linux;;
#     Darwin*)    machine=Mac;;
#     CYGWIN*)    machine=Cygwin;;
#     MINGW*)     machine=MinGw;;
#     *)          machine="UNKNOWN:${unameOut}"
# esac

# echo $machine

# # Install docker on linux

# function install_docker_linux {
#     set -o errexit
#     set -o nounset
#     IFS=$(printf '\n\t')
#     curl -fsSL https://get.docker.com/ | sudo bash
#     sudo groupadd docker
#     sudo usermod -aG docker $USER
#     sudo systemctl restart docker
#     sudo systemctl status docker
# }

## Install docker on Mac

# function install_docker_mac {
#     brew install colima
#     brew install docker docker-compose
#     mkdir -p ~/.docker/cli-plugins
#     ln -sfn $(brew --prefix)/opt/docker-compose/bin/docker-compose ~/.docker/cli-plugins/docker-compose
#     export DOCKER_HOST=unix:///$HOME/.colima/docker.sock
#     colima start
#     docker ps -a
# }

function install_docker {
    if command -v docker &>/dev/null && command -v docker-compose &>/dev/null; then
        sudo rm $(which docker-compose)
    fi


# https://docs.docker.com/engine/installation/linux/ubuntu/#install-using-the-repository
    sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88 | grep docker@docker.com || exit 1
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    docker version
    # curl -fsSL https://get.docker.com/ | sudo bash
    sudo groupadd docker
    sudo usermod -aG docker $USER
    echo "Installing docker compose"
    mkdir -p ~/.docker/cli-plugins/
    curl -s -SL https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
    sudo mv ~/.docker/cli-plugins/docker-compose /usr/bin/docker-compose
    sudo chmod +x /usr/bin/docker-compose
    docker-compose version
}

echo -e "\n[*] ${BPurple}Please make sure you have the following installed ${NC}

1. Docker >= v19.0.0 
    - Check with 'docker --version'
2. Docker compose >= v2.20.3 
    - Check with 'docker-compose version'
"

echo -e -n "[?] ${Yellow}Do you have the above software installed? (y/n) ${NC}"
read is_installed_answer

if [ "$is_installed_answer" != "${is_installed_answer#[Yy]}" ] ;then 
    echo -e "[+] ${Green}Proceeding with mantis installation on docker${NC}"
else 
    echo -e -n "[?] ${Yellow}In case docker or docker-compose is not installed or outdated, the setup script can set them up.
    Would you like to install or update docker & docker-compose (y/n)?${NC}"
    read should_update_answer

    if [ "$should_update_answer" != "${should_update_answer#[Yy]}" ] ;then 
    echo -e "[+] ${Green} Installing & updating docker and docker-compose${NC}"
    install_docker
    fi


fi







#docker-compose version
#sudo rm $(which docker-compose)

# if command -v docker &>/dev/null && command -v docker-compose &>/dev/null; then
#     echo -e "[*] ${BGreen}Looks like docker & docker-compose are installed${NC}"
# else     
#     printf '[?] Looks like docker is not installed on the system \n Do you want the setup to install docker and docker-compose?'
#     read answer

#     if [ "$answer" != "${answer#[Yy]}" ] ;then 
#     # Install docker & docker-compose 
#     echo -e "[+] ${Green}Installing Docker & docker-compose${NC}"

#         if [ "$machine" == "Mac" ]; then
#             echo "Mac"
#             install_docker_mac 
#         elif [ "$machine" == "Mac" ]; then
#             install_docker_linux
#         else 
#             exit -1
#         fi
#     else
#         exit -1
# fi
# fi

echo -e "[?] Have you tried setting up Mantis using this script previously?   
    Selecting yes means, we will remove & recreate all the resources including MongoDB (y/n)?
    ${Cyan}(It is recommended to backup MongoDB before proceeding)${NC}"
read answer

## Setup aliases

COMMAND_NAME="mantis-activate"
COMMAND_PATH="/usr/local/bin/mantis-activate"
COMMAND_CONTENT="docker exec -it mantis bash"


# Check if the command already exists

echo -e "${BPurple}Sudo is only required to provide a seamless user experience by adding aliases on host system ${NC}"
printf '[?] Do you have sudo access? (y/n)?'
    read sudo_answer
    if [ "$sudo_answer" != "${sudo_answer#[Yy]}" ] ;then 
        sudo rm -f /usr/local/bin/mantis-activate
        echo "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"
        cat "$COMMAND_PATH"
        sudo chmod +x "$COMMAND_PATH"
        echo "Command '$COMMAND_NAME' added to system."
    fi

if [ "$answer" != "${answer#[Yy]}" ] ;then 
    docker-compose -f docker-compose-appsmith.yml down
    docker-compose -f docker-compose-mantis.yml down
fi

docker-compose -f docker-compose-mantis.yml up --build -d 
curl -L https://bit.ly/docker-compose-CE -s -o $PWD/docker-compose-appsmith.yml 
docker-compose -f docker-compose-appsmith.yml up -d --build
# rm docker-compose-appsmith.yml
docker network connect mantis-network appsmith
echo -e "${BPurple}Mantis container is at: docker exec -it mantis bash${NC}"

docker exec -it mantis bash