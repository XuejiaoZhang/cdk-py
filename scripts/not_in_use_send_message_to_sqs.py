import boto3

sqs_client = boto3.client('sqs')

def send_branch_name_to_sqs(sqs_url, branch_name):
	# Send message to SQS queue
	response = sqs_client.send_message(
	    QueueUrl=sqs_url,
	    # DelaySeconds=10,
	    # MessageAttributes={
	    #     'Title': {
	    #         'DataType': 'String',
	    #         'StringValue': 'The Whistler'
	    #     },
	    #     'Author': {
	    #         'DataType': 'String',
	    #         'StringValue': 'John Grisham'
	    #     },
	    #     'WeeksOn': {
	    #         'DataType': 'Number',
	    #         'StringValue': '6'
	    #     }
	    # },
	    MessageBody=(branch_name)
	)

	print(response['MessageId'])

branch_creation_queue = os.getenv('branch_creation_queue')
branch_deletion_queue = os.getenv('branch_deletion_queue')
branch_creation_queue = "https://sqs.us-west-2.amazonaws.com/320185343352/pipelineGenerator-GitHub-Webhook-API-branchcreation210925B9-AfZJ8i5p6gYF"
branch_name = "generator2"
send_branch_name_to_sqs(branch_creation_queue, branch_name)