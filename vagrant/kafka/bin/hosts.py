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

    for host in config["hosts"]:
        print(host)
