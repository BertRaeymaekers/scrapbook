#!/bin/bash
# To add this repository please follow the steps below
# The following is already included in the latest Axon or Neuron OS images available at https://kb.unipi.technology
# This should be used if you are running clean Debian OS (Like Raspbian for Neuron family controllers)

# these files will be created during the installation process and removed at the end
APT_LIST_FILE="/etc/apt/sources.list.d/unipi-temp.list"

# this is the cleanup routine for purging temporary files
function cleanup()
{
	echo "Cleaning temporary files"
	[ -f "$APT_LIST_FILE" ] && rm "$APT_LIST_FILE"
}

# hooking up the cleanup routine to these signals
trap cleanup EXIT SIGTERM

# get the version of the Debian
DEBIAN_VERSION=$(lsb_release -sc)

# get the architecture (armhf or arm64)
if uname -a | grep -q aarch64; then
	ARCHITECTURE=arm64
else
	ARCHITECTURE=armhf
fi
echo "Running Raspberry Pi OS Debian/$DEBIAN_VERSION on $ARCHITECTURE"

# check if we are running bullseye+ and in case of armhf exit
if [ "$(lsb_release -sr)" -ge "12" ] ; then
	ADDITIONAL_MAIN_COMPONENT="unipi1-main "
fi


if [ "$(whoami)" != "root" ]; then
    SUDO=sudo
fi


echo "Downloading and importing the Unipi repository signing key"
if [ "$(lsb_release -sr)" -ge "11" ] ; then
    wget https://repo.unipi.technology/debian/unipi_next.asc -qO - | ${SUDO} cat - > /etc/apt/trusted.gpg.d/unipi_pub.asc
else
    echo "Upgrading the libgnutls30 package"
    apt update && apt install -y libgnutls30
    wget https://repo.unipi.technology/debian/unipi_pub.gpg -qO - | ${SUDO} apt-key add -
fi

echo
echo "Downloading the APT definition for Unipi repository"
# the missing space between variables and rest of the command is ok, see how the variables are created
echo "deb https://repo.unipi.technology/debian $DEBIAN_VERSION ${ADDITIONAL_MAIN_COMPONENT}main" | ${SUDO} tee "$APT_LIST_FILE"

echo
echo
echo "Updating the package list"
${SUDO} apt-get update

# if the release is stretch, it is probably a Neuron running older Raspbian
# prefer neuron-kernel package over unipi-kernel-modules
if [ "$(lsb_release -sr)" -ge "12" ] ; then
        PACKAGES="unipi-os-configurator-data unipi-kernel-modules unipi-one-modbus"
        ${SUDO} apt-get install -y $PACKAGES
fi

# clean temporary files
cleanup

if [ "$(lsb_release -sr)" -ge "12" ] ; then
    echo "--------------------------------------------------------------"
    echo "Reboot is required to load the kernel module and so run reboot"
    echo "--------------------------------------------------------------"
fi
# reboot

# Verify the status of unipitcp service
# systemctl status unipitcp

# Or also check the dmesg for UNIPISPI output
# Or check the status of internal MCUs (alter the -i 0 with -i 1 or 2 depending on the size of the controller)
# /opt/unipi/tools/fwspi -i 0

# An upgrade of the internal MCUs firmware is recommended, to do that run:
# /opt/unipi/tools/fwspi -v --auto
