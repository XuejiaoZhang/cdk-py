import json
import hmac
import hashlib
import base64
import re
import boto3
import os

# TO Confirm: read from secret store, #??parameter store manually, how to persistently store? CDK gen, the same, showed in code?

# Gtihub Webhook Secret Key
SECRET = 'abcdefg' 
branch_prefix = 'feature-branch-pipeline-'  # TO Confirm, put into config?
feature_pipeline_suffix = "_FearurePipelineForTesting"
pipeline_template = os.getenv("pipeline_template") # get from config

ssm_client = boto3.client('ssm')
codepipeline_client = boto3.client('codepipeline')

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

    raw_body_data = event.get('body', {})
    body = json.loads(raw_body_data)
    hmac_header = event['headers']['X-Hub-Signature-256']
    msg = ""
    
    verified = verify_webhook(raw_body_data, hmac_header)
    
    if not verified:
        msg = 'Did not pass HMAC validation.'
        print(msg)
        return {
            'statusCode': 401,
            'body': json.dumps(msg)
        }
    
    else:
        print('Passed HMAC validation.')

        ref = body.get('ref', '')
        ref_type = body.get('ref_type', '')
        description = dict_haskey(body, 'description')
        print('ref: %s, ref_type: %s, description: %s', (ref, ref_type, description))

        if ref_type == 'branch':
            branch_name = ref
            if description:
                if branch_name_check(branch_name, branch_prefix):
                    pipeline_name = branch_name + feature_pipeline_suffix
                    print('Generating pipeline %s for branch: %s', (pipeline_name, branch_name))
                    create_feature_pipeline_from_template(branch_name, pipeline_template, pipeline_name)                  
                    msg = 'Done feature pipeline generation for: %s' % (branch_name)
                else:
                    msg = 'Branch name %s does not match the prefix %s' % (branch_name, branch_prefix)

            else:
                if branch_name_check(branch_name, branch_prefix):
                    pipeline_name = branch_name + feature_pipeline_suffix
                    print('Dropping Pipeline %s for branch: %s', (pipeline_name, branch_name))
                    delete_feature_pipeline(pipeline_name)
                    msg = "Done feature pipeline deletion for: %s" % (branch_name)
                else:
                    msg = 'Branch name %s does not match the prefix %s' % (branch_name, branch_prefix)

        else:
            msg = 'Not one of the following events: ["Branch creation", "Branch deletion"]'

    print(msg)
    return {
        'statusCode': 200,
        'body': json.dumps(msg)
    }
 

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

def dict_haskey(d, k):
    if k in d.keys():
        return True
    else:
        return False

def create_feature_pipeline_from_template(branch_name, pipeline_template, pipeline_name):
    codepipeline_client = boto3.client('codepipeline')
    response = codepipeline_client.get_pipeline(
        name=pipeline_template,
    )

    pipeline_describe = response.get('pipeline', {})
    # print(pipeline_describe)

    pipeline_describe['name'] = pipeline_name
    pipeline_describe['stages'][0]['actions'][0]['configuration']['BranchName'] = branch_name

    response = codepipeline_client.create_pipeline(
            pipeline=pipeline_describe
    )
    #print(response)

def delete_feature_pipeline(pipeline_name):
    codepipeline_client = boto3.client('codepipeline')
    response = codepipeline_client.delete_pipeline(
        name=pipeline_name
    )
    #print(response.get('ResponseMetadata').get('HTTPStatusCode'))
