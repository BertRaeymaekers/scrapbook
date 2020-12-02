#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source ${DIR}/../venv/bin/activate
HOSTS=$(python ${DIR}/hosts.py)

cd  ${DIR}/../playbook
ansible-playbook -i inventory/hosts kafka.yml
