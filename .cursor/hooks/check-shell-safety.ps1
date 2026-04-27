param()

$inputJson = [Console]::In.ReadToEnd()
if (-not $inputJson) {
  '{ "permission": "allow" }'
  exit 0
}

try {
  $payload = $inputJson | ConvertFrom-Json
  $cmd = [string]$payload.command
} catch {
  '{ "permission": "allow" }'
  exit 0
}

$dangerous = @(
  "git reset --hard",
  "rm -rf",
  "del /f /q",
  "format ",
  "diskpart"
)

foreach ($pattern in $dangerous) {
  if ($cmd.ToLower().Contains($pattern.ToLower())) {
    '{ "permission": "ask", "user_message": "This shell command may be destructive. Please confirm before running." }'
    exit 0
  }
}

'{ "permission": "allow" }'
exit 0
