import os
import re
import sys
import json
from datetime import datetime, timedelta
import feedparser
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
sns = boto3.client('sns')

def string_to_date(string):
    """ This function converts a string representation of date to the datetime object """
    return datetime.strptime(string, "%a, %d %b %Y %H:%M:%S %z")

def date_to_string(datetime_obj):
    """ This function converts datetime object to a string """
    return datetime_obj.strftime("%a, %d %b %Y %H:%M:%S")

def current_date():
    return datetime.now().replace(
        microsecond=0
    ).isoformat()
    
def format_entry_as_row(entry, short=False):
    id = entry.id
    link = entry.link
    title = entry.title
    summary = entry.summary
    published = entry.published
    product_names = extract_product_name(entry.tags[0]['term'])

    if short:
        return f"{product_names}; {published}; {title}"
    return f"{id}; {product_names}; {published}; {link}; {title}; {summary}"

def extract_product_name(string) -> str:
    """
    This function extracts a product name from a string.
    The product name is assumed to be everything after 'general:products/' and before the next comma or end of the string.
    If there is no product name in the string, the empty string is returned.
    """
    product = re.findall(r'general:products/(.*?)(?:,|$)', string)
    return " ".join(product)

def save_to_file(string, file_name='/tmp/output.csv') -> None:
    with open(file_name, 'a') as output:
        print(string, file=output)


def send_notification(topic_arn, message, subject):
    return sns.publish(TopicArn=topic_arn,
                      Message=message,
                      Subject=subject)

def upload_to_s3(file_name, bucket, object_name=None, topic_arn=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        message=f"""Error occured while uploading file.\n
            Error code - {response['Error']['Code']}\n
            Error message - {response['Error']['Message']}."""
        subject='AWS Feed. Error when uploading file.'
        send_notification(topic_arn, message, subject)
        sys.exit(1)

def save_entries_as_table(feed, start_time, file_name) -> int:
    new_entries_counter = 0
    for entry in feed.entries:
        if string_to_date(entry.published) > start_time:
            row = format_entry_as_row(entry)
            # print(row)
            save_to_file(row, file_name)
            new_entries_counter += 1
    return new_entries_counter


def check_if_feed_was_updated_recently(start_time, update_time):
    feed_last_updated = string_to_date(update_time)

    if feed_last_updated > start_time:
        print(f"New entries found! Feed was updated on {update_time}")
    else:
        print(f"No new entries since {date_to_string(start_time)}")
        sys.exit(123)


def generate_start_date(range):
    """ This function creates a datetime object in the past by substracting number of days from now. """
    result = (datetime.now() - timedelta(days=range)).strftime("%a, %d %b %Y 00:00:05 %z +0000")
    return string_to_date(result)

def delete_file(path):
    try:
        os.remove(path)
    except OSError:
        pass

def lambda_handler(event, context):

    DAYS_RANGE = int(os.environ.get("DAYS_RANGE"))
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    TOPIC_ARN = os.environ.get("TOPIC_ARN")

    url = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
    feed = feedparser.parse(url)
    feed_update_time = feed.feed['updated']
    
    # Remove output file from previous run
    output_file_name = '/tmp/output.csv'
    delete_file(output_file_name)
    
    # We do not want to start feed processing if it was not updated since the last check.
    start_time = generate_start_date(DAYS_RANGE)
    check_if_feed_was_updated_recently(start_time, feed_update_time)

    # When new entries are found, we want to extract them and save them in a tabular form.
    new_entries = save_entries_as_table(feed, start_time, output_file_name)
    
    # Finally, we upload the resulting file to S3.
    object_name = f"{current_date()}_{os.path.basename(output_file_name)}"
    upload_to_s3(output_file_name, BUCKET_NAME, object_name, TOPIC_ARN)

    subject = "AWS Feed. New updates available!"
    message = f"""
    There are {new_entries} new releases.\n
    Check out new file at s3://{BUCKET_NAME}/{object_name}
    """
    send_notification(TOPIC_ARN, message, subject)

    return {
        'statusCode': 200,
        'body': json.dumps('Processing completed successfully!')
    }