import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_rss_parser.aws_rss_parser_stack import AwsRssParserStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_rss_parser/aws_rss_parser_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsRssParserStack(app, "aws-rss-parser")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
