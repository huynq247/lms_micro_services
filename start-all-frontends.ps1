# Multi-Frontend Starter Script for Windows
Write-Host "🚀 Starting Multi-Frontend Development Environment" -ForegroundColor Blue
Write-Host "===============================================" -ForegroundColor Blue

function Start-Frontend {
    param(
        [string]$Name,
        [string]$Port,
        [string]$Path
    )
    
    Write-Host "📦 Starting $Name on port $Port..." -ForegroundColor Yellow
    
    Set-Location $Path
    
    # Install dependencies if node_modules doesn't exist
    if (!(Test-Path "node_modules")) {
        Write-Host "📥 Installing dependencies for $Name..." -ForegroundColor Yellow
        npm install
    }
    
    # Start the frontend in background
    $env:PORT = $Port
    Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "start"
    
    Write-Host "✅ $Name started successfully" -ForegroundColor Green
    Set-Location ..
}

# Start all frontends
Write-Host "🔧 Starting Frontend Applications..." -ForegroundColor Blue

Start-Frontend -Name "Admin Frontend" -Port "3001" -Path "frontend-admin"
Start-Frontend -Name "Teacher Frontend" -Port "3002" -Path "frontend-teacher"
Start-Frontend -Name "Student Frontend" -Port "3003" -Path "frontend-student"
Start-Frontend -Name "Main Frontend" -Port "3000" -Path "frontend"

Write-Host "===============================================" -ForegroundColor Blue
Write-Host "🎉 All frontends are starting up!" -ForegroundColor Green
Write-Host "📱 Frontend URLs:" -ForegroundColor Blue
Write-Host "  Admin:    http://localhost:3001" -ForegroundColor Yellow
Write-Host "  Teacher:  http://localhost:3002" -ForegroundColor Yellow  
Write-Host "  Student:  http://localhost:3003" -ForegroundColor Yellow
Write-Host "  Main:     http://localhost:3000" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Blue
Write-Host "⚠️  Use Ctrl+C to stop individual frontends" -ForegroundColor Red

# Keep script running
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
