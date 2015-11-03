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

def terminate_virtual_machine(module, creds):
    compute_client = azure.mgmt.compute.ComputeManagementClient(creds)

    result = compute_client.virtual_machines.delete(
        module.params.get('group_name'),
        module.params.get('vm_name')
    )

    return (True, azure_object_to_json(result) )

def create_virtual_machine(module, creds):
    compute_client = azure.mgmt.compute.ComputeManagementClient(creds)
    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)

    network_interface_id = network_client.network_interfaces.get(
            module.params.get('group_name'),
            module.params.get('network_interface_name')
        ).network_interface.id

    # virtual_machine_size = module.params.get('virtual_machine_size')
    virtual_machine_size = azure.mgmt.compute.VirtualMachineSizeTypes.standard_a0

    ssh_keys = map(lambda data: azure.mgmt.compute.SshPublicKey(
        key_data=data,
        path="/home/" + module.params.get('admin_username') + "/.ssh/authorized_keys"
    ), module.params.get('public_keys') )

    result = compute_client.virtual_machines.create_or_update(
        module.params.get('group_name'),
        azure.mgmt.compute.VirtualMachine(
            location=module.params.get('region'),
            name=module.params.get('vm_name'),
            os_profile=azure.mgmt.compute.OSProfile(
                admin_username=module.params.get('admin_username'),
                admin_password=module.params.get('admin_password'),
                computer_name=module.params.get('computer_name'),
                linux_configuration=azure.mgmt.compute.LinuxConfiguration(
                    ssh_configuration=azure.mgmt.compute.SshConfiguration(
                        disable_password_authentication=True,
                        public_keys=ssh_keys
                    )
                )
            ),
            hardware_profile=azure.mgmt.compute.HardwareProfile(
                virtual_machine_size=virtual_machine_size
            ),
            network_profile=azure.mgmt.compute.NetworkProfile(
                network_interfaces=[
                    azure.mgmt.compute.NetworkInterfaceReference(
                        reference_uri=network_interface_id,
                    ),
                ],
            ),
            storage_profile=azure.mgmt.compute.StorageProfile(
                os_disk=azure.mgmt.compute.OSDisk(
                    caching=azure.mgmt.compute.CachingTypes.none,
                    create_option=azure.mgmt.compute.DiskCreateOptionTypes.from_image,
                    name=module.params.get('os_disk_name'),
                    virtual_hard_disk=azure.mgmt.compute.VirtualHardDisk(
                        uri='https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
                            module.params.get('storage_name'),
                            module.params.get('os_disk_name'),
                        ),
                    ),
                ),
                image_reference = azure.mgmt.compute.ImageReference(
                    publisher=module.params.get('image_publisher'),
                    offer=module.params.get('image_offer'),
                    sku=module.params.get('image_sku'),
                    version=module.params.get('image_version'),
                ),
            ),
        ),
    )

    result = compute_client.virtual_machines.get(
        module.params.get('group_name'),
        module.params.get('vm_name')
    )

    # we get a tacking operation ID so we should wait for that
    return (True, azure_object_to_json(result.virtual_machine))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, choices=["absent", "present"]),
            group_name=dict(required=True),
            storage_name=dict(required=True),
            virtual_network_name=dict(required=True),
            subnet_name=dict(required=True),
            network_interface_name=dict(required=True),
            vm_name=dict(required=True),
            os_disk_name=dict(required=True),
            public_ip_name=dict(required=True),
            computer_name=dict(required=True),
            admin_username=dict(required=True),
            admin_password=dict(required=True),
            public_keys=dict(required=True),
            region=dict(required=True, choices=AZURE_REGIONS),
            image_publisher=dict(required=True),
            image_offer=dict(required=True),
            image_sku=dict(required=True),
            image_version=dict(required=True),
            virtual_machine_size_type=dict(required=True, choice=AZURE_VIRUTAL_MACHINE_SIZE_TYPES),
            subscription_id=dict(required=True, no_log=True),
            client_id=dict(required=True, no_log=True),
            client_secret=dict(required=True, no_log=True),
            oauth_endpoint=dict(required=True, no_log=True)
        )
    )
    # create azure ServiceManagementService object
    creds = get_azure_creds(module)

    if module.params.get('state') == 'absent':
        (changed, virtual_machine) = terminate_virtual_machine(module, creds)
    elif module.params.get('state') == 'present':
        (changed, virtual_machine) = create_virtual_machine(module, creds)

    # module.exit_json(changed=changed, public_dns_name=public_dns_name, deployment=json.loads(json.dumps(deployment, default=lambda o: o.__dict__)))
    module.exit_json(changed=changed, virtual_machine=virtual_machine)

if __name__ == '__main__':
    main()
