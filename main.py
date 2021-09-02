import boto3, base64
from time import sleep

from pkg_resources import require

######################################
############ My Functions ############
######################################

def require_custom_user_data_64():

    # Read the instances list from file
    with open("config/userdata.txt") as f:

        content = f.read()
        
        sample_string_bytes = content.encode("ascii")

        base64_bytes = base64.b64encode(sample_string_bytes)

        return base64_bytes.decode("ascii")

def create_spot_instance(client):

    # Create the spot instance
    response = client.request_spot_instances(
        InstanceCount=1,
        Type='one-time',
        LaunchSpecification={
            'ImageId': 'ami-08bac620dc84221eb',
            'KeyName': 'mervin-aws-playground',
            'InstanceType': 't3.large',
            'Placement': {
                'AvailabilityZone': 'eu-west-1c',
            },
            'BlockDeviceMappings': [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': 500,
                        'DeleteOnTermination': True,
                        'VolumeType': 'gp3',
                        'Iops': 300,
                        'Encrypted': False
                    },
                },
            ],
            'EbsOptimized': True,
            'Monitoring': {
                'Enabled': False
            },
            'SecurityGroupIds': [
                'sg-0ad89907670b9b627',
            ],
            'UserData': require_custom_user_data_64()
        },
        TagSpecifications=[
        {
            'ResourceType': 'spot-instances-request',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'pager-duty-reporting'
                },
                {
                    'Key': 'CreatorName',
                    'Value': 'mervin.hemaraju@checkout.com'
                },
            ]
        },
    ],
    InstanceInterruptionBehavior='terminate'
    )

    # Iterate through each spot instance created
    for spot in response["SpotInstanceRequests"]:

        # Return the first request ID
        return spot["SpotInstanceRequestId"]

def terminate_spot_instance(client, spot_request_id):
    
    # Cancel the spot instance
    response = client.cancel_spot_instance_requests(
        SpotInstanceRequestIds=[
            spot_request_id,
        ]
    )
    
    return response

def request_spot_request_waiter(client, request_id):

    # Get the waiter
    waiter = client.get_waiter('spot_instance_request_fulfilled')

    # Apply wait
    waiter.wait(
        SpotInstanceRequestIds=[
            request_id,
        ]
    )

def require_spot_instance_id(client, request_id):

    # Describe spot request
    response = client.describe_spot_instance_requests(
        SpotInstanceRequestIds=[
            request_id,
        ]
    )

    # Iterate through each requests
    for instance in response["SpotInstanceRequests"]:
        # Get the instance ID created
        return instance["InstanceId"]

def request_instance_status_checks_waiter(client, instance_id):

    # Get the waiter
    waiter = client.get_waiter('system_status_ok')

    # Apply waiter
    waiter.wait(
        InstanceIds=[
            instance_id,
        ]
    )

#####################################
########### Main Function ###########
#####################################
def lambda_handler(event, context):
    

    # Creates a boto3 EC2 client
    client = boto3.client('ec2')

    # Create the spot instance
    request_id = create_spot_instance(client)

    print(f"Spot request ID {request_id}")

    # Wait for request to be fulfilled
    request_spot_request_waiter(client, request_id)

    print("Spot request fulfilled!")

    # Fetch the instance ID created
    instance_id = require_spot_instance_id(client, request_id)

    print(f"Instance ID: {instance_id}")

    # Wait for system checks to pass
    request_instance_status_checks_waiter(client, instance_id)

    print("Instance is ready!")

    #sleep(3400)

    # Terminate the spot instance
    #response = terminate_spot_instance(client, request_id)
    #print(response)