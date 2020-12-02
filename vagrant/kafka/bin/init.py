#! /usr/bin/env python3


import json
import os.path

import jinja2


DEFAULT_PARAMS = {
    "ansible_user": "vagrant"
}


if __name__ == "__main__":
    # Reading configuration
    here = os.path.dirname(os.path.realpath(__file__ + "/../"))
    with open(here + "/config.json", "r") as rf:
        config = json.load(rf)
    print(json.dumps(config, sort_keys=True, indent=4))

    # Generating an inventory file
    with open(here + "/playbook/inventory/hosts", "w") as inventory:
        inventory.write("[kafka]\n")
        for host in config["hosts"]:
            # Setting default values and updating them when more specific.
            params = dict()
            params.update(DEFAULT_PARAMS)
            params.update(config["params"])
            params.update(config["hosts"][host])
            # Setting some extra ansible paramters.
            params["ansible_ssh_host"] = params["ip"]
            inventory.write("%s\t%s\n" % (host, " ".join(("%s=%s" % (k,v) for k,v in params.items()))))

    # Generating the Vagrantfile
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(here + "/templates/"))
    template = env.get_template('Vagrantfile.j2')
    template.stream(**config).dump(here + '/vagrant/Vagrantfile')

    # Generating group vars for kafka
    with open(here + "/playbook/group_vars/kafka.yml", "w") as gv:
        gv.write("---\n")
        gv.write("hosts:\n")
        for (host, params) in config["hosts"].items():
            gv.write("    %s: '%s.%s'\n" % (params["ip"], params["hostname"], config["params"]["domain" ]))
        gv.write("kafka:\n")
        gv.write("  hosts:\n")
        for (host, params) in config["hosts"].items():
            gv.write("    - %s.%s\n" % (params["hostname"], config["params"]["domain" ]))
