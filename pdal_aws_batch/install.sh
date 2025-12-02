#!/bin/bash

# Build and test the Docker image locally
docker buildx build --platform linux/amd64 --provenance=false -t lambda-docker-batch:test .
docker run --platform linux/amd64 -e S3_TARGET_FOLDER=target/folder -e S3_TARGET_BUCKET=myfoldername -d -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 --entrypoint /aws-lambda/aws-lambda-rie lambda-docker-batch:test /opt/conda/bin/python -m awslambdaric lambda_function.handler
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d  '{"S3_SOURCE_BUCKET":"source-bucket", "S3_SOURCE_OBJECT":"source/object/source.las"}'

# Push the Docker image to AWS ECR 
docker tag lambda-docker-batch:test accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-batch:latest
aws ecr get-login-password | docker login --username AWS --password-stdin accountid.dkr.ecr.us-east-1.amazonaws.com
aws ecr create-repository --repository-name lambda-docker-batch
docker push accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-batch:latest

# Create or update the AWS Lambda function to use the Docker image
# you will need to pre-create a Lambda execution role with permissions to access S3 (and other resources as needed - eg, CloudWatch Logs)
aws lambda create-function --function-name lambda-docker-batch --package-type Image --code ImageUri=accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-batch:latest --role arn:aws:iam::accountid:role/role-name
aws lambda update-function-code   --function-name lambda-docker-batch   --image-uri accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-batch:latest   --publish

# You will need to manually update a few things in the Lambda Function
- Configuration: Increase the timeout to 2 minutes
- Configuration: Increase the memory to 2048 MB
- Configuration: Increase ephemeral storage to 10 GB
- Set Environment Variables:
	S3_TARGET_FOLDER=<folder where you want to put converted files>
	S3_TARGET_BUCKET=<your target bucket of converted files>
	HOME=/tmp