#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for APP in 'init_messages' 'plain'
do

    if [ ! -f ${DIR}/../app/${APP}/venv/bin/activate ]; then
        cd ${DIR}/../app/${APP}
        python3 -m venv venv
    fi

    source ${DIR}/../app/${APP}/venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade -r ${DIR}/../app/${APP}/requirements.txt

done
