#! /usr/bin/env python

import collections
import json
import os.path
import sys


def read_hosts(source=None):
    data = collections.defaultdict(list)
    hosts = collections.defaultdict(dict)
    if not source:
        source = "/etc/ansible/roles"
    with open(source, "r") as source_handle:
        for line in source_handle:
            line = line.strip()
            if not line:
                continue
            if line[0] == "#":
                continue
            hostname = None
            roles = ""
            options = None
            try:
                (hostname, roles, options) = line.split(None, 2)
            except ValueError:
                try:
                    (hostname, roles) = line.split(None, 1)
                except ValueError:
                    print("Error with line %s" % (line))
            for role in roles.split(","):
                role = role.strip()
                data[role].append((hostname, options))
            for option in options.split():
                try:
                    key, value = option.split('=', 1)
                except ValueError:
                    key = option
                    value = True
                hosts[hostname][key] = value
    return (data, hosts)

if __name__ == "__main__":
    (data, hosts) = read_hosts()

    if len(sys.argv) > 1:
        result = {}
        if sys.argv[1] == "--list":
            for role in data:
                result[role] = {"hosts": [x[0] for x in data[role]], "vars": {}}
        elif sys.argv[1] == "--host":
            result = hosts[sys.argv[2]]
        print(json.dumps(result, indent=4))
        exit(0)

    for role in data:
        print("[%s]" % role)
        for host in data[role]:
            print("%s\t%s" % (host))
        print()
