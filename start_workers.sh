#!/bin/bash

for ((i=0; i < 10; i++))
do
$VENV/bin/rq worker -u redis://redis:6379 tasks_queue &
done
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?