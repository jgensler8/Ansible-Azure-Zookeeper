#!/usr/bin/env python

from ansible.module_utils.basic import *

# from azure.mgmt.common import SubscriptionCloudCredentials
from azure.mgmt.common import SubscriptionCloudCredentials
import azure.mgmt.compute
import azure.mgmt.network
import azure.mgmt.resource
import azure.mgmt.storage
import requests

DOCUMENTATION = '''
---
module: customazure
version_added: "0.0.1"
author: Jeff Gensler
short_description: Interface with newer azure pip thing
description:
   - same as other azure module
options:
  compute:
  ...
'''

EXAMPLES = '''
customazure:
  vm: ...
  image: ...
  ...
'''

AZURE_REGIONS = ['South Central US',
                   'Central US',
                   'East US 2',
                   'East US',
                   'West US',
                   'North Central US',
                   'North Europe',
                   'West Europe',
                   'East Asia',
                   'Southeast Asia',
                   'Japan West',
                   'Japan East',
                   'Brazil South']

def azure_object_to_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def get_token_from_client_credentials(module, endpoint, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.core.windows.net/',
    }
    response = requests.post(endpoint, data=payload)
    try:
        decoded_json = response.json()
    except:
        module.fail_json(msg="UHOH, the response couldn't be decoded into json.", response=response.text)
    if 'access_token' not in decoded_json:
        module.fail_json(msg="Sorry, it looks like the credentials you've provided were incorrect.",response=response.text)
    return decoded_json['access_token']

def get_azure_creds(module):

    # management_cert_path = module.params.get('management_cert_path')
    # if not management_cert_path:
    #     management_cert_path = os.environ.get('AZURE_CERT_PATH', None)
    # if not management_cert_path:
    #     module.fail_json(msg="No management_cert_path provided. Please set 'AZURE_CERT_PATH' or use the 'management_cert_path' parameter")

    client_id = module.params.get('client_id')
    if not client_id:
        client_id = os.environ.get('AZRUE_CLIENT_ID', None)
    if not client_id:
        module.fail_json(msg="No azure_client_id provided. Please set 'AZURE_CLIENT_ID' or use the 'azure_client_id' parameter")

    client_secret = module.params.get('client_secret')
    if not client_secret:
        client_secret = os.environ.get('AZRUE_CLIENT_SECRET', None)
    if not client_secret:
        module.fail_json(msg="No azure_client_secret provided. Please set 'AZURE_CLIENT_SECRET' or use the 'azure_client_secret' parameter")

    oauth_endpoint = module.params.get('oauth_endpoint')
    if not oauth_endpoint:
        oauth_endpoint = os.environ.get('AZRUE_OAUTH_ENDPOINT', None)
    if not oauth_endpoint:
        module.fail_json(msg="No azure_client_secret provided. Please set 'AZRUE_OAUTH_ENDPOINT' or use the 'azure_oauth_endpoint' parameter")

    # Check module args for credentials, then check environment vars
    subscription_id = module.params.get('subscription_id')
    if not subscription_id:
        subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID', None)
    if not subscription_id:
        module.fail_json(msg="No subscription_id provided. Please set 'AZURE_SUBSCRIPTION_ID' or use the 'subscription_id' parameter")

    auth_token = get_token_from_client_credentials(module, oauth_endpoint, client_id, client_secret)

    return SubscriptionCloudCredentials(subscription_id, auth_token)

def remove_resource_group(module, creds):
    resource_client = azure.mgmt.resource.ResourceManagementClient(creds)

    result = resource_client.resource_groups.delete(
        module.params.get('group_name'))

    return (True, azure_object_to_json(result))

def create_resource_group(module, creds):
    resource_client = azure.mgmt.resource.ResourceManagementClient(creds)

    result = resource_client.resource_groups.create_or_update(
        module.params.get('group_name'),
        azure.mgmt.resource.ResourceGroup(
            location=module.params.get('region'),
        ),
    )

    return (True, azure_object_to_json(result.resource_group))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, choices=["absent", "present"]),
            group_name=dict(required=True),
            region=dict(required=True, choices=AZURE_REGIONS),
            subscription_id=dict(required=True, no_log=True),
            client_id=dict(required=True, no_log=True),
            client_secret=dict(required=True, no_log=True),
            oauth_endpoint=dict(required=True, no_log=True)
        )
    )
    # create azure ServiceManagementService object
    creds = get_azure_creds(module)

    if module.params.get('state') == 'absent':
        changed, something = remove_resource_group(module, creds)
    elif module.params.get('state') == 'present':
        changed, something = create_resource_group(module, creds)

    # module.exit_json(changed=changed, public_dns_name=public_dns_name, deployment=json.loads(json.dumps(deployment, default=lambda o: o.__dict__)))
    module.exit_json(changed=changed, resource_group=something)

if __name__ == '__main__':
    main()
