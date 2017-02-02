/home/grasparkietbgc/status.sh
if [[ "$?" -eq "0" ]]
then
	echo "Was already running."
else
	echo "Starting twitterage.py..."
	nohup /home/grasparkietbgc/bin/twitterage.py &
	/home/grasparkietbgc/bin/status.sh
fi
