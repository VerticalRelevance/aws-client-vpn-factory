"""Module for deploying set of CloudFormation stacks for Client VPN Test VPC."""

import sys
import os
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

DEPLOY_CFN_STACK = cfn_helper.deploy_cfn_stack
DESCRIBE_CFN_STACK = cfn_helper.describe_stack
GET_STACK_OUTPUT_VALUE = cfn_helper.get_output_value
TGW_ATTACHMENT_SC_STACK_NAME = 'SERVICE-CATALOG-TRANSIT-GATEWAY-ATTACHMENT-PORTFOLIO'
CLIENT_VPN_ROUTE_SETUP_SC_STACK_NAME = 'SERVICE-CATALOG-CLIENT-VPN-ROUTE-SETUP-PORTFOLIO'
CREATE_PROV_ARTIFACT = cfn_helper.create_provisioning_artifact



def main():
    """Main function. Deploys the CloudFormation stack for the Business-Unit-1 VPC"""

    tgw_attachment_sc_portfolio_stack_outputs = \
        DESCRIBE_CFN_STACK(TGW_ATTACHMENT_SC_STACK_NAME)['Stacks'][0]['Outputs']
    client_vpn_route_setup_sc_portfolio_stack_outputs = \
        DESCRIBE_CFN_STACK(CLIENT_VPN_ROUTE_SETUP_SC_STACK_NAME)['Stacks'][0]['Outputs']

    # SC Product ID Vars
    tgw_attachment_product_id = GET_STACK_OUTPUT_VALUE(tgw_attachment_sc_portfolio_stack_outputs,
                                                       'TransitGatewayAttachmentProductId')
    client_vpn_route_setup_product_id = GET_STACK_OUTPUT_VALUE(client_vpn_route_setup_sc_portfolio_stack_outputs,
                                                               'ClientVpnAuthRouteSetupProductId')

    sc_s3_root_url = f"https://s3.amazonaws.com/{os.getenv('SERVICE_CATALOG_S3_BUCKET', '')}"
    # Create Transit Gateway Attachment SC Provisioning Artifact
    resp = CREATE_PROV_ARTIFACT(tgw_attachment_product_id, f"{sc_s3_root_url}/tgw_attachment/tgw_attachment.yml")
    print(f"New Provisioning Artifact for Transit Gateway Attachment created with Id: {resp['ProvisioningArtifactDetail']['Id']}")
    resp = CREATE_PROV_ARTIFACT(client_vpn_route_setup_product_id, f"{sc_s3_root_url}/vpn/client_vpn_route_setup.yml")
    print(f"New Provisioning Artifact for Client VPN Route Setup created with Id: {resp['ProvisioningArtifactDetail']['Id']}")


if __name__ == "__main__":
    main()
