# from __future__ import print_function
# from pprint import pprint
import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection

import urllib
import json

# s3 = boto3.client('s3')

# print('Loading function')

index_doc = {
    "dataRecord" : {
        "properties" : {
          "createdDate" : {
            "type" : "date",
            "format" : "dateOptionalTime"
          },
          "objectKey" : {
            "type" : "string"
          },
          "content_type" : {
            "type" : "string"
          },
          "content_length" : {
            "type" : "long"
          },
          "metadata" : {
            "type" : "string"
          }
        }
      },
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
      }
    }

index = 'metadata-store'

def connect_es(es_endpoint):
    print (f'Connecting to the ES Endpoint {es_endpoint}')
    try:
        es_client = Elasticsearch(
            hosts=[{'host': es_endpoint, 'port': 443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)
        return es_client
    except Exception as E:
        print(f"Unable to connect to {es_endpoint}")
        print(E)
        exit(3)

def create_index(es_client):
    try:
        res = es_client.indices.exists(index)
        if res is False:
            es_client.indices.create(index, body=index_doc)
        return 1
    except Exception as E:
            print(f"Unable to Create Index {index}")
            print(E)
            exit(4)

# def index_doc_element(es_client,key,response):
#     try:
#     	indexObjectKey = key
#     	indexcreatedDate = response['LastModified']
#     	indexcontent_length = response['ContentLength']
#     	indexcontent_type = response['ContentType']
#     	indexmetadata = json.dumps(response['Metadata'])
#         # doc_type='images'
#     	retval = esClient.index(index=index, doc_type='images', body={
#         		'createdDate': indexcreatedDate,
#         		'objectKey': indexObjectKey,
#         		'content_type': indexcontent_type,
#         		'content_length': indexcontent_length,
#         		'metadata': indexmetadata
#     	})
#     except Exception as E:
#     	print("Document not indexed")
#     	print("Error: ",E)
#     	exit(5)	
	  


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    es_endpoint = "https://vpc-batch-event-g344erzfcdnnhcb2gxotnhn2pe.us-west-2.es.amazonaws.com"
    es_client = connect_es(es_endpoint)
    create_index(es_client)
    print("end.")
    # index_doc_element(es_client,"key","response")

    # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    # try:
    #     response = s3.get_object(Bucket=bucket, Key=key)
	# indexDocElement(esClient,key,response)
    #     return response['ContentType']
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e
