import boto3
import csv
import ec2

def Get_Instances(Name=None, Value=None): # This function retrieves EC2 instances from AWS.
    # Name and Value are optional arguments that allow us to
    # add additional filters when searching for instances.

    ec2_client = boto3.client("ec2")     # Create an EC2 client so the script can communicate with the AWS EC2 service.
    paginator = ec2_client.get_paginator("describe_instances") # The paginator automatically retrieves additional pages of results for us.

    # Only retrieve EC2 instances that are currently running.
    Filters = [      
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
            ]
        },
    ]
    # Add an additional filter when Name and Value are provided.
    if Name:
        Filters.append(
            {
                'Name': Name,
                'Values': [Value],
            }
        )

    # Use the paginator to retrieve all pages of EC2 instances that match the filters.
    page_list = paginator.paginate(Filters=Filters)

    response = []  # Create an empty list to store the reservations returned from all of the pages.
    for page in page_list:
        for reservation in page["Reservations"]:
            response.append(reservation)
    return response


def CSV_Writer(header, content):
    # This function writes the EC2 report information to a CSV file called export.csv.

    # header contains the column names.
    # content contains the EC2 instance information.

    with open("export.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for row in content:
            writer.writerow(row)

def generate_test_instances():
    # This function uses the EC2 functions from the ec2.py file to create a test EC2 instance.

    image_id = ec2.get_latest_amazon_linux_2_ami_id()
    print(f"Latest Amazon Linux 2 AMI ID retrieved successfully.")
    print(f"Image ID: {image_id}")

    instance_id = ec2.create_ec2_instance(image_id)
    print(f"EC2 instance created with ID: {instance_id}")

def main():
    header = ["InstanceId", "InstanceType", "State", "PublicIpAddress", "MonitoringState", "InstanceName"]
    content = []

    instances = Get_Instances("instance-type", "t2.micro")
    for reservation in instances:
        for instance in reservation["Instances"]:
            row = {
                "InstanceId": instance["InstanceId"],
                "InstanceType": instance["InstanceType"],
                "State": instance["State"]["Name"],
                "PublicIpAddress": instance.get("PublicIpAddress", "N/A"),
                "MonitoringState": instance.get("Monitoring", {}).get("State", "N/A"),
                "InstanceName": next(
                    (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"),
                    "N/A",
                ),
            }
            content.append(row)

    CSV_Writer(header, content)  # Write the report information to export.csv.

    print(",".join(header))
    for row in content:
        print(",".join(str(row[column]) for column in header))


if __name__ == "__main__":
    main()