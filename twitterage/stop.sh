pid=$(ps -ef | grep twitterage.py | grep -v grep | awk -F" " '{print $2}')
if [[ "$pid" -ne "" ]]
then
	echo "Running as $pid, killing it."
	kill $pid
else
	echo "Not running."
fi
