import boto3
import time
import os
import requests
from requests_aws4auth import AWS4Auth

region = 'us-west-2'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://vpc-batch-event-g344erzfcdnnhcb2gxotnhn2pe.us-west-2.es.amazonaws.com'
host = os.getenv("ES_DOMAIN_ENDPOINT")
estype = '_doc'
headers = { "Content-Type": "application/json" }

def handler(event, context):
    print(event)
    account = event.get('account', '')
    region = event.get('region', '')
    job_time = event.get('time', '')
    detail = event.get('detail', {})
    status = detail.get('status', '')
    job_name = detail.get('jobName', '')
    job_id = detail.get('jobId', '')
    job_queue = detail.get('jobQueue', '')
    attempts = detail.get('attempts', {})
    attempts_run = []
    for attempt in attempts:
        attempt_run = {}
        attempt_run["stopped_at"] = attempt.get("stoppedAt", "")
        attempt_run["reason"] = attempt.get("container", {}).get("reason", "")
        # attempt_run["exitCode"] = attempt.get("container", {}).get("exitCode", "")
        attempt_run["logStreamName"] = attempt.get("container", {}).get("logStreamName", "")
        attempts_run.append(attempt_run)
    job_definition = detail.get("jobDefinition", "")
    
    # status_reason = detail.get('statusReason', {})
    # started_at = detail.get('startedAt', )
    # stopped_at = detail.get('stoppedAt', )

    document = {"account": account, "region": region, "job_time": job_time, "job_name": job_name, "status": status, "job_id": job_id, "job_queue": job_queue, "attempts_run": attempts_run, "job_definition": job_definition}
#    document = {"account": account, "region": region, "timestamp": time.time(), "job_time": job_time, "job_name": job_name, "status": status, "job_id": job_id, "job_queue": job_queue, "attempts_run": attempts_run, "job_definition": job_definition}

    print(document)

    time_date = job_time.split("T")[0]
    index = f'aws-batch-job-{time_date}' 
    url = host + '/' + index + '/' + estype

    r = requests.post(url, auth=awsauth, json=document, headers=headers)
    print(r.text)