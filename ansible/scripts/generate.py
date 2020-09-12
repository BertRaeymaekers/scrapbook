#! /usr/bin/env python3


import copy
import errno
import os.path
import yaml


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_HOSTS_YML_FILENAME = SCRIPT_DIR + '/../conf/hosts.yml'


def load_config(filename):
    with open(filename, 'r') as yml:
        return yaml.load(yml)


config = load_config(SCRIPT_DIR + '/../conf/config.yml')


def get_hosts_from_hosts_file(filename=None, ip_prefix=None):
    """
    A generator that returns a list of local machines
    
    It gets this info from the local hosts file and filters out those starting with the ip_prefix
    """
    if not filename:
        filename = config.get('hosts_file', '/etc/hosts')
    if not ip_prefix:
        ip_prefix = config.get('network_ip_prefix', '')
    with open(filename, 'r') as hosts:
        for line in hosts:
            if line.startswith(ip_prefix):
                ip, names = line.strip().split("#")[0].split(maxsplit=1)
                yield (ip, names)


def get_hosts_from_yml(filename=None):
    if not filename:
        filename = DEFAULT_HOSTS_YML_FILENAME
    return load_config(filename)


def set_hosts_to_yml(hostgroups, filename=None):
    if not filename:
        filename = DEFAULT_HOSTS_YML_FILENAME
    with open(filename, 'w') as yml:
        yaml.dump(hostgroups, yml, default_flow_style=False)


def get_hosts(filename=None):
    """
    Trying to read in the hosts from the yml file.
    If that fails, generate it from the machine's hosts file and create it
    """
    try:
        print("Reading hosts from %s" % (DEFAULT_HOSTS_YML_FILENAME))
        hostgroups = get_hosts_from_yml(filename)
    except FileNotFoundError as fnfe:
        print(fnfe)
        print("Falling back to the hosts file.")
        hostgroups = {'OTHER': dict()}
        for ip,names in get_hosts_from_hosts_file():
            hostgroups['OTHER'][ip] = names
        print("Writing the import from the hosts file to %s" % (DEFAULT_HOSTS_YML_FILENAME))
        set_hosts_to_yml(hostgroups, filename)
    return hostgroups


def filter(hostgroups, groups=None, hosts=None):
    if not groups and not hosts:
        return hostgroups
    if hosts:
        hosts = set(hosts)
    else:
        hosts = set()
    result = {}
    for group, ips in hostgroups.items():
        if groups and group in groups:
                result.update(ips)
        elif hosts and ips:
            for ip,names in ips.items():
                if set(names.split()) & hosts:
                    result[ip] = names
    return result


def generate_group_vars_yml(hostgroups=None, path=None):
    if not path:
        path = SCRIPT_DIR + '/../group_vars'
    template_path = SCRIPT_DIR + '/../conf/group_vars'
    if not hostgroups:
        hostgroups = get_hosts()
    # Getting the default configuration items
    defaults = config.copy()
    # Rename groups as config because groups is a reserved name in Ansible.
    # The deep copy is needed to avoid issues with the yml generation.
    defaults['config'] = copy.deepcopy(defaults['groups'])
    del defaults['groups']
    # Finding all potential groups: from the config and from conf/group_vars
    try:
        groups = set(config['groups'].keys())
    except:
        groups = set()
    try:
        groups = groups.union(set([os.path.basename(filename).rsplit('.', maxsplit=1)[0] for filename in os.listdir(template_path)]))
    except FileNotFoundError:
        pass
    for group in groups:
        print("Processing group %s..." % (group))
        group_vars = defaults.copy()
        try:
            with open(template_path + '/%s.yml' % (group), 'r') as input:
                group_vars = yaml.load(input)
        except FileNotFoundError:
            pass
        hosts_file = group_vars.get('hosts_file', dict())
        if ('groups' in config) and (group in config['groups']) and config['groups'][group]:
            groupconfig  = config['groups'][group]
            group_vars.update(groupconfig)
            for ip,names in  filter(hostgroups, groups=groupconfig.get('hosts_file_groups', []), hosts=groupconfig.get('hosts_file_hosts', [])).items():
                hosts_file[ip] = names
            user_machines = []
            for ip,names in filter(hostgroups, groups=['USER_MACHINES']).items():
                user_machines.append(names.split()[-1])
            group_vars['user_machines'] = user_machines
        group_vars['hosts_file'] = hosts_file
        try:
            os.makedirs(path)
        except OSError as ose:
            if ose.errno !=  errno.EEXIST:
                raise
        with open(path + '/%s.yml' % (group), 'w') as output:
            print("Writing %s/%s.yml." % (path, group))
            yaml.dump(group_vars, output, default_flow_style=False)


if __name__ == "__main__":
    hostgroups = get_hosts()
    generate_group_vars_yml(hostgroups)
    #generate_host_vars_yml(hostgroups)
