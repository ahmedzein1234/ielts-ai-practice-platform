# Enhanced AI Tutor Deployment Script for Windows
# This script deploys the enhanced AI Tutor features with WebSocket and speech processing

param(
    [switch]$SkipChecks,
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Enhanced AI Tutor Deployment..." -ForegroundColor Blue

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
    Write-Warning "Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY"
    exit 1
}

# Check if required environment variables are set
Write-Status "Checking environment variables..."

# Read .env file and check for required variables
$envContent = Get-Content ".env" | Where-Object { $_ -match "=" }
$envVars = @{}

foreach ($line in $envContent) {
    if ($line -match "^([^#][^=]+)=(.*)$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

$requiredVars = @("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY")
$missingVars = @()

foreach ($var in $requiredVars) {
    if (-not $envVars.ContainsKey($var) -or $envVars[$var] -eq "your-$var.ToLower()-api-key") {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Error "Missing or invalid environment variables: $($missingVars -join ', ')"
    Write-Error "Please update .env file with valid API keys"
    exit 1
}

Write-Success "Environment variables configured"

# Check if Docker is running
Write-Status "Checking Docker status..."
try {
    docker version | Out-Null
    Write-Success "Docker is running"
}
catch {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Stop any running containers
Write-Status "Stopping existing containers..."
try {
    docker-compose down --remove-orphans
    Write-Success "Existing containers stopped"
}
catch {
    Write-Warning "No existing containers to stop"
}

# Build and start the enhanced services
Write-Status "Building enhanced AI Tutor services..."
try {
    docker-compose build ai-tutor web
    Write-Success "Services built successfully"
}
catch {
    Write-Error "Failed to build services"
    exit 1
}

Write-Status "Starting enhanced services..."
try {
    docker-compose up -d postgres redis api scoring ai-tutor
    Write-Success "Core services started"
}
catch {
    Write-Error "Failed to start core services"
    exit 1
}

# Wait for services to be ready
Write-Status "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Check if services are running
Write-Status "Checking service health..."

# Function to check service health
function Test-ServiceHealth {
    param([string]$Url, [string]$ServiceName)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "$ServiceName is healthy"
            return $true
        }
        else {
            Write-Error "$ServiceName is not responding (Status: $($response.StatusCode))"
            return $false
        }
    }
    catch {
        Write-Error "$ServiceName is not responding"
        return $false
    }
}

# Check AI Tutor service
$aiTutorHealthy = Test-ServiceHealth "http://localhost:8001/health" "AI Tutor service"
if (-not $aiTutorHealthy) {
    Write-Status "AI Tutor service logs:"
    docker-compose logs ai-tutor
    exit 1
}

# Check API service
$apiHealthy = Test-ServiceHealth "http://localhost:8000/health" "API service"
if (-not $apiHealthy) {
    Write-Status "API service logs:"
    docker-compose logs api
    exit 1
}

# Start the web frontend
Write-Status "Starting web frontend..."
try {
    docker-compose up -d web
    Write-Success "Web frontend started"
}
catch {
    Write-Error "Failed to start web frontend"
    exit 1
}

# Wait for web service
Start-Sleep -Seconds 5

# Check web service
$webHealthy = Test-ServiceHealth "http://localhost:3000" "Web frontend"
if (-not $webHealthy) {
    Write-Status "Web frontend logs:"
    docker-compose logs web
    exit 1
}

Write-Success "🎉 Enhanced AI Tutor deployment completed successfully!"

Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Cyan
Write-Host "  🌐 Web Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  🤖 AI Tutor API: http://localhost:8001" -ForegroundColor White
Write-Host "  📊 API Service: http://localhost:8000" -ForegroundColor White
Write-Host "  📈 Scoring Service: http://localhost:8001" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Enhanced Features:" -ForegroundColor Cyan
Write-Host "  💬 Enhanced AI Tutor: http://localhost:3000/ai-tutor/enhanced" -ForegroundColor White
Write-Host "  🎤 Voice Interaction: Available in enhanced interface" -ForegroundColor White
Write-Host "  📊 Speech Analysis: Real-time feedback" -ForegroundColor White
Write-Host "  🔄 WebSocket: ws://localhost:8001/ws" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  📖 API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  📖 Deployment Guide: DEPLOYMENT_GUIDE_ENHANCED.md" -ForegroundColor White
Write-Host "  📖 Integration Summary: FRONTEND_INTEGRATION_SUMMARY.md" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "  📊 View logs: docker-compose logs -f [service-name]" -ForegroundColor White
Write-Host "  🛑 Stop services: docker-compose down" -ForegroundColor White
Write-Host "  🔄 Restart services: docker-compose restart" -ForegroundColor White
Write-Host "  🧹 Clean up: docker-compose down -v --remove-orphans" -ForegroundColor White
Write-Host ""

# Show running containers
Write-Status "Running containers:"
docker-compose ps

Write-Success "Enhanced AI Tutor is ready for use! 🚀"

# Open the enhanced AI Tutor in default browser
Write-Status "Opening Enhanced AI Tutor in browser..."
Start-Process "http://localhost:3000/ai-tutor/enhanced"
