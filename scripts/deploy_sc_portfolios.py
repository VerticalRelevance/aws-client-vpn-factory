"""Module for deploying set of CloudFormation stacks for Client VPN Test VPC."""

import sys
import os
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

DEPLOY_CFN_STACK = cfn_helper.deploy_cfn_stack
TGW_ATTACHMENT_SC_STACK_NAME = 'SERVICE-CATALOG-TRANSIT-GATEWAY-ATTACHMENT-PORTFOLIO'
CLIENT_VPN_ROUTE_SETUP_SC_STACK_NAME = 'SERVICE-CATALOG-CLIENT-VPN-ROUTE-SETUP-PORTFOLIO'


def main():
    """Main function. Deploys the CloudFormation stack for the test VPC"""

    sc_portfolio_params = [
        {'ParameterKey': 'RepoRootURL', 'ParameterValue': f"https://s3.amazonaws.com/{os.getenv('SERVICE_CATALOG_S3_BUCKET', '')}/"},
        {'ParameterKey': 'LinkedIamUser', 'ParameterValue': os.getenv('SERVICE_CATALOG_LINKED_IAM_USER', '')},
        {'ParameterKey': 'LinkedIamRoleArn', 'ParameterValue': os.getenv('SERVICE_CATALOG_LINKED_IAM_ROLE_ARN', '')}
    ]
    # Deploy Service Catalog Transit Gateway Attachment Portfolio
    DEPLOY_CFN_STACK(
        'Deploying Service Catalog Transit Gateway Attachment Portfolio',
        TGW_ATTACHMENT_SC_STACK_NAME,
        'service-catalog/tgw_attachment/sc-portfolio-tgw-attachment.yml',
        ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
        sc_portfolio_params)

    # Deploy Service Catalog Client Vpn Route Setup Portfolio
    DEPLOY_CFN_STACK(
        'Deploying Service Catalog Client Vpn Route Setup Portfolio',
        CLIENT_VPN_ROUTE_SETUP_SC_STACK_NAME,
        'service-catalog/vpn/sc-portfolio-vpn-route-setup.yml',
        ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
        sc_portfolio_params)


if __name__ == "__main__":
    main()