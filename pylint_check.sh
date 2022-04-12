#!/bin/bash

# Check whether Pylint score passes the threshold

set -e

threshold=$1
echo "Threshold: $threshold"

score=$(pylint * | grep "Your code has been rated at"|awk '{print $7}'|awk -F'/' '{print $1}')
echo "Score: $score"

ret=$(awk -v score=$score -v threshold=$threshold 'BEGIN{print(score>threshold)?0:1}')
echo "Ret: $ret"
if [[ $ret -eq 0 ]]; then 
	echo "$score>$threshold"
else 
	echo "$score<=$threshold"
	exit 1
fi
