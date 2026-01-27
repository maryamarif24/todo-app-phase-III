#!/usr/bin/env pwsh
# Script to start both backend (port 8000) and frontend (port 3000) servers

Write-Host "Starting Todo App Servers..." -ForegroundColor Green

# Start backend server in a new PowerShell window
Write-Host "Starting backend server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "Set-Location '$PSScriptRoot/backend'; python -m uvicorn src.main:app --reload --port 8000"

# Small delay to ensure backend starts first
Start-Sleep -Seconds 3

# Start frontend server in a new PowerShell window
Write-Host "Starting frontend server on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "Set-Location '$PSScriptRoot/frontend'; npm run dev"

Write-Host "Both servers started!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Chat Interface: http://localhost:3000/chat" -ForegroundColor Cyan