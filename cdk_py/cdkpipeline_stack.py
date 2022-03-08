from aws_cdk import (
    # Duration,
    core,
    aws_sqs,
    # aws_s3 as s3,
    aws_iam,
)
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import pipelines
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_codebuild

from constructs import Construct
import boto3
import os
import re
from cdk_py.cdk_py_stack import CdkPyStack





def branch_name_check(branch_name, branch_prefox):
    if branch_name.startswith(branch_prefox):
        return True
    else:
        return False

def get_brance_name_from_sqs(sqs_url):
    branch_name = 'generator2'
    branch_prefox = 'feature-branch-pipeline-'

    if sqs_url:
        # Receive message from SQS queue
        response = sqs_client.receive_message(
            QueueUrl=sqs_url,
        )
        # print(response)
        if response.get('Messages', []):
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Delete received message from queue
            sqs_client.delete_message(
                QueueUrl=sqs_url,
                ReceiptHandle=receipt_handle
            )
            # print('Received and deleted message: %s' % message)
            branch_name = message.get('Body', '')
            # print(branch_name)

        if branch_name_check(branch_name, branch_prefox):
            return branch_name




# from cdk_py.codebuild_stack import CodeBuildStack

# class S3Bucket(Stack):
#     def __init__(self, scope, id):
#         super().__init__(scope, id)
#         self.bucket = s3.Bucket(self, "Bucket")

# class GithubWebhookAPIStack(core.Stack):
#     def __init__(self, scope, id):
#         super().__init__(scope, id)

#         s3.Bucket(self, id)


# class CodeBuildProjectStack(core.Stack):
#     def __init__(self, scope, id):
#         super().__init__(scope, id)

#         s3.Bucket(self, id)


# TODO: APIGateway + Lambda + CodeBuild
# class PipelineGeneratorApplication(core.Stage):
#     def __init__(self, scope, id, *, env=None, outdir=None):
#         super().__init__(scope, id, env=env, outdir=outdir)
#         GithubWebhookAPIStack(self, "Github-Webhook")

        # GithubWebhookAPIStack(self, "MyFirstBucket-webhook", synthesizer=core.DefaultStackSynthesizer())
        # CodeBuildProjectStack(self, "Create-branch")
        # CodeBuildProjectStack(self, "Deletee-branch")
        # bucket = s3.Bucket(self, "MyFirstBucket-webhook")

# branch_name='feature-branch-pipeline-webhook'

#synth_dev_account_role_arn = f"arn:aws:iam::320185343352:role/synth-role"
#synth_dev_account_role_arn = f"arn:aws:iam::{dev_account}:role/xxxx"


# class MyCdkPipeline extends CdkPipeline {
#   constructor(scope: cdk.Construct, id: string, props: CdkPipelineProps) {
#     // pass self mutating false to prevent bug behaviour
#     super(scope, id, {...props, selfMutating: false});

#     const pipelineStack = cdk.Stack.of(this);

#     if (props.selfMutating ?? true) {
#       this.codePipeline.addStage({
#         stageName: 'UpdatePipeline',
#         actions: [new UpdatePipelineAction(this, 'UpdatePipeline', {
#           cloudAssemblyInput: props.cloudAssemblyArtifact,
#           // use logical id as pipelineStackName to get correct cli command
#           pipelineStackName: pipelineStack.node.id,
#           cdkCliVersion: props.cdkCliVersion,
#           projectName: `${props.pipelineName}-selfupdate`,
#         })]
#       })
#     }
#   }
# }

# def get_branch_name_from_queue(queue_url):
#     sqs_client = boto3.client('sqs')

#     # Receive message from SQS queue
#     response = sqs_client.receive_message(
#         QueueUrl=queue_url,
#         # AttributeNames=[
#         #     'SentTimestamp'
#         # ],
#         # MaxNumberOfMessages=1,
#         # MessageAttributeNames=[
#         #     'All'
#         # ],
#         # VisibilityTimeout=0,
#         # WaitTimeSeconds=0
#     )
#     return response

class CDKPipelineStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        # branch_name: str,
        creation_or_deletion: str,
        branch_name_queue: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # branch_name = core.CfnParameter(self, "branch_name")
        # branch_name = app.node.try_get_context("branch_name")


        # config = app.node.try_get_context("config")
        # branch_name = app.node.try_get_context("branch_name")

        sqs_url = os.getenv('SQS_URL')
        branch_name = get_brance_name_from_sqs(sqs_url)
        if branch_name:
            branch_chars = re.sub('[^0-9a-zA-Z]+', '', str(branch_name))
            stack_id = branch_chars + "ReadyForFeatureBranchPipeline"

            CdkPyStack(self, stack_id,
                branch_name=branch_name,
                config={**config},
            )
        else:
            branch_name = ''
            stack_id = ''
        # The code that defines your stack goes here
        # branch_name = get_branch_name_from_queue(queue_url)
        branch_name = "not_exist" # dev to be safe instead of master ? branch name not exist?
        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo")

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        # pipeline = pipelines.CdkPipeline(
        pipeline = pipelines.CdkPipeline(
            self,
            id,
            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name=id,
            source_action=cpactions.CodeStarConnectionsSourceAction(
                action_name="GitHub",
                connection_arn=codestar_connection_arn,
                owner=repo_owner,
                repo=repo,   
                branch=branch_name,
                #branch=branch_name.value_as_string,
                trigger_on_push=True,
                output=source_artifact,
            ),
            synth_action=pipelines.SimpleSynthAction.standard_npm_synth(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command="npm install -g aws-cdk && pip install -r requirements.txt",
                environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                    # environment_variables={"branch_name": branch_name}
                ),
                build_command="BRANCH=$(python scripts/get_branch_name_from_ssm.py); cdk list -c branch_name=$BRANCH",
                synth_command="BRANCH=$(python scripts/get_branch_name_from_ssm.py); cdk synth -c branch_name=$BRANCH",
                role_policy_statements=[
                    aws_iam.PolicyStatement(
                        actions=["ssm:GetParameter"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=['*'
                            # synth_dev_account_role_arn,
                            # synth_qa_account_role_arn,
                            # synth_prod_account_role_arn,
                        ],
                    )
                ],
                # role_policy_statements=[
                #     aws_iam.PolicyStatement(
                #         actions=["sts:AssumeRole"],
                #         effect=aws_iam.Effect.ALLOW,
                #         resources=[
                #             # synth_dev_account_role_arn,
                #             # synth_qa_account_role_arn,
                #             # synth_prod_account_role_arn,
                #         ],
                #     )
                # ],
            ),


            #     # Defaults for all CodeBuild projects
            # code_build_defaults=pipelines.CodeBuildOptions(
            #     # Prepend commands and configuration to all projects
            #     # partial_build_spec=codebuild.BuildSpec.from_object({
            #     #     "version": "0.2"
            #     # }),

            #     # Control the build environment
            #     build_environment=aws_codebuild.BuildEnvironment(
            #         environment_variables = {"branch_name": branch_name}
            #     ),

            #     # Control Elastic Network Interface creation
            #     # vpc=vpc,
            #     # subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            #     # security_groups=[my_security_group],

            #     # # Additional policy statements for the execution role
            #     # role_policy=[
            #     #     iam.PolicyStatement()
            #     # ]
            # ),
            # synth_code_build_defaults=pipelines.CodeBuildOptions(),
            # asset_publishing_code_build_defaults=pipelines.CodeBuildOptions(),
            # self_mutation_code_build_defaults=pipelines.CodeBuildOptions()
        )


        # pipeline_generator_stage = PipelineGeneratorApplication(self, "pipelineGenerator",
        #     # env=cdk.Environment(
        #     #     account="123456789012",
        #     #     region="eu-west-1"
        #     # )
        # )

        # TODO: run in parallel
        # wave = pipeline.add_wave("Testing")

        # ut_stage = pipeline.add_stage("UT") # Empty stage since we are going to run tests only, not deploy resources
        # ut_stage.add_actions(
        #     pipelines.ShellScriptAction(
        #         action_name="UnitTests",
        #         run_order=feature_stage.next_sequential_run_order(),
        #         additional_artifacts=[source_artifact],
        #         commands=[
        #             "pip install -r requirements.txt",
        #             "pip install -r requirements_dev.txt",
        #             "pytest --cov=dags --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
        #         ],
        #     )
        # )
        # wave.add_stage(ut_stage)

        # it_stage = pipeline.add_stage("IT")
        # it_stage.add_actions(
        #     pipelines.ShellScriptAction(
        #         action_name="InfrastructureTests",
        #         run_order=feature_stage.next_sequential_run_order(),
        #         additional_artifacts=[source_artifact],
        #         commands=[
        #             "pip install -r requirements.txt",
        #             "pip install -r requirements_dev.txt",
        #             # when no tests are found, exit code 5 will cause a problem in the pipeline
        #             # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s infrastructure/tests",
        #             "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
        #         ],
        #     )
        # )
        # wave.add_stage(it_stage)

        ## feature_stage = pipeline.add_application_stage(feature_app)

        deploy_stage = pipeline.add_stage("Deplpy_Feature_Branch_Pipeline") # Empty stage since we are going to run tests only, not deploy resources
        # testing_stage.add_actions(
        #     pipelines.ShellScriptAction(
        #         action_name="UnitTests",
        #         run_order=testing_stage.next_sequential_run_order(),
        #         additional_artifacts=[source_artifact],
        #         commands=[
        #             "pip install -r requirements.txt",
        #             "pip install -r requirements_dev.txt",
        #           #  "pytest --cov=dags --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
        #         ],
        #     )
        # )
        #SQS_URL??????

        deploy_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="InfrastructureTests",
                environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                    privileged=True,
                ),
                run_order=deploy_stage.next_sequential_run_order(),
                additional_artifacts=[source_artifact],
                environment_variables={
                    "SQS_URL": aws_codebuild.BuildEnvironmentVariable(
                        value=branch_name_queue,
                        # the properties below are optional
                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    ),
                    "BRANCH": aws_codebuild.BuildEnvironmentVariable(
                        value=branch_name,
                        # the properties below are optional
                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    ),
                    "creation_or_deletion": aws_codebuild.BuildEnvironmentVariable(
                        value=creation_or_deletion,
                        # the properties below are optional
                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    ),
                    "stack_id": aws_codebuild.BuildEnvironmentVariable(
                        value=stack_id,
                        # the properties below are optional
                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    ),
                },
                commands=[
                   # "BRANCH=$(python )"
                   # "if [[ $BRANCH =~ ^feature-branch-pipeline- ]]; then echo 'match'; else echo 'not match'; fi" 
                    "echo $SQS_URL, $branch_name, $stack_id, $creation_or_deletion",
                    # "git status; git branch -a; git checkout $BRANCH; git status" # Not git repo

                    # "export BRANCH=$(python scripts/get_branch_name_from_sqs.py); echo $BRANCH;",
                    # "cat cdk.json",
                    # - cdk ls; cdk synth; cdk diff; cdk deploy --require-approval never
                    "if [[ $BRANCH =~ ^feature-branch-pipeline- ]]; then npm -v; npm install -g aws-cdk; cdk --version; pip install -r requirements.txt; cdk ls -c branch_name=$BRANCH; cdk synth $stack_id -c branch_name=$BRANCH; cdk diff -c branch_name=$BRANCH; if [[ $reation_or_deletion == 'deletion' ]]; then cdk deploy $stack_id -c branch_name=$BRANCH --require-approval never; fi; if [[ $reation_or_deletion == 'creation' ]]; then   cdk destroy $stack_id -c branch_name=$BRANCH -f; else echo 'Not match feature branch prefix'; fi; fi"
                ],
                role_policy_statements=[
                    aws_iam.PolicyStatement(
                        actions=["iam:PassRole"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=["*"],
                    ),
                    # aws_iam.PolicyStatement(
                    #     actions=["ssm:GetParameter"],
                    #     effect=aws_iam.Effect.ALLOW,
                    #     resources=["*"],
                    # ),
                    aws_iam.PolicyStatement(
                        actions=["sqs:ReceiveMessage", "sqs:DeleteMessage"], ## Readonly? TODO
                        effect=aws_iam.Effect.ALLOW,
                        resources=["*"],
                    ),
                    aws_iam.PolicyStatement(
                        actions=["S3:*"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=["*"],
                    ),
                    aws_iam.PolicyStatement(
                        actions=["cloudformation:*"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=["*"],
                    )
                ],
            )
        )

        # pipeline_generator_stage = PipelineGeneratorApplication()
        # pipeline.add_application_stage(pipeline_generator_stage)

        ## feature_stage = pipeline.add_application_stage(feature_app)


        # 'MyApplication' is defined below. Call `addStage` as many times as
        # necessary with any account and region (may be different from the
        # pipeline's).
