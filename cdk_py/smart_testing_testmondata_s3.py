from aws_cdk import (
    aws_s3,
    aws_iam,
    core,
    aws_ssm,
)


class SmartTestingTestmondataS3Stack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        config: dict,
        **kwargs,
    ) -> None:
        """
        Creates and configures S3 buckets for archiving old MTS docker images
        """
        super().__init__(scope, id, **kwargs)

        smart_testing_testmondata_s3 = aws_s3.Bucket(
            self,
            id="smart-testing-testmondata-bucket",
            bucket_name=f"smart-testing-testmondata-bucket-{self.account}",
            # TODO: Change to KMS_MANAGED encryption once the policies are provided
            encryption=aws_s3.BucketEncryption.UNENCRYPTED,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
        )

        smart_testing_testmondata_s3.add_to_resource_policy(
            aws_iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=["*"],  ## TO Confrim : "arn:aws:s3:::examplebucket/shared/*"
                principals=[aws_iam.AccountRootPrincipal()],
            )
        )

        # Create a SSM Parameter holding the S3 bucket name
        param = aws_ssm.StringParameter(
            self,
            "smart-testing-testmondata-bucket-name",
            string_value=smart_testing_testmondata_s3.bucket_name,
        )
