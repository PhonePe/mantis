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


# Install essential tools
echo -e "[*] ${BCyan}Installing essential tools${NC}"

# Required for python 3.9
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa

# Required for findcdn
sudo apt-get install -y python3.9-distutils

sudo apt-get update
sudo apt-get install -y wget unzip -qq tar gcc libpcap-dev dnsutils git python3.9 python3.9-dev python3-pip gnupg curl ca-certificates
echo "export PATH='$HOME/.local/bin:$PATH'" | tee -a ~/.bashrc
source ~/.bashrc

# Install amass
echo -e "[+]${Green} Installing AMass${NC}"
wget -q -O amass.zip https://github.com/owasp-amass/amass/releases/download/v4.1.0/amass_Linux_amd64.zip
unzip -qq -d amass -j amass.zip
sudo mv amass/amass /usr/bin

## Install subfinder
echo -e "[+]${Green} Installing Subfinder${NC}"
wget -q -O subfinder.zip https://github.com/projectdiscovery/subfinder/releases/download/v2.6.3/subfinder_2.6.3_linux_amd64.zip
unzip -qq -d subfinder -j subfinder.zip
sudo mv subfinder/subfinder /usr/bin/

## Install httpx
echo -e "[+]${Green} Installing httpx${NC}"
wget -q -O httpx.zip https://github.com/projectdiscovery/httpx/releases/download/v1.3.7/httpx_1.3.7_linux_amd64.zip
unzip -qq -d httpx -j httpx.zip
sudo mv httpx/httpx /usr/bin/

## Install naabu
echo -e "[+]${Green} Installing naabu${NC}"
wget -q -O naabu.zip https://github.com/projectdiscovery/naabu/releases/download/v2.1.9/naabu_2.1.9_linux_amd64.zip
unzip -qq -d naabu -j naabu.zip
sudo mv naabu/naabu /usr/bin/

# Install nuclei
echo -e "[+]${Green} Installing Nuclei${NC}"
wget -q -O nuclei.zip https://github.com/projectdiscovery/nuclei/releases/download/v3.0.4/nuclei_3.0.4_linux_amd64.zip
unzip -qq -d nuclei -j nuclei.zip
sudo mv nuclei/nuclei /usr/bin/

# Install gitleaks
echo -e "[+]${Green} Installing gitleaks${NC}"
wget -q -O gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz
tar -xf gitleaks.tar.gz
sudo mv gitleaks /usr/bin/

# Install Findcdn
echo -e "[+]${Green} Installing findcdn ${NC}"

pip install "dnspython<=2.0.0" ipwhois
python3.9 -m pip install "git+https://github.com/cisagov/findcdn.git"

echo -e "[+]${Green} Installing dnstwist ${NC}"
python3.9 -m pip install dnstwist[full]

# Install IPinfo
echo -e "[+]${Green} Installing IPinfo ${NC}"
curl -sLO https://github.com/ipinfo/cli/releases/download/ipinfo-3.2.0/ipinfo_3.2.0.deb
sudo dpkg -i ipinfo_3.2.0.deb

# Install wafw00f

echo -e "[+]${Green} Installing wafw00f ${NC}"
python3.9 -m pip install wafw00f --quiet

#Install gau
echo -e "[+]${Green} Installing gau${NC}"
wget -O gau.tar.gz https://github.com/lc/gau/releases/download/v2.2.1/gau_2.2.1_linux_amd64.tar.gz
tar -xvf gau.tar.gz
sudo mv gau /usr/bin

# Installing Corsy
echo -e "[+]${Green} Installing Corsy${NC}"
wget https://github.com/s0md3v/Corsy/archive/refs/tags/1.0-rc.zip
unzip -qq 1.0-rc.zip
mv Corsy-1.0-rc Corsy
sudo mv Corsy /usr/bin

# Install Python dependencies

echo -e "[+]${Green} Installing Python dependencies ${NC}"
python3.9 -m pip install -r requirements.txt

echo -e "[+]${Green} Installation Completed ${NC}"