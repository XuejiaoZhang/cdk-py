import json
import hmac
import hashlib
import base64
import re
import boto3
import os

# Secret Secret Key used for verification
# TODO: read from secret store
SECRET = 'abcdefg' #??parameter store manually, how to persistently store? CDK gen, the same, showed in code?
branch_prefix = 'feature-branch-pipeline-'
# gen_pipeline = "FeatureBranchPipelineGenerator"
# branch_creation_pipeline = 'Create-Branch'
# branch_deletion_pipeline = 'Delete-Branch'
pipeline_template = os.getenv("pipeline_template")
# branch_creation_pipeline = os.getenv('branch_creation_pipeline')
# branch_deletion_pipeline = os.getenv('branch_deletion_pipeline')
# branch_creation_queue = os.getenv('branch_creation_queue')
# branch_deletion_queue = os.getenv('branch_deletion_queue')
#branch_creation_queue = "https://sqs.us-west-2.amazonaws.com/320185343352/pipelineGenerator-GitHub-Webhook-API-branchcreation210925B9-AfZJ8i5p6gYF"

# codebuild_client = boto3.client('codebuild')
ssm_client = boto3.client('ssm')
codepipeline_client = boto3.client('codepipeline')
# sqs_client = boto3.client('sqs')



def branch_name_check(branch_name, branch_prefix):
    if branch_name.startswith(branch_prefix):
        return True
    else:
        return False
    
def verify_webhook(data, hmac_header):
    caculation = hmac.new(SECRET.encode('utf-8'), data.encode('utf-8'), hashlib.sha256)
    received_hmac = re.sub(r'^sha256=', '', hmac_header)
    hexdigest = hmac.new(SECRET.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()
    # print(hexdigest, received_hmac)
    return hexdigest == received_hmac

def handler(event, context):
    # print('event', event)
    # print('Entering into the Lambda Function now.')
    # print('......................................')
    # print('The JSON body received from the API Gateway after passing through the mapping template is: ')
    # print(json.dumps(event))
    # print('The Header is: ')
    # print(event['headers'])
    # print('The Headers X-Hub-Signature-256 signature is: ')
    # print(event['headers']['X-Hub-Signature-256'])
    # print('Completed the printout of the passed in values.')

    rawbodydata = event.get('body', {})
    # print("body", body)
    msg = "Done"
    # rawbodydata = event['rawbody']
    body = json.loads(rawbodydata)
    hmac_header = event['headers']['X-Hub-Signature-256']
    
    verified = verify_webhook(rawbodydata, hmac_header)
    
    if not verified:
        msg = 'Did not pass HMAC validation!'
        print(msg)
        return {
            'statusCode': 401,
            'body': json.dumps(msg)
        }
    
    else:
        print('Passed HMAC validation!')

        ref = body.get('ref', '')
        ref_type = body.get('ref_type', '')
        description = dict_haskey(body, 'description')
        before = dict_haskey(body, 'before')
        after = dict_haskey(body, 'after')     
        # description = body.has_key('description')  
        # # TODO: deal with push?
        # before = body.has_key('before')  
        # after = body.has_key('after')  
        print('ref', ref)
        print('ref_type', ref_type)
        print('description', description)
        print('before', before)
        print('after', after)

        if ref_type == 'branch':
            if description:
                branch_name = ref
                if branch_name_check(branch_name, branch_prefix):
                    # print('Save branch name is parameter store::', branch_name)
                    # save_branch_name_in_ssm(branch_name)
                    # print('Send created branch name to SQS::', branch_name)
                    # send_branch_name_to_sqs(branch_creation_queue, branch_name)
                    print('Generate pipeline for branch:', branch_name)
                    create_feature_pipeline_from_template(branch_name, pipeline_template)
                    
                    msg = 'Done feature pipeline generation for: %s' % (branch_name)
                else:
                    msg = 'Branch name %s does not match the prefix %s' % (branch_name, branch_prefix)

            else:
                if branch_name_check(branch_name, branch_prefix):
                    # print('Delete branch name is parameter store::', branch_name)
                    # delete_branch_name_in_ssm(branch_name)
                    # print('Send deleted branch name to SQS::', branch_name)
                    # send_branch_name_to_sqs(branch_deletion_queue, branch_name)
                    print('Drop Pipeline for branch:', branch_name)
                    delete_feature_pipeline(branch_name)
                    
                    msg = "Done feature pipeline deletion for: %s" % (branch_name)
                else:
                    msg = 'Branch name %s does not match the prefix %s' % (branch_name, branch_prefix)

        # if not ref_type:
        #     if before and after:
        #         print('Push commit to branch:', ref.split("/")[-1])
        else:
            msg = 'Not one of the events: ["Branch creation", "Branch deletion"]'

    print(msg)
    return {
        'statusCode': 200,
        'body': json.dumps(msg)
    }
 


def dict_haskey(d, k):
    if k in d.keys():
        return True
    else:
        return False

# def save_branch_name_in_ssm(branch_name):
#     branch_chars = re.sub('[^0-9a-zA-Z]+', '', str(branch_name))

#     response = ssm_client.put_parameter(
#         Name = branch_chars,
#         Value = branch_name,
#         Type = 'String',
#         Overwrite = True
#     )

# def delete_branch_name_in_ssm(branch_name):
#     branch_chars = re.sub('[^0-9a-zA-Z]+', '', str(branch_name))

#     response = ssm_client.delete_parameter(
#         Name=branch_chars
#     )


def create_feature_pipeline_from_template(branch_name, pipeline_template)
    codepipeline_client = boto3.client('codepipeline')
    response = codepipeline_client.get_pipeline(
        name=pipeline_template,
    )

    pipeline_describe = response.get('pipeline', {})
    # print(pipeline_describe)

    pipeline_describe['name'] = branch_name + "_PipelineForTesting"
    pipeline_describe['stages'][0]['actions'][0]['configuration']['BranchName'] = branch_name

    response = codepipeline_client.create_pipeline(
            pipeline=pipeline_describe
    )
    #print(response)

def delete_feature_pipeline(branch_name):
    codepipeline_client = boto3.client('codepipeline')

    response = codepipeline_client.delete_pipeline(
        name=branch_name
    )
    print("delete_feature_pipeline", response.get('ResponseMetadata').get('HTTPStatusCode'))

# def send_branch_name_to_sqs(sqs_url, branch_name):
#     # Send message to SQS queue
#     response = sqs_client.send_message(
#         QueueUrl=sqs_url,
#         # DelaySeconds=10,
#         # MessageAttributes={
#         #     'Title': {
#         #         'DataType': 'String',
#         #         'StringValue': 'The Whistler'
#         #     },
#         #     'Author': {
#         #         'DataType': 'String',
#         #         'StringValue': 'John Grisham'
#         #     },
#         #     'WeeksOn': {
#         #         'DataType': 'Number',
#         #         'StringValue': '6'
#         #     }
#         # },
#         MessageBody=(branch_name)
#     )

#     print(response['MessageId'])