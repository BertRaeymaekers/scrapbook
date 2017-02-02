#!/bin/bash

for file in /home/etem/orig/*

do

    file="${file:16}"

    wget -O "/home/etem/live/${file}" "http://${file}/"

    if [ $? -ne 0 ]

    then

        date >> /home/etem/change.log
        echo "${file} could not be downloaded!" >> /home/etem/change.log
        mail -s "${file} unavailable!" -c foo@bar.org bar@bar.org < "/home/etem/live/${file}"

    else

        diff "/home/etem/orig/${file}" "/home/etem/live/${file}" > /home/etem/diff.txt

        if [ $? -ne 0 ]

        then

            date >> /home/etem/change.log
            echo "${file} changed!" >> /home/etem/change.log
            mail -s "${file} changed!" -c foo@bar.org bar@bar.org < "/home/etem/diff.txt"
            mv "/home/etem/orig/${file}" "/home/etem/changed/${file}"

        else

            date >> /home/etem/ok.log
            echo "${file}" >> /home/etem/ok.log

        fi
    fi

done
