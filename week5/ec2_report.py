import boto3
import csv
import ec2

def Get_Instances():
    ec2_client = boto3.client("ec2")
    paginator = ec2_client.get_paginator("describe_instances")
    page_list = paginator.paginate()

    response = []
    for page in page_list:
        for reservation in page["Reservations"]:
            response.append(reservation)
    return response


def CSV_Writer(header, content):
    with open("export.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for row in content:
            writer.writerow(row)

def generate_test_instances():
    image_id = ec2.get_latest_amazon_linux_2_ami_id()
    print(f"Latest Amazon Linux 2 AMI ID retrieved successfully.")
    print(f"Image ID: {image_id}")

    instance_id = ec2.create_ec2_instance(image_id)
    print(f"EC2 instance created with ID: {instance_id}")

def main():
    header = ["InstanceId", "InstanceType", "State", "PublicIpAddress"]
    content = []

    instances = Get_Instances()
    for reservation in instances:
        for instance in reservation["Instances"]:
            row = {
                "InstanceId": instance["InstanceId"],
                "InstanceType": instance["InstanceType"],
                "State": instance["State"]["Name"],
                "PublicIpAddress": instance.get("PublicIpAddress", ""),
            }
            content.append(row)

    CSV_Writer(header, content)


if __name__ == "__main__":
    main()