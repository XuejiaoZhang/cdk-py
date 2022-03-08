import boto3

codepipeline_client = boto3.client('codepipeline')
response = codepipeline_client.get_pipeline(
    name='FeatureBranchPipelineGenerator',
    # version=123
)

pipeline_describe = response.get('pipeline', {})

branch_name = 'dev'
pipeline_describe['stages'][0]['actions'][0]['configuration']['BranchName'] = branch_name
pipeline_describe['version'] = pipeline_describe.get('version') + 1

print(pipeline)
print('--------------------------')
response = codepipeline_client.update_pipeline(
    pipeline=pipeline_describe
)
print(response)


get_pipeline = "FeatureBranchPipelineGenerator"

response = codepipeline_client.start_pipeline_execution(
    name=get_pipeline,
    # clientRequestToken='string'
)

print(response)
pipeline_execution_id = response.get('pipelineExecutionId', '')
print(pipeline_execution_id)