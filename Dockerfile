FROM --platform=$BUILDPLATFORM golang:1.22 as go-wayback-builder
ARG TARGETOS TARGETARCH
RUN git clone https://github.com/Abhinandan-Khurana/go-wayback.git
WORKDIR go-wayback
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o go-wayback v2/main.go
RUN chmod +x go-wayback
RUN cp go-wayback /usr/bin/

FROM --platform=$BUILDPLATFORM golang:1.22 as go-virustotal-builder
ARG TARGETOS TARGETARCH
RUN git clone https://github.com/Abhinandan-Khurana/go_virustotal.git
WORKDIR go_virustotal
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o go_virustotal .
RUN chmod +x go_virustotal
RUN cp go_virustotal /usr/bin/

FROM python:3.9-slim

# Install wget
RUN apt-get update && apt-get install -y wget unzip tar gcc libpcap-dev dnsutils git dnstwist

# Install git
RUN apt-get update --fix-missing && apt install git -y

# Setup work directory
WORKDIR /home/mantis

# Install Go_Virustotal
COPY --from=go-virustotal-builder /usr/bin/go_virustotal /usr/bin

# Install Go_Wayback
COPY --from=go-wayback-builder /usr/bin/go-wayback /usr/bin

ARG TARGETARCH
# Map Docker arch names to tool-specific naming conventions
# Saving it in the different formats to use for different tools as needed
RUN echo "TARGETARCH=$TARGETARCH" && \
    case "$TARGETARCH" in \
        amd64|x86_64) \
            echo "amd64" > /tmp/arch && echo "x64" > /tmp/arch_alt && echo "x86_64" > /tmp/arch_uname ;; \
        arm64|aarch64) \
            echo "arm64" > /tmp/arch && echo "aarch64" > /tmp/arch_alt ;; \
    esac

# Install amass
RUN echo "Installing amass" && \
    ARCH=$(cat /tmp/arch) && \
    wget -O amass.zip https://github.com/owasp-amass/amass/releases/download/v4.1.0/amass_Linux_${ARCH}.zip && \
    unzip amass.zip && \
    mv amass_Linux_${ARCH}/amass /usr/bin && \
    rm -rf *

# Install subfinder
RUN ARCH=$(cat /tmp/arch) && \
    wget -O subfinder.zip https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_linux_${ARCH}.zip && \
    unzip subfinder.zip && mv subfinder /usr/bin && rm -rf *

# Install HTTPX
RUN ARCH=$(cat /tmp/arch) && \
    wget -O httpx.zip https://github.com/projectdiscovery/httpx/releases/download/v1.6.8/httpx_1.6.8_linux_${ARCH}.zip && \
    unzip httpx.zip && mv httpx /usr/bin && rm -rf *

# Install Findcdn
RUN echo "Installing Findcdn"
RUN pip install git+https://github.com/cisagov/findcdn.git

# Install ipinfo
RUN ARCH=$(cat /tmp/arch) && \
    wget -O ipinfo.tar.gz https://github.com/ipinfo/cli/releases/download/ipinfo-3.3.1/ipinfo_3.3.1_linux_${ARCH}.tar.gz && \
    tar -xvf ipinfo.tar.gz && mv ipinfo_3.3.1_linux_${ARCH} ipinfo && mv ipinfo /usr/bin && rm -rf *

# Install naabu
RUN ARCH=$(cat /tmp/arch) && \
    wget -O naabu.zip https://github.com/projectdiscovery/naabu/releases/download/v2.5.0/naabu_2.5.0_linux_${ARCH}.zip && \
    unzip naabu.zip && mv naabu /usr/bin && rm -rf *

# Install nuclei
RUN ARCH=$(cat /tmp/arch) && \
    wget -O nuclei.zip https://github.com/projectdiscovery/nuclei/releases/download/v3.3.4/nuclei_3.3.4_linux_${ARCH}.zip && \
    unzip nuclei.zip && mv nuclei /usr/bin && rm -rf *

RUN ARCH=$(cat /tmp/arch) && \
    wget -O gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_${ARCH}.tar.gz && \
    tar -xvf gitleaks.tar.gz && mv gitleaks /usr/bin && rm -rf *

# Install wafw00f
RUN pip install wafw00f

# Install gau
RUN ARCH=$(cat /tmp/arch) && \
    wget -O gau.tar.gz https://github.com/lc/gau/releases/download/v2.2.1/gau_2.2.1_linux_${ARCH}.tar.gz && \
    tar -xvf gau.tar.gz && mv gau /usr/bin && rm -rf *

# Installing Corsy
RUN echo "Installing Corsy"
RUN wget -O corsy.zip https://github.com/s0md3v/Corsy/archive/refs/tags/1.0-rc.zip
RUN unzip corsy.zip
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
