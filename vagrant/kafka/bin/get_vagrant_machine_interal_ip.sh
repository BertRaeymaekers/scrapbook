#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}/../${1}
IP=$(vagrant ssh -c 'ip addr' 2>/dev/null | gawk 'match($0, /inet ([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)[/].* eth0/, ip) {print ip[1]}')

echo "${IP}"