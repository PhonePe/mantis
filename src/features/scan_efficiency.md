# Understanding Scan Efficiency
---

<product-team>product security teams</product-team> <bug-bounty>bug bounty hunters </bug-bounty>

## 🤔 Use-Case
**I want to:**
- *understand whether my scans succeeded or failed*
- *determine the time taken for the scans*


## 😃 Feature
Mantis provides you with efficient scan statistics at a granular level, including the following:
- Total scan time and efficiency
- Module level scan time and efficiency
- Success or Failure status for each asset

The **Efficiency** is calcuated based on the success/failure rates

## Scan Efficiency 
Post scan, Mantis outputs a file which is present in `{mantis_dir}/logs/scan_efficiency/`, which provides you with the scan metadata.
### Success Scenario


```json
{
    "module_name": "PRERECON",
    "module_start_time": "524109.441001708",
    "module_end_time": "524288.824489208",
    "module_time_taken": "0:02:59",
    "module_tool_logs": [
        {
            "tool_name": "FindCDN",
            "success": 1,
            "failure": 0,
            "code": 0,
            "command": "findcdn list example.in -o /tmp/7917f79d-8b06-4727-8953-dcf5c84efde6.json -v",
            "errors": null,
            "exception": null,
            "tool_time_taken": "0:02:59"
        }
    ]
}
```
The above stats clearly states:
- the **python subprocess** exit code was 0, indicating success (warning - this depends on how efficiently the tool handles exit codes as well)
- the scan for a particular asset example.com was **successful**
- the **total time taken** to run subfinder on that asset

### Failure Scenario

```json
{
    "module_name": "DISCOVERY",
    "module_start_time": "525058.566098541",
    "module_end_time": "525059.556518666",
    "module_time_taken": "0:00:01",
    "module_tool_logs": [
        {
            "tool_name": "Subfinder",
            "success": 0,
            "failure": 1,
            "code": 2,
            "command": "subfinder -te -d example.com -o /tmp/de4c5987-d4fe-46f9-89ef-f19af67cd1d0.txt",
            "errors": null,
            "exception": "[Errno 2] No such file or directory: '/tmp/de4c5987-d4fe-46f9-89ef-f19af67cd1d0.txt'",
            "tool_time_taken": "0:00:00"
        }
    ]
}

```

The above stats clearly states:
- the **python subprocess** exit code with a non-zero exit code (2), indicating failure 
- the scan for a particular asset example.com was a **failure**, this is because a wrong subfinder command was passed