param(
    [Parameter(Mandatory = $true)]
    [string]$CurrentRunId,

    [Parameter(Mandatory = $true)]
    [string]$NextConfig,

    [int]$PollSeconds = 15
)

$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$currentRunDir = Join-Path $root ("data\raw_runs\" + $CurrentRunId)
$manifestPath = Join-Path $currentRunDir "run_manifest.json"
$logDir = Join-Path $root "outputs\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$chainLog = Join-Path $logDir ("chain_" + $CurrentRunId + "_" + $timestamp + ".log")

function Write-ChainLog {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Add-Content -Path $chainLog -Value $line
}

Write-ChainLog "Watcher started."
Write-ChainLog ("Current run: " + $CurrentRunId)
Write-ChainLog ("Next config: " + $NextConfig)

while ($true) {
    if (-not (Test-Path $manifestPath)) {
        Write-ChainLog "Manifest not found yet. Sleeping."
        Start-Sleep -Seconds $PollSeconds
        continue
    }

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    $status = $manifest.status
    Write-ChainLog ("Observed status: " + $status)

    if ($status -eq 'completed') {
        break
    }

    if ($status -eq 'interrupted') {
        Write-ChainLog "Current run interrupted. Chain cancelled."
        exit 1
    }

    if ($status -eq 'failed') {
        Write-ChainLog "Current run failed. Chain cancelled."
        exit 1
    }

    Start-Sleep -Seconds $PollSeconds
}

$env:GLM_API_KEY = [Environment]::GetEnvironmentVariable('GLM_API_KEY', 'User')
$env:GLM_BASE_URL = [Environment]::GetEnvironmentVariable('GLM_BASE_URL', 'User')
$nextConfigPath = Join-Path $root $NextConfig

Write-ChainLog "Current run completed. Starting next run."
Write-ChainLog ("Resolved next config path: " + $nextConfigPath)

Push-Location $root
try {
    conda run -n srtp python runner/run_batch.py --config $nextConfigPath *>> $chainLog
    Write-ChainLog "Next run finished. Rebuilding processed outputs."
    conda run -n srtp python scripts/build_phase3_processed.py *>> $chainLog
    Write-ChainLog "Processed outputs rebuilt."
}
finally {
    Pop-Location
}

Write-ChainLog "Watcher finished."
