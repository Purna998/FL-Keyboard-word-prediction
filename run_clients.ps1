param([int]$Count = 12, [int]$BasePort = 9001)

$pidFile = "$PSScriptRoot\.client_pids"
Remove-Item $pidFile -ErrorAction SilentlyContinue
$python = "$PSScriptRoot\venv\Scripts\python.exe"
$files = Get-ChildItem "$PSScriptRoot\data\clients\client_*.txt" | Sort-Object Name | Select-Object -First $Count

$i = 0
foreach ($f in $files) {
    $port = $BasePort + $i
    $argList = "backend\client_node.py --cid $($f.BaseName) --data `"$($f.FullName)`" --port $port"
    $p = Start-Process -FilePath $python -ArgumentList $argList -WorkingDirectory $PSScriptRoot -WindowStyle Minimized -PassThru
    $p.Id | Add-Content $pidFile
    Write-Host "started $($f.BaseName) on port $port (pid $($p.Id))"
    $i++
}