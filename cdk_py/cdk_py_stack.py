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


        )


 
        feature_stage = pipeline.add_stage("Testing") # Empty stage since we are going to run tests only, not deploy resources
        feature_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="UnitTests",
                run_order=feature_stage.next_sequential_run_order(),
                additional_artifacts=[source_artifact],
                environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                    # environment_variables={"branch_name": branch_name}
                ),                
                commands=[
                    "pip install -r requirements.txt",
                    "pip install -r requirements_dev.txt",
                    "pytest -vvv -s tests/"
                    #"pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
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
                environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                    # environment_variables={"branch_name": branch_name}
                ),
                commands=[
                    "pip install -r requirements.txt",
                    "pip install -r requirements_dev.txt",
                    # when no tests are found, exit code 5 will cause a problem in the pipeline
                    # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s infrastructure/tests",
                    # "pytest --cov=infrastructure --cov-branch --cov-report term-missing -vvvv -s tests", #TODO
                ],
            )
        )


