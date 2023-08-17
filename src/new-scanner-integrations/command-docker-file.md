# Install instructions

## Docker File

Add the install instructions below the `WORKDIR /home/mantis`

```shell
RUN echo "Installing Amass"
RUN wget https://github.com/owasp-amass/amass/releases/download/v3.23.2/amass_Linux_amd64.zip
RUN unzip amass_Linux_amd64.zip
RUN mv amass_Linux_amd64/amass /usr/bin

```


## DevBox

Devbox creates isolated and reproducible development environments capable of running anywhere. It also features a package manager, NixOS. Please verify whether the package of the newly integrated tool is present [here](https://search.nixos.org/packages).  

If the package is present in NixOs, then add the package name with relevant version to the **package** list under `setup/ubuntu/devbox.json` or `setup/mac/devbox.json`

```json
 "packages": [
    "python@3.10",
    "stdenv.cc.cc.lib",
    "amass@3.22.2",
    "subfinder@2.6.0",
    "httpx@1.3.3",
    "ipinfo@2.10.1",
    "naabu@2.1.6",
    "nuclei@2.9.7",
    "gitleaks@8.17.0",
    "gau@2.1.2",
    "python310Packages.pip",
    "gccStdenv"
  ],
```

Else add the native installation in the **setup** list in `setup/ubuntu/devbox.json` or `setup/mac/devbox.json`
