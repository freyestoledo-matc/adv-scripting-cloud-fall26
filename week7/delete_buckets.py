import boto3
import sys
from botocore.exceptions import ClientError

# Create an S3 client
s3client = boto3.client("s3")

try:
    # Get all buckets in the account
    response = s3client.list_buckets()
    buckets = response["Buckets"]

    if not buckets:
        print("No S3 buckets found.")
        sys.exit(0)

    print("The following buckets will be deleted:")
    for bucket in buckets:
        print(f"- {bucket['Name']}")

    confirmation = input(
        "\nWARNING: This will permanently delete these buckets and their objects.\n"
        "Type DELETE to continue: "
    )

    if confirmation != "DELETE":
        print("Deletion cancelled.")
        sys.exit(0)

    # Loop through all buckets
    for bucket in buckets:
        bucket_name = bucket["Name"]
        print(f"\nProcessing bucket: {bucket_name}")

        # List objects in the bucket
        paginator = s3client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                # Delete each object
                s3client.delete_object(
                    Bucket=bucket_name,
                    Key=obj["Key"]
                )
                print(f"Deleted object: {obj['Key']}")

        # Delete the bucket after its objects are deleted
        s3client.delete_bucket(Bucket=bucket_name)
        print(f"Deleted bucket: {bucket_name}")

    print("\nFinished processing all buckets.")

except ClientError as e:
    error_code = e.response.get("Error", {}).get(
        "Code", "Unknown"
    )
    print(f"AWS Error Code: {error_code}")
    print(f"Error: {e}")
    sys.exit(1)