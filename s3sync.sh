#!/bin/bash

# Before first use:
# Install awscli (pip install awscli)
# Configure access credentials (aws configure), region is "eu-central-1"

bucket=mytrezor
repository=webwallet-data
github=https://github.com/trezor/$repository/archive/master.zip

set -e
cd `dirname $0`

rm -rf tmp/
mkdir tmp
cd tmp

wget -O "master.zip" $github
unzip master.zip

aws s3 sync $repository-master s3://$bucket/

cd ..
rm -rf tmp/

echo "DONE"
