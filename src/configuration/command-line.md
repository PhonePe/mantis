# 🖥️ Command Line
---

Mantis ships with a simple list of command line options.

<img src="command-line.png" class="img-rounded" alt="Assets">

## Quick Help

```shell

  usage: 
        ONBOARD: (First time scan, Run this !!)

        mantis onboard -o example_org -t www.example.org
        mantis onboard -o example_org -f file.txt

        SCAN:

        mantis scan -o example_org
        mantis scan -o example_org -a example_app
            

options:
  -h, --help      list command line options

subparser:
  {onboard,scan}
    onboard       Onboard a target
    scan          Scan an org
```

## Onboard Help

```shell
usage: 
        ONBOARD: (First time scan, Run this !!)

        mantis onboard -o example_org -t example.tld
        mantis onboard -o example_org -f file.txt

            

options:
  -h, --help            show this help message and exit
  -t HOST, --host HOST  top level domain to scan
  -f FILE_NAME, --file_input FILE_NAME
                        path to file containing any combination of TLD, subdomain, IP-range, IP-CIDR
  -w WORKFLOW, --workflow WORKFLOW
                        workflow to be executed as specified in config file
  -o ORG, --org ORG     name of the organisation
  -a APP, --app APP     scan only subdomains that belong to an app
  -p, --passive         run passive port scan
  -s, --stale           mark domains as stale (domains purchased but not in use)
  -i, --ignore_stale    ignore stale domains during scan
  -tc THREAD_COUNT, --thread_count THREAD_COUNT
                        thread count, default 10
  -r, --use_ray         use ray framework for distributed scans
  -n NUM_ACTORS, --num_actors NUM_ACTORS
                        number of ray actors, default 10
  -d, --delete_logs     delete logs of previous scans
  -v, --verbose         print debug logs
  -aws AWS_PROFILES, --aws_profiles AWS_PROFILES
                        List of comma separated aws profiles for Route53

```

## Scan Help

```shell
usage: 
        SCAN:

        mantis scan -o example_org
        mantis scan -o example_org -a example_app
            

options:
  -h, --help            show this help message and exit
  -w WORKFLOW, --workflow WORKFLOW
                        workflow to be executed as specified in config file
  -o ORG, --org ORG     name of the organisation
  -a APP, --app APP     scan only subdomains that belong to an app
  -p, --passive         run passive port scan
  -s, --stale           mark domains as stale (domains purchased but not in use)
  -i, --ignore_stale    ignore stale domains during scan
  -tc THREAD_COUNT, --thread_count THREAD_COUNT
                        thread count, default 10
  -r, --use_ray         use ray framework for distributed scans
  -n NUM_ACTORS, --num_actors NUM_ACTORS
                        number of ray actors, default 10
  -d, --delete_logs     delete logs of previous scans
  -v, --verbose         print debug logs
  -aws AWS_PROFILES, --aws_profiles AWS_PROFILES
                        List of comma separated aws profiles for Route53

```