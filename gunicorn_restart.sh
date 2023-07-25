#!/bin/bash

# Find the process ID of the running Gunicorn server
process_id=$(ps -ef | grep "gunicorn myaccount:app" | grep -v "grep" | awk '{print $2}')

# If the process is found, gracefully stop it using the process ID
if [ ! -z "$process_id" ]; then
    echo "Stopping myaccount:app with process ID: $process_id"
    kill -15 "$process_id"
    sleep 2
else
    echo "No myaccount:app process found."
fi

# Restart the myaccount:app and monitor the nohup.out log
echo "Starting myaccount:app..."
nohup gunicorn myaccount:app -w 4 -b 0.0.0.0:5000 & tail -f nohup.out &

