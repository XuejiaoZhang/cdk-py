import boto3

codepipeline_client = boto3.client('codepipeline')

branch_name = 'devPipelineForTestingNNNNNNOO'
response = codepipeline_client.delete_pipeline(
    name=branch_name
)
print(response.get('ResponseMetadata').get('HTTPStatusCode'))

# print('-----------List---------------')
# response = codepipeline_client.list_pipelines(maxResults=10)
# nextToken = response.get('nextToken', '')
# pipelines = response.get('pipelines', [])
# for p in pipelines:
# 	print(p.get('name'))

# while nextToken != '':
# 	print('------')
# 	response = codepipeline_client.list_pipelines(nextToken=nextToken, maxResults=10)
# 	nextToken = response.get('nextToken', '')
# 	pipelines = response.get('pipelines', [])
# 	# print(pipelines)
# 	for p in pipelines:
# 		print(p.get('name'))




# print('-----------create---------------')

# response = codepipeline_client.get_pipeline(
#     name='dev-pipeline',
#     # version=123
# )

# pipeline_describe = response.get('pipeline', {})

# print(pipeline_describe)


# feature_branch_name='feature-branch-pipeline-us01'


# pipeline_describe['name'] = feature_branch_name + "PipelineForTesting"
# pipeline_describe['stages'][0]['actions'][0]['configuration']['BranchName'] = feature_branch_name

# # pipeline_describe['version'] = pipeline_describe.get('version') + 1


# response = codepipeline_client.create_pipeline(
#     	pipeline=pipeline_describe
#     )
# print(response)


# print('-----------update---------------')
# branch_name = 'dev'
# pipeline_describe['stages'][0]['actions'][0]['configuration']['BranchName'] = branch_name
# pipeline_describe['version'] = pipeline_describe.get('version') + 1


# response = codepipeline_client.update_pipeline(
#     pipeline=pipeline_describe
# )
# print(response)


# get_pipeline = "FeatureBranchPipelineGenerator"

# response = codepipeline_client.start_pipeline_execution(
#     name=get_pipeline,
#     # clientRequestToken='string'
# )

# print(response)
# pipeline_execution_id = response.get('pipelineExecutionId', '')
# print(pipeline_execution_id)