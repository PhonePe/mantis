# Add scanner to config file
---

Now that the Amass.py tool class is ready, adding it to config is simple. Add the class name Amass under moduleName **discovery** under **tools**

```yaml
- workflowName: 'default'
    schedule: 'daily between 00:00 and 04:00'
    cmd: ['python3 launch.py -o org_name -f org-stale.txt --ignore_stale --stale']
    workflowConfig:
      - moduleName : discovery
        tools: ['Subfinder', 'SSLMate', 'Amass'] 
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
