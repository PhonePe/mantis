FROM --platform=linux/amd64 python:3.9-slim
# Install wget
RUN apt-get update && apt-get install -y wget unzip tar gcc libpcap-dev dnsutils git dnstwist

# Install git
RUN apt-get update --fix-missing && apt install git -y

# Setup work directory
WORKDIR /home/mantis
# Install amass
RUN echo "Installing Amass"
RUN wget https://github.com/owasp-amass/amass/releases/download/v3.23.2/amass_Linux_amd64.zip
RUN unzip amass_Linux_amd64.zip
RUN mv amass_Linux_amd64/amass /usr/bin

# Install subfinder
RUN echo "Installing subfinder"
RUN wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.0/subfinder_2.6.0_linux_amd64.zip
RUN unzip subfinder_2.6.0_linux_amd64.zip
RUN mv subfinder /usr/bin

# Install Puredns
RUN echo "Installing Puredns"
RUN wget https://github.com/d3mondev/puredns/releases/download/v2.1.1/puredns-Linux-amd64.tgz
RUN tar -xvf puredns-Linux-amd64.tgz
RUN mv puredns /usr/bin

# Install HTTPX
RUN echo "Installing HTTPX"
RUN wget https://github.com/projectdiscovery/httpx/releases/download/v1.3.2/httpx_1.3.2_linux_amd64.zip
RUN unzip httpx_1.3.2_linux_amd64.zip
RUN mv httpx /usr/bin

# Install Findcdn
RUN echo "Installing Findcdn"
RUN pip install git+https://github.com/cisagov/findcdn.git

# Install Ipinfo
RUN echo "Installing Ipinfo"
RUN wget https://github.com/ipinfo/cli/releases/download/ipinfo-2.10.1/ipinfo_2.10.1_linux_amd64.tar.gz
RUN tar -xvf ipinfo_2.10.1_linux_amd64.tar.gz
RUN mv ipinfo_2.10.1_linux_amd64 ipinfo
RUN mv ipinfo /usr/bin

# Install naabu
RUN echo "Installing naabu"
RUN wget https://github.com/projectdiscovery/naabu/releases/download/v2.1.6/naabu_2.1.6_linux_amd64.zip
RUN unzip naabu_2.1.6_linux_amd64.zip
RUN mv naabu /usr/bin

# Install nuclei
RUN echo "Installing nuclei"
RUN wget https://github.com/projectdiscovery/nuclei/releases/download/v2.9.6/nuclei_2.9.6_linux_amd64.zip
RUN unzip nuclei_2.9.6_linux_amd64.zip
RUN mv nuclei /usr/bin

# Install gitleaks 
RUN echo "Installing gitleaks"
RUN wget https://github.com/gitleaks/gitleaks/releases/download/v8.17.0/gitleaks_8.17.0_linux_x64.tar.gz
RUN tar -xvf gitleaks_8.17.0_linux_x64.tar.gz
RUN mv gitleaks /usr/bin


# Copy requirements.txt for mantis
COPY ./requirements.txt /home/mantis/requirements.txt
RUN pip install -r requirements.txt

# Install wafw00f
RUN pip install wafw00f

#Install gau
RUN echo "Installing GAU"
RUN wget https://github.com/lc/gau/releases/download/v2.1.2/gau_2.1.2_linux_amd64.tar.gz
RUN tar -xvf gau_2.1.2_linux_amd64.tar.gz
RUN mv gau /usr/bin

RUN echo "Installing and setting up awscli"
RUN wget "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
RUN unzip awscli-exe-linux-x86_64.zip
RUN ./aws/install

RUN rm -rf *
RUN echo 'export PS1="🦗 Mantis > " && alias mantis="python /home/mantis/launch.py"' | tee -a /root/.bash_profile
RUN echo 'export PS1="🦗 Mantis > " && alias mantis="python /home/mantis/launch.py"' | tee -a ~/.profile
RUN echo 'export PS1="🦗 Mantis > " && alias mantis="python /home/mantis/launch.py"' | tee -a ~/.bashrc

# Copy Code
COPY ./mantis /home/mantis/mantis
COPY ./configs /home/mantis/configs
COPY ./launch.py /home/mantis/launch.py
COPY ./scheduler.py /home/mantis/scheduler.py
COPY ./*.txt /home/mantis/
RUN mkdir /home/mantis/logs
RUN mkdir /home/mantis/logs/scan_efficiency
RUN mkdir /home/mantis/logs/tool_logs


# Required for displaying stdout sequentially
ENV PYTHONUNBUFFERED=1

#ENTRYPOINT ["python3","launch.py"]% 