#!/bin/bash

if [ -z $REGION ];
  then echo "ERROR: Please set 'REGION' to your current AWS Region!" && exit 1;
fi
ROOT_DIR=`pwd`

git clone https://github.com/OpenVPN/easy-rsa.git
cd easy-rsa/easyrsa3
./easyrsa init-pki
./easyrsa build-ca nopass
./easyrsa build-server-full clientvpn-ad-test nopass
mkdir custom_folder/
cp pki/ca.crt custom_folder/
cp pki/issued/clientvpn-ad-test.crt custom_folder/
cp pki/private/clientvpn-ad-test.key custom_folder/
cd custom_folder/

# Import server cert to ACM
aws acm import-certificate \
  --certificate fileb://clientvpn-ad-test.crt \
  --private-key fileb://clientvpn-ad-test.key \
  --certificate-chain fileb://ca.crt \
  --tags Key=Name,Value=clientvpn-ad-test \
  --region $REGION
cd $ROOT_DIR
rm -rf easy-rsa



