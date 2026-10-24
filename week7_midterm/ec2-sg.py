
import boto3
import argparse
from botocore.exceptions import ClientError, BotoCoreError


# Function 1: Convert an inbound rule's protocol and port settings
# into a readable description.
def get_port_description(permission):
    protocol = permission.get('IpProtocol', '-1')

    # Protocol -1 means all traffic and all ports.
    if protocol == '-1':
        return 'All ports'

    # ICMP rules use type/code rather than TCP or UDP ports.
    if protocol in ('icmp', 'icmpv6'):
        from_port = permission.get('FromPort', 'All')
        to_port = permission.get('ToPort', 'All')
        return f'Type {from_port}, Code {to_port}'

    # TCP and UDP rules can specify one port or a port range.
    from_port = permission.get('FromPort')
    to_port = permission.get('ToPort')

    if from_port is None:
        return 'Ports not specified'
    elif from_port == to_port:
        return str(from_port)
    else:
        return f'{from_port}-{to_port}'


# Function 2: Check and display inbound rules for a security group.
def audit_security_group(group):
    group_name = group.get('GroupName', 'Unknown')
    group_id = group.get('GroupId', 'Unknown')
    permissions = group.get('IpPermissions', [])

    print('\n' + '=' * 65)
    print(f'Security Group: {group_name}')
    print(f'Security Group ID: {group_id}')
    print('=' * 65)

    # Branch if the group has no inbound rules.
    if not permissions:
        print('No inbound rules configured.')
        return

    # Examine each inbound permission in the security group.
    for permission in permissions:
        protocol = permission.get('IpProtocol', '-1')
        port_description = get_port_description(permission)

        # Check IPv4 CIDR ranges.
        for ip_range in permission.get('IpRanges', []):
            cidr = ip_range.get('CidrIp', 'Unknown')
            description = ip_range.get('Description', '')

            print(f'  Protocol: {protocol}')
            print(f'  IP Range: {cidr}')
            print(f'  Ports: {port_description}')

            if description:
                print(f'  Rule Description: {description}')

            # Flag inbound access from every IPv4 address.
            if cidr == '0.0.0.0/0':
                print('  WARNING: Open to the public internet!')

            print('-' * 40)

        # Also check IPv6 ranges for unrestricted public access.
        for ip_range in permission.get('Ipv6Ranges', []):
            cidr = ip_range.get('CidrIpv6', 'Unknown')
            description = ip_range.get('Description', '')

            print(f'  Protocol: {protocol}')
            print(f'  IPv6 Range: {cidr}')
            print(f'  Ports: {port_description}')

            if description:
                print(f'  Rule Description: {description}')

            if cidr == '::/0':
                print('  WARNING: Open to the public internet!')

            print('-' * 40)

        # Report rules that reference another security group or prefix list.
        # These sources are not CIDR ranges, so they are displayed separately.
        for source in permission.get('UserIdGroupPairs', []):
            source_id = source.get('GroupId', 'Unknown')
            print(f'  Source Security Group: {source_id}')
            print(f'  Protocol: {protocol}')
            print(f'  Ports: {port_description}')
            print('-' * 40)

        for source in permission.get('PrefixListIds', []):
            prefix_id = source.get('PrefixListId', 'Unknown')
            print(f'  Source Prefix List: {prefix_id}')
            print(f'  Protocol: {protocol}')
            print(f'  Ports: {port_description}')
            print('-' * 40)


# Function 3: Retrieve all groups or filter by a supplied group name.
def get_security_groups(security_group_name=None):
    ec2 = boto3.client('ec2', region_name='us-east-1')
    paginator = ec2.get_paginator('describe_security_groups')

    # Filter by exact security group name if the user supplied one.
    if security_group_name:
        pages = paginator.paginate(
            Filters=[
                {
                    'Name': 'group-name',
                    'Values': [security_group_name]
                }
            ]
        )
    else:
        # No filter means retrieve all security groups.
        pages = paginator.paginate()

    found_groups = []

    for page in pages:
        found_groups.extend(page.get('SecurityGroups', []))

    return found_groups


# Main section: Parse command-line arguments and run the audit.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Audit EC2 security group inbound rules for public access.'
    )

    # Accept either -s or --security-group to specify a group name.
    parser.add_argument(
        '-s',
        '--security-group',
        type=str,
        help='Name of the security group to audit. Omit to audit all groups.'
    )

    args = parser.parse_args()

    try:
        # Retrieve either the specified security group or all groups.
        groups = get_security_groups(args.security_group)

        # Branch if the requested group name was not found.
        if not groups:
            if args.security_group:
                print(
                    f"No security group found with name: "
                    f"{args.security_group}"
                )
            else:
                print('No security groups found in this AWS region.')

        else:
            print('\nEC2 SECURITY GROUP INBOUND RULE AUDIT')
            print('Checking for rules open to the public internet.')

            # Audit each group returned by AWS.
            for group in groups:
                audit_security_group(group)

    # Handle AWS API errors, including access-denied errors.
    except ClientError as error:
        code = error.response.get('Error', {}).get('Code', 'Unknown')
        message = error.response.get('Error', {}).get(
            'Message', 'No additional details'
        )
        print(f'\nAWS error: {code}')
        print(f'Details: {message}')
        print('Check your AWS credentials, permissions, and region.')

    # Handle other AWS SDK errors, such as connection failures.
    except BotoCoreError as error:
        print(f'\nAWS SDK error: {error}')
