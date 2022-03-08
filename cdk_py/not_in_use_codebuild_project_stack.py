from aws_cdk import (
    # aws_iam,
    aws_codebuild as codebuild,
    # aws_apigateway,
    # aws_cognito,
    # aws_dynamodb,
    # aws_route53,
    # aws_ec2,
    # aws_certificatemanager,
    core,
    # aws_logs,
    # aws_ssm,
)

# from aws_cdk.aws_lambda_python import PythonFunction

# from aws_cdk.core import Duration

# import os


class CodeBuildProjectStack(core.Stack):
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



        project = codebuild.Project(
            self,
            "BranchPipelineCreation",
            # You'll need to configure this first. See:
            # https://docs.aws.amazon.com/cdk/api/latest/docs/aws-codebuild-readme.html#githubsource-and-githubenterprisesource
            source=codebuild.Source.git_hub(
                owner=repo_owner, repo=repo, branch=branch_name, connection_arn=codestar_connection_arn
            ),

            # source_action=cpactions.CodeStarConnectionsSourceAction(
            #     action_name="GitHub",
            #     connection_arn=codestar_connection_arn,
            #     owner=repo_owner,
            #     repo=repo,   
            #     branch=branch_name,
            #     #branch=branch_name.value_as_string,
            #     trigger_on_push=True,
            #     output=source_artifact,
            # ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": ["ls -al"]
                    }
                },
                # "cache": {
                #     "paths": ["/root/cachedir/**/*"
                #     ]
                # }
            })
        )

