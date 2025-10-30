#!/bin/bash

docker build -t pdal-conda .
# For Testing
docker run -e S3_TARGET_FOLDER=target/folder/ -e S3_TARGET_BUCKET=mybucketname -e S3_SOURCE_FOLDER=source/folder -e S3_SOURCE_BUCKET=mybucketname -it pdal-conda

aws ecr get-login-password | docker login --username AWS --password-stdin accountid.dkr.ecr.us-east-1.amazonaws.com
docker tag pdal-conda:latest accountid.dkr.ecr.us-east-1.amazonaws.com/repo-name:latest
docker push accountid.dkr.ecr.us-east-1.amazonaws.com/repo-name:latest
