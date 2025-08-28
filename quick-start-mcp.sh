#!/bin/bash

# IELTS AI Platform - MCP Integration Quick Start Script
# This script automates the initial setup for MCP integration

set -e

echo "🚀 IELTS AI Platform - MCP Integration Quick Start"
echo "=================================================="

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

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    print_warning "Detected Windows. Some commands may need adjustment."
    # Use PowerShell equivalent for Windows
    SCRIPT_EXTENSION=".ps1"
else
    SCRIPT_EXTENSION=".sh"
fi

# Step 1: Check prerequisites
print_status "Step 1: Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    echo "Download from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node --version)"
    exit 1
fi

print_success "Node.js $(node --version) is installed"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed."
    exit 1
fi

print_success "npm $(npm --version) is installed"

# Step 2: Install global dependencies
print_status "Step 2: Installing global dependencies..."

# Install Railway CLI
if ! command -v railway &> /dev/null; then
    print_status "Installing Railway CLI..."
    npm install -g @railway/cli
    print_success "Railway CLI installed"
else
    print_success "Railway CLI already installed"
fi

# Install Wrangler CLI
if ! command -v wrangler &> /dev/null; then
    print_status "Installing Wrangler CLI..."
    npm install -g wrangler
    print_success "Wrangler CLI installed"
else
    print_success "Wrangler CLI already installed"
fi

# Install Supabase CLI
if ! command -v supabase &> /dev/null; then
    print_status "Installing Supabase CLI..."
    npm install -g supabase
    print_success "Supabase CLI installed"
else
    print_success "Supabase CLI already installed"
fi

# Step 3: Install project dependencies
print_status "Step 3: Installing project dependencies..."

if [ -f "package.json" ]; then
    npm install
    print_success "Project dependencies installed"
else
    print_warning "No package.json found. Creating basic package.json..."
    cat > package.json << EOF
{
  "name": "ielts-ai-platform-mcp-deployment",
  "version": "1.0.0",
  "description": "IELTS AI Platform - MCP Integration Deployment Script",
  "main": "mcp-deployment-integration.js",
  "scripts": {
    "deploy": "node mcp-deployment-integration.js",
    "test": "node scripts/test-mcp-integration.js",
    "setup": "npm install -g @railway/cli wrangler supabase"
  },
  "dependencies": {
    "node-fetch": "^3.3.2",
    "commander": "^11.1.0",
    "chalk": "^5.3.0",
    "ora": "^7.0.1",
    "inquirer": "^9.2.12",
    "dotenv": "^16.3.1"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
    npm install
    print_success "Basic package.json created and dependencies installed"
fi

# Step 4: Create environment template
print_status "Step 4: Creating environment template..."

if [ ! -f ".env" ]; then
    cat > .env.template << EOF
# Railway Configuration
RAILWAY_TOKEN=your_railway_token_here

# Cloudflare Configuration
CLOUDFLARE_API_TOKEN=your_cloudflare_token_here

# Supabase Configuration
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
SUPABASE_ACCESS_TOKEN=your_supabase_access_token_here

# AI API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Project Configuration
PROJECT_NAME=ielts-ai-platform
SUPABASE_PROJECT_ID=zzvskbvqtglzonftpikf
EOF
    print_success "Environment template created: .env.template"
    print_warning "Please copy .env.template to .env and fill in your actual values"
else
    print_success "Environment file already exists"
fi

# Step 5: Make scripts executable
print_status "Step 5: Making scripts executable..."

if [ -f "mcp-deployment-integration.js" ]; then
    chmod +x mcp-deployment-integration.js
    print_success "Deployment script made executable"
fi

if [ -f "scripts/test-mcp-integration.js" ]; then
    chmod +x scripts/test-mcp-integration.js
    print_success "Test script made executable"
fi

if [ -f "deploy-supabase-production.sh" ]; then
    chmod +x deploy-supabase-production.sh
    print_success "Production deployment script made executable"
fi

# Step 6: Create quick start guide
print_status "Step 6: Creating quick start guide..."

cat > QUICK_START_GUIDE.md << EOF
# IELTS AI Platform - Quick Start Guide

## 🚀 Getting Started

### 1. Set up Environment Variables
\`\`\`bash
# Copy the template and fill in your values
cp .env.template .env

# Edit the .env file with your actual API keys and tokens
nano .env
\`\`\`

### 2. Test the Setup
\`\`\`bash
# Run the test script to verify everything is working
npm run test

# Or run directly
node scripts/test-mcp-integration.js
\`\`\`

### 3. Deploy the Platform
\`\`\`bash
# Deploy everything
npm run deploy

# Or run directly
node mcp-deployment-integration.js
\`\`\`

## 📋 Required API Keys & Tokens

| Platform | Token/Key | Where to Get |
|----------|-----------|--------------|
| **Railway** | \`RAILWAY_TOKEN\` | [Railway Account Tokens](https://railway.app/account/tokens) |
| **Cloudflare** | \`CLOUDFLARE_API_TOKEN\` | [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens) |
| **Supabase** | \`SUPABASE_ANON_KEY\` | [Supabase Project Settings](https://supabase.com/dashboard/project/_/settings/api) |
| **Supabase** | \`SUPABASE_SERVICE_ROLE_KEY\` | [Supabase Project Settings](https://supabase.com/dashboard/project/_/settings/api) |
| **OpenAI** | \`OPENAI_API_KEY\` | [OpenAI API Keys](https://platform.openai.com/api-keys) |
| **Anthropic** | \`ANTHROPIC_API_KEY\` | [Anthropic Console](https://console.anthropic.com/) |
| **OpenRouter** | \`OPENROUTER_API_KEY\` | [OpenRouter Dashboard](https://openrouter.ai/keys) |

## 🎯 Next Steps

1. **Configure Environment**: Fill in your API keys in the \`.env\` file
2. **Test Setup**: Run \`npm run test\` to verify everything works
3. **Deploy**: Run \`npm run deploy\` to deploy your platform
4. **Monitor**: Check the deployment status and logs
5. **Customize**: Modify configuration as needed

## 📚 Documentation

- [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)
- [Deployment Strategy](DEPLOYMENT_STRATEGY_SUPABASE.md)
- [Troubleshooting](MCP_INTEGRATION_GUIDE.md#troubleshooting)

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section in the documentation
2. Run \`npm run test\` to identify specific problems
3. Check the logs for detailed error messages
4. Verify all API keys and tokens are correct

---

**Happy deploying! 🚀✨**
EOF

print_success "Quick start guide created: QUICK_START_GUIDE.md"

# Step 7: Display next steps
echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "1. Copy .env.template to .env and fill in your API keys"
echo "2. Run: npm run test (to verify everything works)"
echo "3. Run: npm run deploy (to deploy your platform)"
echo ""
echo "📚 Documentation:"
echo "- Quick Start Guide: QUICK_START_GUIDE.md"
echo "- MCP Integration: MCP_INTEGRATION_GUIDE.md"
echo "- Deployment Strategy: DEPLOYMENT_STRATEGY_SUPABASE.md"
echo ""
echo "🔧 Available Commands:"
echo "- npm run test     # Test the setup"
echo "- npm run deploy   # Deploy the platform"
echo "- npm run setup    # Reinstall global dependencies"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning "⚠️  IMPORTANT: You need to create a .env file with your API keys"
    echo "   Run: cp .env.template .env"
    echo "   Then edit .env with your actual API keys and tokens"
    echo ""
fi

print_success "Setup complete! Ready to deploy your IELTS AI Platform with MCP integration! 🚀"
