#!/bin/bash

# Enhanced AI Tutor Deployment Script
# This script deploys the enhanced AI Tutor features with WebSocket and speech processing

set -e

echo "🚀 Starting Enhanced AI Tutor Deployment..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.example .env
    print_warning "Please update .env file with your API keys before continuing."
    print_warning "Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY"
    exit 1
fi

# Check if required environment variables are set
print_status "Checking environment variables..."
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key" ]; then
    print_error "OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-anthropic-api-key" ]; then
    print_error "ANTHROPIC_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$OPENROUTER_API_KEY" ] || [ "$OPENROUTER_API_KEY" = "your-openrouter-api-key" ]; then
    print_error "OPENROUTER_API_KEY not set in .env file"
    exit 1
fi

print_success "Environment variables configured"

# Stop any running containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Build and start the enhanced services
print_status "Building enhanced AI Tutor services..."
docker-compose build ai-tutor web

print_status "Starting enhanced services..."
docker-compose up -d postgres redis api scoring ai-tutor

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
print_status "Checking service health..."

# Check AI Tutor service
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "AI Tutor service is healthy"
else
    print_error "AI Tutor service is not responding"
    docker-compose logs ai-tutor
    exit 1
fi

# Check API service
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API service is healthy"
else
    print_error "API service is not responding"
    docker-compose logs api
    exit 1
fi

# Start the web frontend
print_status "Starting web frontend..."
docker-compose up -d web

# Wait for web service
sleep 5

# Check web service
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Web frontend is healthy"
else
    print_error "Web frontend is not responding"
    docker-compose logs web
    exit 1
fi

print_success "🎉 Enhanced AI Tutor deployment completed successfully!"

echo ""
echo "📋 Service URLs:"
echo "  🌐 Web Frontend: http://localhost:3000"
echo "  🤖 AI Tutor API: http://localhost:8001"
echo "  📊 API Service: http://localhost:8000"
echo "  📈 Scoring Service: http://localhost:8001"
echo ""
echo "🔗 Enhanced Features:"
echo "  💬 Enhanced AI Tutor: http://localhost:3000/ai-tutor/enhanced"
echo "  🎤 Voice Interaction: Available in enhanced interface"
echo "  📊 Speech Analysis: Real-time feedback"
echo "  🔄 WebSocket: ws://localhost:8001/ws"
echo ""
echo "📚 Documentation:"
echo "  📖 API Docs: http://localhost:8001/docs"
echo "  📖 Deployment Guide: DEPLOYMENT_GUIDE_ENHANCED.md"
echo "  📖 Integration Summary: FRONTEND_INTEGRATION_SUMMARY.md"
echo ""
echo "🔧 Management Commands:"
echo "  📊 View logs: docker-compose logs -f [service-name]"
echo "  🛑 Stop services: docker-compose down"
echo "  🔄 Restart services: docker-compose restart"
echo "  🧹 Clean up: docker-compose down -v --remove-orphans"
echo ""

# Show running containers
print_status "Running containers:"
docker-compose ps

print_success "Enhanced AI Tutor is ready for use! 🚀"
