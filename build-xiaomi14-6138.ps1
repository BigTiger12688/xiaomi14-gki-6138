$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir ".github/workflows/scripts")

python build.py `
  --android android14 `
  --kernel 6.1 `
  --sub-level 138 `
  --os-patch 2025-06 `
  --custom-version=-android14-11-g965475777129-mi `
  --no-kpm
