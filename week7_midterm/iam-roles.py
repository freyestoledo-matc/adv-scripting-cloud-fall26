
import boto3
import datetime
import pytz
from botocore.exceptions import ClientError, BotoCoreError


# Function 1: Find IAM roles created within the last 90 days.
def get_recent_roles(days=90):
    """Return IAM roles created within the specified number of days."""

    # Create an IAM client and paginator to retrieve all roles.
    iam = boto3.client('iam')
    paginator = iam.get_paginator('list_roles')

    # Calculate the cutoff date using UTC and pytz.
    utc_now = datetime.datetime.now(pytz.utc)
    age_limit = utc_now - datetime.timedelta(days=days)

    recent_roles = []

    # Loop through every page of IAM roles.
    for page in paginator.paginate():
        for role in page['Roles']:

            # Only include roles created within the last 90 days.
            create_date = role['CreateDate']

            # Ensure the creation date is timezone-aware.
            if create_date.tzinfo is None:
                create_date = pytz.utc.localize(create_date)

            if create_date > age_limit:
                recent_roles.append({
                    'RoleName': role['RoleName'],
                    'Arn': role['Arn'],
                    'CreateDate': create_date
                })

    return recent_roles


# Function 2: Retrieve managed and inline policies for one role.
def get_role_policy_info(iam, role_name):
    """Return the managed and inline policies attached to a role."""

    attached = []
    inline = []
    attached_error = None
    inline_error = None

    # List managed policies attached to this specific role.
    try:
        resp = iam.list_attached_role_policies(RoleName=role_name)
        attached = resp['AttachedPolicies']

    except ClientError as e:
        attached_error = e.response.get('Error', {}).get(
            'Code', 'Unknown error'
        )

    # List inline (unmanaged) policies for this specific role.
    try:
        resp = iam.list_role_policies(RoleName=role_name)
        inline = resp['PolicyNames']

    except ClientError as e:
        inline_error = e.response.get('Error', {}).get(
            'Code', 'Unknown error'
        )

    return {
        'attached': attached,
        'inline': inline,
        'attached_error': attached_error,
        'inline_error': inline_error
    }


# Main section: Run the audit and display the results.
if __name__ == '__main__':

    try:
        # Create the IAM client and retrieve recent roles.
        iam = boto3.client('iam')
        roles = get_recent_roles(days=90)

        print('=' * 65)
        print('IAM ROLE POLICY AUDIT')
        print('Roles created within the last 90 days')
        print('=' * 65)

        # Branch depending on whether any recent roles were found.
        if roles:
            for role in roles:
                print(f"\nRole: {role['RoleName']}")
                print(f"Created: {role['CreateDate']}")

                # Retrieve policies only for this recent role.
                policy_info = get_role_policy_info(
                    iam, role['RoleName']
                )

                # Display attached managed policies.
                print('\n  Attached Managed Policies:')

                if policy_info['attached_error']:
                    print(
                        '    Unable to list policies: '
                        f"{policy_info['attached_error']}"
                    )
                elif policy_info['attached']:
                    for policy in policy_info['attached']:
                        print(f"    - {policy['PolicyName']}")
                else:
                    print('    No attached managed policies found.')

                # Display unmanaged policy names.
                print('\n  Unmanaged Policies:')

                if policy_info['inline_error']:
                    print(
                        '    Unable to list policies: '
                        f"{policy_info['inline_error']}"
                    )
                elif policy_info['inline']:
                    for policy_name in policy_info['inline']:
                        print(f"    - {policy_name}")
                else:
                    print('    No unmanaged policies found.')

                print('-' * 65)

        else:
            print('\nNo IAM roles created in the last 90 days.')

    # Handle AWS API errors that prevent the audit from running.
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', 'Unknown')
        print(f'\nAWS error: {code}')
        print('Check your AWS credentials and IAM permissions.')

    # Handle other AWS SDK errors, such as connection issues.
    except BotoCoreError as e:
        print(f'\nAWS SDK error: {e}')
