
#########################################
############# Instance Specs ############
#########################################

def require_instance_launch_specifications(userdata):
    return {
        "ImageId": "ami-0585cc9245d7565e4",
        "KeyName": "mervin-aws-playground",
        "InstanceType": "t4g.micro",
        "Placement": {
            "AvailabilityZone": "eu-west-1c",
        },
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "VolumeSize": 500,
                    "DeleteOnTermination": True,
                    "VolumeType": "gp3",
                    "Iops": 300,
                    "Encrypted": False
                },
            },
        ],
        "EbsOptimized": True,
        "Monitoring": {
            "Enabled": False
        },
        "SecurityGroupIds": [
            "sg-0ad89907670b9b627",
        ],
        "UserData": userdata
    }


SPECS_INSTANCE_LAUNCH_TAGS = [
    {
        'Key': 'Name',
        'Value': 'pager-duty-reporting'
    },
    {
        'Key': 'CreatorName',
        'Value': 'mervin.hemaraju@checkout.com'
    },
]
