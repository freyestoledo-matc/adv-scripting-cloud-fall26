import boto3

s3 = boto3.client("s3")

response = s3.list_buckets()

for bucket in response["Buckets"]:
    print(bucket["Name"])

    objects = s3.list_objects_v2(Bucket=bucket["Name"])

    if "Contents" in objects:
        for obj in objects["Contents"]:
            print(obj["Key"])
