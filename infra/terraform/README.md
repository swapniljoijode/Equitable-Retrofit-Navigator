# Terraform Deployment (AWS ECS + Lambda Image)

This module provides a production scaffold for:

- ECS Fargate service for the FastAPI runtime.
- ALB HTTPS ingress with `/health` target checks.
- Secrets Manager integration for runtime API keys.
- Optional Lambda image function for burst or batch invocation.

## Prerequisites

- Terraform >= 1.6
- AWS credentials configured
- Container image pushed to ECR

## Usage

1. Copy vars:
   - `cp terraform.tfvars.example terraform.tfvars`
2. Edit values for your VPC/subnets/security group and image URI.
3. Deploy:
   - `terraform init`
   - `terraform plan`
   - `terraform apply`

## Notes

- This is an infrastructure scaffold; add API Gateway (if needed), autoscaling, WAF, and tighter IAM policies before production launch.
- Keep sensitive values in AWS Secrets Manager or SSM Parameter Store.
- For CI usage, provide GitHub secrets:
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
  - `CONTAINER_IMAGE`, `VPC_ID`
  - `PUBLIC_SUBNET_IDS` and `PRIVATE_SUBNET_IDS` as JSON list strings (example: `["subnet-1","subnet-2"]`)
  - `ECS_SECURITY_GROUP_ID`, `ALB_SECURITY_GROUP_ID`, `CERTIFICATE_ARN`
  - `API_AUTH_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `NYC_OPEN_DATA_APP_TOKEN`
