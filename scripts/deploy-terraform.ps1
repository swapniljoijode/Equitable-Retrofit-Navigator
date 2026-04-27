param(
  [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"
$tf = "C:\Users\gjric\AppData\Local\Microsoft\WinGet\Links\terraform.exe"
if (!(Test-Path $tf)) {
  throw "Terraform not found at $tf"
}

$working = "infra/terraform"

Write-Host "Running terraform init..."
& $tf -chdir=$working init

Write-Host "Running terraform validate..."
& $tf -chdir=$working validate

Write-Host "Running terraform plan..."
& $tf -chdir=$working plan

if ($AutoApprove) {
  Write-Host "Applying terraform with auto-approve..."
  & $tf -chdir=$working apply -auto-approve
} else {
  Write-Host "Terraform apply is pending manual confirmation."
  & $tf -chdir=$working apply
}
