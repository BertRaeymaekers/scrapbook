#!/bin/bash

NUMBER=$1

# Hostname
sudo hostname E${NUMBER}

# Fix hosts
mv /etc/hosts /etc/hosts.orig
grep -v "^127.0.0.1" /etc/hosts.orig | grep -v "^::1 " > /etc/hosts
echo "" >> /etc/hosts
echo "127.0.0.1 localhost E${NUMBER}.schilduil.org E${NUMBER}" >> /etc/hosts
echo "::1     localhost ip6-localhost ip6-loopback" >> /etc/hosts

# Preparing APT
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https -y
echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-5.x.list
sudo apt-get update

# Installing Apache
sudo apt-get install apache2 -y

# Installing Java
sudo apt-get install openjdk-8-jre-headless -y

# Installing elasticsearch
sudo apt-get install elasticsearch -y

# Installing curl
sudo apt-get install curl -y

# Configuring elasticsearch
echo "# elasticsearch.yml from install_e.sh" > /etc/elasticsearch/elasticsearch.yml
echo "cluster.name: su-e-cluster" >> /etc/elasticsearch/elasticsearch.yml
echo "node.name: su-e-node-${NUMBER}" >> /etc/elasticsearch/elasticsearch.yml
echo 'discovery.zen.ping.unicast.hosts: ["E1.schilduil.org", "E2.schilduil.org", "E3.schilduil.org"]' >> /etc/elasticsearch/elasticsearch.yml
echo "discovery.zen.minimum_master_nodes: 2" >> /etc/elasticsearch/elasticsearch.yml

# Restarting elasticsearch
service elasticsearch stop
service elasticsearch start

