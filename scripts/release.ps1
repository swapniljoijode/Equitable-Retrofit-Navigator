param(
  [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

Write-Host "Running release preflight checks..."
python -m compileall src app | Out-Host
pytest -q | Out-Host

if (-not $SkipDocker) {
  Write-Host "Building Docker image..."
  docker build -t equitable-retrofit-navigator:release . | Out-Host
}

Write-Host "Release preflight complete."
