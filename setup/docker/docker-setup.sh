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


echo "[*] ${BPurple}Please make sure you have docker & docker-compose installed.${NC}\n"

printf '[?] Have you tried setting up Mantis using this script previously? \n    Selecting yes means, we will remove & recreate all the resources (y/n)?'
read answer

## Setup aliases

COMMAND_NAME="mantis-activate"
COMMAND_PATH="/usr/local/bin/mantis-activate"
COMMAND_CONTENT="docker exec -it mantis bash"


# Check if the command already exists
if command -v "$COMMAND_NAME" &>/dev/null; then
    echo "Command '$COMMAND_NAME' already exists."
    echo "${BPurple}Sudo is only required to provide a seamless user experience by adding aliases on host system ${NC}"
    printf '[?] Do you have sudo access? (y/n)?'
    read sudo_answer
    if [ "$sudo_answer" != "${sudo_answer#[Yy]}" ] ;then 
        sudo rm -f /usr/local/bin/mantis-activate
        echo "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"
        cat "$COMMAND_PATH"
        sudo chmod +x "$COMMAND_PATH"
        echo "Command '$COMMAND_NAME' added to system."
    fi
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
echo "Mantis container is at: docker exec -it mantis bash"

/usr/local/bin/mantis-activate