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
from cdk_py.github_webhook_api_stack import GithubWebhookAPIStack


class PipelineStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        branch_name: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)


        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo")

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        # pipeline = pipelines.CdkPipeline(
        pipeline = pipelines.CdkPipeline(
            self,
            id,
            self_mutating=False,
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

            ),

        )


        testing_stage = pipeline.add_stage("BuildCache") # Empty stage since we are going to run tests only, not deploy resources
        testing_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="Build",
                environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                ),
                run_order=testing_stage.next_sequential_run_order(),
                additional_artifacts=[source_artifact],
                commands=[
                    "pip install -r requirements.txt",
                    # "pip install -r requirements_dev.txt",
                    "export DOCKER_BUILDKIT=1",
                    "aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 320185343352.dkr.ecr.us-west-2.amazonaws.com",
                    # "docker pull 320185343352.dkr.ecr.us-west-2.amazonaws.com/ubuntu:18.04",
                    "docker build --cache-from 320185343352.dkr.ecr.us-west-2.amazonaws.com/build_cache:latest  --tag 320185343352.dkr.ecr.us-west-2.amazonaws.com/build_cache:v2.0  --build-arg BUILDKIT_INLINE_CACHE=1  docker_build_path1/",
                    "docker tag 320185343352.dkr.ecr.us-west-2.amazonaws.com/build_cache:v2.0 320185343352.dkr.ecr.us-west-2.amazonaws.com/build_cache:latest",
                    "docker push 320185343352.dkr.ecr.us-west-2.amazonaws.com/build_cache:latest",
                    "docker push 320185343352.dkr.ecr.us-west-2.amazonaws.com/build_cache:v2.0",
                    "python scripts/build_cache.py",
                ],
                role_policy_statements=[
                    aws_iam.PolicyStatement(
                        actions=["sts:*"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=['*'
                            # synth_dev_account_role_arn,
                            # synth_qa_account_role_arn,
                            # synth_prod_account_role_arn,
                        ],
                    ),
                    aws_iam.PolicyStatement(
                        actions=["ecr:*"],
                        effect=aws_iam.Effect.ALLOW,
                        resources=['*'
                            # synth_dev_account_role_arn,
                            # synth_qa_account_role_arn,
                            # synth_prod_account_role_arn,
                        ],
                    ),
                ],
            )
        )

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

        # pipeline_generator_stage = PipelineGeneratorApplication(self, "pipelineGenerator", branch_name=branch_name, config=config
        #     # env=cdk.Environment(
        #     #     account="123456789012",
        #     #     region="eu-west-1"
        #     # )
        # )
        # pipeline.add_application_stage(pipeline_generator_stage)
