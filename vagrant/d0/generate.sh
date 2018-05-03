source .token

sed -e "s/\${DIGITAL_OCEAN_TOKEN}/$DIGITAL_OCEAN_TOKEN/" Vagrantfile.template > Vagrantfile

