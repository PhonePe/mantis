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


echo -e "
${BIYellow}
MANDATORY PREREQUISITES 

Please ensure your system meets them before proceeding.

1. Docker >= v19.0.0
   - Check with 'docker --version'
2. Docker compose >= v2.0.0
   - Check with 'docker-compose version'
3. Homebrew installed 
4. Port 1337 & 13337 available on host machine (for appsmith dashboard)
   - If these ports cannot be freed. Modify port mappings in docker-compose-appsmith.yml
     file with available ports
5. Sudo access on the machine
${NC}
"

echo -e -n "[?] ${BICyan}Does your system meet the above prerequisites(y/n)? ${NC}"
   read prereq_answer

   if [ "$prereq_answer" != "${prereq_answer#[Yy]}" ] ;then 
      echo "[-] Proceeding with installation."
   else
      echo -e "[-] ${Red}Please setup the prerequisites. Exiting.${NC}"
      exit -1
   fi


echo -e "
Mantis setup will install the following major components: 

1. Devbox/Nix to create an isolated environment for Mantis
   that doesn't conflict with your system packages - https://www.jetpack.io/devbox
2. MongoDB will be setup locally. You can use your own MongoDB as well.
3. Appsmith for dashboards will be setup on a Docker container - https://www.appsmith.com/
"

echo -e "[*] ${BIGreen}Mantis will approximately take NNN minutes to build depending on the Internet connection bandwidth${NC}"

# Variables for services state & setup

setup_appsmith=true
mongo_exists=true

mantis_status="Newly installed"
mongodb_status="Not installed"
appsmith_status="Not installed"

# Create folder structure

if [ -d "/usr/local/mantis" ] 
then
    echo -e "[!] ${Yellow}Looks like Mantis Project was installed before${NC}"
    echo -e -n "[?]${BICyan} Would you like to delete old installation and reinstall (y/n)? ${NC}"
    read answer
        if [ "$answer" != "${answer#[Yy]}" ] ;then 
           echo -e "[!] ${Red}Deleting older Mantis & reinstalling new Mantis${NC}"
           sudo rm -rf /usr/local/mantis
           mantis_status="Reinstalled"
           CNAME=appsmith
           if [ "$(docker ps -qa -f name=$CNAME)" ]; then
               echo -e -n "[?]${BICyan} Do you want to delete the Appsmith dashboard? (y/n)? ${NC}"
               read appsmith_answer
               if [ "$appsmith_answer" != "${appsmith_answer#[Yy]}" ] ;then
                  echo -e "[!] ${Red}Deleting Appsmith containers${NC}"
                  appsmith_status="Reinstalled"
                  sudo docker stop appsmith &> /dev/null
                  sudo docker rm appsmith &> /dev/null
               else 
                  setup_appsmith=false
                  appsmith_status="Preserved old instance"
               fi
            fi
        else
           echo "[-] Exiting..."
           exit -1
        fi
else
    echo -e "[+] ${Green}Installing Mantis${NC}"
fi

sudo mkdir /usr/local/mantis
sudo chmod -R 777 /usr/local/mantis
cp -r ../../* /usr/local/mantis
echo -e "[*] ${BCyan}Mantis project Directory - /usr/local/mantis${NC}"
cd /usr/local/mantis

## Install Devbox
brew install curl
echo -e "[+] ${Green}Installing Devbox${NC}"
curl -fsSL https://get.jetpack.io/devbox | bash

## Install Mongo

if pgrep mongo; then

echo -e "[!] ${Yellow}Looks like you have MongoDB service running. Skipping MongoDB setup${NC}"
mongo_exists=true

echo -e -n ""
else
   mongo_exists=false
   echo -e "[+] ${Green}No MongoDB service is detected. Installing MongoDB locally${NC}"
   brew tap mongodb/brew
   brew update
   brew install mongodb/brew/mongodb-community
   brew services start mongodb-community
   #sudo sed -i 's/^\( *bindIp *: *\).*/127.0.0.1/' /etc/mongod.conf
   #brew services restart mongodb-community@7.0
   mongodb_status="Newly installed"
fi

# Run devbox

echo -e "[+] ${Green}Configuring Mantis environment on Devbox${NC}"
devbox version update
devbox run -c /usr/local/mantis/setup/macos setup

# Permissions for the project dir

echo -e "[+] ${Green}Setting up permissions for Mantis${NC}"
sudo chmod 777 /usr/local/bin/devbox

if [ "$setup_appsmith" = true ];then
   echo -e "[+] ${Green} Setting up Appsmith on Docker ${NC}"
   sudo docker compose up -d --build
fi

#appsmith_ip=$(sudo docker inspect \
#   -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' appsmith)

# Adding user friendly hostnames to /etc/hosts
sudo  sed -i "" '/mantis/d' /etc/hosts
sudo -- sh -c -e "echo '127.0.0.1   mantis.db' >> /etc/hosts";
sudo -- sh -c -e "echo '127.0.0.1  mantis.dashboard' >> /etc/hosts";

## Setup commands

echo -e "[+] ${Green} Setting up alias and commands for a seamless experience ${NC}"
COMMAND_NAME="mantis-activate"
COMMAND_PATH="/usr/local/bin/mantis-activate"
COMMAND_CONTENT="cd /opt/mantis/; devbox shell -c /usr/local/mantis/setup/macos"

sudo rm -f /usr/local/bin/mantis-activate
# Create the command script
echo -e "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"
echo -e "$COMMAND_CONTENT" | sudo tee "$COMMAND_PATH"
sudo chmod +x "$COMMAND_PATH"
echo "Command '$COMMAND_NAME' added to system."


# Define the data for each column
Service=("Mantis" "MongoDB" "Appsmith")
Status=("$mantis_status" "$mongodb_status" "$appsmith_status")
Access=("Run mantis-activate command" "Hostname: mantis.db (127.0.0.1)" "Hostname: mantis.dashboard (127.0.0.1)")

# Define the widths of each column
SERVICE_WIDTH=15
STATUS_WIDTH=26
ACCESS_WIDTH=40

echo -e "${BIYellow}\n\nINSTALLATION SUMMARY${NC}"

# Display the table header
printf "\e[32m%-${SERVICE_WIDTH}s | %-${STATUS_WIDTH}s | %-${ACCESS_WIDTH}s\e[0m\n" "Service" "Status" "Access (If installed)"
echo -e "${Green}---------------------------------------------------------------------------------------------${NC}"
# Display the table data
for (( i=0; i<${#Service[@]}; i++ ))
do
  printf "\e[36m%-${SERVICE_WIDTH}s | %-${STATUS_WIDTH}s | %-${ACCESS_WIDTH}s\e[0m\n" "${Service[$i]}" "${Status[$i]}" "${Access[$i]}"
done


if [ "$mongo_exists" = true ]; then
   echo -e "
   ${BYellow}
   A MongoDB instance was identified running on the system. You have following options to proceed: 

   1. If the existing MongoDB is from previous Mantis installation or 
      if you ran this script to update Mantis version then existing MongoDB works and no action is required
   2. If the existing MongoDB is not related to Mantis & if you are okay stopping the service
      Stop the MongoDB service running and setup Mantis again
   2. If the existing MongoDB is not related to Mantis & if you are NOT okay stopping the service
      Add your existing MongoDB's connection string to - /opt/mantis/configs/local.yml file
   ${NC}
   "  
fi

echo -e -n "
${BIGreen}
   Mantis has been setup successfully!

   1. Appsmith dashboard application is accessible on the host's localhost port 1337
         - For ease of use, you can access dashboard from your system at http://mantis.dashboard:1337
         - Configure your dashboard using instructions at https://
   2. Mantis project Directory - /usr/local/mantis ${BICyan}
   3. Command "mantis-activate" is added to your local system. Run this from anywhere to drop into Mantis shell
   4. Mantis documentation is available at https://phonepe.github.io/mantis
   5. Get help and give feedback at https://slack.com
   ${NC}
"

## Drop into devbox shell
cd /usr/local/mantis
devbox shell -c /usr/local/mantis/setup/macos