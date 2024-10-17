FROM --platform=linux/amd64 python:3.9-slim

# Install wget
RUN apt-get update && apt-get install -y wget unzip tar gcc libpcap-dev dnsutils git dnstwist

# Install git
RUN apt-get update --fix-missing && apt install git -y

# Setup work directory
WORKDIR /home/mantis

# Install subfinder 
RUN echo "Installing subfinder"
RUN wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_linux_amd64.zip
RUN unzip subfinder_2.6.6_linux_amd64.zip
RUN mv subfinder /usr/bin
RUN rm -rf *

# Install HTTPX
RUN echo "Installing HTTPX"
RUN wget https://github.com/projectdiscovery/httpx/releases/download/v1.6.8/httpx_1.6.8_linux_amd64.zip
RUN unzip httpx_1.6.8_linux_amd64.zip
RUN mv httpx /usr/bin
RUN rm -rf *

# Install Findcdn
RUN echo "Installing Findcdn"
RUN pip install git+https://github.com/cisagov/findcdn.git

# Install Ipinfo
RUN echo "Installing Ipinfo"
RUN wget https://github.com/ipinfo/cli/releases/download/ipinfo-3.3.1/ipinfo_3.3.1_linux_amd64.tar.gz
RUN tar -xvf ipinfo_3.3.1_linux_amd64.tar.gz
RUN mv ipinfo_3.3.1_linux_amd64 ipinfo
RUN mv ipinfo /usr/bin
RUN rm -rf *

# Install naabu
RUN echo "Installing naabu"
RUN wget https://github.com/projectdiscovery/naabu/releases/download/v2.1.9/naabu_2.1.9_linux_amd64.zip
RUN unzip naabu_2.1.9_linux_amd64.zip
RUN mv naabu /usr/bin
RUN rm -rf *

# Install nuclei
RUN echo "Installing nuclei"
RUN wget https://github.com/projectdiscovery/nuclei/releases/download/v3.3.4/nuclei_3.3.4_linux_amd64.zip
RUN unzip nuclei_3.3.4_linux_amd64.zip
RUN mv nuclei /usr/bin
RUN rm -rf *

# Install gitleaks 
RUN echo "Installing gitleaks"
RUN wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz
RUN tar -xvf gitleaks_8.18.1_linux_x64.tar.gz
RUN mv gitleaks /usr/bin
RUN rm -rf *

# Install wafw00f
RUN pip install wafw00f

#Install gau
RUN echo "Installing GAU"
RUN wget https://github.com/lc/gau/releases/download/v2.2.1/gau_2.2.1_linux_amd64.tar.gz
RUN tar -xvf gau_2.2.1_linux_amd64.tar.gz
RUN mv gau /usr/bin
RUN rm -rf *

# Installing Corsy
RUN echo "Installing Corsy"
RUN wget https://github.com/s0md3v/Corsy/archive/refs/tags/1.0-rc.zip
RUN unzip 1.0-rc.zip
RUN mv Corsy-1.0-rc Corsy
RUN mv Corsy /usr/bin
RUN rm -rf *

# Install Poetry
RUN pip install poetry==1.4.2

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Setup Poetry ENV variables
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* /home/mantis/

# Install dependencies using Poetry
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Creating Mantis alias
RUN echo 'export PS1="🦗 Mantis > " && \
alias mantis="python /home/mantis/launch.py" && \
alias help="python /home/mantis/launch.py --help"' | tee -a ~/.bashrc

RUN echo 'echo -e "\033[1;94mWelcome to Mantis Shell! Enter help for more details\033[0m"' | tee -a ~/.bashrc

# Copy Code
COPY ./mantis /home/mantis/mantis
COPY ./configs /home/mantis/configs
COPY ./launch.py /home/mantis/launch.py
COPY ./scheduler.py /home/mantis/scheduler.py
COPY ./*.txt /home/mantis/

# Create Directories
RUN mkdir /home/mantis/logs
RUN mkdir /home/mantis/logs/scan_efficiency
RUN mkdir /home/mantis/logs/tool_logs

# Required for displaying stdout sequentially
ENV PYTHONUNBUFFERED=1
