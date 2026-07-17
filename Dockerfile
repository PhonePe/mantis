# syntax=docker/dockerfile:1
#
# Multi-arch image. Build with buildx to target amd64 + arm64:
#   docker buildx build --platform linux/amd64,linux/arm64 -t <tag> --push .
# A plain `docker build` still works and targets the host arch.
#
# NOTE: go-wayback and go_virustotal are intentionally NOT installed here (they lack
# multi-arch prebuilt binaries and need a dedicated source-build; tracked separately).
# Their modules will be unavailable until re-added.

FROM python:3.9-slim

# System packages: build/runtime deps for the recon tools + installer prerequisites.
# libpcap-dev -> naabu SYN scan; dnsutils -> dig; git/curl/unzip/tar -> installer.
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget unzip tar gcc g++ libpcap-dev dnsutils git curl ca-certificates gnupg \
    && rm -rf /var/lib/apt/lists/*

# yq (mikefarah v4) — required by the tool manifest installer.
# Detect arch at build time so this works on both amd64 and arm64.
RUN ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/') \
    && curl -fsSL "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_${ARCH}" \
        -o /usr/bin/yq \
    && chmod +x /usr/bin/yq

# Setup work directory
WORKDIR /home/mantis

# Install external recon tools from the platform-aware manifest (single source of truth).
COPY configs/tools.yml /home/mantis/configs/tools.yml
COPY setup/install_tools.sh /home/mantis/setup/install_tools.sh
RUN chmod +x /home/mantis/setup/install_tools.sh \
    && /home/mantis/setup/install_tools.sh docker /home/mantis/configs/tools.yml

# Install Python dependencies
COPY requirements.txt /home/mantis/
RUN pip install --no-cache-dir -r /home/mantis/requirements.txt

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
