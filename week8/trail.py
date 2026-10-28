"""Set up a CloudTrail trail."""

import json
import sys

import boto3
from botocore.exceptions import ClientError

import s3enforce


def CreateTrail(trail_name, bucket_name):
    """Create a CloudTrail trail and start logging to an S3 bucket.

    Args:
        trail_name: Name of the CloudTrail trail.
        bucket_name: Name of the S3 bucket to deliver logs to.

    Returns:
        The create_trail response, the existing trail on reruns,
        or None on failure.
    """
    # Create the CloudTrail client
    try:
        trail_client = boto3.client("cloudtrail")
    except Exception as e:
        print(f"Error creating CloudTrail client: {e}")
        return None

    # Create the trail, or reuse it if it already exists
    try:
        response = trail_client.create_trail(
            Name=trail_name,
            S3BucketName=bucket_name,
        )
        print(f"Trail created: {trail_name}")

    except trail_client.exceptions.TrailAlreadyExistsException:
        print(f"Trail already exists: {trail_name}")
        try:
            response = trail_client.get_trail(Name=trail_name)
        except ClientError as e:
            print(f"Error getting existing trail: {e}")
            return None

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")

        if error_code in (
            "InvalidToken",
            "ExpiredToken",
            "InvalidClientTokenId",
        ):
            print(
                "Invalid or expired AWS token. "
                "Please update your ~/.aws/credentials file."
            )
        else:
            print(f"AWS Error Code: {error_code}")
            print(f"Error creating trail: {e}")

        return None

    except Exception as e:
        print(f"Unexpected error creating trail: {e}")
        return None

    # Start logging for the trail
    try:
        trail_client.start_logging(Name=trail_name)
        print(f"Logging started for trail: {trail_name}")

    except ClientError as e:
        print(f"Error starting trail logging: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error starting trail logging: {e}")
        return None

    return response


def main():
    # Create an STS client to get the AWS account ID.
    sts_client = boto3.client("sts")
    account_id = sts_client.get_caller_identity()["Account"]

    print(f"AWS Account ID: {account_id}")

    # Create the bucket that CloudTrail will log to.
    bucket_name = f"cloudtrail-logs-{account_id}"
    print(f"CloudTrail bucket: {bucket_name}")

    if s3enforce.CreateBucket(bucket_name) is None:
        sys.exit(1)

    # Enable versioning on the log bucket.
    if s3enforce.EnforceVersioning(bucket_name) is None:
        print("Failed to enable bucket versioning.")
        sys.exit(1)

    # Bucket policy that allows CloudTrail to write logs to the bucket.
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck20150319",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:GetBucketAcl",
                "Resource": f"arn:aws:s3:::{bucket_name}",
            },
            {
                "Sid": "AWSCloudTrailWrite20150319",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:PutObject",
                "Resource": (
                    f"arn:aws:s3:::{bucket_name}"
                    f"/AWSLogs/{account_id}/*"
                ),
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                },
            },
        ],
    }

    # Convert the policy dictionary to a JSON string.
    policy_string = json.dumps(policy)

    # Apply the bucket policy so CloudTrail can write logs.
    if s3enforce.SetBucketPolicy(bucket_name, policy_string) is None:
        print("Failed to apply the bucket policy.")
        sys.exit(1)

    # Create the trail and start logging to the bucket.
    trail_name = "CloudTrail"
    if CreateTrail(trail_name, bucket_name) is None:
        print("Failed to create the CloudTrail.")
        sys.exit(1)
    
    print("CloudTrail setup completed successfully.")
    return account_id


if __name__ == "__main__":
    main()
