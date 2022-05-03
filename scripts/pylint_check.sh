#!/bin/bash

# Check whether Pylint score passes the threshold


set -e

threshold=$1
echo "Threshold: $threshold"
# pylint *
# pylint cdk_py/

pylint_output_file="pylint_output"
echo "$pylint_output_file"
pylint * > $pylint_output_file
cat $pylint_output_file

score=$(cat $pylint_output_file |grep -oE '\-?[0-9]+\.[0-9]+'| sed -n '1p')
# score=$(pylint * |grep -oE '\-?[0-9]+\.[0-9]+'| sed -n '1p')

echo "Score: $score"
ret=$(awk -v score=$score -v threshold=$threshold 'BEGIN{print(score>threshold)?0:1}')
echo "Ret: $ret"
if [[ $ret -eq 0 ]]; then 
	echo "$score>$threshold"
else 
	echo "$score<=$threshold"
	exit 1
fi
