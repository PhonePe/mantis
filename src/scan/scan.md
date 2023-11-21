# 📨 Run a Scan
---

Mantis provides two modes to scan:
- Onbaord and Scan
- Scan


### Onboard and Scan
---

You want to onboard an org with its TLDs/IPs/IP-CIDRs/IP Range for the first time, use the onboard mode. This runs the scan on the default workflow.

#### TLD
```shell
$ python3 launch.py onboard -o org_name -t example.in   
```
#### IP
```shell
$ python3 launch.py onboard -o org_name -t 10.123.123.12
```

#### IP-Range
```shell
$ python3 launch.py onboard -o org_name -t 203.0.113.0-10
```

#### IP-CIDR
```shell
$ python3 launch.py onboard -o org_name -t 203.0.113.0/24
```

### Onboard Known Assets and Scan
```shell
$ python3 launch.py onboard -o org_name -f input.txt
```

### Scan on all assets belonging to an organisation
---

Now that you have onboarded, you just need to run scheduled scans for an org, you can just use the scan mode

```shell
$ python3 launch.py scan -o org_name
```

### Scan on all assets belonging to an organisation and app
---

```shell
$ python3 launch.py scan -o org_name -a app_name
```

