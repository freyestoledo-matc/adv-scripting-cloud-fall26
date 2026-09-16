import boto3;
import json;

s3client = boto3.client('s3')

myBucketName = 'my-unique-bucket-name-freyestoledofall26'
s3client.create_bucket(Bucket=myBucketName)
print("Bucket created: " + myBucketName)

s3client.delete_public_access_block(Bucket=myBucketName)
print("Public access block deleted for bucket: " + myBucketName)

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
s3client.put_bucket_policy(Bucket=myBucketName, Policy=json.dumps(bucket_policy))
print("Bucket policy added for bucket: " + myBucketName)

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