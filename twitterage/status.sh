pid=$(ps -ef | grep twitterage.py | grep -v grep | awk -F" " '{print $2}')
if [[ "$pid" -ne "" ]]
then
	echo "Running as $pid."
	exit 0
else
	echo "Not running."
	exit 1
fi
