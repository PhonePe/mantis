# Installation
---

>  *As mentioned earlier, it is recommended to install the database and dashboard on a separate VM or setup, apart from the controller and worker VMs.*

## 1. Mongo DB
You can set this up based on your convenience; here are multiple options:

- Setup MongoDB on [**cosmos Azure**](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/introduction)
- Setup MongoDB on a [**Linux VM**](https://www.mongodb.com/docs/manual/administration/install-on-linux/)

> 🚨 Warning - By default when you install mongoDB in linux, its bound to accept traffic only from localhost. Change this setting [**here**](https://www.mongodb.com/docs/manual/core/security-mongodb-configuration/) to accept connections from external IPs too.

Once installed, copy the conenction string

## 2. Dashboard
- Setup [**Appsmith Dashboard**](https://docs.appsmith.com/getting-started/setup/installation-guides/docker)
- Setup Proprietary Dashboard (coming soon) 


## 3. Mantis 

> Please Note - The below steps have to repeated in controller and all the worker VMs. If you have 1 controller and 2 workers, install them in all the 3 VMs

### Setup Mantis (Native Installation)

## Pre-Requisites

- OS: 22.04.1-Ubuntu (x86_64)

A few tools require glibc 2.34 and hence this version is ideal.

Clone the repository

```shell
git clone https://github.com/PhonePe/mantis.git
```

Install Mantis dependencies 

Within the repository, traverse to **/setup/** path, change permissions and run the native setup file. 

```shell
chmod +x native-setup.sh
```

```shell
./native-setup.sh
```

> ⏭️ Now that the required components are installed, let's make changes to the configuration.