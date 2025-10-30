#!/bin/bash

docker buildx build --platform linux/amd64 --provenance=false -t lambda-docker-custom:test .
docker run --platform linux/amd64 -e S3_TARGET_FOLDER=target/folder -e S3_TARGET_BUCKET=myfoldername -d -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 --entrypoint /aws-lambda/aws-lambda-rie lambda-docker-custom:test /opt/conda/bin/python -m awslambdaric lambda_function.handler
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d  '{"S3_SOURCE_BUCKET":"source-bucket", "S3_SOURCE_OBJECT":"source/object/source.las"}'

docker tag lambda-docker-custom:test accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-custom:latest
docker push accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-custom:latest
aws lambda update-function-code   --function-name lambda-docker-custom   --image-uri accountid.dkr.ecr.us-east-1.amazonaws.com/lambda-docker-custom:latest   --publish
