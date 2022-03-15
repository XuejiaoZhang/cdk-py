from aws_cdk import (
    aws_iam,
    aws_lambda,
    aws_apigateway,
    # aws_s3 as s3,
    # aws_cognito,
    # aws_dynamodb,
    # aws_route53,
    # aws_ec2,
    # aws_certificatemanager,
    core,
    aws_logs,
    aws_ssm,
    aws_sqs
)

from aws_cdk.aws_lambda_python import PythonFunction

from aws_cdk.core import Duration
from aws_cdk.aws_apigateway import IntegrationResponse, MethodResponse
import os
import json

class GithubWebhookAPIStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        config: dict,
        # hosted_zone_id,
        # hosted_zone_name,
        # dynamo_table: aws_dynamodb.Table,
        **kwargs,
    ) -> None:
        """
        Creates the following infrastructure:
            API Gateway
            Lambda
            Lambda Role
            IAM Role
            # TODO pipline
        """
        super().__init__(scope, id, **kwargs)

        # bucket = s3.Bucket(self, "MyFirstBucket-webhook")
        # return

        # stage = config.get("stage") ##??????

        # Create an IAM Role for use with lambda
        handler_role = aws_iam.Role(
            self,
            id="generator-lambda-role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{id}-lambda-role",
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # TODO
        handler_role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "ssm:PutParameter",
                    "ssm:GetParameter",
                    "ssm:DeleteParameter",
                    "sqs:SendMessage",
                    "iam:PassRole",
                    "codepipeline:GetPipeline",
                    "codepipeline:UpdatePipeline",
                    "codepipeline:StartPipelineExecution",
                    "codestar-connections:PassConnection"
                ],
                resources=["*"],
            )
        )

        # TODO: existing policies in AWSLambdaBasicExecutionRole
        ## Creating the role and policy for the Kpireport
        # Creating the Policy Document for Managed Policy
        # AWSLambdaBasicExecution = aws_iam.PolicyDocument(
        #     statements=[
        #         aws_iam.PolicyStatement(
        #             actions=["logs:CreateLogGroup"],
        #             effect=aws_iam.Effect.ALLOW,
        #             resources=[f"arn:aws:logs:{self.region}:{self.account}:github-webhook-api-*"],
        #         ),
        #         aws_iam.PolicyStatement(
        #             actions=["logs:CreateLogStream", "logs:PutLogEvents"],
        #             effect=aws_iam.Effect.ALLOW,
        #             resources=[
        #                 f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/kpireport-handler:*"
        #             ],
        #         ),
        #     ]
        # )

        # Creating the Policy Document for Managed Policy
        # AWSLambdaVPCAccessExecutionRole = aws_iam.PolicyDocument(
        #     statements=[
        #         aws_iam.PolicyStatement(
        #             actions=[
        #                 "ec2:CreateNetworkInterface",
        #                 "ec2:DeleteNetworkInterface",
        #                 "ec2:DescribeNetworkInterfaces",
        #             ],
        #             effect=aws_iam.Effect.ALLOW,
        #             resources=["*"],
        #         )
        #     ]
        # )

        # Creating the Managed Policy for kpireport IAM Role
        # kpireportAWSLambdaBasicExecutionRole = aws_iam.ManagedPolicy(
        #     self,
        #     id="kpireport-awslambdabasicexecutionrole",
        #     managed_policy_name="kpireport-AWSLambdaBasicExecutionRole",
        #     document=AWSLambdaBasicExecution,
        # )

        # # Creating the Managed Policy for kpireport IAM Role
        # kpireportAWSLambdaVPCAccessExecutionRole = aws_iam.ManagedPolicy(
        #     self,
        #     id="kpireport-awslambdavpcaccessexecutionrole",
        #     managed_policy_name="kpireport-AWSLambdaVPCAccessExecutionRole",
        #     document=AWSLambdaVPCAccessExecutionRole,
        # )

        # Creating the IAM Role for kpireport lambda
        # kpireport_handler_role = aws_iam.Role(
        #     self,
        #     id="kpireport-lambda-role",
        #     assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
        #     role_name="kpireport-lambda-role",
        #     managed_policies=[
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "service-role/AWSElasticBeanstalkEnhancedHealth"
        #         ),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "AWSElasticBeanstalkWebTier"
        #         ),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "AWSElasticBeanstalkMulticontainerDocker"
        #         ),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "AWSElasticBeanstalkCustomPlatformforEC2Role"
        #         ),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy"
        #         ),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "service-role/AWSElasticBeanstalkRoleECS"
        #         ),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #             "AmazonSSMReadOnlyAccess"
        #         ),
        #         kpireportAWSLambdaBasicExecutionRole,
        #         kpireportAWSLambdaVPCAccessExecutionRole,
        #     ],
        # )

        # Creates authorizer using WS1 user pool
        # user_pool = aws_cognito.UserPool.from_user_pool_id(
        #     self, "auth-user-pool", "eu-west-1_qlG9jmccO"
        # )

        # authorizer = aws_apigateway.CognitoUserPoolsAuthorizer(
        #     self, id="api-authorizer", cognito_user_pools=[user_pool]
        # )

        branch_creation_queue = aws_sqs.Queue(self, "branch_creation")
        branch_deletion_queue = aws_sqs.Queue(self, "branch_deletion")
        self.branch_creation_queue = branch_creation_queue.queue_url
        self.branch_deletion_queue = branch_deletion_queue.queue_url

        # Create a lambda function that can act as a handler for API Gateway requests
        integration_handler_lambda_function = PythonFunction(
            self,
            id="githubWebhookApiHandler",
            function_name=f"{id}-handler",
            entry=os.path.join(
                os.getcwd(), "lambdas/github_webhook_api" # TODO
            ),
            index="github_webhook.py",
            role=handler_role,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            environment={"branch_creation_queue": self.branch_creation_queue, "branch_deletion_queue": self.branch_deletion_queue, "branch_creation_pipeline":config.get('branch_creation_pipeline', ''), "branch_deletion_pipeline":config.get('branch_deletion_pipeline', '')},
            memory_size=1024,
            timeout=Duration.minutes(1),
        )
        core.CfnOutput(
            self,
            f"{id}-github-webhook-api-handler-lambda-arn",
            value=integration_handler_lambda_function.function_arn,
            export_name=f"{id}-github-webhook-api-handler-lambda-arn",
        )
        
        # Use VPC created by WS1
        # internet_vpc = config.get("internet_vpc")
        # vpc_details = aws_ec2.Vpc.from_lookup(self, "VPC", vpc_name=internet_vpc)
        # subnet_id_list = vpc_details.private_subnets
        # subnet_details = aws_ec2.SubnetSelection(subnets = subnet_id_list)
            
        # # Create a lambda function for kpireport that can act as a handler for API Gateway requests
        # integration_handler_lambda_function_kpireport = PythonFunction(
        #     self,
        #     id="kpireportapihandler",
        #     function_name="kpireport-handler",
        #     entry=os.path.join(
        #         os.getcwd(), "caedge_sim_gen/infrastructure/lambdas/kpireport_api"
        #     ),
        #     index="kpireport.py",
        #     role=kpireport_handler_role,
        #     runtime=aws_lambda.Runtime.PYTHON_3_8,
        #     memory_size=1024,
        #     timeout=Duration.minutes(1),
        #     vpc=vpc_details,
        #     vpc_subnets=subnet_details
        # )
        # core.CfnOutput(
        #     self,
        #     "kpireport-handler-lambda-arn",
        #     value=integration_handler_lambda_function_kpireport.function_arn,
        #     export_name="kpireport-handler-lambda-arn",
        # )

        # # make the  table name available to lambda as CONFIGURATION_TEMPLATE_TABLE_NAME environment variable
        # integration_handler_lambda_function.add_environment(
        #     "CONFIGURATION_TEMPLATE_TABLE_NAME", dynamo_table.table_name
        # )

        # # grant permission to lambda to read from demo table
        # dynamo_table.grant_read_data(integration_handler_lambda_function)

        # Create a REST API using API Gateway
        prd_log_group = aws_logs.LogGroup(self, "Github-Webhook-API-Logs")
        deploy_options = aws_apigateway.StageOptions(
            access_log_destination=aws_apigateway.LogGroupLogDestination(prd_log_group),
            access_log_format=aws_apigateway.AccessLogFormat.json_with_standard_fields(
                caller=False,
                http_method=True,
                ip=True,
                protocol=True,
                request_time=True,
                resource_path=True,
                response_length=True,
                status=True,
                user=True,
            ),
            metrics_enabled=True,
        )
        github_webhook_api_gateway = aws_apigateway.RestApi(
            self,
            f"{id}-api-gateway",
            deploy_options=deploy_options,
            default_cors_preflight_options={
                "allow_origins": aws_apigateway.Cors.ALL_ORIGINS,
                "allow_methods": aws_apigateway.Cors.ALL_METHODS,
            },
        )
        core.CfnOutput(
            self,
            f"{id}-api-gateway-domain-arn",
            value=github_webhook_api_gateway.arn_for_execute_api(),
            export_name=f"{id}-api-gateway-domain-arn",
        )

        # Connect the hanlder lambda function to API Gateway
        lambda_integration = aws_apigateway.LambdaIntegration(
            integration_handler_lambda_function,
            proxy=True,
            # integration_responses=[IntegrationResponse(
            #     status_code="200"
            # )],
            # request_templates={
            #     # You can define a mapping that will build a payload for your integration, based
            #     #  on the integration parameters that you have specified
            #     # Check: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
            #     #"application/json": json.dumps({"action": "sayHello", "poll_id": "$util.escapeJavaScript($input.params('who'))"})
            #    # "application/json": json.dumps({"body" : "$input.json('$')","rawbody": "$util.escapeJavaScript($input.body)","headers": {"$header": "$util.escapeJavaScript($input.params().header.get($header))"},"method": "$context.httpMethod","params": {"$param": "$util.escapeJavaScript($input.params().path.get($param))"},"query": {"$queryParam": "$util.escapeJavaScript($input.params().querystring.get($queryParam))"}})
            #     "application/json": "{ "statusCode": 200 }"
            #   # "application/json": json.dumps("{ "body" : $input.json('$'), "rawbody": "$util.escapeJavaScript($input.body)", "headers": { #foreach($header in $input.params().header.keySet()) "$header": "$util.escapeJavaScript($input.params().header.get($header))" #if($foreach.hasNext),#end #end } }")
            # },
            # request_templates={
            #     # You can define a mapping that will build a payload for your integration, based
            #     #  on the integration parameters that you have specified
            #     # Check: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
            #     "application/json": json.dumps({"body" : $input.json('$'),"rawbody": "$util.escapeJavaScript($input.body)","headers": {"$header": "$util.escapeJavaScript($input.params().header.get($header))"},"method": "$context.httpMethod","params": {"$param": "$util.escapeJavaScript($input.params().path.get($param))"},"query": {"$queryParam": "$util.escapeJavaScript($input.params().querystring.get($queryParam))"}})
            # },
        )

        # Connect the kpireport hanlder lambda function to API Gateway
        # lambda_integration_kpiReport = aws_apigateway.LambdaIntegration(
        #     integration_handler_lambda_function_kpireport
        # )

        # add /dags endpoint
        webhooks_resource = github_webhook_api_gateway.root.add_resource("webhook")

        webhooks_resource.add_method(
            "POST",
            lambda_integration,
            # method_responses=[MethodResponse(status_code="200")],

        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        )




        # dags_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # add /dags/{dagId} endpoint
        # dagid_resource = dags_resource.add_resource("{dagId}")
        # dagid_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # add /dags/{dagId}/simulationConfigurationTemplates endpoint
        # simulationConfigurationTemplates_resource = dagid_resource.add_resource(
        #     "simulationConfigurationTemplates"
        # )
        # simulationConfigurationTemplates_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # add /dags/{dagId}/kpireport endpoint
        # simulationConfigurationTemplates_resource = dagid_resource.add_resource(
        #     "kpireport"
        # )
        # simulationConfigurationTemplates_resource.add_method(
        #     "GET",
        #     lambda_integration_kpiReport,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # add /dags/{dagId}/sensors endpoint
        # sensors_resource = dagid_resource.add_resource("sensors")
        # sensors_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # add /dags/{dagId}/dagRuns POST endpoint
        # dag_runs_resource = dagid_resource.add_resource("dagRuns")
        # dag_runs_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )
        # webhooks_resource.add_method(
        #     "POST",
        #     lambda_integration,
        # #     authorizer=authorizer,
        # #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # add /dags/{dagId}/dagRuns/{dagRunId} endpoint
        # dagRunId_resource = dag_runs_resource.add_resource("{dagRunId}")
        # taskInstance_resource = dagRunId_resource.add_resource("taskInstances")
        # taskInstance_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # add /dags/{dagId}/dagRuns/{dagRunId}/{taskId}/logs/{id} endpoint
        # taskId_resource = taskInstance_resource.add_resource("{taskId}")
        # logs_resource = taskId_resource.add_resource("logs")
        # id_resource = logs_resource.add_resource("{id}")
        # id_resource.add_method(
        #     "GET",
        #     lambda_integration,
        #     authorizer=authorizer,
        #     authorization_type=aws_apigateway.AuthorizationType.COGNITO,
        # )

        # # get the hosted zone which was created by the route53 stack
        # hosted_zone = aws_route53.HostedZone.from_hosted_zone_attributes(
        #     self,
        #     f"{id}-{stage}-simulation-api-hosted-zone",
        #     zone_name=hosted_zone_name,
        #     hosted_zone_id=hosted_zone_id,
        # )

        # # Create a certificate using the certificate manager
        # api_domain_name = f"api.{hosted_zone_name}"
        # certificate = aws_certificatemanager.Certificate(
        #     self,
        #     f"{id}-{stage}-api-domain-certificate",
        #     domain_name=api_domain_name,
        #     subject_alternative_names=[],
        #     validation=aws_certificatemanager.CertificateValidation.from_dns(
        #         hosted_zone
        #     ),
        # )

        # # Create a custom domain:
        # api_gateway_domain_name = aws_apigateway.DomainName(
        #     self,
        #     f"{id}-{stage}--api-domain-name",
        #     mapping=simulation_api_gateway,
        #     domain_name=api_domain_name,
        #     certificate=certificate,
        # )
        # core.CfnOutput(
        #     self,
        #     f"{id}-{stage}-api-domain-name",
        #     export_name=f"{id}-{stage}-api-domain-name",
        #     value=f"https://{api_gateway_domain_name.domain_name}",
        # )

        # # # Finally, add a CName record in the hosted zone with a value of the new custom domain that was created above:
        # aws_route53.CnameRecord(
        #     self,
        #     f"{id}-{stage}-api-cname-record",
        #     zone=hosted_zone,
        #     domain_name=api_gateway_domain_name.domain_name_alias_domain_name,
        #     record_name=f"{api_domain_name}.",
        # )  # The name of the domain. This must be a fully-specified domain, ending with a period as the last label indication.

        # # Associate the custom domain that we created with the APIGateway using BasePathMapping:
        # # aws_apigateway.BasePathMapping(self, f"{id}-{stage}-simulation-api-basepath-mapping", domain_name= api_gateway_domain_name, rest_api=simulation_api_gateway)
