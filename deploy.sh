#!/bin/bash

# 🚀 IELTS AI Platform - Quick Deployment Script
# This script helps you deploy your IELTS AI Platform to Railway and Vercel

set -e

echo "🚀 IELTS AI Platform Deployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        print_status "Installing Railway CLI..."
        npm install -g @railway/cli
        print_success "Railway CLI installed"
    else
        print_success "Railway CLI already installed"
    fi
}

# Check if user is logged into Railway
check_railway_login() {
    if ! railway whoami &> /dev/null; then
        print_warning "Please login to Railway first:"
        echo "railway login"
        exit 1
    fi
    print_success "Logged into Railway"
}

# Deploy API Gateway
deploy_api_gateway() {
    print_status "Deploying API Gateway..."
    cd services/api
    
    if [ ! -f "railway.json" ]; then
        railway init --name "ielts-api-gateway"
    fi
    
    railway up
    print_success "API Gateway deployed"
    cd ../..
}

# Deploy Scoring Service
deploy_scoring_service() {
    print_status "Deploying Scoring Service..."
    cd services/scoring
    
    if [ ! -f "railway.json" ]; then
        railway init --name "ielts-scoring-service"
    fi
    
    railway up
    print_success "Scoring Service deployed"
    cd ../..
}

# Deploy AI Tutor Service
deploy_ai_tutor_service() {
    print_status "Deploying AI Tutor Service..."
    cd services/ai-tutor
    
    if [ ! -f "railway.json" ]; then
        railway init --name "ielts-ai-tutor-service"
    fi
    
    railway up
    print_success "AI Tutor Service deployed"
    cd ../..
}

# Main deployment function
main() {
    print_status "Starting deployment process..."
    
    # Check prerequisites
    check_railway_cli
    check_railway_login
    
    # Deploy services
    deploy_api_gateway
    deploy_scoring_service
    deploy_ai_tutor_service
    
    print_success "Backend services deployed successfully!"
    echo ""
    print_status "Next steps:"
    echo "1. Set up environment variables in Railway dashboard"
    echo "2. Deploy frontend to Vercel"
    echo "3. Configure database (Supabase)"
    echo "4. Set up Redis Cloud"
    echo ""
    print_status "See DEPLOYMENT_GUIDE.md for detailed instructions"
}

# Run main function
main "$@"
