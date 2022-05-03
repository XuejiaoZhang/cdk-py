import boto3


codebuild_client = boto3.client("codebuild")


def codebuild_run(branch_name):
    response = codebuild_client.start_build(
        projectName="lambda-codebuild",
        sourceVersion=branch_name,
        environmentVariablesOverride=[
            {"name": "BRANCH", "value": branch_name, "type": "PLAINTEXT"},
        ],
    )


branch_name = "dev"
branch_name = "feature-branch-pipeline-us03-deploy-self-mutating-false-01"
print("CDK deploy branch:", branch_name)
codebuild_run(branch_name)
