# 🎛️ Workflow Configuration
---

> Warning 🚨 - In onboard mode, you should run scans only with the 'default' workflow

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

> Warning 🚨 - Do not modify the default workflow config, always create a new workflow before modifying it as shown in example 3

### Example 1
Run a single module, say just 'Discovery', this is how your config is going to look, simply remove the rest of the modules

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

### Example 3

Now say you want to go one step ahead and create you own workflow, you can do that by simply copy, pasting the default workflow, make the corresponding changes and rename it according your requirement.


```yml
workflow:
  - workflowName: 'custom_workflow'
    schedule: 'daily between 00:00 and 04:00'
    cmd: ['python3 launch.py -o org_name -f org-tlds.txt --ignore_stale --stale']
    workflowConfig:
      - moduleName : discovery
        tools: ['Subfinder', 'Amass'] 
        order: 1
      - moduleName: prerecon
        tools: ['FindCDN', 'Naabu'] 
        order: 2
      - moduleName: activehostscan
        tools: ['HTTPX_Tech', 'HTTPX']
        order: 3
      - moduleName: scan
        tools: [ 'DNSTwister', 'Csper', 'Nuclei', 'NucleiRecon']
        order: 4

```

As you can see, the new workflow does not contain modules like Route53, ActiveRecon, SecretsScanning etc. A couple of tools like SSLMate and IPInfo have been removed too. The name of the workflow is also changed to **custom_workflow**

Now to run this new workflow, you can make use of the -w options

```shell
$ mantis -o example -t example.org -w custom_workflow
```
