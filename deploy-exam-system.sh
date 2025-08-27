#!/bin/bash

# IELTS Exam Generation System Deployment Script
# This script deploys the complete exam generation system with OpenRouter integration

set -e

echo "🚀 Starting IELTS Exam Generation System Deployment..."

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
    print_warning "Required: OPENROUTER_API_KEY"
    exit 1
fi

# Check if OpenRouter API key is set
if ! grep -q "OPENROUTER_API_KEY=sk-or-" .env; then
    print_error "OpenRouter API key not found in .env file"
    print_error "Please add your OpenRouter API key to the .env file"
    exit 1
fi

print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build the exam generator service
print_status "Building exam generator service..."
docker-compose build exam-generator

# Build the web frontend
print_status "Building web frontend..."
docker-compose build web

# Start the core services
print_status "Starting core services..."
docker-compose up -d postgres redis

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Start the exam generator service
print_status "Starting exam generator service..."
docker-compose up -d exam-generator

# Start the web frontend
print_status "Starting web frontend..."
docker-compose up -d web

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 15

# Check service health
print_status "Checking service health..."

# Check exam generator health
if curl -f http://localhost:8006/health > /dev/null 2>&1; then
    print_success "Exam Generator Service is healthy"
else
    print_error "Exam Generator Service is not responding"
    docker-compose logs exam-generator
    exit 1
fi

# Check web frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Web Frontend is healthy"
else
    print_error "Web Frontend is not responding"
    docker-compose logs web
    exit 1
fi

print_success "🎉 IELTS Exam Generation System deployed successfully!"

echo ""
echo "📋 Service URLs:"
echo "  • Web Frontend: http://localhost:3000"
echo "  • Exam Creator: http://localhost:3000/exam-creator"
echo "  • Exam Simulator: http://localhost:3000/exam-simulator"
echo "  • Exam Generator API: http://localhost:8006"
echo "  • API Documentation: http://localhost:8006/docs"
echo ""

echo "🔧 Available Features:"
echo "  • AI-powered exam generation using OpenRouter"
echo "  • Academic and General Training IELTS exams"
echo "  • 4 difficulty levels (Beginner to Expert)"
echo "  • Real-time exam simulation"
echo "  • Custom topic selection"
echo "  • Authentic IELTS-style content"
echo ""

echo "📚 Next Steps:"
echo "  1. Open http://localhost:3000/exam-creator"
echo "  2. Configure your exam parameters"
echo "  3. Generate your first IELTS practice test"
echo "  4. Use the exam simulator for realistic practice"
echo ""

print_success "Deployment completed! The IELTS Exam Generation System is ready to use."
