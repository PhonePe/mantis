# Scheduler Configuration
---

Mantis also lets you schedule scans, this scheduler option is present in in the workflow config itself.

## Examples 

### Example 1

Setup default workflow module to be run everyday at 9AM.

> INFO 💡 - Schedule key words are based on [Python Rocketery Framework](https://rocketry.readthedocs.io/en/stable/)

```yml
workflow:
  - workflowName: 'default'
    schedule: 'daily between 09:00 and 11:00'
    cmd: ['python3 launch.py -o org_name -f org-tlds.txt --ignore_stale --stale']
    workflowConfig:
      - moduleName : Route53
        tools: ['Route53'] 
        order: 1
      - moduleName : discovery
        tools: ['Subfinder', 'SSLMate'] 
        order: 1
      - moduleName: prerecon
        tools: ['FindCDN', 'Naabu', 'IPinfo'] 
        order: 2
      - moduleName: activehostscan
        tools: ['HTTPX_Tech', 'HTTPX']
        order: 3
      - moduleName: activerecon
        tools: ['Wafw00f']
        order: 4
      - moduleName: scan
        tools: [ 'DNSTwister', 'Csper', 'Nuclei', 'NucleiRecon']
        order: 5
      - moduleName: secretscanner
        tools: ['SecretScanner']
        order: 6

```

- Created a new config **discovery_workflow** that only runs discovery module
- Set the **schedule** parameter to **daily at 9:00**


### Example 2

Setup discovery module to be run everyday at 11AM.

```yml
workflow:
  - workflowName: 'discovery_workflow'
    schedule: 'daily between 11:00 and 14:00'
    cmd: ['python3 launch.py -o org_name -f org-tlds.txt -w discovery_workflow']
    workflowConfig:
      - moduleName : discovery
        tools: ['Subfinder', 'SSLMate'] 
        order: 1

```

- Created a new config **discovery_workflow** that only runs discovery module
- Set the **schedule** parameter to **daily at 9:00**
