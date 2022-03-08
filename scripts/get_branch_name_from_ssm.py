import boto3
import os
ssm_client = boto3.client('ssm')

#CODEBUILD_INITIATOR=codepipeline/featurebranchpipelinewebhookReadyForFeatureBranchPipeline

branch_chars = ''
branch_name = ''

CODEBUILD_INITIATOR_LIST = os.getenv('CODEBUILD_INITIATOR').split('/')
if len(CODEBUILD_INITIATOR_LIST) >= 2:
	if CODEBUILD_INITIATOR_LIST[0] == 'codepipeline':
		if CODEBUILD_INITIATOR_LIST[1] == 'FeatureBranchPipelineGenerator':
			branch_chars = 'generator' # TODO dev, master
		else:
			branch_chars = CODEBUILD_INITIATOR_LIST[1].strip('ReadyForFeatureBranchPipeline')


if branch_chars:
    response = ssm_client.get_parameter(
        Name=branch_chars,
    )
    branch_name = response.get('Parameter', {}).get('Value', '')
print(branch_name)

