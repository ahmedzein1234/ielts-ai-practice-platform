#!/bin/bash

# IELTS AI Platform - Production Deployment Script with Supabase
# Hybrid Deployment: Cloudflare Pages (Frontend) + Railway (Backend) + Supabase (Database/Auth/Storage)

set -e

echo "🚀 Starting IELTS AI Platform Production Deployment with Supabase..."

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
SUPABASE_PROJECT_ID="zzvskbvqtglzonftpikf"

# Environment variables
export RAILWAY_TOKEN="${RAILWAY_TOKEN}"
export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN}"
export SUPABASE_ACCESS_TOKEN="${SUPABASE_ACCESS_TOKEN}"

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
    
    # Check if Supabase CLI is installed
    if ! command -v supabase &> /dev/null; then
        print_warning "Supabase CLI is not installed. Installing..."
        npm install -g supabase
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
    
    if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
        print_warning "SUPABASE_ACCESS_TOKEN environment variable is not set (optional for deployment)"
    fi
    
    print_success "Prerequisites check passed"
}

# Verify Supabase setup
verify_supabase() {
    print_status "Verifying Supabase setup..."
    
    # Check if Supabase project exists
    if supabase projects list --access-token "$SUPABASE_ACCESS_TOKEN" | grep -q "$SUPABASE_PROJECT_ID"; then
        print_success "Supabase project found"
    else
        print_error "Supabase project not found. Please check your project ID."
        exit 1
    fi
    
    # Verify database schema
    print_status "Verifying database schema..."
    if supabase db diff --project-ref "$SUPABASE_PROJECT_ID" --access-token "$SUPABASE_ACCESS_TOKEN" | grep -q "No differences"; then
        print_success "Database schema is up to date"
    else
        print_warning "Database schema has differences. Consider running migrations."
    fi
    
    print_success "Supabase verification completed"
}

# Deploy backend services to Railway (simplified - no database)
deploy_backend() {
    print_status "Deploying backend services to Railway..."
    
    # Login to Railway
    echo "$RAILWAY_TOKEN" | railway login
    
    # Deploy each service (no PostgreSQL/Redis needed)
    services=("api" "scoring" "exam-generator" "ocr" "speech" "ai-tutor" "worker")
    
    for service in "${services[@]}"; do
        print_status "Deploying $service service..."
        
        cd "services/$service" || cd "workers"
        
        # Deploy to Railway
        railway up --service "$service" --detach
        
        cd ../..
        
        print_success "$service service deployed successfully"
    done
    
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

# Setup Supabase storage buckets
setup_supabase_storage() {
    print_status "Setting up Supabase storage buckets..."
    
    # Create storage buckets if they don't exist
    buckets=("ielts-uploads" "audio-recordings" "documents" "user-avatars")
    
    for bucket in "${buckets[@]}"; do
        print_status "Creating bucket: $bucket"
        
        # Create bucket using Supabase CLI
        supabase storage create-bucket "$bucket" \
            --project-ref "$SUPABASE_PROJECT_ID" \
            --access-token "$SUPABASE_ACCESS_TOKEN" || print_warning "Bucket $bucket might already exist"
    done
    
    # Set up bucket policies
    print_status "Setting up bucket policies..."
    
    # Create RLS policies for storage
    cat > storage-policies.sql << EOF
-- Enable RLS on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy for authenticated users to upload files
CREATE POLICY "Users can upload files" ON storage.objects
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Policy for users to view their own files
CREATE POLICY "Users can view own files" ON storage.objects
    FOR SELECT USING (auth.uid()::text = (storage.foldername(name))[1]);

-- Policy for users to update their own files
CREATE POLICY "Users can update own files" ON storage.objects
    FOR UPDATE USING (auth.uid()::text = (storage.foldername(name))[1]);

-- Policy for users to delete their own files
CREATE POLICY "Users can delete own files" ON storage.objects
    FOR DELETE USING (auth.uid()::text = (storage.foldername(name))[1]);
EOF
    
    # Apply policies
    supabase db push --project-ref "$SUPABASE_PROJECT_ID" --access-token "$SUPABASE_ACCESS_TOKEN" --file storage-policies.sql
    
    print_success "Supabase storage configured successfully"
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
        --env-production NEXT_PUBLIC_SUPABASE_URL="https://$SUPABASE_PROJECT_ID.supabase.co" \
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
    
    # Check Supabase connection
    SUPABASE_URL="https://$SUPABASE_PROJECT_ID.supabase.co"
    if curl -f "$SUPABASE_URL/rest/v1/" > /dev/null 2>&1; then
        print_success "Supabase connection check passed"
    else
        print_warning "Supabase connection check failed (continuing...)"
    fi
    
    print_success "Health checks completed"
}

# Main deployment flow
main() {
    print_status "Starting production deployment with Supabase..."
    
    check_prerequisites
    verify_supabase
    deploy_backend
    deploy_frontend
    setup_supabase_storage
    setup_dns
    health_check
    
    print_success "🎉 Production deployment completed successfully!"
    print_status "Frontend URL: https://$CLOUDFLARE_PAGES_PROJECT.pages.dev"
    print_status "Backend Services: Railway Dashboard"
    print_status "Database & Auth: Supabase Dashboard"
    print_status "File Storage: Supabase Storage"
    print_status "Supabase Project: https://$SUPABASE_PROJECT_ID.supabase.co"
}

# Run main function
main "$@"
