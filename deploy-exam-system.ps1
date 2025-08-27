# IELTS Exam Generation System Deployment Script for Windows
# This script deploys the complete exam generation system with OpenRouter integration

param(
    [switch]$SkipChecks,
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting IELTS Exam Generation System Deployment..." -ForegroundColor Blue

# Function to print colored output
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

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Warning ".env file not found. Creating from template..."
    Copy-Item "env.example" ".env"
    Write-Warning "Please update .env file with your API keys before continuing."
    Write-Warning "Required: OPENROUTER_API_KEY"
    exit 1
}

# Check if OpenRouter API key is set
$envContent = Get-Content ".env"
if ($envContent -notmatch "OPENROUTER_API_KEY=sk-or-") {
    Write-Error "OpenRouter API key not found in .env file"
    Write-Error "Please add your OpenRouter API key to the .env file"
    exit 1
}

Write-Status "Checking Docker installation..."
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
    Write-Success "Docker and Docker Compose are available"
}
catch {
    Write-Error "Docker is not installed or not running. Please install Docker Desktop first."
    exit 1
}

# Stop any existing containers
Write-Status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build the exam generator service
Write-Status "Building exam generator service..."
docker-compose build exam-generator

# Build the web frontend
Write-Status "Building web frontend..."
docker-compose build web

# Start the core services
Write-Status "Starting core services..."
docker-compose up -d postgres redis

# Wait for database to be ready
Write-Status "Waiting for database to be ready..."
Start-Sleep -Seconds 10

# Start the exam generator service
Write-Status "Starting exam generator service..."
docker-compose up -d exam-generator

# Start the web frontend
Write-Status "Starting web frontend..."
docker-compose up -d web

# Wait for services to be ready
Write-Status "Waiting for services to be ready..."
Start-Sleep -Seconds 15

# Check service health
Write-Status "Checking service health..."

# Check exam generator health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8006/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Exam Generator Service is healthy"
    }
    else {
        throw "Service not responding"
    }
}
catch {
    Write-Error "Exam Generator Service is not responding"
    docker-compose logs exam-generator
    exit 1
}

# Check web frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Web Frontend is healthy"
    }
    else {
        throw "Service not responding"
    }
}
catch {
    Write-Error "Web Frontend is not responding"
    docker-compose logs web
    exit 1
}

Write-Success "🎉 IELTS Exam Generation System deployed successfully!"

Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Cyan
Write-Host "  • Web Frontend: http://localhost:3000"
Write-Host "  • Exam Creator: http://localhost:3000/exam-creator"
Write-Host "  • Exam Simulator: http://localhost:3000/exam-simulator"
Write-Host "  • Exam Generator API: http://localhost:8006"
Write-Host "  • API Documentation: http://localhost:8006/docs"
Write-Host ""

Write-Host "🔧 Available Features:" -ForegroundColor Cyan
Write-Host "  • AI-powered exam generation using OpenRouter"
Write-Host "  • Academic and General Training IELTS exams"
Write-Host "  • 4 difficulty levels (Beginner to Expert)"
Write-Host "  • Real-time exam simulation"
Write-Host "  • Custom topic selection"
Write-Host "  • Authentic IELTS-style content"
Write-Host ""

Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open http://localhost:3000/exam-creator"
Write-Host "  2. Configure your exam parameters"
Write-Host "  3. Generate your first IELTS practice test"
Write-Host "  4. Use the exam simulator for realistic practice"
Write-Host ""

Write-Success "Deployment completed! The IELTS Exam Generation System is ready to use."
