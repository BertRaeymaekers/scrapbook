source .token

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
