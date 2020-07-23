"""Helper module for deploying and tearing down CloudFormation Stacks."""

import time
import sys
import datetime
import boto3
import uuid


cfn = boto3.client('cloudformation')
ssm = boto3.client('ssm')
asg = boto3.client('autoscaling')
acm = boto3.client('acm')
sc = boto3.client('servicecatalog')
TEMPLATE_DIRECTORY = 'cfn_templates'


def read_template(file):
    """Read template file and return object."""
    with open(file) as template:
        return template.read()


def describe_stack(stack_name):
    """Describe CloudFormation Stack and return dict response."""
    response = cfn.describe_stacks(
        StackName=stack_name
    )
    return response


def get_output_value(dict_list, key):
    """Get output value from list of CloudFormation outputs."""
    output_dict = \
        next(item for item in dict_list if item["OutputKey"] == key)

    return output_dict['OutputValue']

def get_ssm_param_value(name):
    """Retrieve SSM Parameter value."""
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound as e:
        print(e)
        sys.exit(f'ABORTING! - Parameter {name} does not exist')
    except:
        raise


def wait_for_stack_completion(start_desc, stack_id, desired_stack_status):
    """Wait for CloudFormation Stack completion before proceeding. Abort process if Stack fails to create or update."""
    print(start_desc)
    counter = 0
    stack_name = describe_stack(stack_id)['Stacks'][0]['StackName']
    stack_status = ''
    print(f'Waiting for Stack {stack_name} to Reach {desired_stack_status} Status....')
    while stack_status != desired_stack_status:
        stack_status = describe_stack(stack_id)['Stacks'][0]['StackStatus']
        if stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
            counter += 1
            time.sleep(5)
        elif stack_status in ['ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS']:
            sys.exit(f'ABORTING! - Stack {stack_name} {stack_status}')
    print(f'Stack {stack_name} {desired_stack_status} Completed')

def update_cfn_stack(stack_name, template_path, capabilities=None, parameters=None):
    """Update CloudFormation Stack."""
    response = cfn.update_stack(
        StackName=stack_name,
        TemplateBody=read_template(f'{TEMPLATE_DIRECTORY}/{template_path}'),
        Parameters=parameters,
        Capabilities=capabilities
    )
    return response


def deploy_cfn_stack(deploy_desc, stack_name, template_path, capabilities=None, parameters=None):
    """Deploy CloudFormation Stack. Attempts to update stack if stack already exists."""
    print(''.rjust(50, '-'))
    if parameters is None:
        parameters = [{}]
    if capabilities is None:
        capabilities = []
    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=read_template(f'{TEMPLATE_DIRECTORY}/{template_path}'),
            Parameters=parameters,
            Capabilities=capabilities
        )
        wait_for_stack_completion(deploy_desc,
                                  response['StackId'], "CREATE_COMPLETE")
        return response['StackId']
    except cfn.exceptions.AlreadyExistsException:
        try:
            print(f'Attempting to update stack {stack_name} and continue with deployment of downstream stacks.')
            response = update_cfn_stack(stack_name, template_path, capabilities, parameters)
            wait_for_stack_completion(deploy_desc,
                                      response['StackId'], "UPDATE_COMPLETE")
        except cfn.exceptions.ClientError:
            print(f'Stack {stack_name} already exists and no updates are to be performed, '
                  f'continuing deployment of downstream stacks.')
        return describe_stack(stack_name)['Stacks'][0]['StackId']


# Deletion methods
def wait_for_stack_deletion(delete_desc, stack_name):
    """Wait for CloudFormation stack to delete before proceeding."""
    print(delete_desc)
    counter = 0
    stack_status = describe_stack(stack_name)['Stacks'][0]['StackStatus']
    print(f'Waiting for Stack {stack_name} to Reach DELETE_COMPLETE Status....')
    while stack_status == 'DELETE_IN_PROGRESS':
        stack_status = describe_stack(stack_name)['Stacks'][0]['StackStatus']
        if stack_status == 'DELETE_IN_PROGRESS':
            counter += 1
            time.sleep(5)
        elif stack_status == 'DELETE_FAILED':
            sys.exit(f'ABORTING! - Stack {stack_name} resulted in DELETE_FAILED')


def delete_cfn_stack(delete_desc, stack_name):
    """Delete CloudFormation stack."""
    print(''.rjust(50, '-'))
    try:
        cfn.delete_stack(
            StackName=stack_name
        )
        wait_for_stack_deletion(delete_desc, stack_name)
    except cfn.exceptions.ClientError:
        print(f'Stack {stack_name} DELETED')


def get_acm_cert_arn(domain_name):
    """Get ACM Server Cert ARN based on Domain Name"""
    try:
        cert_list = acm.list_certificates(CertificateStatuses=['ISSUED'])['CertificateSummaryList']
        cert = next(item for item in cert_list if item["DomainName"] == domain_name)
    except:
        raise
    return cert['CertificateArn']


def launch_sc_product(prod_id, prov_art_id, prov_prod_name, params):
    """Launch Service Catalog Product"""
    print(f"Launching Service Catalog Product {prod_id} with name {prov_prod_name}")
    try:
        sc.provision_product(
            ProductId=prod_id,
            ProvisioningArtifactId=prov_art_id,
            ProvisionedProductName=prov_prod_name,
            ProvisioningParameters=params,
        )
    except:
        raise


def get_prov_artifact_id(product_id):
    """Get Provisioning Product Artifact ID"""
    try:
        response = sc.describe_product(Id=product_id)
    except:
        raise
    return response['ProvisioningArtifacts'][0]['Id']


def validate_cfn_template(templates):
    """Validate CFN Templates"""
    for t in templates:
        print(f"Validating Template: {t}")
        try:
            cfn.validate_template(
                TemplateBody=read_template(t)
            )
        except:
            print(f"ERROR: Template {t} failed validation!")
            sys.exit(1)
    print(''.rjust(50, '-'))
    print("All Templates Validated")


def create_provisioning_artifact(product_id, s3objectkey):
    """Create Service Catalog Provisioning Artifact"""
    try:
        response = sc.create_provisioning_artifact(
            ProductId=product_id,
            Parameters={
                'Name': f"pa-{str(uuid.uuid4())}",
                'Description': str(datetime.datetime.now()),
                'Info': {
                    'LoadTemplateFromURL': s3objectkey
                },
                'Type': 'CLOUD_FORMATION_TEMPLATE'
            },
            IdempotencyToken=str(uuid.uuid4())
        )
    except:
        raise
    return response


