$pidFile = "$PSScriptRoot\.client_pids"
if (Test-Path $pidFile) {
    Get-Content $pidFile | ForEach-Object { Stop-Process -Id $_ -ErrorAction SilentlyContinue }
    Remove-Item $pidFile
    Write-Host "client processes stopped"
} else { Write-Host "no client pid file found" }