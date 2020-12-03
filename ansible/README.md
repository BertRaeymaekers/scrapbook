# Ansible scripts to maintain my own network

- **apt-upgrade.yml** to keep all my Debian machines up to date.
- **backup-server.yml** to configure my backup server (i.e. a Raspberry Pi)
- **monitoring-server.yml** to setup my monitoring server (i.e. a Rasberry Pi)

## Pre-requisites

This is what you need before you can run the playbooks:
- **Ansible** is installed.
- An ansible **hosts** file (see the Ansible docs on how to set this up).
- Create your YAML files under **hosts_vars** and **group_vars**. This can be generated (see lower).

## Generation of the files for *hosts_vars* and *group_vars*

What YAML files under the **hosts_vars** and **groups_vars** do: see the Ansible docs.

