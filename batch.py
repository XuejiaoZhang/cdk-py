import boto3
client = boto3.client('batch')

response = client.list_jobs(
    jobQueue='test',
    # arrayJobId='string',
    # multiNodeJobId='string',
    # jobStatus='SUBMITTED'|'PENDING'|'RUNNABLE'|'STARTING'|'RUNNING'|'SUCCEEDED'|'FAILED',
    # maxResults=123,
    # nextToken='string',
    # filters=[
    #     {
    #         'name': 'string',
    #         'values': [
    #             'string',
    #         ]
    #     },
    # ]
)
print(response)

# 'jobSummaryList': []