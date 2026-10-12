import boto3
import json
import argparse
import random
import string

from botocore.exceptions import ClientError


def generate_random_string(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(letters, k=length))


def site_exists(bucket_name):
    s3client = boto3.client('s3')
    try:
        s3client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False


parser = argparse.ArgumentParser(
    description='Create an S3 bucket'
)
parser.add_argument(
    '--sitename',
    help='The name of the S3 bucket to create',
    required=True
)

args = parser.parse_args()
random_suffix = generate_random_string(10)

s3client = boto3.client('s3')
myBucketName = args.sitename.lower()

# Check if the bucket already exists
if site_exists(myBucketName):
    print(
        f"Bucket {myBucketName} already exists. "
        "Generating a unique name."
    )
    myBucketName += random_suffix
    print(f"New bucket name is {myBucketName}")


# Build the website
try:
    # Create the S3 bucket
    region = s3client.meta.region_name or 'us-east-1'

    if region == 'us-east-1':
        s3client.create_bucket(Bucket=myBucketName)
    else:
        s3client.create_bucket(
            Bucket=myBucketName,
            CreateBucketConfiguration={
                'LocationConstraint': region
            }
        )

    # Remove the bucket public access block
    s3client.delete_public_access_block(
        Bucket=myBucketName
    )
    print(
        "Public access block deleted for bucket: "
        + myBucketName
    )

    # Set the bucket policy to allow public read access
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'AddPerm',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject'],
            'Resource': "arn:aws:s3:::%s/*" % myBucketName
        }]
    }

    s3client.put_bucket_policy(
        Bucket=myBucketName,
        Policy=json.dumps(bucket_policy)
    )
    print("Bucket policy added for bucket: " + myBucketName)

    # Configure static website hosting
    s3client.put_bucket_website(
        Bucket=myBucketName,
        WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        }
    )
    print(
        "Bucket website configuration added for bucket: "
        + myBucketName
    )

    # Upload index.html
    with open('index.html', 'rb') as file:
        s3client.put_object(
            Bucket=myBucketName,
            Key='index.html',
            Body=file,
            ContentType='text/html'
        )

    print("index.html uploaded to bucket: " + myBucketName)

    # Print the website URL
    website_url = (
        f"http://{myBucketName}.s3-website-"
        f"{region}.amazonaws.com"
    )
    print("Website URL: " + website_url)

except (ClientError, OSError) as e:
    print("Error building website")