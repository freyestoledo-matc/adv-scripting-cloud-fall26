import sys

import boto3
from botocore.exceptions import ClientError

DRYRUN = False # Set to True to perform a dry run without actually creating the instance

def get_image(ec2_client): # Function to get the latest Amazon Linux 2 AMI ID
    
    Filters = [
        {
            'Name': 'description',
            'Values': ['Amazon Linux 2 AMI*']
        },
        {
            'Name': 'architecture',
            'Values': ['x86_64']
        },
        {
            'Name': 'owner-alias',
            'Values': ['amazon']
        }
    ]

    image_data = ec2_client.describe_images(Filters=Filters)

    image_id = image_data['Images'][0]['ImageId']
    #print(f"Image ID: {image_id}")
    return image_id

def create_ec2(image_id, ec2_client):  # Function to create an EC2 instance

    response = ec2_client.run_instances(
        ImageId=image_id,
        InstanceType='t3.micro',
        MinCount=1,
        MaxCount=1,
        DryRun=DRYRUN, # Set to False to actually create the instance
        SecurityGroups=['WebSG'],
        KeyName='vockey',
        UserData='''
            #!/bin/bash -ex 
            # Updated to use Amazon Linux 2 
            yum -y update 
            yum -y install httpd php mysql php-mysql wget unzip 
            /usr/bin/systemctl enable httpd 
            /usr/bin/systemctl start httpd 
            cd /var/www/html 
            wget https://aws-tc-largeobjects.s3-us-west-2.amazonaws.com/CUR-TF-100-ACCLFO-2/lab6-scaling/lab-app.zip 
            unzip lab-app.zip -d /var/www/html/ 
            chown apache:root /var/www/html/rds.conf.php 
        '''
    )

    #print(response['Instances'][0]['InstanceId'])
    #print(f"EC2 instance created with ID: {instance_id}")
    instance_id = response['Instances'][0]['InstanceId'] #Get the instance ID from the AWS response
    return instance_id   

def print_instance_details(instance): #Information about the EC2 instance

    print(f"Instance ID: {instance.id}")
    print(f"Instance State: {instance.state['Name']}")
    print(f"Public DNS: {instance.public_dns_name}")
    print(f"Public IP: {instance.public_ip_address}")
    print(f"Tags: {instance.tags}") # Print the tags
    

def main():

    try:
        ec2_client = boto3.client("ec2")

        image_id = get_image(ec2_client)

        print("Latest Amazon Linux 2 AMI ID retrieved successfully.")
        print(f"Image ID: {image_id}")

        instance_id = create_ec2(image_id, ec2_client)
        print(f"EC2 instance created with ID: {instance_id}")

        ec2 = boto3.resource("ec2")
        instance = ec2.Instance(instance_id)

        instance.wait_until_running()
        instance.reload()

        print_instance_details(instance)

        instance.create_tags(
            Tags=[
                {
                    "Key": "Name",
                    "Value": "Fabian"
                }
            ]
        )

        instance.reload()
        print_instance_details(instance)

        print("Instance is running and details are updated.")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")

        if error_code == "UnauthorizedOperation":
            print("Unauthorized operation. Please check your region configuration.")
        else:
            print(f"AWS Error Code: {error_code}")

        sys.exit(1)


    ###instance.terminate()
    ###instance.wait_until_terminated()  # Wait until the instance is terminated

    ###print(f"EC2 instance with ID {instance.id} has been terminated.")


if __name__ == "__main__":
    main()