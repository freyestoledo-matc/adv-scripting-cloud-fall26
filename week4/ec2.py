import boto3

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
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        DryRun=DRYRUN # Set to False to actually create the instance
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

    ec2_client = boto3.client('ec2') # Create an EC2 client
    image_id = get_image(ec2_client) # Find the latest Amazon Linux 2 AMI ID

    print(f"Latest Amazon Linux 2 AMI ID retrieved successfully.") 
    print(f"Image ID: {image_id}")

    instance_id = create_ec2(image_id, ec2_client) # Create the instance and get the instance ID

    print(f"EC2 instance created with ID: {instance_id}")

    ec2 = boto3.resource('ec2') # Create an EC2 resource object
    instance = ec2.Instance(instance_id)  # Create an instance object using the instance ID

    instance.wait_until_running() # Wait until the instance is running
    instance.reload()

    print_instance_details(instance)   # ← tags should be []

    instance.create_tags( # Add tags to the instance
        Tags=[
            {
                'Key': 'Name',
                'Value': 'Fabian'
            }
        ]
    )

    instance.reload()  # Refresh the instance attributes

    print_instance_details(instance) #print the instance details and new tag

    print("Instance is running and details are updated.")

    instance.terminate()
    instance.wait_until_terminated()  # Wait until the instance is terminated

    print(f"EC2 instance with ID {instance.id} has been terminated.")


if __name__ == "__main__":
    main()