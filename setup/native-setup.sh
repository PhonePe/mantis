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

# Install yq (required by the platform-aware tool installer)
if ! command -v yq >/dev/null 2>&1; then
  echo -e "[+]${Green} Installing yq${NC}"
  case "$(uname -m)" in x86_64|amd64) YQ_ARCH=amd64;; aarch64|arm64) YQ_ARCH=arm64;; *) YQ_ARCH=amd64;; esac
  sudo wget -q -O /usr/bin/yq "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_${YQ_ARCH}"
  sudo chmod +x /usr/bin/yq
fi

# findcdn native compatibility shim (kept for the Ubuntu/python3.9 path)
python3.9 -m pip install "dnspython<=2.0.0" ipwhois

# Install all external recon tools from the platform-aware manifest (configs/tools.yml).
# Single source of truth for versions; resolves the correct binary per OS/arch.
echo -e "[+]${Green} Installing recon tools via manifest${NC}"
SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 ; pwd -P )"
MANTIS_PIP="python3.9 -m pip" bash "${SCRIPT_DIR}/install_tools.sh" native "${SCRIPT_DIR}/../configs/tools.yml"

# Install Python dependencies

echo -e "[+]${Green} Installing Python dependencies ${NC}"
python3.9 -m pip install -r requirements.txt

echo -e "[+]${Green} Installation Completed ${NC}"