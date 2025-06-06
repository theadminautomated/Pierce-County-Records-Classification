<#
.SYNOPSIS
  Prepare a Windows shell for building this project.
.DESCRIPTION
  Detects Visual Studio Build Tools, Node.js and Rust.
  Sets MSVC environment variables using `vswhere` if necessary.
  Run this script in every new PowerShell session before invoking `cargo`.
#>

param()

$ErrorActionPreference = 'Stop'

function Assert-Command($Name, $Url) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: '$Name' not found. Please install from $Url" -ForegroundColor Red
        exit 1
    }
}

Assert-Command 'cargo' 'https://rustup.rs/'
Assert-Command 'node' 'https://nodejs.org/'
Assert-Command 'vswhere' 'https://aka.ms/vswhere'

# Discover latest VS Build Tools
$vsPath = & vswhere -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsPath) {
    Write-Host 'Visual Studio Build Tools not found. Install the "Desktop development with C++" workload.' -ForegroundColor Red
    exit 1
}

$vcvars = Join-Path $vsPath 'VC\Auxiliary\Build\vcvars64.bat'
if (-not (Test-Path $vcvars)) {
    Write-Host "Unable to locate vcvars64.bat at $vcvars" -ForegroundColor Red
    exit 1
}

Write-Host 'Configuring MSVC environment...'
cmd /c "`"$vcvars`"" > $null

$required = @('VCINSTALLDIR','VisualStudioVersion','WindowsSdkDir')
$missing = @()
foreach ($r in $required) {
    if (-not $env:$r) { $missing += $r }
}
if ($missing.Count -gt 0) {
    Write-Host "ERROR: the following environment variables are missing: $($missing -join ', ')" -ForegroundColor Red
    exit 1
}

Write-Host 'Environment ready. Run your cargo commands now.' -ForegroundColor Green
