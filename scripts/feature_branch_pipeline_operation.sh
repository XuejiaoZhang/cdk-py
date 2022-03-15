#!/bin/bash

echo $BRANCH, $creation_or_deletion, $stack_id

if [[ $BRANCH =~ ^feature-branch-pipeline- ]]; then 

	branch_chars=$(echo $BRANCH |sed "s/[^0-9a-zA-Z]//g")
    stack_id=$branch_chars"ReadyForFeatureBranchPipeline"
    echo $stack_id
	npm -v; npm install -g aws-cdk; cdk --version; pip install -r requirements.txt; 
	echo "cdk ls"
	cdk ls -c branch_name=$BRANCH; 
	echo "cdk synth"

	cdk synth -c branch_name=$BRANCH; 
	echo "cdk diff"
	cdk diff -c branch_name=$BRANCH; 
	echo "cdk deploy"
	if [[ $creation_or_deletion == 'creation' ]]; then 
		echo "creation"
		# cdk deploy FeatureBranchPipelineGenerator/pipelineGenerator/Create-Branch -c branch_name=$BRANCH  --require-approval never #TODO
		#stack_id=FeatureBranchPipelineGenerator/pipelineGenerator/Create-Branch
		
		stack_id = branch_name + "-pipeline"
		
		cdk deploy $stack_id -c branch_name=$BRANCH  --require-approval never
	elif [[ $creation_or_deletion == 'deletion' ]]; then 
		echo "deletion"
		cdk destroy $stack_id -c branch_name=$BRANCH -f
	else:
		echo 'Not a branch creation or deletion event'
	fi
else 
	echo 'Not match feature branch prefix'
fi