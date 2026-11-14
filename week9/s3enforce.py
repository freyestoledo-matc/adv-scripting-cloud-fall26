"""Create or delete an S3 bucket using boto3."""

import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError


def CreateBucket(bucket_name):
    """Create an S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket to create.

    Returns:
        The bucket name on success, None on failure.
    """
    # Create the S3 client
    try:
        s3client = boto3.client("s3")
        region = s3client.meta.region_name
        print(f"AWS Region: {region}")
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return None

    # Create the bucket
    try:
        if region == "us-east-1":
            s3client.create_bucket(Bucket=bucket_name)
        else:
            s3client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": region
                },
            )

        print(f"Bucket created: {bucket_name}")
        return bucket_name

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")

        if error_code == "BucketAlreadyOwnedByYou":
            # Treat an existing bucket as success so reruns continue.
            print(f"You already own bucket: {bucket_name}")
            return bucket_name
        elif error_code == "BucketAlreadyExists":
            print(f"Bucket name already taken: {bucket_name}")
        elif error_code in (
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
            print(f"Error creating bucket: {e}")

        return None

    except Exception as e:
        print(f"Unexpected error creating bucket: {e}")
        return None


def DeleteBucket(bucket_name):
    """Delete an S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket to delete.

    Returns:
        The bucket name on success, None on failure.
    """
    # Create the S3 client
    try:
        s3client = boto3.client("s3")
        region = s3client.meta.region_name
        print(f"AWS Region: {region}")
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return None

    # Delete the bucket
    try:
        s3client.delete_bucket(Bucket=bucket_name)

        print(f"Bucket deleted: {bucket_name}")
        return bucket_name

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")

        if error_code == "NoSuchBucket":
            print(f"Bucket does not exist: {bucket_name}")
        elif error_code == "BucketNotEmpty":
            print(f"Bucket is not empty: {bucket_name}")
            print("Empty the bucket before deleting it.")
        elif error_code == "AccessDenied":
            print(f"Access denied deleting bucket: {bucket_name}")
        elif error_code in (
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
            print(f"Error deleting bucket: {e}")

        return None

    except Exception as e:
        print(f"Unexpected error deleting bucket: {e}")
        return None


def EnforceVersioning(bucket_name):
    """Enable versioning on an S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket to version.

    Returns:
        The bucket name on success, None on failure.
    """
    # Create the S3 client
    try:
        s3client = boto3.client("s3")
        region = s3client.meta.region_name
        print(f"AWS Region: {region}")
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return None

    # Enable versioning on the bucket
    try:
        s3client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                "MFADelete": "Disabled",
                "Status": "Enabled",
            },
        )

        print(f"Versioning enabled for bucket: {bucket_name}")
        return bucket_name

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")

        if error_code == "NoSuchBucket":
            print(f"Bucket does not exist: {bucket_name}")
        elif error_code == "AccessDenied":
            print(f"Access denied versioning bucket: {bucket_name}")
        elif error_code in (
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
            print(f"Error enabling versioning: {e}")

        return None

    except Exception as e:
        print(f"Unexpected error enabling versioning: {e}")
        return None


def SetBucketPolicy(bucket_name, policy):
    """Set the bucket policy on an S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket to update.
        policy: Bucket policy document as a JSON string.

    Returns:
        The bucket name on success, None on failure.
    """
    # Create the S3 client
    try:
        s3client = boto3.client("s3")
        region = s3client.meta.region_name
        print(f"AWS Region: {region}")
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return None

    # Set the bucket policy
    try:
        s3client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=policy,
        )

        print(f"Bucket policy applied to bucket: {bucket_name}")
        return bucket_name

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")

        if error_code == "NoSuchBucket":
            print(f"Bucket does not exist: {bucket_name}")
        elif error_code == "AccessDenied":
            print(f"Access denied setting policy on bucket: {bucket_name}")
        elif error_code == "MalformedPolicy":
            print(f"Malformed bucket policy for bucket: {bucket_name}")
        elif error_code in (
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
            print(f"Error setting bucket policy: {e}")

        return None

    except Exception as e:
        print(f"Unexpected error setting bucket policy: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Create an S3 bucket and enforce versioning and policy"
    )
    parser.add_argument(
        "bucket_name",
        help="The name of the S3 bucket to create",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the bucket instead of creating it",
    )
    parser.add_argument(
        "--policy",
        default=None,
        help=(
            "Bucket policy as an inline JSON string, "
            "or the path to a JSON file"
        ),
    )
    args = parser.parse_args()

    bucket_name = args.bucket_name.lower()
    print(f"Bucket name: {bucket_name}")

    # Deleting is a separate flow
    if args.delete:
        if DeleteBucket(bucket_name) is None:
            sys.exit(1)
        return

    # Create the bucket
    created = CreateBucket(bucket_name)

    # Enable versioning on the bucket
    versioned = EnforceVersioning(bucket_name)

    # Optionally apply a bucket policy
    policy_ok = True
    if args.policy:
        if args.policy.lstrip().startswith("{"):
            policy = args.policy
        else:
            try:
                with open(args.policy, "r", encoding="utf-8") as file:
                    policy = file.read()
            except OSError as e:
                print(f"Error reading policy file: {e}")
                sys.exit(1)

        policy_ok = SetBucketPolicy(bucket_name, policy) is not None

    if created is None or versioned is None or not policy_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
