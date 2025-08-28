#!/bin/bash

# IELTS AI Platform - Production Deployment Script
# Hybrid Deployment: Cloudflare Pages (Frontend) + Railway (Backend)

set -e

echo "🚀 Starting IELTS AI Platform Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ielts-ai-platform"
RAILWAY_PROJECT_ID="your-railway-project-id"
CLOUDFLARE_ACCOUNT_ID="your-cloudflare-account-id"
CLOUDFLARE_PAGES_PROJECT="ielts-ai-platform"

# Environment variables
export RAILWAY_TOKEN="${RAILWAY_TOKEN}"
export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if Wrangler CLI is installed
    if ! command -v wrangler &> /dev/null; then
        print_error "Wrangler CLI is not installed. Please install it first:"
        echo "npm install -g wrangler"
        exit 1
    fi
    
    # Check environment variables
    if [ -z "$RAILWAY_TOKEN" ]; then
        print_error "RAILWAY_TOKEN environment variable is not set"
        exit 1
    fi
    
    if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
        print_error "CLOUDFLARE_API_TOKEN environment variable is not set"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Deploy backend services to Railway
deploy_backend() {
    print_status "Deploying backend services to Railway..."
    
    # Login to Railway
    echo "$RAILWAY_TOKEN" | railway login
    
    # Deploy each service
    services=("api" "scoring" "exam-generator" "ocr" "speech" "ai-tutor" "worker")
    
    for service in "${services[@]}"; do
        print_status "Deploying $service service..."
        
        cd "services/$service" || cd "workers"
        
        # Deploy to Railway
        railway up --service "$service" --detach
        
        cd ../..
        
        print_success "$service service deployed successfully"
    done
    
    # Deploy databases
    print_status "Setting up databases..."
    railway up --service postgres --detach
    railway up --service redis --detach
    
    print_success "Backend services deployed successfully"
}

# Deploy frontend to Cloudflare Pages
deploy_frontend() {
    print_status "Deploying frontend to Cloudflare Pages..."
    
    cd apps/web
    
    # Build the application
    print_status "Building Next.js application..."
    npm run build
    
    # Deploy to Cloudflare Pages
    print_status "Deploying to Cloudflare Pages..."
    wrangler pages deploy .next --project-name="$CLOUDFLARE_PAGES_PROJECT" --branch=main
    
    cd ../..
    
    print_success "Frontend deployed successfully"
}

# Setup Cloudflare R2 for file storage
setup_file_storage() {
    print_status "Setting up Cloudflare R2 file storage..."
    
    # Create R2 bucket
    wrangler r2 bucket create ielts-uploads
    
    # Configure CORS
    cat > r2-cors.json << EOF
{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
            "AllowedHeaders": ["*"],
            "MaxAgeSeconds": 3000
        }
    ]
}
EOF
    
    wrangler r2 bucket cors put ielts-uploads --file r2-cors.json
    
    print_success "File storage configured successfully"
}

# Setup DNS and routing
setup_dns() {
    print_status "Setting up DNS and routing..."
    
    # Get Railway service URLs
    API_URL=$(railway status --service api --json | jq -r '.url')
    AI_TUTOR_URL=$(railway status --service ai-tutor --json | jq -r '.url')
    SCORING_URL=$(railway status --service scoring --json | jq -r '.url')
    SPEECH_URL=$(railway status --service speech --json | jq -r '.url')
    OCR_URL=$(railway status --service ocr --json | jq -r '.url')
    EXAM_GENERATOR_URL=$(railway status --service exam-generator --json | jq -r '.url')
    
    # Update Cloudflare Pages environment variables
    wrangler pages project update "$CLOUDFLARE_PAGES_PROJECT" \
        --env-production NEXT_PUBLIC_API_URL="$API_URL" \
        --env-production NEXT_PUBLIC_AI_TUTOR_URL="$AI_TUTOR_URL" \
        --env-production NEXT_PUBLIC_AI_TUTOR_WS_URL="wss://${AI_TUTOR_URL#https://}/ws" \
        --env-production NEXT_PUBLIC_SCORING_URL="$SCORING_URL" \
        --env-production NEXT_PUBLIC_SPEECH_URL="$SPEECH_URL" \
        --env-production NEXT_PUBLIC_OCR_URL="$OCR_URL" \
        --env-production NEXT_PUBLIC_EXAM_GENERATOR_URL="$EXAM_GENERATOR_URL"
    
    print_success "DNS and routing configured successfully"
}

# Run health checks
health_check() {
    print_status "Running health checks..."
    
    # Get frontend URL
    FRONTEND_URL=$(wrangler pages project list --json | jq -r ".[] | select(.name==\"$CLOUDFLARE_PAGES_PROJECT\") | .url")
    
    # Check frontend
    if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
        print_success "Frontend health check passed"
    else
        print_error "Frontend health check failed"
        exit 1
    fi
    
    # Check backend services
    services=("api" "scoring" "exam-generator" "ocr" "speech" "ai-tutor")
    
    for service in "${services[@]}"; do
        SERVICE_URL=$(railway status --service "$service" --json | jq -r '.url')
        
        if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
            print_success "$service health check passed"
        else
            print_warning "$service health check failed (continuing...)"
        fi
    done
    
    print_success "Health checks completed"
}

# Main deployment flow
main() {
    print_status "Starting production deployment..."
    
    check_prerequisites
    deploy_backend
    deploy_frontend
    setup_file_storage
    setup_dns
    health_check
    
    print_success "🎉 Production deployment completed successfully!"
    print_status "Frontend URL: https://$CLOUDFLARE_PAGES_PROJECT.pages.dev"
    print_status "Backend Services: Railway Dashboard"
    print_status "File Storage: Cloudflare R2"
}

# Run main function
main "$@"
