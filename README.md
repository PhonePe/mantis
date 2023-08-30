# Mantis

## Summary

Mantis simplifies the efforts of an organisation's product security team by automating asset discovery, recon and scan. If you are already thinking why another recon framework, well, if you are a product security engineer you are in for a surprise! The framework gives you the power to distribute a single scan across multiple machines making your scan time 2x faster or even more depending on the resources you have. Recon frameworks combine a lot of open source tools that are seldom not in our control, hence we designed the framework to provide you with scan stats,scan timings and tool failures at a module, tool and subdomain level. Not done yet, there are a few bonus - deciding on the modules or tools to be run is config driven, criteria for alerts is config driven, even notifiying specific teams for specific alerts is config driven. Oh yea, new tool additions have never been simpler.


## Features :rocket:

- **Make yours scans 2x faster**
    - *I am fed up with my scan times, I can bump up my infrastructure, but will the framework utilize it efficiently*
    - Mantis can distribute a single scan across multiple machines (baremetal, AWS, Azure)
- **Understand Scan Efficiency**
    - *I really need to understand my scan results for every subdomain succeeded or failed at a granular level*
    - Easily understand your scan efficiency, were there failures in scan, modules, tools etc.
- **Integrate with your Org's DNS Service** 
    - *I want to integrate my DNS service to this tool, right now Mantis supports Route53*
    - Just add your AWS Route53 Read-only ceredentials to the configuration and have your assets synced automatically
- **Quickly Integrate new tools**
    - *I need to add a new tool for a specific vulnerability or for subdomain discovery, it's a command line tool/API*
    - Integrating tool in Mantis takes only a few minutes
- **Dashboard Support**
    - *I need a dashboard to visualize my organisation's assets* 
    - We store almost every detail in MongoDB, you are free to integrate with any dashboard that supports MongoDB integration. Appsmith, Metabase and chartbrew are some excellent out-of-the-box dashboards you can integrate with our framework
- **Choose what modules/tools you need to run**
    - *I just need to run my discovery module weekly, recon once a month and scan module everyday*
    - Just comment/uncomment the configurations you need to skip/run
- **Configurable Slack Alerts**
    - *I need to get alerts immediately when new vulnerabilities are identified, I changed my mind, I need it for phishing domains too*
    - Alerts for new assets (subdomains, IPs, certificates) and findings (vulnerabiltiies, misconfiguration, phishing and secrets) are configurable, no additonal coding required
- **Configurable Team Notifications in slack** 
    - *I need to tag the right teams for the right findings, example, tag my phising team when new phising domains are identified, tag my Infra team when a new certificate is added*
    - With Mantis, you can tag specific teams/members for asset types (subdomains, IPs, certificates) and finding types (vulnerabiltiies, misconfiguration, phishing and secrets) 
- **Secrets Scanning** 🔥🔥
    - *I need to know if my organisation's secrets or secrets provided by my organisation is leaked in public forums* 
    - An independent secrets scanning module will help you integrate with Github, Gitlab, GAU tool, dorks to find secrets in public forums


## Modules and Tools 🧰

- Discovery
    - Subfinder: Subdomain Discovery
    - AMASS:  Subdomain Discovery
    - SSLMate: Find Certificates
- PreRecon
    - FindCDN: Identify CDNs
    - Naabu: Active/Passive Ports
    - IPInfo: Identify where your assets are located
- ActiveHostScan
    - HTTPX: Find Active Assets 
- ActiveRecon
    - wafw00f: Identifty WAF
- Scan
    - Nuclei: Technology Recon
    - Nuclei: Identify vulnerabilities 
    - DNSTwister: Identify Phishing domains
    - Csper: CSP Misconfigurations

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

Run the docker setup file

```
$ ./docker-setup.sh
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
$ mantis -m onboard -o org_name -t 10.123.123.12
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

**Recon Tools Design/Launch scripts** - Bharath Kumar  
**Secret Scanning** - Hitesh Kumar, Saddam Hussain  
**Dashboard** - Pragya Gupta  
**Design Suggestions** - Dhruv Shekawat, Santanu Sinha  
**Framework Design** - Praveen Kanniah  
**Development** - Prateek Thakare  

**Special Thanks** - Ankur Bhargava

## Special Thanks 

* [Ray Framework](https://www.ray.io/)
* [Project Discovery](https://github.com/projectdiscovery)


## Disclaimer

Usage of this program for attacking targets without consent is illegal. It is the user's responsibility to obey all applicable laws. The developer assumes no liability and is not responsible for any misuse or damage caused by this program. Please use responsibly.

The material contained in this repository is licensed under Apache2.








