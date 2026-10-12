import boto3;
import json;
import argparse;
from botocore.exceptions import ClientError

def generate_random_string(length):
    import random
    import string
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(letters) for i in range(length))


def site_exists(bucket_name):
    s3client = boto3.client('s3')
    try:
        s3client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Create an S3 bucket')
parser.add_argument('--sitename', help='The name of the S3 bucket to create', required=True)

args = parser.parse_args()
random_suffix = generate_random_string(10)  # Generate a random suffix for the bucket name

s3client = boto3.client('s3')

myBucketName = args.sitename

#Check if the bucket already exists and generate a unique name if it does
if site_exists(myBucketName):
    print(f"Bucket {myBucketName} already exists. Generating a unique name.")
    myBucketName += random_suffix  # Append the random suffix to the bucket name
    print(f"New bucket name is {myBucketName}")


#check if the bucket already exists before creating it
try:
    s3client.head_bucket(Bucket=myBucketName)
    print(f"Bucket {myBucketName} already exists. Please choose a different name.")
except ClientError as e:
    print(f"Bucket {myBucketName} does not exist. Proceeding to create it.")

#try to create the bucket and handle any exceptions that may occur
try:
    s3client.create_bucket(Bucket=myBucketName)
except ClientError as e:
    print(f"Error creating bucket: {e}")
    #exit(1)

#set the bucket policy to allow public read access
try:
    s3client.delete_public_access_block(Bucket=myBucketName)
    print("Public access block deleted for bucket: " + myBucketName)
except ClientError as e:
    print(f"Error deleting public access block: {e}")

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

#set the bucket policy to allow public read access
s3client.put_bucket_policy(Bucket=myBucketName, Policy=json.dumps(bucket_policy))
print("Bucket policy added for bucket: " + myBucketName)

try:
    s3client.put_bucket_website(
        Bucket=myBucketName,
        WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        })
except ClientError as e:
    print(f"Error configuring bucket website: {e}")

file = "index.html" \
"body = open(file, 'rb')".read()


try:
    s3client.put_bucket_website(
        Bucket=myBucketName,
        WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        })

    print("Bucket website configuration added for bucket: " + myBucketName)

file = open('index.html', 'rb')

s3client.put_object(
    Bucket=myBucketName,
    Key='index.html',
    Body=file,
    ContentType='text/html')
print("index.html uploaded to bucket: " + myBucketName)