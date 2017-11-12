#!/bin/bash

NUMBER=$1

## Hostname
#sudo hostname E${NUMBER}
#
## Fix hosts
#mv /etc/hosts /etc/hosts.orig
#grep -v "^127.0.0.1" /etc/hosts.orig | grep -v "^::1 " > /etc/hosts
#echo "" >> /etc/hosts
#echo "127.0.0.1 localhost E${NUMBER}.schilduil.org E${NUMBER}" >> /etc/hosts
#echo "::1     localhost ip6-localhost ip6-loopback" >> /etc/hosts

# Preparing APT
sudo apt-get update

# Installing Apache
sudo apt-get install mongodb -y

# Installing netstat
sudo apt-get install net-tools -y

## For the course
## Installing git
#sudo apt-get install git -y
#
## Installing python3-venv
#sudo apt-get install python3-venv -y

