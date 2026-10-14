import boto3
import json
import argparse
import random
import string
import sys

from botocore.exceptions import ClientError


def generate_random_string(length=10):
    return "".join(random.choices(string.ascii_lowercase, k=length))


# Create the command-line parser
parser = argparse.ArgumentParser(
    description="Create an S3 bucket"
)

parser.add_argument(
    "--sitename",
    help="The name of the S3 bucket to create",
    default=None
)

args = parser.parse_args()

# Use the supplied name or generate a default name
if args.sitename:
    myBucketName = args.sitename.lower()
else:
    myBucketName = "my-website-" + generate_random_string()

print(f"Bucket name: {myBucketName}")

# Create the S3 client
try:
    region = "us-east-1"

    s3client = boto3.client(
        "s3",
        region_name=region,
        endpoint_url="https://s3.us-east-1.amazonaws.com"
    )

    print(f"AWS Region: {region}")

except Exception as e:
    print(f"Error creating S3 client: {e}")
    sys.exit(1)


# Try to create the bucket
try:
    if region == "us-east-1":
        s3client.create_bucket(Bucket=myBucketName)
    else:
        s3client.create_bucket(
            Bucket=myBucketName,
            CreateBucketConfiguration={
                "LocationConstraint": region
            }
        )

    print(f"Bucket created: {myBucketName}")

except s3client.exceptions.BucketAlreadyExists as err:
    print(
        "Bucket {} already exists!".format(
            err.response["Error"].get(
                "BucketName", myBucketName
            )
        )
    )
    sys.exit(1)

except ClientError as e:
    error_code = e.response.get(
        "Error", {}
    ).get("Code", "Unknown")

    if error_code in (
        "InvalidToken",
        "ExpiredToken",
        "InvalidClientTokenId"
    ):
        print(
            "Invalid or expired AWS token. "
            "Please update your ~/.aws/credentials file."
        )
    elif error_code == "BucketAlreadyOwnedByYou":
        print(f"You already own bucket: {myBucketName}")
    else:
        print(f"AWS Error Code: {error_code}")
        print(f"Error creating bucket: {e}")

    sys.exit(1)

except Exception as e:
    print(f"Unexpected error creating bucket: {e}")
    sys.exit(1)

except ClientError as e:
    error_code = e.response.get(
        "Error", {}
    ).get("Code", "Unknown")

    if error_code in (
        "InvalidToken",
        "ExpiredToken",
        "InvalidClientTokenId"
    ):
        print(
            "Invalid or expired AWS token. "
            "Please update your ~/.aws/credentials file."
        )
    elif error_code in (
        "BucketAlreadyExists",
        "BucketAlreadyOwnedByYou"
    ):
        print(f"Bucket {myBucketName} already exists "
              "or is already owned by your account.")
    else:
        print(f"AWS Error Code: {error_code}")
        print(f"Error creating bucket: {e}")

    sys.exit(1)

except Exception as e:
    print(f"Unexpected error creating bucket: {e}")
    sys.exit(1)


# Set the bucket policy to allow public read access
try:
    s3client.delete_public_access_block(
        Bucket=myBucketName
    )
    print(
        f"Public access block deleted for bucket: "
        f"{myBucketName}"
    )

except ClientError as e:
    print(f"Error deleting public access block: {e}")
    sys.exit(1)


bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "AddPerm",
        "Effect": "Allow",
        "Principal": "*",
        "Action": ["s3:GetObject"],
        "Resource": f"arn:aws:s3:::{myBucketName}/*"
    }]
}

# Apply the bucket policy
try:
    s3client.put_bucket_policy(
        Bucket=myBucketName,
        Policy=json.dumps(bucket_policy)
    )
    print(f"Bucket policy added for bucket: {myBucketName}")

except ClientError as e:
    print(f"Error adding bucket policy: {e}")
    sys.exit(1)


# Configure static website hosting
try:
    s3client.put_bucket_website(
        Bucket=myBucketName,
        WebsiteConfiguration={
            "ErrorDocument": {"Key": "error.html"},
            "IndexDocument": {"Suffix": "index.html"}
        }
    )
    print(
        f"Bucket website configuration added for bucket: "
        f"{myBucketName}"
    )

except ClientError as e:
    print(f"Error configuring bucket website: {e}")
    sys.exit(1)


# Upload index.html
try:
    with open("index.html", "rb") as file:
        s3client.put_object(
            Bucket=myBucketName,
            Key="index.html",
            Body=file,
            ContentType="text/html"
        )

    print(f"index.html uploaded to bucket: {myBucketName}")

except ClientError as e:
    print(f"Error uploading index.html: {e}")
    sys.exit(1)

except OSError as e:
    print(f"Error opening index.html: {e}")
    sys.exit(1)