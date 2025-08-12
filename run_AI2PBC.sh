#!/bin/bash

echo "Starting AI²PBC Voice Assistant..."
sleep 10

cd /home/faraz/AI2PBC
PYTHON=/home/faraz/AI2PBC/env/bin/python

# Log file path
LOG_FILE="ai2pbc_log.txt"
while true
do
  $PYTHON main.py >> "$LOG_FILE" 2>&1 

done
