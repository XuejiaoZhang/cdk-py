#!/usr/bin/env python3
import os
import re
from aws_cdk import core

from cdk_py.cdk_py_stack import CdkPyStack
from cdk_py.pipeline_generator_stack import PipelineGeneratorStack
# from pygit2 import Repository


app = core.App()

config = app.node.try_get_context("config")




# def get_repo_current_branch():
#     return Repository('.').head.shorthand

# branch_name = app.node.try_get_context("branch_name")


# branch_name = get_repo_current_branch()

# import subprocess
# cmd = 'pwd; ls -al; git status'
#cmd = 'pwd; ls -al .; git status'

# process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
# output, error = process.communicate()
# # branch_name = str(output.split()[1])
# print(output)
# print(error)


# branch_chars = re.sub('[^0-9a-zA-Z]+', '', str(branch_name))


branch_name = 'dev'
PipelineGeneratorStack(app, 'FeatureBranchPipelineGenerator',
        branch_name=branch_name, # dev, master
        config={**config},
    )


# branch_name = "aa"
#branch_name = core.CfnParameter(self, "branch_name")

#stack_id = branch_chars + "ReadyForFeatureBranchPipeline" # for feature-branch pipeline

stack_id = "OriginalStack" # OriginalStack

CdkPyStack(app, "dev-pipeline",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
        # branch_name=branch_name,
        feature_branch_name='',
        development_pipeline=True,
        config={**config},
        # synthesizer=core.DefaultStackSynthesizer(
        #     deploy_role_arn="arn:${AWS::Partition}:iam::${AWS::AccountId}:role/cdk-${Qualifier}-deploy-my-role-${AWS::AccountId}-${AWS::Region}",
        #     cloud_formation_execution_role="arn:${AWS::Partition}:iam::${AWS::AccountId}:role/cdk-${Qualifier}-cfn-my-exec-role-${AWS::AccountId}-${AWS::Region}",  # noqa
        # ),
      #  synthesizer=DefaultStackSynthesizer(
      #   deploy_role_arn="arn:aws:iam::320185343352:role/cdk-deploy-webhook",
      #   cloud_formation_execution_role="arn:aws:iam::320185343352:role/cdk-cfn-my-exec-webhook",
      # ),
    )

CdkPyStack(app, "prod-pipeline",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
        feature_branch_name='',
        development_pipeline=False,
        config={**config},
        # synthesizer=core.DefaultStackSynthesizer(
        #     deploy_role_arn="arn:${AWS::Partition}:iam::${AWS::AccountId}:role/cdk-${Qualifier}-deploy-my-role-${AWS::AccountId}-${AWS::Region}",
        #     cloud_formation_execution_role="arn:${AWS::Partition}:iam::${AWS::AccountId}:role/cdk-${Qualifier}-cfn-my-exec-role-${AWS::AccountId}-${AWS::Region}",  # noqa
        # ),
      #  synthesizer=DefaultStackSynthesizer(
      #   deploy_role_arn="arn:aws:iam::320185343352:role/cdk-deploy-webhook",
      #   cloud_formation_execution_role="arn:aws:iam::320185343352:role/cdk-cfn-my-exec-webhook",
      # ),
    )
app.synth()


CdkPyStack(app, "feature-branch-A-Pipeline",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
        feature_branch_name='feature-branch-pipeline-us01',
        development_pipeline=True,
        config={**config},
        # synthesizer=core.DefaultStackSynthesizer(
        #     deploy_role_arn="arn:${AWS::Partition}:iam::${AWS::AccountId}:role/cdk-${Qualifier}-deploy-my-role-${AWS::AccountId}-${AWS::Region}",
        #     cloud_formation_execution_role="arn:${AWS::Partition}:iam::${AWS::AccountId}:role/cdk-${Qualifier}-cfn-my-exec-role-${AWS::AccountId}-${AWS::Region}",  # noqa
        # ),
      #  synthesizer=DefaultStackSynthesizer(
      #   deploy_role_arn="arn:aws:iam::320185343352:role/cdk-deploy-webhook",
      #   cloud_formation_execution_role="arn:aws:iam::320185343352:role/cdk-cfn-my-exec-webhook",
      # ),
    )
app.synth()
