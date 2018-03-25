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

# Setting the sources for mongodb
# (https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/)
wget -qO - https://www.mongodb.org/static/pgp/server-3.6.asc | sudo apt-key add -
curl -O http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u7_amd64.deb
# WHEN IT COMES AVAILABLE: STRETCH
# echo "deb http://repo.mongodb.org/apt/debian stretch/mongodb-org/3.6 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.6 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list

# Creating the data directory for mongodb
sudo mkdir -p /data/db
sudo chmod ugo+rwx /data/db

# Preparing APT
sudo apt-get update

# Installing MongoDB
#sudo apt-get install mongodb -y # OLD VERSION
sudo dpkg -i libssl1.0.0_1.0.1t-1+deb8u7_amd64.deb
sudo apt-get install mongodb-org -y

sudo chown mongodb:mongodb /data/db
sudo chmod go-rwx /data/db

# Installing netstat
sudo apt-get install net-tools -y

# Installing curl
sudo apt-get install curl -y

# Installing dependencies for robo3t
sudo apt-get install qt5-default -y
sudo apt-get install libgl1-mesa-glx -y
sudo apt-get install libglib2.0-0 -y

# Downloading and installing robo3t
curl -O https://download.robomongo.org/1.1.1/linux/robo3t-1.1.1-linux-x86_64-c93c6b0.tar.gz
tar -xf robo3t-1.1.1-linux-x86_64-c93c6b0.tar.gz

