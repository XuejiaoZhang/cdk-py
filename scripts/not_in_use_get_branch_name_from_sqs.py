import boto3
import os

sqs_client = boto3.client("sqs")

# CODEBUILD_INITIATOR=codepipeline/featurebranchpipelinewebhookReadyForFeatureBranchPipeline


def branch_name_check(branch_name, branch_prefix):
    if branch_name.startswith(branch_prefix):
        return True
    else:
        return False


# branch_name = 'generator2'
branch_prefix = "feature-branch-pipeline-"

sqs_url = os.getenv("SQS_URL")
if sqs_url:
    # Receive message from SQS queue
    response = sqs_client.receive_message(
        QueueUrl=sqs_url,
        # AttributeNames=[
        #     'SentTimestamp'
        # ],
        # MaxNumberOfMessages=1,
        # MessageAttributeNames=[
        #     'All'
        # ],
        # VisibilityTimeout=0,
        # WaitTimeSeconds=0
    )
    # print(response)
    if response.get("Messages", []):
        message = response["Messages"][0]
        receipt_handle = message["ReceiptHandle"]

        # Delete received message from queue
        sqs_client.delete_message(QueueUrl=sqs_url, ReceiptHandle=receipt_handle)
        # print('Received and deleted message: %s' % message)
        branch_name = message.get("Body", "")
        # print(branch_name)

        if branch_name_check(branch_name, branch_prefix):
            print(branch_name)
