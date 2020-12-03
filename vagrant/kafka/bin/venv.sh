#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ ! -f ${DIR}/../venv/bin/activate ]; then
    cd ${DIR}
    python3 -m venv venv
fi

source ${DIR}/../venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r ${DIR}/../requirements.txt
