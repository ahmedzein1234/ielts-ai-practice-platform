# 🚀 IELTS AI Platform - Quick Deployment Script (PowerShell)
# This script helps you deploy your IELTS AI Platform to Railway and Vercel

param(
    [switch]$SkipRailwayLogin
)

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Railway CLI is installed
function Test-RailwayCLI {
    try {
        $null = Get-Command railway -ErrorAction Stop
        Write-Success "Railway CLI already installed"
        return $true
    }
    catch {
        Write-Status "Installing Railway CLI..."
        npm install -g @railway/cli
        Write-Success "Railway CLI installed"
        return $true
    }
}

# Check if user is logged into Railway
function Test-RailwayLogin {
    if ($SkipRailwayLogin) {
        Write-Warning "Skipping Railway login check"
        return $true
    }
    
    try {
        $null = railway whoami 2>$null
        Write-Success "Logged into Railway"
        return $true
    }
    catch {
        Write-Warning "Please login to Railway first:"
        Write-Host "railway login" -ForegroundColor Cyan
        return $false
    }
}

# Deploy API Gateway
function Deploy-APIGateway {
    Write-Status "Deploying API Gateway..."
    Push-Location services/api
    
    if (-not (Test-Path "railway.json")) {
        railway init --name "ielts-api-gateway"
    }
    
    railway up
    Write-Success "API Gateway deployed"
    Pop-Location
}

# Deploy Scoring Service
function Deploy-ScoringService {
    Write-Status "Deploying Scoring Service..."
    Push-Location services/scoring
    
    if (-not (Test-Path "railway.json")) {
        railway init --name "ielts-scoring-service"
    }
    
    railway up
    Write-Success "Scoring Service deployed"
    Pop-Location
}

# Deploy AI Tutor Service
function Deploy-AITutorService {
    Write-Status "Deploying AI Tutor Service..."
    Push-Location services/ai-tutor
    
    if (-not (Test-Path "railway.json")) {
        railway init --name "ielts-ai-tutor-service"
    }
    
    railway up
    Write-Success "AI Tutor Service deployed"
    Pop-Location
}

# Main deployment function
function Start-Deployment {
    Write-Host "🚀 IELTS AI Platform Deployment Script" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Status "Starting deployment process..."
    
    # Check prerequisites
    if (-not (Test-RailwayCLI)) {
        Write-Error "Failed to install Railway CLI"
        exit 1
    }
    
    if (-not (Test-RailwayLogin)) {
        Write-Error "Please login to Railway and run the script again"
        exit 1
    }
    
    # Deploy services
    Deploy-APIGateway
    Deploy-ScoringService
    Deploy-AITutorService
    
    Write-Success "Backend services deployed successfully!"
    Write-Host ""
    Write-Status "Next steps:"
    Write-Host "1. Set up environment variables in Railway dashboard" -ForegroundColor White
    Write-Host "2. Deploy frontend to Vercel" -ForegroundColor White
    Write-Host "3. Configure database (Supabase)" -ForegroundColor White
    Write-Host "4. Set up Redis Cloud" -ForegroundColor White
    Write-Host ""
    Write-Status "See DEPLOYMENT_GUIDE.md for detailed instructions"
}

# Run main function
Start-Deployment
