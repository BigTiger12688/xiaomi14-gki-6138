param(
    [switch]$PreflightOnly,
    [string]$Workspace,
    [ValidateSet(
        "clone_support_repos",
        "prepare_toolchain",
        "sync_kernel_source",
        "integrate_kernelsu",
        "integrate_susfs",
        "apply_compat_fixes",
        "configure_kernel",
        "build_kernel",
        "package_artifacts"
    )]
    [string]$FromStage,
    [ValidateSet(
        "clone_support_repos",
        "prepare_toolchain",
        "sync_kernel_source",
        "integrate_kernelsu",
        "integrate_susfs",
        "apply_compat_fixes",
        "configure_kernel",
        "build_kernel",
        "package_artifacts"
    )]
    [string]$UntilStage,
    [string]$KernelSURef = "v4.1.3",
    [string]$SusfsRef = "",
    [string]$BootSignKeyPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Convert-ToWslPath {
    param([Parameter(Mandatory = $true)][string]$WindowsPath)

    $fullPath = [System.IO.Path]::GetFullPath($WindowsPath)
    if ($fullPath -match '^([A-Za-z]):\\(.*)$') {
        $drive = $matches[1].ToLowerInvariant()
        $rest = $matches[2] -replace '\\', '/'
        return "/mnt/$drive/$rest"
    }

    throw "Cannot convert to WSL path: $WindowsPath"
}

function Quote-ForBash {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value.Contains("'")) {
        throw "Single quotes are not supported in arguments: $Value"
    }

    return "'$Value'"
}

function Test-WslAvailable {
    $null = & wsl.exe -l -q 2>$null
    return $LASTEXITCODE -eq 0
}

function Invoke-WslBuilder {
    param(
        [Parameter(Mandatory = $true)][string]$ScriptsDirWsl,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$BootKeyPathWsl
    )

    $quotedArgs = ($Arguments | ForEach-Object { Quote-ForBash $_ }) -join " "
    $bootKeyExport = ""
    if ($BootKeyPathWsl) {
        $bootKeyExport = "export BOOT_SIGN_KEY_PATH=$(Quote-ForBash $BootKeyPathWsl) && "
    }
    $command = "cd $(Quote-ForBash $ScriptsDirWsl) && ${bootKeyExport}python3 xiaomi14_builder.py $quotedArgs"
    & wsl.exe bash -lc $command
    if ($LASTEXITCODE -ne 0) {
        throw "WSL build command failed with exit code $LASTEXITCODE"
    }
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptsDir = Join-Path $repoRoot ".github\workflows\scripts"

if (-not $Workspace) {
    $Workspace = Join-Path $repoRoot ".local-workspaces\xiaomi14-6138"
}

if (-not (Test-WslAvailable)) {
    throw @"
No usable WSL distro was detected.
This repository now builds only through Linux/WSL because the whole chain is shell-driven.

Options:
1. Install WSL: wsl.exe --install
2. Or use the GitHub Actions workflow: .github/workflows/xiaomi14-6.1.138.yml
"@
}

$scriptsDirWsl = Convert-ToWslPath $scriptsDir
$workspaceWsl = Convert-ToWslPath $Workspace
$bootKeyWsl = ""
if ($BootSignKeyPath) {
    $bootKeyWsl = Convert-ToWslPath $BootSignKeyPath
}

$baseArgs = @(
    "--workspace", $workspaceWsl,
    "--kernelsu-ref", $KernelSURef
)

if ($SusfsRef) {
    $baseArgs += @("--susfs-ref", $SusfsRef)
}

if ($FromStage) {
    $baseArgs += @("--from-stage", $FromStage)
}

if ($UntilStage) {
    $baseArgs += @("--until-stage", $UntilStage)
}

Write-Host "Running Xiaomi 14 preflight with workspace $Workspace"
Invoke-WslBuilder -ScriptsDirWsl $scriptsDirWsl -Arguments ($baseArgs + "--preflight-only") -BootKeyPathWsl $bootKeyWsl

if (-not $PreflightOnly) {
    Write-Host "Starting Xiaomi 14 build"
    Invoke-WslBuilder -ScriptsDirWsl $scriptsDirWsl -Arguments $baseArgs -BootKeyPathWsl $bootKeyWsl
}
