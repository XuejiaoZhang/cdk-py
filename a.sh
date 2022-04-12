pylint_output_file=$2
echo $pylint_output_file
score=$(cat $pylint_output_file) 
echo $score
