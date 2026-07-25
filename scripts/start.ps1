# 一键启动本机 API + Web UI（Windows PowerShell）
# 用法：在仓库根目录执行  .\scripts\start.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:PYTHONPATH = Join-Path $Root "src"
if (-not $env:ES_DATA_DIR) {
    $env:ES_DATA_DIR = Join-Path $env:USERPROFILE ".es_app"
}
if (-not $env:ES_BIND) {
    $env:ES_BIND = "127.0.0.1"
}
if (-not $env:OLLAMA_HOST) {
    $env:OLLAMA_HOST = "http://127.0.0.1:11434"
}

Write-Host "ES_DATA_DIR=$($env:ES_DATA_DIR)"
Write-Host "Open: http://127.0.0.1:8000/ui/"
Write-Host "API docs: http://127.0.0.1:8000/docs"
Write-Host ""

python -m uvicorn es_app.main:create_app --factory --host $env:ES_BIND --port 8000 --reload
