# Workflow Customisation
---

<product-team>product security teams</product-team> <bug-bounty>bug bounty hunters </bug-bounty>

## 🤔 Use-Case
**I want to:**
- *customize scans with ease to best suit my organization's or bug bounty requirements*
- *ability to choose from various modules, including discovery and vulnerability scanning, to create a tailored scan that meets my specific needs*
- *granular options to specify tools within each module, allowing me to optimize my security operations for maximum efficiency*

## 😃 Feature
In Mantis:
- we refer to the entire automation process as a **Workflow**
- Worflow is further divided into individual blocks called as a **Module** 
- Modules are further divided as **Tools**

All the above are easily customisable via a **config file**

## 🎛️ Workflow Customisation

This is the workflow snippet from **config.yml**, you can just add/remove the module or tool you want to customise:

```yml
workflow:
  - workflowName: 'default'
    schedule: 'daily between 00:00 and 04:00'
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

- **moduleName** - Pre-packaged or custom modules 
- **tools** - Tools included as part of the module 
- **order** - The order in which the module needs to be executed, e.g., discovery needs to be run before recon
## Examples
### Example 1
Run a single module, say just 'Discovery', this is how your config is going to look, simply comment or remove the rest of the modules

```yml
workflow: 
  - moduleName : discovery
    tools: ['Subfinder', 'SSLMate', 'Amass'] 
    order: 1
```

### Example 2
Remove a tool, say you just want to run subdomain discovery and not identify 'certificates', so just remove 'SSLMate' from tools section under Discovery moduleName

```yml
workflow: 
  - moduleName : discovery
    tools: ['Subfinder', 'Amass'] 
    order: 1
```
## Understanding config.yml
> INFO💡: For more details on config.yml and how to edit it, [Click here](/./configuration/configuration.md)