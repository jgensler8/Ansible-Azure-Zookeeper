#!/usr/bin/python

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

def create_network_interface(network_client, region, group_name, interface_name,
                             network_name, subnet_name, ip_name):

    result = network_client.virtual_networks.create_or_update(
        group_name,
        network_name,
        azure.mgmt.network.VirtualNetwork(
            location=region,
            address_space=azure.mgmt.network.AddressSpace(
                address_prefixes=[
                    '10.0.0.0/16',
                ],
            ),
            subnets=[
                azure.mgmt.network.Subnet(
                    name=subnet_name,
                    address_prefix='10.0.0.0/24',
                ),
            ],
        ),
    )

    result = network_client.subnets.get(group_name, network_name, subnet_name)
    subnet = result.subnet

    result = network_client.public_ip_addresses.create_or_update(
        group_name,
        ip_name,
        azure.mgmt.network.PublicIpAddress(
            location=region,
            public_ip_allocation_method='Dynamic',
            idle_timeout_in_minutes=4,
        ),
    )

    result = network_client.public_ip_addresses.get(group_name, ip_name)
    public_ip_id = result.public_ip_address.id

    result = network_client.network_interfaces.create_or_update(
        group_name,
        interface_name,
        azure.mgmt.network.NetworkInterface(
            name=interface_name,
            location=region,
            ip_configurations=[
                azure.mgmt.network.NetworkInterfaceIpConfiguration(
                    name='default',
                    private_ip_allocation_method=azure.mgmt.network.IpAllocationMethod.dynamic,
                    subnet=subnet,
                    public_ip_address=azure.mgmt.network.ResourceId(
                        id=public_ip_id,
                    ),
                ),
            ],
        ),
    )

    result = network_client.network_interfaces.get(
        group_name,
        interface_name,
    )

    return result.network_interface.id

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
    resource_client = azure.mgmt.resource.ResourceManagementClient(creds)
    storage_client = azure.mgmt.storage.StorageManagementClient(creds)
    compute_client = azure.mgmt.compute.ComputeManagementClient(creds)
    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)

    result = compute_client.virtual_machines.delete(
        module.params.get('group_name'),
        module.params.get('vm_name')
    )

    return (False, {}, str(result))

def create_virtual_machine(module, creds):
    resource_client = azure.mgmt.resource.ResourceManagementClient(creds)
    storage_client = azure.mgmt.storage.StorageManagementClient(creds)
    compute_client = azure.mgmt.compute.ComputeManagementClient(creds)
    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)

    # 1. Create a resource group
    resource_client.resource_groups.create_or_update(
        module.params.get('group_name'),
        azure.mgmt.resource.ResourceGroup(
            location=module.params.get('region'),
        ),
    )

    # 2. Create a storage account
    # TODO: change standard_lrs to other
    storage_client.storage_accounts.create(
        module.params.get('group_name'),
        module.params.get('storage_name'),
        azure.mgmt.storage.StorageAccountCreateParameters(
            location=module.params.get('region'),
            account_type=azure.mgmt.storage.AccountType.standard_lrs,
        ),
    )

    # 3. Helper function to get nic_id
    nic_id = create_network_interface(
        network_client,
        module.params.get('region'),
        module.params.get('group_name'),
        module.params.get('network_interface_name'),
        module.params.get('virtual_network_name'),
        module.params.get('subnet_name'),
        module.params.get('public_ip_name'),
    )

    # 4. Create Virtual Machine
    # virtual_machine_size = module.params.get('virtual_machine_size')
    virtual_machine_size = azure.mgmt.compute.VirtualMachineSizeTypes.standard_a0
    result = compute_client.virtual_machines.create_or_update(
        module.params.get('group_name'),
        azure.mgmt.compute.VirtualMachine(
            location=module.params.get('region'),
            name=module.params.get('vm_name'),
            os_profile=azure.mgmt.compute.OSProfile(
                admin_username=module.params.get('admin_username'),
                admin_password=module.params.get('admin_password'),
                computer_name=module.params.get('computer_name'),
            ),
            hardware_profile=azure.mgmt.compute.HardwareProfile(
                virtual_machine_size=virtual_machine_size
            ),
            network_profile=azure.mgmt.compute.NetworkProfile(
                network_interfaces=[
                    azure.mgmt.compute.NetworkInterfaceReference(
                        reference_uri=nic_id,
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

    net_result = network_client.public_ip_addresses.get(module.params.get('group_name'), module.params.get('public_ip_name'))

    # we get a tacking operation ID so we should wait for that
    return (True, net_result.public_ip_address.ip_address, str(result))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(require=True, choices=["absent", "present"]),
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
            region=dict(require=True, choices=AZURE_REGIONS),
            image_publisher=dict(required=True),
            image_offer=dict(required=True),
            image_sku=dict(required=True),
            image_version=dict(required=True),
            virtual_machine_size_type=dict(require=True, choice=AZURE_VIRUTAL_MACHINE_SIZE_TYPES),
            subscription_id=dict(required=True, no_log=True),
            client_id=dict(required=True, no_log=True),
            client_secret=dict(required=True, no_log=True),
            oauth_endpoint=dict(required=True, no_log=True)
        )
    )
    # create azure ServiceManagementService object
    creds = get_azure_creds(module)

    if module.params.get('state') == 'absent':
        (changed, public_ip, deployment) = terminate_virtual_machine(module, creds)
    elif module.params.get('state') == 'present':
        (changed, public_ip, deployment) = create_virtual_machine(module, creds)

    # module.exit_json(changed=changed, public_dns_name=public_dns_name, deployment=json.loads(json.dumps(deployment, default=lambda o: o.__dict__)))
    module.exit_json(changed=changed, public_ip=public_ip, deployment=deployment)

if __name__ == '__main__':
    main()
