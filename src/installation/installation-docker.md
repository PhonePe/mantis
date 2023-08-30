# Docker
---

Mantis supports multiple installation types. Installing Mantis via Docker would be a good start to get a hang of the framework.

Considering that Mantis also includes mongoDB and AppSmith, we have provided a shell script that installs all the components.

## Setup

Clone the Mantis repository 

```shell
$ git clone https://github.com/PhonePe/mantis.git
```

cd into the Mantis directory    

```shell
$ cd mantis/setup/docker
```

Run the respective docker setup file based on your OS

```shell
$ ./docker-setup-macos.sh

$ ./docker-setup-ubuntu.sh
```