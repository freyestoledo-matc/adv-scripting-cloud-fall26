
"""
Student Choice: S3 Bucket Security Audit

This script audits Amazon S3 buckets by checking their Block Public Access configurations.
It identifies buckets with all four protections enabled and flags buckets that have
disabled protections or lack a bucket-level configuration.
This helps identify potential security concerns that may require further investigation.

The audit does not independently determine whether a bucket is publicly accessible.
"""

import boto3
from botocore.exceptions import ClientError


# Create an S3 client to communicate with AWS.
s3_client = boto3.client("s3")


def audit_s3_buckets():
    """Audit S3 bucket public-access block settings."""

    try:
        # Retrieve all S3 buckets in the current AWS account.
        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            print("No S3 buckets were found in this account.")
            return

        # Initialize counters for the final audit summary.
        total_buckets = 0
        fully_protected = 0
        missing_configuration = 0
        disabled_protections = 0
        access_errors = 0

        print("=" * 60)
        print("S3 BUCKET SECURITY AUDIT")
        print("=" * 60)

        # Check each bucket's public-access block configuration.
        for bucket in buckets:
            bucket_name = bucket["Name"]
            total_buckets += 1

            print(f"\nBucket: {bucket_name}")

            try:
                # Retrieve the bucket-level public-access settings.
                result = s3_client.get_public_access_block(
                    Bucket=bucket_name
                )

                settings = result[
                    "PublicAccessBlockConfiguration"
                ]

                # Check whether each of the four protections is enabled.
                protections = {
                    "BlockPublicAcls": settings.get(
                        "BlockPublicAcls", False
                    ),
                    "IgnorePublicAcls": settings.get(
                        "IgnorePublicAcls", False
                    ),
                    "BlockPublicPolicy": settings.get(
                        "BlockPublicPolicy", False
                    ),
                    "RestrictPublicBuckets": settings.get(
                        "RestrictPublicBuckets", False
                    ),
                }

                # Print the status of each protection.
                for name, enabled in protections.items():
                    status = "ENABLED" if enabled else "DISABLED"
                    print(f"  {name}: {status}")

                # Update the summary based on the configuration.
                if all(protections.values()):
                    fully_protected += 1
                    print("  Result: All four protections enabled.")
                else:
                    disabled_protections += 1
                    print(
                        "  WARNING: One or more public-access "
                        "protections are disabled!"
                    )

            except ClientError as error:
                # Handle missing configurations and permission errors.
                error_code = error.response.get(
                    "Error", {}
                ).get("Code", "Unknown")

                if error_code == (
                    "NoSuchPublicAccessBlockConfiguration"
                ):
                    missing_configuration += 1
                    print(
                        "  WARNING: No bucket-level public-access "
                        "block configuration was found."
                    )

                elif error_code in (
                    "AccessDenied",
                    "AccessDeniedException",
                ):
                    access_errors += 1
                    print(
                        "  ERROR: Permission denied when checking "
                        "this bucket's settings."
                    )
                else:
                    access_errors += 1
                    print(
                        f"  ERROR: Could not audit this bucket "
                        f"({error_code})."
                    )

        # Display the final audit summary.
        print("\n" + "=" * 60)
        print("AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total buckets found: {total_buckets}")
        print(f"All four protections enabled: {fully_protected}")
        print(f"Protections disabled: {disabled_protections}")
        print(
            "Missing bucket-level configuration: "
            f"{missing_configuration}"
        )
        print(f"Buckets with audit errors: {access_errors}")
        print("=" * 60)
        print("Audit complete.")

    except ClientError as error:
        # Handle errors when listing buckets.
        error_code = error.response.get(
            "Error", {}
        ).get("Code", "Unknown")
        print(f"ERROR: Could not list S3 buckets ({error_code}).")


# Run the audit when the script is executed directly.
if __name__ == "__main__":
    audit_s3_buckets()
