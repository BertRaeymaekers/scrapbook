source .token
export ENV="DEV"
if [ ! -z "$1" ]
then
    export ENV="$1"
fi
ansible-playbook -C -l $ENV playbook.yml -e "mongo_connection_string=${MONGODB_CONNECTION_STRING}"
