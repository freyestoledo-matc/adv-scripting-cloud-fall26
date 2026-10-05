import boto3 
import ec2 
from sns import create_sns_topic, subscribe_email_to_topic


DRY_RUN = False  # Set to True to test the stop operation without actually stopping the instance.

def put_metric_alarm(account_id,instance_id):
    cw_client = boto3.client('cloudwatch')
    cw_client.put_metric_alarm(
        AlarmName='Web_Server_LOW_CPU_Utilization',
        ComparisonOperator='LessThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=300,
        Statistic='Average',
        Threshold=10.0,
        ActionsEnabled=True,
        AlarmActions=[f'arn:aws:swf:us-east-1:{account_id}:action/actions/AWS_EC2.InstanceId.Stop/1.0',
                      f'arn:aws:sns:us-east-1:{account_id}:TestTopic'],
              # Replace with your region if different
        AlarmDescription='Alarm to stop EC2 instance when CPU is lower than10%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id  # Replace with your instance ID
            },
        ],
    )


def main():
    # Create an STS client to get the AWS account ID.
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()['Account']

    # Create an EC2 client to interact with the EC2 service.
    ec2_client = boto3.client('ec2')

    # Get the latest Amazon Linux 2 AMI ID.
    image_id = ec2.get_image(ec2_client)

    # Create an EC2 instance and get the instance ID.
    instance_id = ec2.create_ec2(image_id, ec2_client)

    # Create an EC2 resource to interact with the EC2 service.
    ec2_resource = boto3.resource('ec2')
    instance = ec2_resource.Instance(instance_id)

    # Wait until the instance is running.
    print(f"Instance {instance_id} is starting...")
    instance.wait_until_running()
    instance.reload()  # Refresh the instance attributes.
    print(f"Instance {instance_id} is now running.")


    #create SNS topic and subscribe email
    topic_arn = create_sns_topic("TestTopic")
    email_address = "fabicircus@gmail.com"
    subscribe_email_to_topic(topic_arn, email_address)


    put_metric_alarm(account_id, instance_id)
    print(f"CloudWatch alarm for low CPU utilization has been created for instance {instance_id}.")

if __name__ == "__main__":
    main()  # Call the main function to execute the script
    