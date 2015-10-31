#!/usr/bin/env python

from ansible.module_utils.basic import *

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

AZURE_VIRUTAL_MACHINE_SIZE_TYPES = ['ExtraSmall',
                    'Small',
                    'Medium',
                    'Large',
                    'ExtraLarge',
                    'A5',
                    'A6',
                    'A7',
                    'A8',
                    'A9',
                    'Basic_A0',
                    'Basic_A1',
                    'Basic_A2',
                    'Basic_A3',
                    'Basic_A4',
                    'Standard_D1',
                    'Standard_D2',
                    'Standard_D3',
                    'Standard_D4',
                    'Standard_D11',
                    'Standard_D12',
                    'Standard_D13',
                    'Standard_D14',
                    'Standard_DS1',
                    'Standard_DS2',
                    'Standard_DS3',
                    'Standard_DS4',
                    'Standard_DS11',
                    'Standard_DS12',
                    'Standard_DS13',
                    'Standard_DS14',
                    'Standard_G1',
                    'Standard_G2',
                    'Standard_G3',
                    'Standard_G4',
                    'Standard_G5']

def azure_object_to_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def get_token_from_client_credentials(module, endpoint, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.core.windows.net/',
    }
    response = requests.post(endpoint, data=payload).json()
    if 'access_token' not in response:
        module.fail_json(msg="Sorry, it looks like the credentials you've provided were incorrect.",response=response)
    return response['access_token']

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

def delete_network_interface(module, creds):
    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)

    result = network_client.network_interfaces.delete(
        module.params.get('group_name'),
        module.params.get('network_interface_name')
    )

    return (True, azure_object_to_json(result))

def create_network_interface(module, creds):
    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)

    subnet = network_client.subnets.get(
        module.params.get('group_name'),
        module.params.get('virtual_network_name'),
        module.params.get('subnet_name')).subnet

    public_ip_address = network_client.public_ip_addresses.get(
        module.params.get('group_name'),
        module.params.get('public_ip_name')).public_ip_address

    result = network_client.network_interfaces.create_or_update(
        module.params.get('group_name'),
        module.params.get('network_interface_name'),
        azure.mgmt.network.NetworkInterface(
            name=module.params.get('network_interface_name'),
            location=module.params.get('region'),
            ip_configurations=[
                azure.mgmt.network.NetworkInterfaceIpConfiguration(
                    name='default',
                    private_ip_allocation_method=azure.mgmt.network.IpAllocationMethod.dynamic,
                    subnet=subnet,
                    public_ip_address=public_ip_address
                ),
            ],
        ),
    )

    result = network_client.network_interfaces.get(
        module.params.get('group_name'),
        module.params.get('network_interface_name')
    )

    # we get a tacking operation ID so we should wait for that
    return (True, azure_object_to_json(result.network_interface))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, choices=["absent", "present"]),
            group_name=dict(required=True),
            subnet_name=dict(required=True),
            virtual_network_name=dict(required=True),
            network_interface_name=dict(required=True),
            public_ip_name=dict(required=True),
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
        (changed, network_interface) = delete_network_interface(module, creds)
    elif module.params.get('state') == 'present':
        (changed, network_interface) = create_network_interface(module, creds)

    # module.exit_json(changed=changed, public_dns_name=public_dns_name, deployment=json.loads(json.dumps(deployment, default=lambda o: o.__dict__)))
    module.exit_json(changed=changed, network_interface=network_interface)

if __name__ == '__main__':
    main()
