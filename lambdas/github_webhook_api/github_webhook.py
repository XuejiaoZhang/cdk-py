import json
import hmac
import hashlib
import base64
import re
import boto3
import os

# Secret Secret Key used for verification
# TODO: read from secret store
SECRET = 'abcdefg' #??parameter store? CDK gen?
branch_prefox = 'feature-branch-pipeline-'
# gen_pipeline = "FeatureBranchPipelineGenerator"
# branch_creation_pipeline = 'Create-Branch'
# branch_deletion_pipeline = 'Delete-Branch'

branch_creation_pipeline = os.getenv('branch_creation_pipeline')
branch_deletion_pipeline = os.getenv('branch_deletion_pipeline')
branch_creation_queue = os.getenv('branch_creation_queue')
branch_deletion_queue = os.getenv('branch_deletion_queue')
#branch_creation_queue = "https://sqs.us-west-2.amazonaws.com/320185343352/pipelineGenerator-GitHub-Webhook-API-branchcreation210925B9-AfZJ8i5p6gYF"

# codebuild_client = boto3.client('codebuild')
ssm_client = boto3.client('ssm')
codepipeline_client = boto3.client('codepipeline')
sqs_client = boto3.client('sqs')



def branch_name_check(branch_name, branch_prefox):
    if branch_name.startswith(branch_prefox):
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
    print('Entering into the Lambda Function now.')
    print('......................................')
    print('The JSON body received from the API Gateway after passing through the mapping template is: ')
    print(json.dumps(event))
    # print('The RAW body received from the API Gateway after passing through the mapping template is: ')
    # print(event['rawbody'])
    print('The Header is: ')
    print(event['headers'])
    print('The Headers X-Hub-Signature-256 signature is: ')
    print(event['headers']['X-Hub-Signature-256'])
    print('Completed the printout of the passed in values.')

    rawbodydata = event.get('body', {})
    # print("body", body)
    msg = "Done"
    # rawbodydata = event['rawbody']
    body = json.loads(rawbodydata)
    hmac_header = event['headers']['X-Hub-Signature-256']
    
    verified = verify_webhook(rawbodydata, hmac_header)
    
    if not verified:
        print('Did not pass HMAC validation!')
        return {
        'statusCode': 401,
        'body': json.dumps('Did not pass HMAC validation!')
        }
    
    
    if verified:
        print('Passed HMAC validation!')
        #
        # YOUR APP LOGIC GOES HERE!!!!
        #

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
                if not branch_name_check(branch_name, branch_prefox): # TODO not
                    print('Save branch name is parameter store::', branch_name)
                    save_branch_name_in_ssm(branch_name)
                    # print('Calling CodeBuild for branch:', branch_name)
                    # codebuild_run(branch_name)
                    print('Send created branch name to SQS::', branch_name)
                    send_branch_name_to_sqs(branch_creation_queue, branch_name)
                    print('Generate Pipeline for branch:', branch_name)
                    exec_code_pipeline(branch_name, branch_creation_pipeline)
                    
                    msg = "Done feature pipeline generation for: "+branch_name
                    
                    return {
                        'statusCode': 200,
                        'body': json.dumps(msg)
                    }
                else:
                    msg = 'Branch name %s does not match the prefix %s' % (branch_name, branch_prefox)
                    print(msg)
                    return
                    # return {
                    #     'statusCode': 200,
                    #     'body': json.dumps(msg)
                    # }                   
            
            else:
                # print('Deleted branch:', ref)
                if not branch_name_check(branch_name, branch_prefox): # TODO not
                    print('Delete branch name is parameter store::', branch_name)
                    delete_branch_name_in_ssm(branch_name)
                    # print('Calling CodeBuild for branch:', branch_name)
                    # codebuild_run(branch_name)
                    print('Send deleted branch name to SQS::', branch_name)
                    send_branch_name_to_sqs(branch_deletion_queue, branch_name)
                    print('Drop Pipeline for branch:', branch_name)
                    exec_code_pipeline(branch_name, branch_deletion_pipeline)
                    
                    msg = "Done feature pipeline deletion for: "+branch_name
                    
                    return {
                        'statusCode': 200,
                        'body': json.dumps(msg)
                    }
                else:
                    msg = 'Branch name %s does not match the prefix %s' % (branch_name, branch_prefox)
                    print(msg)
                    return
                    # return {
                    #     'statusCode': 200,
                    #     'body': json.dumps(msg)
                    # }    


        # if not ref_type:
        #     if before and after:
        #         print('Push commit to branch:', ref.split("/")[-1])
        else:
            print('Not one of the events: ["Branch creation", "Branch deletion", "Push to the tracking branchs"]')


        
        # branch_name = "webhook-test"
        # client = boto3.client('codebuild')
        # response = client.start_build(
        #     projectName='lambda-codebuild',
        #     sourceVersion=branch_name,
        #     environmentVariablesOverride=[
        #         {
        #             'name': 'BRANCH',
        #             'value': branch_name,
        #             'type': 'PLAINTEXT'
        #         },
        #     ],
        # )        
        
        return
        # return {
        # 'statusCode': 200,
        # 'body': json.dumps(msg)
        # }
        
    
    




###################
# import json

# import logging
# import hmac
# import hashlib
# import re
# import ast
# from urllib.parse import unquote
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

def dict_haskey(d, k):
    if k in d.keys():
        return True
    else:
        return False


# def codebuild_run(branch_name):
#     response = codebuild_client.start_build(
#         projectName='lambda-codebuild',
#         sourceVersion=branch_name,
#         environmentVariablesOverride=[
#             {
#                 'name': 'BRANCH',
#                 'value': branch_name,
#                 'type': 'PLAINTEXT'
#             },
#         ],
#     )


def save_branch_name_in_ssm(branch_name):
    branch_chars = re.sub('[^0-9a-zA-Z]+', '', str(branch_name))

    response = ssm_client.put_parameter(
        Name = branch_chars,
        Value = branch_name,
        Type = 'String',
        Overwrite = True
    )

#TODO: delete parameter

def delete_branch_name_in_ssm(branch_name):
    branch_chars = re.sub('[^0-9a-zA-Z]+', '', str(branch_name))

    response = ssm_client.delete_parameter(
        Name=branch_chars
    )




def exec_code_pipeline(branch_name, branch_operation_pipeline):
    response = codepipeline_client.get_pipeline(
        name=branch_creation_pipeline,
        # version=123
    )

    pipeline_describe = response.get('pipeline', {})

    # branch_name = 'dev'
    pipeline_describe['stages'][0]['actions'][0]['configuration']['BranchName'] = branch_name
    pipeline_describe['version'] = pipeline_describe.get('version') + 1

    # print(pipeline)
    # print('--------------------------')
    response = codepipeline_client.update_pipeline(
        pipeline=pipeline_describe
    )
    # print(response)

    response = codepipeline_client.start_pipeline_execution(
        # name=gen_pipeline,
        name=branch_operation_pipeline
        # clientRequestToken='string'
    )

    # print(response)
    pipeline_execution_id = response.get('pipelineExecutionId', '')
    # print(pipeline_execution_id)



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