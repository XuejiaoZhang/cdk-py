from aws_cdk import (
    # Duration,
    core,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_iam,
)
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import pipelines
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_codebuild

from constructs import Construct



class S3Bucket(core.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        s3.Bucket(self, id)


# # TODO: APIGateway + Lambda + CodeBuild
class DeployApplication(core.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        s3_bucket = S3Bucket(self, "MyFirstBucket-webhook")
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
class CdkPyStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        feature_branch_name: str,
        development_pipeline: bool,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)


        if not feature_branch_name:
            if development_pipeline == True:
                branch_name = 'dev'
            else:
                branch_name = 'master'
        else:
            branch_name = feature_branch_name
        # branch_name = dev

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
            # self_mutating=False,
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
                ## botocore.errorfactory.ParameterNotFound: An error occurred (ParameterNotFound) when calling the GetParameter operation: 
                # "BRANCH=master"
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


        # feature_app = MyApplication(self, "webhook",
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

        # TODO: development_pipeline
        # feature_stage = pipeline.add_application_stage(feature_app)

        feature_stage = pipeline.add_stage("Testing") # Empty stage since we are going to run tests only, not deploy resources
        feature_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="UnitTests",
                run_order=feature_stage.next_sequential_run_order(),
                additional_artifacts=[source_artifact],
                commands=[
                    "cat tests/not_in_use_test_cdkpipeline_stack.py ",
                    # "pip install -r requirements.txt",
                    # "pip install -r requirements_dev.txt",
                    # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
                    # "pytest --cov=dags --cov-branch term-missing -vvvv -s tests", #TODO
                   # "pytest --cov=dags --cov-branch --cov-report term-missing -vvvv -s tests", #TODO

                ],
            )
        )

        feature_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="InfrastructureTests",
                run_order=feature_stage.next_sequential_run_order(),
                additional_artifacts=[source_artifact],
                commands=[
                    "pip install -r requirements.txt",
                    "pip install -r requirements_dev.txt",
                    # when no tests are found, exit code 5 will cause a problem in the pipeline
                    # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s infrastructure/tests",
                    # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
                ],
            )
        )



        deploy_stage = DeployApplication(self, "revision-deploy-sample",
            #     account="123456789012",
            #     region="eu-west-1"
            # )
        )
        pipeline.add_application_stage(deploy_stage)


        # 'MyApplication' is defined below. Call `addStage` as many times as
        # necessary with any account and region (may be different from the
        # pipeline's).
