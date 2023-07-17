#!/bin/bash

# Find the process ID of the running Python3 myaccount.py
process_id=$(ps -ef | grep "python3 myaccount.py" | grep -v "grep" | awk '{print $2}')

# If the process is found, gracefully stop it using the process ID
if [ ! -z "$process_id" ]; then
    echo "Stopping myaccount.py with process ID: $process_id"
    kill -15 "$process_id"
    sleep 2
else
    echo "No myaccount.py process found."
fi

# Restart the myaccount.py and monitor the nohup.out log
echo "Starting myaccount.py..."
nohup python3 myaccount.py & tail -f nohup.out &

