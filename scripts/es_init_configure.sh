#!/bin/bash

# Check whether Pylint score passes the threshold

set -e
echo -e "Starting dashboard generation"

# TODO: Read variables from Parameter Store 
DOMAIN_ADMIN_UNAME="esadmin"
DOMAIN_ADMIN_PW='g6o7KdS3FO7YMpS8!'
DOMAIN_ENDPOINT="vpc-aws-batch-event-es-7bdgb3ew3cev4djzq5ekrji4me.us-west-2.es.amazonaws.com"
LAMBDA_CW_LOGS_ROLE_ARN="arn:aws:lambda:us-west-2:320185343352:function:batch-job-ui-handler"

# There was a bug in elastic which can't store the origin url when string field is converted to URL type and it is exported to another domain. Workaround is to replace it manually.
# https://github.com/elastic/kibana/issues/63924
# InstanceIP=`curl ifconfig.me`
# sed -i 's/CHANGE_ORIGIN_URL/'$InstanceIP'/g' /tmp/assets/export_opensearch_dashboards_V1_0.ndjson

# Create backend role mapping for lambda role
# curl -XPATCH -u $DOMAIN_ADMIN_UNAME:$DOMAIN_ADMIN_PW "https://$DOMAIN_ENDPOINT/_opendistro/_security/api/rolesmapping/all_access" -H 'Content-Type: application/json' -d '[ {"op":"add","path":"/backend_roles","value":[ "$LAMBDA_CW_LOGS_ROLE_ARN"]}]'
curl -XPATCH -u $DOMAIN_ADMIN_UNAME:$DOMAIN_ADMIN_PW "https://$DOMAIN_ENDPOINT/_opendistro/_security/api/rolesmapping/all_access" -H 'Content-Type: application/json' -d '[ {"op":"add","path":"/backend_roles","value":[ "'$LAMBDA_CW_LOGS_ROLE_ARN'"]}]'

# TODO: not automte this
# Create a readonly user
curl -XPUT -u $DOMAIN_ADMIN_UNAME:$DOMAIN_ADMIN_PW "https://$DOMAIN_ENDPOINT/_opendistro/_security/api/internalusers/readall_user" -H 'Content-Type: application/json' -d '{ "password": "readonly123_PWD", "opendistro_security_roles": ["readall"]}'
## Missing role...; another request: create role mapping
#curl -XPUT -u $DOMAIN_ADMIN_UNAME:$DOMAIN_ADMIN_PW "https://$DOMAIN_ENDPOINT/_opendistro/_security/api/rolesmapping/readall" -H 'Content-Type: application/json' -d '[ {"op":"add","path":"/user","value":[ "readall"]}]'


# Create a all_acess user
curl -XPUT -u $DOMAIN_ADMIN_UNAME:$DOMAIN_ADMIN_PW "https://$DOMAIN_ENDPOINT/_opendistro/_security/api/internalusers/all_access_user" -H 'Content-Type: application/json' -d '{ "password": "all_access123_PWD", "opendistro_security_roles": ["all_access"]}'

# Create index Pattern
# TODO: fail to create if index matching not exist, not automate this?
curl -XPOST -u $DOMAIN_ADMIN_UNAME:$DOMAIN_ADMIN_PW "https://$DOMAIN_ENDPOINT/api/index_patterns/index_pattern" -H 'Content-Type: application/json' -d '{"aws-batch-job-2022-04-1*": {"timeFieldName": "job_time"}}'


# # Generate auth for Default Dashboards
# curl -XPOST 'https://DOMAIN_ENDPOINT/_dashboards/auth/login' -H "osd-xsrf: true" -H "content-type:application/json" -d '{"username":"DOMAIN_ADMIN_UNAME", "password" : "DOMAIN_ADMIN_PW"} ' -c auth.txt

# # Load Default Dashboard
# curl -XPOST 'https://DOMAIN_ENDPOINT/_dashboards/api/saved_objects/_import' -H "osd-xsrf:true" -b auth.txt --form file=@export_opensearch_dashboards_V1_0.ndjson


# ################# Index Templates and ISM ###################
# # Create ISM ploicy to delete data after 366 days
# curl -s -XPUT -u DOMAIN_ADMIN_UNAME:DOMAIN_ADMIN_PW "https://DOMAIN_ENDPOINT/_opendistro/_ism/policies/domains" -H 'Content-Type: application/json' -d'{"policy":{"ism_template":{"index_patterns" : ["domains-*", "cwl-*"]},"policy_id":"domains","description":"hot-delete workflow","last_updated_time":1612206385815,"schema_version":1,"error_notification":null,"default_state":"hot","states":[{"name":"hot","actions":[],"transitions":[{"state_name":"delete","conditions":{"min_index_age":"366d"}}]},{"name":"delete","actions":[{"delete":{}}],"transitions":[]}]}}'

# # Create Template
# curl -s -XPUT -u DOMAIN_ADMIN_UNAME:DOMAIN_ADMIN_PW "https://DOMAIN_ENDPOINT/_template/domains" -H 'Content-Type: application/json' -d'{"index_patterns":["domains-*", "cwl-*"],"settings":{"number_of_shards":1,"number_of_replicas":1}}'
