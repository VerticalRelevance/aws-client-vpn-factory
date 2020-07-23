#!/bin/bash

if [ -z $GITHUB_TOKEN ];
  then echo "ERROR: Please set 'GITHUB_TOKEN' to your GitHub token!" && exit 1;
fi

aws cloudformation deploy \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-file cfn_templates/vpn_network_pipeline.yml \
  --stack-name NETWORK-ACCOUNT-VPC-DEPLOYMENT-PIPELINE \
  --parameter-overrides RepoOwner=VerticalRelevance \
    RepoName=aws-client-vpn-factory \
    BranchName=master \
    GitHubToken=$GITHUB_TOKEN
