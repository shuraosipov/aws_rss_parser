from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_s3 as _s3,
    aws_sns as sns,
    aws_iam as iam,
    aws_sns_subscriptions as subscriptions,
    aws_events_targets as targets
)

from aws_cdk.aws_events import Rule, Schedule
from constructs import Construct

class AwsRssParserStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read context parameters defined in cdk.json
        bucket_name = self.node.try_get_context("bucket_name")
        days_range = self.node.try_get_context("days_range")
        email = self.node.try_get_context("email")

        # Create IAM role for lambda function
        lambda_role = iam.Role(self, "My Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Attach AWS managed default service role for Lambda function
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))

        # Create s3 bucket
        s3 = _s3.Bucket(self, "s3bucket", bucket_name=bucket_name)

        # Create sns topic
        topic = sns.Topic(self, "MyTopic")
        topic.add_subscription(subscriptions.EmailSubscription(email))


        # Import existing Lambda Layer
        layer = lambda_.LayerVersion.from_layer_version_arn(self, "LambdaLayer",
            layer_version_arn = self.node.try_get_context("layer_version_arn")
        ) 

        # Create Lambda function
        function = lambda_.Function(self, "MyLambda",
            code=lambda_.Code.from_asset("lambda"),
            handler="lambda_function.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            layers=[layer],
            role=lambda_role,
            timeout=Duration.seconds(15),
            environment = {
                "DAYS_RANGE": days_range,
                "BUCKET_NAME": bucket_name,
                "TOPIC_ARN": topic.topic_arn
            }
        )

        # Create schedule to invoke lambda
        rule = Rule(self, "ScheduleRule",
            schedule=Schedule.cron(minute="02", hour="00"),
            targets=[targets.LambdaFunction(function)]
        )

        # Configure grants and permissions
        s3.grant_put(function)
        topic.grant_publish(function)
               