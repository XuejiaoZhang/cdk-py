from aws_cdk import (
    # Duration,
    core,
    # aws_sqs as sqs,
    # aws_s3 as s3,
    aws_iam,
)
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import pipelines
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_codebuild

from aws_cdk.core import DefaultStackSynthesizer

from constructs import Construct
from cdk_py.github_webhook_api_stack import GithubWebhookAPIStack
from cdk_py.cdk_py_stack import CdkPyStack
# from cdk_py.cdkpipeline_stack import CDKPipelineStack
from cdk_py.smart_testing_testmondata_s3 import SmartTestingTestmondataS3Stack

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
class PipelineGeneratorApplication(core.Stage):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        branch_name: str,
        pipeline_template: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        # GithubWebhookAPIStack(self, "GitHub-Webhook-API")

        # branch_creation_pipeline = 'Create-Branch'
        # branch_deletion_pipeline = 'Delete-Branch'  #TODO:pass to PipelineGeneratorApplication, then lambda env, and cdkpipeline


        # feature_branch_name = "not_exist_branch_just_for_template"



        #GithubWebhookAPIStack(self, "GitHub-Webhook-API", pipeline_template=pipeline_template, config=config)


        smarttestingtestmondatas3 = SmartTestingTestmondataS3Stack(
            self,
            "smarttestingtestmondatas3stack",
            config=config,
            synthesizer=DefaultStackSynthesizer(),
        )

        # CDKPipelineStack(self, config.get('branch_creation_pipeline'), branch_name=branch_name, branch_name_queue=webhook_api_stack.branch_creation_queue, creation_or_deletion="creation", config=config)
        # CDKPipelineStack(self, config.get('branch_deletion_pipeline'), branch_name=branch_name, branch_name_queue=webhook_api_stack.branch_deletion_queue, creation_or_deletion="deletion", config=config)


        # webhook_api_stack = GithubWebhookAPIStack(self, "GitHub-Webhook-API")
        # # GithubWebhookAPIStack(self, "MyFirstBucket-webhook", synthesizer=core.DefaultStackSynthesizer())
        # # CDKPipelineStack(self, "Create-Branch", config=config)


        # CDKPipelineStack(self, "Create-Branch", branch_name_queue=webhook_api_stack.branch_creation_queue, creation_or_deletion="creation", config=config)
        # CDKPipelineStack(self, "Delete-Branch", branch_name_queue=webhook_api_stack.branch_deletion_queue, creation_or_deletion="deletion", config=config)

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
class PipelineGeneratorStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        branch_name: str,
        pipeline_template: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # branch_name = core.CfnParameter(self, "branch_name")
        # branch_name = app.node.try_get_context("branch_name")

        # The code that defines your stack goes here

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
                ),
                environment_variables={
                    "BRANCH": aws_codebuild.BuildEnvironmentVariable(
                        value=branch_name,
                        # the properties below are optional
                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    ),
                },
                build_command="echo $BRANCH; cdk list -c branch_name=$BRANCH",
                synth_command="echo $BRANCH; cdk synth -c branch_name=$BRANCH",

                # build_command="BRANCH=$(python scripts/get_branch_name_from_ssm.py); echo $BRANCH; cdk list -c branch_name=$BRANCH",
                # synth_command="BRANCH=$(python scripts/get_branch_name_from_ssm.py); echo $BRANCH; cdk synth -c branch_name=$BRANCH",
                # role_policy_statements=[
                #     aws_iam.PolicyStatement(
                #         actions=["ssm:GetParameter"],
                #         effect=aws_iam.Effect.ALLOW,
                #         resources=['*'
                #             # synth_dev_account_role_arn,
                #             # synth_qa_account_role_arn,
                #             # synth_prod_account_role_arn,
                #         ],
                #     )
                # ],
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
        pipeline_generator_stage = PipelineGeneratorApplication(self, "pipelineGenerator-boto3", branch_name=branch_name, pipeline_template=pipeline_template, config=config
            # env=cdk.Environment(
            #     account="123456789012",
            #     region="eu-west-1"
            # )
        )
        pipeline.add_application_stage(pipeline_generator_stage)


        testing_stage = pipeline.add_stage("Testing") # Empty stage since we are going to run tests only, not deploy resources

#         testing_stage.add_actions(
#             pipelines.ShellScriptAction(
#                 action_name="SmartTesting",
#                 run_order=testing_stage.next_sequential_run_order(),
#                 additional_artifacts=[source_artifact],
#                 # environment_variables={
#                 #     "BUCKET_NAME": aws_codebuild.BuildEnvironmentVariable(
#                 #         value=pipeline_generator_stage.smarttestingtestmondatas3.smart_testing_testmondata_s3.bucket_name,
#                 #         type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
#                 #     ),
#                 # },
#                 commands=[
#                     "pip install -r requirements.txt",
#                     "pip install -r requirements_dev.txt",
#                     "set -e; export BUCKET_NAME=$(python scripts/get_bucket_name_from_ssm.py);ls -al;python scripts/download_smart_testing_testmondata_from_s3.py; ls -al; pytest --testmon; ls -al; python scripts/upload_smart_testing_testmondata_to_s3.py"
#                 ],
#                 role_policy_statements=[
#                     aws_iam.PolicyStatement(
#                         actions=[
#                             "S3:ListBucket",
#                             "s3:PutObject",
#                             "s3:GetObject"
#                         ],
#                         effect=aws_iam.Effect.ALLOW,
#                         resources=["*"]
#                         #resources=[pipeline_generator_stage.smarttestingtestmondatas3.smart_testing_testmondata_s3.bucket_arn],
#                     ),
#                     aws_iam.PolicyStatement(
#                         actions=["ssm:GetParameter"],
#                         effect=aws_iam.Effect.ALLOW,
#                         resources=["*"],
#                     ),
#                 ],
#             )
#         )

        testing_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="StaticCodeAnalysis",
                run_order=testing_stage.next_sequential_run_order(),
                additional_artifacts=[source_artifact],
                environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                ),
                environment_variables={
                    "THRESHOLD": aws_codebuild.BuildEnvironmentVariable(
                        value=config.get("smart_testing").get("threshold"),
                        type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                    ),
                    "secret": aws_codebuild.BuildEnvironmentVariable(
                        value="github_webhook_secret:github_webhook_secret",
                        type=aws_codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER,
                    ),
                    "token": aws_codebuild.BuildEnvironmentVariable(
                        value="token",
                        type=aws_codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER,
                    ),
                    "token2": aws_codebuild.BuildEnvironmentVariable(
                        value="token2:token2",
                        type=aws_codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER,
                    ),
                    # NODE_AUTH_TOKEN: {
                    #     value: secretGithubAccessToken.secretValue,
                    #     type: BuildEnvironmentVariableType.SECRETS_MANAGER,
                    #   },
                },
                commands=[
                    # Not git repo
                    "echo $secret",
                    "echo $token",
                    "echo $token2"
                    # "pip install -r requirements.txt",
                    # "pip install -r requirements_dev.txt",
                    # "set -e; bash scripts/pylint_check.sh $THRESHOLD"
                    #     "pylint $(git ls-files '*.py')",
                    #     "#!bin/bash; set -e; export score=$(pylint * |grep -oE '\-?[0-9]+\.[0-9]+'| sed -n '1p');",
                    #     "#!bin/bash; set -e; echo $score; export ret=$(awk -v score=$score -v threshold=$THRESHOLD 'BEGIN{print(score>threshold)?0:1}'); ",
                    #     "#!bin/bash; set -e; echo $ret;if [[ $ret -eq 0 ]]; then echo $score>$threshold; else echo $score<=$threshold; exit 1 ; fi"
                ],
                role_policy_statements=[
                    aws_iam.PolicyStatement(
                        actions=["secretsmanager:GetSecretValue"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=["*"]
                    )
                ],
            )
        )


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

        # testing_stage.add_actions(
        #     pipelines.ShellScriptAction(
        #         action_name="InfrastructureTests",
        #         run_order=testing_stage.next_sequential_run_order(),
        #         additional_artifacts=[source_artifact],
        #         commands=[
        #             "pip install -r requirements.txt",
        #             "pip install -r requirements_dev.txt",
        #             # when no tests are found, exit code 5 will cause a problem in the pipeline
        #             # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s infrastructure/tests",
        #         #    "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
        #         ],
        #     )
        # )


        # pipeline.add_application_stage(pipeline_generator_stage)

        ## feature_stage = pipeline.add_application_stage(feature_app)


        # 'MyApplication' is defined below. Call `addStage` as many times as
        # necessary with any account and region (may be different from the
        # pipeline's).
