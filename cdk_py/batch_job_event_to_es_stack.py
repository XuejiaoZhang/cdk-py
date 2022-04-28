from aws_cdk import (
    aws_iam,
    aws_lambda,
    aws_ec2 as ec2,
    aws_elasticsearch as es,
    aws_events as events,
    aws_events_targets as targets,
    core,
    aws_s3,
    aws_dynamodb,
    aws_kms
)

from aws_cdk.aws_lambda_python import PythonFunction
from aws_cdk.aws_lambda import Function

from aws_cdk.core import Duration
# from aws_cdk.aws_apigateway import IntegrationResponse, MethodResponse
import os
# import json
import random
import string


class BatchJobEventToESStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        # pipeline_template: str,
        config: dict,
        **kwargs,
    ) -> None:
        """
        Creates the following infrastructure:
            EventBridge Rule
            Lambda
            Openserch
        """
        super().__init__(scope, id, **kwargs)


        key = aws_kms.Key(self, "MyKey",
            pending_window=Duration.days(10)
        )

        # 01) S3 - KMS
        # from KMS/KMS_MANAGED to S3_MANAGED

        # encryption (Optional[BucketEncryption]) – The kind of server-side encryption to apply to this bucket. 
            # If you choose KMS, you can specify a KMS key via encryptionKey. 
            # If encryption key is not specified, a key will automatically be created. 
            # Default: - Kms if encryptionKey is specified, or Unencrypted otherwise.

        # encryption_key (Optional[IKey]) – External KMS key to use for bucket encryption. 
            # The ‘encryption’ property must be either not specified or set to “Kms”. 
            # An error will be emitted if encryption is set to “Unencrypted” or “Managed”.
            # Default: - If encryption is set to “Kms” and this property is undefined, a new KMS key will be created and associated with this bucket.
        # aws_s3.Bucket(self, "encryption_at_rest_s3_kms",
        #     encryption=aws_s3.BucketEncryption.KMS,
        #     encryption_key=key
        #     )
        # # 02) Dynamodb - KMS
        # # from CUSTOMER_MANAGED/AWS_MANAGED to DEFAULT
        # # encryption_key  – This property can only be set if encryption is set to TableEncryption.CUSTOMER_MANAGED
        # aws_dynamodb.Table(self, "encryption_at_rest_db_kms",
        #     encryption=aws_dynamodb.TableEncryption.CUSTOMER_MANAGED,
        #     partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
        #     encryption_key=key
        #     )

        # # -----------
        # aws_s3.Bucket(self, "encryption_at_rest_s3_kms",
        #     encryption=aws_s3.BucketEncryption.KMS_MANAGED,
        #     )

        # aws_dynamodb.Table(self, "encryption_at_rest_db_kms",
        #     partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
        #     encryption=aws_dynamodb.TableEncryption.AWS_MANAGED,
        #     )

        # # -----------

        aws_s3.Bucket(self, "encryption_at_rest_s3_kms",
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
            )

        aws_dynamodb.Table(self, "encryption_at_rest_db_kms",
            partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
            encryption=aws_dynamodb.TableEncryption.DEFAULT,
            )


        # 1) create OpeanSearch Domain

        # Use VPC created by WS1
        #internet_vpc = config.get("internet_vpc") #TODO
        internet_vpc = "vpc-404ee838"
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=internet_vpc)
        # subnet_id_list = vpc.private_subnets
        # subnet_details = ec2.SubnetSelection(subnets = subnet_id_list)

        vpc_private = ec2.Vpc.from_vpc_attributes(self, "VPC-private", vpc_id=internet_vpc, private_subnet_ids=["subnet-77390a0e", "subnet-60fba62b"], availability_zones=["us-west-2a", "us-west-2b"])

        # Amazon ES Service domain
        lambda_es_sg = ec2.SecurityGroup(self, 'lambda-es-sg', 
                                        vpc=vpc,
                                        allow_all_outbound=True,
                                        security_group_name='lambda-es-sg')
        # lambda_es_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        lambda_es_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))
        # lambda_es_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        # lambda_es_sg.add_ingress_rule(lambda_es_sg, ec2.Port.all_tcp())

        # subnet_private = ec2.PrivateSubnet.from_subnet_id(
        #     self,
        #     "subnet_pri",
        #     subnet_id="subnet-77390a0e"
        # )

        # security_group = ec2.SecurityGroup.from_lookup(
        #   self,
        #   "SG",
        #   security_group_id="sg-25c4966d"
        # )


        # ES and Dashboards specific constants 
        DOMAIN_NAME = 'aws-batch-event-es'
        DOMAIN_ADMIN_UNAME='esadmin'
        DOMAIN_ADMIN_PW=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(13)) + random.choice(string.ascii_lowercase) + random.choice(string.ascii_uppercase) + random.choice(string.digits) + "!" 
        DOMAIN_DATA_NODE_INSTANCE_TYPE='m6g.large.elasticsearch'
        DOMAIN_DATA_NODE_INSTANCE_COUNT=2
        DOMAIN_INSTANCE_VOLUME_SIZE=10
        DOMAIN_AZ_COUNT=2
        ## By default without dedicated master node, to have dedicated master node in stack do change the number of nodes and type (if needed)
        ## Maximum Master Instance count supported by service is 5, so either have 3 or 5 dedicated node for master
        DOMAIN_MASTER_NODE_INSTANCE_TYPE='c6g.large.elasticsearch'
        DOMAIN_MASTER_NODE_INSTANCE_COUNT=0

        ## To enable UW, please make master node count as 3 or 5, and UW node count as minimum 2
        ## Also change data node to be non T2/T3 as UW does not support T2/T3 as data nodes
        DOMAIN_UW_NODE_INSTANCE_TYPE='ultrawarm1.medium.elasticsearch'
        DOMAIN_UW_NODE_INSTANCE_COUNT=0

        # VPC
        # vpc = ec2.Vpc(self, "Monitoring VPC", max_azs=3)


        domain = es.Domain(self, 'es-service-monitor',  # TODO: modify name: batch-job-history-domain
            version=es.ElasticsearchVersion.V7_10, # Upgrade when CDK upgrades
            domain_name=DOMAIN_NAME,
            removal_policy=core.RemovalPolicy.DESTROY,
            capacity=es.CapacityConfig(
                data_node_instance_type=DOMAIN_DATA_NODE_INSTANCE_TYPE,
                data_nodes=DOMAIN_DATA_NODE_INSTANCE_COUNT,
                master_node_instance_type=DOMAIN_MASTER_NODE_INSTANCE_TYPE,
                master_nodes=DOMAIN_MASTER_NODE_INSTANCE_COUNT,
                warm_instance_type=DOMAIN_UW_NODE_INSTANCE_TYPE,
                warm_nodes=DOMAIN_UW_NODE_INSTANCE_COUNT
            ),
            ebs=es.EbsOptions(
                enabled=True,
                volume_size=DOMAIN_INSTANCE_VOLUME_SIZE,
                volume_type=ec2.EbsDeviceVolumeType.GP2
            ),
            vpc=vpc_private,
            # vpc=vpc,
            # vpc_subnets=[subnet_details],
            # vpc_subnets=[ec2.SubnetType.PRIVATE],
            security_groups=[lambda_es_sg],
            zone_awareness=es.ZoneAwarenessConfig(
                enabled=True,
                availability_zone_count=DOMAIN_AZ_COUNT
            ),
            enforce_https=True,
            node_to_node_encryption=True,
            encryption_at_rest={
                "enabled": True
            },
            use_unsigned_basic_auth=True,
            fine_grained_access_control={
                "master_user_name": DOMAIN_ADMIN_UNAME,
                "master_user_password": core.SecretValue.plain_text(DOMAIN_ADMIN_PW)
            }
        )

        core.CfnOutput(self, "MasterUser",
                        value=DOMAIN_ADMIN_UNAME,
                        description="Master User Name for Amazon es Service")

        core.CfnOutput(self, "MasterPW",
                        value=DOMAIN_ADMIN_PW,
                        description="Master User Password for Amazon es Service")


        # 2) create lambda function
        # Create an IAM Role for Lambda
        handler_role = aws_iam.Role(
            self,
            id="batch-job-event-to-es-lambda-role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{id}-lambda-role",
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        handler_role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "ec2:CreateNetworkInterface",
                    "ec2:DetachNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "ec2:AttachNetworkInterface"
                    # "iam:PassRole",
                    # "es:*"
                ],
                resources=["*"],
            )
        )

        batch_event_handler_lambda_function = PythonFunction(
            self,
            id="batchJobEventHandler",
            function_name=f"{id}-handler",
            entry=os.path.join(os.getcwd(), "lambdas/batch_job_ui"),  # TODO
            index="batch_job_event_handler.py",
            role=handler_role,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            memory_size=1024,
            timeout=Duration.minutes(1),
            vpc=vpc_private
            # vpc=vpc,
            # vpc_subnets=subnet_details,
            # security_groups=[security_group]
        )


        # TODO: install dependencies
        # batch_event_handler_lambda_function = Function(
        #     self,
        #     id="batchJobEventHandler",
        #     function_name=f"{id}-handler",
        #     # entry=os.path.join(os.getcwd(), "lambdas/batch_job_ui"),  # TODO
        #     handler="batch_job_event_handler.handler",
        #     # code=lambda_.Code.from_asset(os.path.join(__dirname, "lambdas/batch_job_ui")),
        #     code=aws_lambda.Code.from_asset(os.path.join(os.getcwd(), "lambdas/batch_job_ui")),
        #     role=handler_role,
        #     runtime=aws_lambda.Runtime.PYTHON_3_8,
        #     memory_size=1024,
        #     timeout=Duration.minutes(1),
        #     vpc=vpc_private
        #     # vpc=vpc,
        #     # vpc_subnets=subnet_details,
        #     # security_groups=[security_group]
        # )
        core.CfnOutput(
            self,
            f"{id}-batch-job-event-handler-lambda-arn",
            value=batch_event_handler_lambda_function.function_arn,
            export_name=f"{id}-batch-job-event-handler-lambda-arn",
        )

        # TODO: SG to ES
        # batch_event_handler_lambda_function.security_group.
        # lambda_es_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        # lambda_es_sg.add_ingress_rule(lambda_es_sg, ec2.Port.all_tcp())

        # 3) prepare resources: EventBus, EventPattern, Rule-Target
        # event_bus = events.EventBus(self, "batch_event_bus", event_bus_name="default")
        account = config.get("accounts").get("test").get("account")
        region = config.get("accounts").get("test").get("region")
        event_bus = events.EventBus.from_event_bus_arn(self, "batch_event_bus", "arn:aws:events:"+region+":"+account+":event-bus/default")
        event_pattern = events.EventPattern(source=["aws.batch"], detail_type=["Batch Job State Change"], detail={"status": ["SUCCEEDED", "FAILED"]})
        lambda_target = targets.LambdaFunction(handler=batch_event_handler_lambda_function)

        # 3) create rule using resources: EventBus, EventPattern, Rule-Targets: Lambda
        events.Rule(self,
                    id="batch_job_event",
                    rule_name="batch_job_event",
                    targets=[lambda_target],
                    description="Batch job Event Rule navigates to Lambda",
                    event_bus=event_bus,
                    event_pattern=event_pattern,
        )

        batch_event_handler_lambda_function.add_environment('ES_DOMAIN_ENDPOINT', 'https://' + domain.domain_endpoint)

        # 5) Create EC2 Bastion Server
        # # Jump host for SSH tunneling and direct access
        # sn_public = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
 
        # amzn_linux = ec2.MachineImage.latest_amazon_linux(
        #     generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        #     edition=ec2.AmazonLinuxEdition.STANDARD,
        #     virtualization=ec2.AmazonLinuxVirt.HVM,
        #     storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        #     )
 
        # # Instance Role and SSM Managed Policy
        # role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
  
        # instance = ec2.Instance(self, 'instance',
        #                         instance_type=ec2.InstanceType(EC2_INSTANCE_TYPE),
        #                         vpc=vpc,
        #                         machine_image=amzn_linux,
        #                         vpc_subnets=sn_public,
        #                         key_name=EC2_KEY_NAME,
        #                         role=role,
        #                         )
        # instance.connections.allow_from_any_ipv4(ec2.Port.tcp(22), 'SSH')
        # instance.connections.allow_from_any_ipv4(ec2.Port.tcp(443), 'HTTPS')
 
        # stmt = iam.PolicyStatement(actions=['es:*'],
        #                            resources=[domain.domain_arn])
        # instance.add_to_role_policy(stmt)

