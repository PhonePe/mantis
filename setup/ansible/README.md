# Ansible Setup

Configures mantis dependencies on ubuntu x86_64 arch

## Configuration 

### Ansible hosts/nodes

* They must have python3 installed

    ```bash
    sudo apt install python3 -y
    ```

### Ansible Controller

* Python deps

    ```bash
    python3 -m pip install ansible ansible-core
    ```

* Generate host file `hosts`

    ```txt
    [mantisnodes]
    mantis-node-1 ansible_host=192.168.0.105 ansible_user=root
    mantis-node-2 ansible_host=192.168.0.107 ansible_user=root
    mantis-node-3 ansible_host=192.168.0.109 ansible_user=root
    ```

    > Please ensure that ansible controller is able to ssh into the `mantisnodes` as `root` user using its private key

* Test connectivity with hosts

    ```bash
    ansible all -m ping
    ```

* Run playbook

    ```bash
    ansible-playbook -i hosts native-setup.yml
    ```
