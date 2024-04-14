# Run the Scan
---

> Ensure there is network connectivity between the controller and the workers, and that there are no blocks from the firewall

## Initialise Ray

In the controller VM, run this command to start ray

```shell
ray start --head
```

You will also get the command to run on the workers once you execute the above command.

In all of the worker VMs, run this command to start ray and listen to the controller. 

```shell
ray start --address='CONTROLLER_IP'
```

## Run Scans

From the controller VM, you can simply start a scan using '-r', check the last command mentioned [**here**](https://phonepe.github.io/mantis/scan/scan.html)

> Please Note - Add python3.9 instead python3

```shell
python3.9 launch.py scan -o org_name -a app_name -r
```

You can view the ray dashboard here - **http://127.0.0.1:8265/#/cluster**, This will help us understand how the scans are being distributed across your controller and workers.

> ⏭️ The last step is to setup the dashboard
