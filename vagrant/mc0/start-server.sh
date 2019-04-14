#!/bin/bash

#/usr/bin/screen -S $1
nohup /usr/bin/java -Xmx1024M -Xms1024M -jar ~/Minecraft/minecraft_server.jar nogui &
