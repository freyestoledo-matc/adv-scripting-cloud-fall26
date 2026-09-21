import boto3
import json

def get_latest_amazon_linux_2_ami():
    client = boto3.client('ec2')

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

    image_data = client.describe_images(Filters=Filters)

    image_id = image_data['Images'][0]['ImageId']
    #print(f"Image ID: {image_id}")
    return image_id

def create_ec2_instance(image_id):  
    ec2 = boto3.client('ec2')

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        DryRun=False # Set tp False to actually create the instance
    )

    #print(response['Instances'][0]['InstanceId'])
    #print(f"EC2 instance created with ID: {instance_id}")
    return response['Instances'][0]['InstanceId']  # Return the instance object

def print_instance_details(instance):

    print(f"Instance ID: {instance.id}")
    print(f"Instance State: {instance.state['Name']}")
    print(f"Public DNS: {instance.public_dns_name}")
    print(f"Public IP: {instance.public_ip_address}")
    
    
def main():
    image_id = get_latest_amazon_linux_2_ami()
    print(f"Latest Amazon Linux 2 AMI ID retrieved successfully.") 
    print(f"Image ID: {image_id}")

    instance_id = create_ec2_instance(image_id) #create the instance and get the instance ID
    print(f"EC2 instance created with ID: {instance_id}")

    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)  # Create an instance object using the instance ID

    instance.wait_until_running() # Wait until the instance is running
    instance.reload()  # Refresh the instance attributes
    print_instance_details(instance) #print the instance details

    print("Instance is running and details are updated.")
    instance.terminate()
    instance.wait_until_terminated()  # Wait until the instance is terminated
    print(f"EC2 instance with ID {instance.id} has been terminated.")


if __name__ == "__main__":
    main()