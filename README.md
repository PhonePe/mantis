# Mantis

## Summary

Mantis is a command-line framework designed to automate the workflow of asset discovery, reconnaissance, and scanning. It takes the top-level domains as input, then seamlessly progresses to discovering corresponding assets, including subdomains and certificates. The tool performs reconnaissance on active assets and concludes with a comprehensive scan for vulnerabilities, secrets, misconfigurations and phishing domains - all powered by a blend of open-source and custom tools.


## Features :rocket:

- Automated Discovery, Recon & Scan
- Distributed Scanning (split a single scan across multiple machines)
- Super-Easy Scan Customisation
- Dashboard Support
- Vulnerability Management
- Advanced Alerting
- DNS Service Integration
- Integrate new tool (existing and custom) in minutes


## Modules 🧰

- Discovery
    - Subdomains
    - Certificateds
- Recon
    - Open Ports
    - Technologies
    - CDN
    - WAF
    - Web Server
    - IP
    - ASN Information
    - Location
- Scan
    - Domain Level Vulnerabilities and Misconfigurations
    - Secrets Scanning
    - Phishing Domains

## Installation ⚙️

Mantis supports multiple installation types. Installing Mantis via Docker would be a good start to get a hang of the framework.

Considering that Mantis also includes MongoDB and AppSmith, we have provided a shell script that installs all the components.

### Docker 

Clone the Mantis repository 

```
$ git clone https://github.com/PhonePe/mantis.git
```

cd into the Mantis directory    

```
$ cd mantis/setup/docker
```

Run the respective docker setup file based on your OS

```
$ ./docker-setup-macos.sh

$ ./docker-setup-ubuntu.sh
```


### Ubuntu - Linux

To install Mantis directly on Ubuntu, follow the below steps. 

Clone the Mantis repository 

```
$ git clone https://github.com/PhonePe/mantis.git
```

cd into the Mantis directory    

```
$ cd mantis/setup/ubuntu
```

Run the mac setup file

```
$ ./setup-mantis-ubuntu.sh
```

### MacOS

To install Mantis directly on MacOS, follow the below steps. 

Clone the Mantis repository 

```
$ git clone https://github.com/PhonePe/mantis.git
```

cd into the Mantis directory    

```
$ cd mantis/setup/macos
```

Run the mac setup file

```
$ ./setup-mantis-macos.sh
```

## Command Line Options 🖥️

```
usage: 
        ONBOARD: (First time scan, Run this !!)

        mantis onboard -o example_org -t www.example.org
        mantis onboard -o example_org -f file.txt

        SCAN:

        mantis scan -o example_org
        mantis scan -o example_org -a example_app
            

optional arguments:
  -h, --help      list command line options

subparser:
  {onboard,scan}
    onboard       Onboard a target
    scan          Scan an org

```

```
usage: 
        SCAN:

        mantis scan -o example_org
        mantis scan -o example_org -a example_app
            

optional arguments:
  -h, --help            show this help message and exit
  -w WORKFLOW, --workflow WORKFLOW
                        workflow to be executed as specified in config file
  -o ORG, --org ORG     name of the organisation
  -a APP, --app APP     scan only subdomains that belong to an app
  -p, --passive         run passive port scan
  -s, --stale           mark domains as stale (domains purchased but not in use)
  -i, --ignore_stale    ignore stale domains during scan
  -r, --use_ray         use ray framework for distributed scans
  -n NUM_ACTORS, --num_actors NUM_ACTORS
                        number of ray actors, default 10
  -d, --delete_logs     delete logs of previous scans
  -v, --verbose         print debug logs

```

## Run a scan 🔍

You want to onboard an org with its TLDs/IPs/IP-CIDRs/IP Range for the first time, use the onboard mode. This runs the scan on the default workflow.

#### TLD

```shell
$ mantis onboard -o org_name -t example.in   
```
#### IP

```shell
$ mantis onboard -o org_name -t 10.123.123.12
```

#### IP-Range

```shell
$ mantis onboard -o org_name -t 203.0.113.0-203.0.113.255
```

#### IP-CIDR

```shell
$ mantis onboard -o org_name -t 203.0.113.0/24
```

### Onboard Known Assets and Scan
```shell
$ mantis onboard -o org_name -f input.txt
```

### Scan on all assets belonging to an organisation

Now that you have onboarded, you just need to run scheduled scans for an org, you can just use the scan mode

```shell
$ mantis scan -o org_name
```

### Scan on all assets belonging to an organisation and app

```shell
$ mantis scan -o org_name -a app_name
```


## How to contribute ?

If you want to contribute to this project:

* Submit an issue if you found a bug, or a have a feature request.
* Make a Pull Request from dev branch if you want to improve the code.

## Need Help ? 🙋‍♂️
    
* Take a look at the wiki section.
* Check FAQ for commonly asked questions.

## Credits 🎖

**Development** - Prateek Thakare  
**Recon Tools Design/Launch scripts** - Bharath Kumar  
**Secret Scanning** - Hitesh Kumar, Saddam Hussain  
**Dashboard** - Pragya Gupta  
**Design Suggestions** - Dhruv Shekawat, Santanu Sinha  
**Framework Design** - Praveen Kanniah  

**Special Thanks** - Ankur Bhargava

## Disclaimer

Usage of this program for attacking targets without consent is illegal. It is the user's responsibility to obey all applicable laws. The developer assumes no liability and is not responsible for any misuse or damage caused by this program. Please use responsibly.

The material contained in this repository is licensed under Apache2.

