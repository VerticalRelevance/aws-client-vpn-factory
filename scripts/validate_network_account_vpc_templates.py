import os
import sys
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

VALIDATE_TEMPLATE = cfn_helper.validate_cfn_template
TEMPLATES = ['cfn_templates/client_vpn_endpoint.yml',
             'cfn_templates/network_account_main_vpc_with_simple_ad.yml',
             'cfn_templates/test_vpc_added_to_vpn_network.yml']


def main():
    """Main function for validating CFN templates"""
    VALIDATE_TEMPLATE(TEMPLATES)


if __name__ == "__main__":
    main()
