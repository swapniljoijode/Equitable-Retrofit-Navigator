param(
  [string]$Repo = "swapniljoijode/Equitable-Retrofit-Navigator"
)

$ErrorActionPreference = "Stop"
$gh = "C:\Program Files\GitHub CLI\gh.exe"
if (!(Test-Path $gh)) {
  throw "GitHub CLI not found at $gh"
}

Write-Host "Setting GitHub repository secrets for $Repo"

function Set-SecretFromEnv {
  param(
    [string]$Name,
    [string]$EnvVarName
  )
  $value = [Environment]::GetEnvironmentVariable($EnvVarName)
  if ([string]::IsNullOrWhiteSpace($value)) {
    Write-Host "Skipping $Name (env $EnvVarName is empty)."
    return
  }
  $value | & $gh secret set $Name --repo $Repo --body -
  Write-Host "Set $Name"
}

# Core cloud/runtime secrets expected by workflow and Terraform.
Set-SecretFromEnv -Name "AWS_ACCESS_KEY_ID" -EnvVarName "AWS_ACCESS_KEY_ID"
Set-SecretFromEnv -Name "AWS_SECRET_ACCESS_KEY" -EnvVarName "AWS_SECRET_ACCESS_KEY"
Set-SecretFromEnv -Name "AWS_REGION" -EnvVarName "AWS_REGION"

Set-SecretFromEnv -Name "CONTAINER_IMAGE" -EnvVarName "CONTAINER_IMAGE"
Set-SecretFromEnv -Name "VPC_ID" -EnvVarName "VPC_ID"
Set-SecretFromEnv -Name "PUBLIC_SUBNET_IDS" -EnvVarName "PUBLIC_SUBNET_IDS"
Set-SecretFromEnv -Name "PRIVATE_SUBNET_IDS" -EnvVarName "PRIVATE_SUBNET_IDS"
Set-SecretFromEnv -Name "ECS_SECURITY_GROUP_ID" -EnvVarName "ECS_SECURITY_GROUP_ID"
Set-SecretFromEnv -Name "ALB_SECURITY_GROUP_ID" -EnvVarName "ALB_SECURITY_GROUP_ID"
Set-SecretFromEnv -Name "CERTIFICATE_ARN" -EnvVarName "CERTIFICATE_ARN"

Set-SecretFromEnv -Name "API_AUTH_KEY" -EnvVarName "API_AUTH_KEY"
Set-SecretFromEnv -Name "OPENAI_API_KEY" -EnvVarName "OPENAI_API_KEY"
Set-SecretFromEnv -Name "GOOGLE_API_KEY" -EnvVarName "GOOGLE_API_KEY"
Set-SecretFromEnv -Name "NYC_OPEN_DATA_APP_TOKEN" -EnvVarName "NYC_OPEN_DATA_APP_TOKEN"

Write-Host "GitHub secret setup completed."
