"""Module for deploying set of CloudFormation stacks for Client VPN Test VPC."""

import sys
import os
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

DEPLOY_CFN_STACK = cfn_helper.deploy_cfn_stack


def main():
    """Main function. Deploys the CloudFormation stack for the test VPC"""
    DEPLOY_CFN_STACK(
        'Deploying Test VPC for Client VPN Testing',
        'CLIENT-VPN-TESTING-VPC',
        'test_vpc_added_to_vpn_network.yml',
        [])


if __name__ == "__main__":
    main()