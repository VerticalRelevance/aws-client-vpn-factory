import sys
import os
import boto3
import time
from cfn_utils import cfn_helper

sys.path.insert(0, os.path.abspath('..'))

DEPLOY_CFN_STACK = cfn_helper.deploy_cfn_stack
DESCRIBE_CFN_STACK = cfn_helper.describe_stack
GET_STACK_OUTPUT_VALUE = cfn_helper.get_output_value
GET_SSM_PARAM_VALUE = cfn_helper.get_ssm_param_value
GET_PROV_ARTIFACT_ID = cfn_helper.get_prov_artifact_id
LAUNCH_SC_PRODUCT = cfn_helper.launch_sc_product


def main():
    """Main function for deploying SC Products"""
    #### CloudFormation Stack Outputs ####
    network_account_vpc_stack_outputs = \
        DESCRIBE_CFN_STACK('NETWORK-ACCOUNT-HUB-VPC-SIMPLE-AD')['Stacks'][0]['Outputs']
    network_account_client_vpn_stack_outputs = \
        DESCRIBE_CFN_STACK('NETWORK-ACCOUNT-HUB-VPC-CLIENT-VPN')['Stacks'][0]['Outputs']
    testing_vpc_stack_outputs = \
        DESCRIBE_CFN_STACK('CLIENT-VPN-TESTING-VPC')['Stacks'][0]['Outputs']
    tgw_attachment_sc_portfolio_stack_outputs = \
        DESCRIBE_CFN_STACK('SERVICE-CATALOG-TRANSIT-GATEWAY-ATTACHMENT-PORTFOLIO')['Stacks'][0]['Outputs']
    client_vpn_route_setup_sc_portfolio_stack_outputs = \
        DESCRIBE_CFN_STACK('SERVICE-CATALOG-CLIENT-VPN-ROUTE-SETUP-PORTFOLIO')['Stacks'][0]['Outputs']

    ### Network Account Hub VPC Stack Outputs ###
    network_account_vpc_cidr = GET_STACK_OUTPUT_VALUE(network_account_vpc_stack_outputs, 'VpcCidr')
    network_account_vpc_subnet_1 = GET_STACK_OUTPUT_VALUE(network_account_vpc_stack_outputs, 'SubnetOneID')
    network_account_vpc_subnet_2 = GET_STACK_OUTPUT_VALUE(network_account_vpc_stack_outputs, 'SubnetTwoID')
    network_account_vpc_subnet_route_table_id = GET_STACK_OUTPUT_VALUE(network_account_vpc_stack_outputs,
                                                                       'RouteTableId')
    transit_gateway_id = GET_STACK_OUTPUT_VALUE(network_account_vpc_stack_outputs, 'TransitGatewayId')

    ### Network Account Hub Client VPN Endpoint Stack Outputs ###
    network_account_client_vpn_endpoint = GET_STACK_OUTPUT_VALUE(network_account_client_vpn_stack_outputs,
                                                                 'ClientVpnEndpoint')

    ### Testing VPC Stack Outputs ###
    tgw_attachment_subnet1 = GET_STACK_OUTPUT_VALUE(testing_vpc_stack_outputs, 'PrivateSubnetOneID')
    tgw_attachment_subnet2 = GET_STACK_OUTPUT_VALUE(testing_vpc_stack_outputs, 'PrivateSubnetTwoID')
    test_vpc_id = GET_STACK_OUTPUT_VALUE(testing_vpc_stack_outputs, 'VpcID')
    test_vpc_cidr = GET_STACK_OUTPUT_VALUE(testing_vpc_stack_outputs, 'VpcCidr')
    subnet_route_table_id = GET_STACK_OUTPUT_VALUE(testing_vpc_stack_outputs, 'PrivateSubnetRouteTableId')

    ### Service Catalog Transit Gateway Attachment Portfolio Stack Outputs ###
    tgw_attachment_sc_product_id = GET_STACK_OUTPUT_VALUE(tgw_attachment_sc_portfolio_stack_outputs,
                                                          'TransitGatewayAttachmentProductId')
    ### Service Catalog Client VPN Route Setup Portfolio Stack Outputs ###
    client_vpn_route_setup_sc_product_id = GET_STACK_OUTPUT_VALUE(client_vpn_route_setup_sc_portfolio_stack_outputs,
                                                                  'ClientVpnAuthRouteSetupProductId')

    ### Service Catalog Provisioning Product Artifact ID for Transit Gateway Attachment Product ###
    tgw_attachment_sc_prov_prod_art_id = GET_PROV_ARTIFACT_ID(tgw_attachment_sc_product_id)
    ### Service Catalog Provisioning Product Artifact ID for Client VPN Route Setup Product ###
    client_vpn_route_setup_sc_prov_prod_art_id = GET_PROV_ARTIFACT_ID(client_vpn_route_setup_sc_product_id)

    ### TGW Attachment Params ###
    tgw_attachment_sc_product_params = [
        {'Key': 'CentralNetworkAccountVpnVpcCIDR', 'Value': network_account_vpc_cidr},
        {'Key': 'TgwAttachmentSubnet1', 'Value': tgw_attachment_subnet1},
        {'Key': 'TgwAttachmentSubnet2', 'Value': tgw_attachment_subnet2},
        {'Key': 'TransitGatewayId', 'Value': transit_gateway_id},
        {'Key': 'VpcId', 'Value': test_vpc_id},
        {'Key': 'RouteTableId1', 'Value': subnet_route_table_id}
    ]

    ### Client VPN Route Setup Params ###
    client_vpn_route_setup_sc_product_params = [
        {'Key': 'NewVpcCIDR', 'Value': test_vpc_cidr},
        {'Key': 'ClientVpnEndpoint', 'Value': network_account_client_vpn_endpoint},
        {'Key': 'ClientVpnTargetNetworkSubnet1', 'Value': network_account_vpc_subnet_1},
        {'Key': 'ClientVpnTargetNetworkSubnet2', 'Value': network_account_vpc_subnet_2},
        {'Key': 'TransitGatewayId', 'Value': transit_gateway_id},
        {'Key': 'RouteTableId', 'Value': network_account_vpc_subnet_route_table_id}
    ]

    ### Launch Transit Gateway Attachment Service Catalog Product ###
    LAUNCH_SC_PRODUCT(tgw_attachment_sc_product_id,
                      tgw_attachment_sc_prov_prod_art_id,
                      'business-unit-1-vpc-tgw-attachment',
                      tgw_attachment_sc_product_params)

    time.sleep(3)
    print(''.rjust(50, '-'))

    ### Launch Client VPN Route Setup Service Catalog Product ###
    LAUNCH_SC_PRODUCT(client_vpn_route_setup_sc_product_id,
                      client_vpn_route_setup_sc_prov_prod_art_id,
                      'business-unit-1-vpc-client-vpn-route-setup',
                      client_vpn_route_setup_sc_product_params)


if __name__ == "__main__":
    main()
