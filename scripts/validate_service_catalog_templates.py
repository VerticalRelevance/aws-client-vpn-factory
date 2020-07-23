import os
import sys
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

VALIDATE_TEMPLATE = cfn_helper.validate_cfn_template
TGW_SC_ROOT = 'cfn_templates/service-catalog/tgw_attachment'
VPN_SC_ROOT = 'cfn_templates/service-catalog/vpn'

TEMPLATES = [f'{TGW_SC_ROOT}/sc-portfolio-tgw-attachment.yml',
             f'{TGW_SC_ROOT}/sc-product-tgw-attachment.yml',
             f'{TGW_SC_ROOT}/tgw_attachment.yml',
             f'{VPN_SC_ROOT}/sc-portfolio-vpn-route-setup.yml',
             f'{VPN_SC_ROOT}/sc-product-vpn-route-setup.yml',
             f'{VPN_SC_ROOT}/client_vpn_route_setup.yml']


def main():
    """Main function for validating CFN templates"""
    VALIDATE_TEMPLATE(TEMPLATES)


if __name__ == "__main__":
    main()
