#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source ${DIR}/venv/bin/activate
# Topic: one
# #Messages: 1000
# Size of Message: 100
# Start id: 0
python ${DIR}/put.py one 1000 100 0
