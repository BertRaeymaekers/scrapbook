source .token

# NOT USED ANYMORE, PASSES AS AN EXTRA_ARGS TO ANSIBLE.
#sed -e "s/\${MONGODB_CONNECTION_STRING}/$MONGODB_CONNECTION_STRING/" roles/testsusmapi/files/template_wsgi.py > roles/testsusmapi/files/wsgi.py
if [[ "$1" == "do" ]]
then
    sed -e "s/\${DIGITAL_OCEAN_TOKEN}/$DIGITAL_OCEAN_TOKEN/" Vagrantfile.template > Vagrantfile
elif [[ "$1" == "vb" ]]
then
    cat Vagrantfile.vb > Vagrantfile
else
    printf "\nParameter required:\n\tdo: Digital Ocean droplet.\n\tvb: Virtualbox virtual machine.\n\n"
    exit 1
fi
