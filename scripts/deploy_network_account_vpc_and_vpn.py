"""Module for deploying set of CloudFormation stacks for BR testing infrastructure."""

import sys
import os
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

DEPLOY_CFN_STACK = cfn_helper.deploy_cfn_stack
DESCRIBE_CFN_STACK = cfn_helper.describe_stack
GET_STACK_OUTPUT_VALUE = cfn_helper.get_output_value
GET_ACM_CERT_ARN = cfn_helper.get_acm_cert_arn


def main():
    """Main function. Deploys the CloudFormation stacks used to create BR testing infrastructure."""

    ## Deploy Main Network Hub Account VPC and Simple AD ##
    vpc_stack_id = DEPLOY_CFN_STACK(
        'Deploying Main Network Hub Account VPC and Simple AD Resources',
        'NETWORK-ACCOUNT-HUB-VPC-SIMPLE-AD',
        'network_account_main_vpc_with_simple_ad.yml',
        [])

    # Main Network Hub Account VPC Stack Outputs
    vpc_stack_outputs = DESCRIBE_CFN_STACK(vpc_stack_id)['Stacks'][0]['Outputs']
    vpc_cidr = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'VpcCidr')
    vpc_id = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'VpcID')
    subnet_1_id = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'SubnetOneID')
    subnet_2_id = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'SubnetTwoID')
    simple_ad_id = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'DirectoryID')
    ad_dns_1 = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'PrimaryDNS')
    ad_dns_2 = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'SecondaryDNS')
    business_unit = GET_STACK_OUTPUT_VALUE(vpc_stack_outputs, 'BusinessUnit')
    # Server Certificate ARN in ACM that was previously created
    server_cert_arn = GET_ACM_CERT_ARN("clientvpn-ad-test")

    ## Deploy Main Client VPN Endpoint Creation for Network Hub Account VPC ##
    client_vpn_stack_params = [
        {'ParameterKey': 'ServerCertificateArn', 'ParameterValue': server_cert_arn},
        {'ParameterKey': 'ClientVpnTargetNetworkVpcCidr', 'ParameterValue': vpc_cidr},
        {'ParameterKey': 'ClientVpnTargetNetworkVpc', 'ParameterValue': vpc_id},
        {'ParameterKey': 'ClientVpnTargetNetworkSubnet1', 'ParameterValue': subnet_1_id},
        {'ParameterKey': 'ClientVpnTargetNetworkSubnet2', 'ParameterValue': subnet_2_id},
        {'ParameterKey': 'ActiveDirectoryId', 'ParameterValue': simple_ad_id},
        {'ParameterKey': 'ActiveDirectoryDnsServer1', 'ParameterValue': ad_dns_1},
        {'ParameterKey': 'ActiveDirectoryDnsServer2', 'ParameterValue': ad_dns_2},
        {'ParameterKey': 'BusinessUnit', 'ParameterValue': business_unit}
    ]

    client_vpn_endpoint_stack_id = DEPLOY_CFN_STACK(
        'Deploying Main Client VPN Endpoint Creation for Network Hub Account VPC',
        'NETWORK-ACCOUNT-HUB-VPC-CLIENT-VPN',
        'client_vpn_endpoint.yml',
        ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
        client_vpn_stack_params)


if __name__ == "__main__":
    main()
