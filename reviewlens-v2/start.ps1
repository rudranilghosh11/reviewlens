# ReviewLens V2 - PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host "  REVIEW LENS V2 - NOCTURNAL PERFORMANCE SUITE" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host ""

$Root = $PSScriptRoot
Write-Host "Starting FastAPI Backend Engine on http://127.0.0.1:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH = '$Root;$Root\backend'; Set-Location '$Root'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

Write-Host "Starting Vite Frontend on http://127.0.0.1:5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\frontend'; npm run dev"

Write-Host ""
Write-Host "Both servers launched! Open your browser at:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Yellow
