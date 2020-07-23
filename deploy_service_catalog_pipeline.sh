#!/bin/bash

if [ -z $LINKED_IAM_ROLE_ARN ] && [ -z $LINKED_IAM_USER ]
  then echo "ERROR: Either 'LINKED_IAM_ROLE_ARN' or  'LINKED_IAM_USER' must be set!" && exit 1;
elif [ -z $LINKED_IAM_ROLE_ARN ]
  then LINKED_IAM_ROLE_ARN='';
elif [ -z $LINKED_IAM_USER ]
  then LINKED_IAM_USER='';
fi

if [ -z $GITHUB_TOKEN ];
  then echo "ERROR: Please set 'GITHUB_TOKEN' to your GitHub token!" && exit 1;
fi
if [ -z $BUCKET_NAME ];
  then echo "ERROR: Please set 'BUCKET_NAME' as a unique name for the Service Catalog S3 Bucket!" && exit 1;
fi

aws cloudformation deploy \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-file cfn_templates/service_catalog_pipeline.yml \
  --stack-name NETWORK-ACCOUNT-SERVICE-CATALOG-PIPELINE \
  --parameter-overrides RepoOwner=VerticalRelevance \
    RepoName=aws-client-vpn-factory \
    BranchName=master \
    GitHubToken=$GITHUB_TOKEN \
    ServiceCatalogBucketName=$BUCKET_NAME \
    ServiceCatalogLinkedIamUser=$LINKED_IAM_USER \
    ServiceCatalogLinkedIamRole=$LINKED_IAM_ROLE_ARN
