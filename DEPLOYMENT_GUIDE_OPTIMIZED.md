# IELTS AI Platform - Optimized MCP Deployment Guide

## 🎯 **Overview**

This guide covers the streamlined deployment using **Railway (backend) + Cloudflare Pages (frontend) + Supabase (database)** with proper MCP integration.

## 🚀 **Quick Start**

### **1. Install MCP Servers**
```bash
# Install all required MCP servers and CLI tools
npm run setup:mcp
```

### **2. Configure Environment Variables**
```bash
# Copy and configure environment variables
cp env.example .env
# Edit .env with your API keys and tokens
```

### **3. Deploy Everything**
```bash
# Deploy with debug logging
npm run deploy:debug
```

## 📋 **Prerequisites**

### **Required API Keys & Tokens**

| Service | Token/Key | Where to Get |
|---------|-----------|--------------|
| **Railway** | `RAILWAY_TOKEN` | [Railway Account Tokens](https://railway.app/account/tokens) |
| **Cloudflare** | `CLOUDFLARE_API_TOKEN` | [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens) |
| **Cloudflare** | `CLOUDFLARE_ACCOUNT_ID` | [Cloudflare Dashboard](https://dash.cloudflare.com/) |
| **Supabase** | `SUPABASE_ANON_KEY` | [Supabase Project Settings](https://supabase.com/dashboard/project/_/settings/api) |
| **Supabase** | `SUPABASE_SERVICE_ROLE_KEY` | [Supabase Project Settings](https://supabase.com/dashboard/project/_/settings/api) |
| **GitHub** | `GITHUB_PERSONAL_ACCESS_TOKEN` | [GitHub Personal Access Tokens](https://github.com/settings/tokens) |
| **OpenRouter** | `OPENROUTER_API_KEY` | [OpenRouter Dashboard](https://openrouter.ai/keys) |
| **OpenAI** | `OPENAI_API_KEY` | [OpenAI API Keys](https://platform.openai.com/api-keys) |
| **Anthropic** | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) |

### **Environment Setup**
```bash
# Create .env file with all required variables
cat > .env << EOF
# Railway Deployment
RAILWAY_TOKEN=your_railway_token_here
CLOUDFLARE_API_TOKEN=your_cloudflare_token_here
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id_here

# Supabase Configuration
SUPABASE_URL=https://zzvskbvqtglzonftpikf.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# GitHub Integration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here

# AI API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Database
DATABASE_URL=postgresql://postgres:[password]@db.zzvskbvqtglzonftpikf.supabase.co:5432/postgres
EOF
```

## 🛠 **Installation Steps**

### **Step 1: Setup MCP Servers**
```bash
# Install all MCP servers and CLI tools
npm run setup:mcp

# Verify installation
railway --version
wrangler --version
supabase --version
```

### **Step 2: Configure Authentication**
```bash
# Login to each platform
railway login
wrangler login
supabase login
```

### **Step 3: Validate Configuration**
```bash
# Test MCP integration
npm run test
```

## 🚀 **Deployment Commands**

### **Full Deployment**
```bash
# Deploy everything with debug logging
npm run deploy:debug

# Deploy without debug output
npm run deploy
```

### **Individual Components**
```bash
# Frontend only (Cloudflare Pages)
cd apps/web && npm run deploy

# Backend services (Railway)
railway up --service api
railway up --service scoring
# ... etc for each service
```

## 📊 **Deployment Architecture**

```mermaid
graph TB
    subgraph "MCP Integration Layer"
        A[Optimized MCP Manager]
        B[Railway MCP Server]
        C[Cloudflare MCP Server]
        D[Supabase MCP Server]
    end

    subgraph "Railway Platform"
        E[API Service]
        F[Scoring Service]
        G[Exam Generator]
        H[OCR Service]
        I[Speech Service]
        J[AI Tutor Service]
        K[Worker Service]
    end

    subgraph "Cloudflare Platform"
        L[Pages - Frontend]
        M[CDN & DNS]
    end

    subgraph "Supabase Platform"
        N[PostgreSQL Database]
        O[Authentication]
        P[File Storage]
        Q[Real-time]
    end

    A --> B
    A --> C
    A --> D

    B --> E
    B --> F
    B --> G
    B --> H
    B --> I
    B --> J
    B --> K

    C --> L
    C --> M

    D --> N
    D --> O
    D --> P
    D --> Q
```

## 🔧 **Key Improvements**

### **✅ What's Fixed**
- ❌ **Removed Vercel** - No more platform conflicts
- ✅ **Real MCP Protocol** - Proper JSON-RPC 2.0 implementation
- ✅ **Streamlined Config** - Only 5 essential MCP servers
- ✅ **Static Export** - Next.js configured for Cloudflare Pages
- ✅ **Environment Variables** - Proper Railway + Cloudflare URLs
- ✅ **CSP Policies** - Updated for Cloudflare CDN

### **🗑️ Removed Redundancies**
- Vercel MCP server
- UI Components MCP server  
- Context Assistant MCP server
- Multiple deployment scripts
- Hardcoded personal URLs

### **🎯 Optimized MCP Servers (5 servers)**
1. **Railway** - Backend deployment
2. **Cloudflare** - Frontend deployment
3. **Supabase** - Database, auth, storage
4. **GitHub** - Source control
5. **OpenRouter** - AI model access

## 🏥 **Health Checks**

### **Automated Validation**
```bash
# Check all services
npm run health-check

# Monitor deployment
npm run monitor
```

### **Manual Verification**
- **Frontend**: `https://ielts-ai-platform.pages.dev`
- **API Service**: `https://api-ielts-ai-platform.railway.app/health`
- **Supabase**: `https://zzvskbvqtglzonftpikf.supabase.co/rest/v1/`

## 💰 **Cost Optimization**

### **Monthly Costs**
- **Cloudflare Pages**: Free (100k requests/month)
- **Railway**: ~$30-60/month (7 services)
- **Supabase**: Free tier (500MB database, 1GB storage)
- **Total**: ~$30-60/month

### **vs Previous Setup**
- **50% cost reduction** by removing Vercel
- **Simplified billing** - only 2 paid platforms
- **Better performance** with Cloudflare CDN

## 🚨 **Troubleshooting**

### **Common Issues**

#### **MCP Server Not Starting**
```bash
# Check if packages are installed
npm list -g @jason-tan-swe/railway-mcp
npm list -g @cloudflare/wrangler-mcp

# Reinstall if missing
npm run setup:mcp
```

#### **Environment Variables Missing**
```bash
# Validate all required variables
node scripts/setup-mcp-servers.js
```

#### **Build Failures**
```bash
# Check Next.js configuration
cd apps/web
npm run build

# Common fix: ensure output is set to 'export'
```

#### **Railway Deployment Issues**
```bash
# Check Railway status
railway status

# View logs
railway logs --service api
```

#### **Cloudflare Pages Issues**
```bash
# Check Wrangler authentication
wrangler whoami

# Manual deployment
cd apps/web
npm run build
wrangler pages deploy out --project-name ielts-ai-platform
```

## 📚 **Additional Resources**

### **Documentation**
- [Railway MCP Server](https://smithery.ai/server/@jason-tan-swe/railway-mcp)
- [Cloudflare Wrangler MCP](https://smithery.ai/server/@cloudflare/wrangler-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### **Platform Docs**
- [Railway Documentation](https://docs.railway.app)
- [Cloudflare Pages](https://developers.cloudflare.com/pages)
- [Supabase Documentation](https://supabase.com/docs)

## 🎉 **Success Metrics**

After successful deployment, you should have:

✅ **7 Backend Services** running on Railway  
✅ **Frontend** deployed to Cloudflare Pages  
✅ **Database** configured in Supabase  
✅ **5 MCP Servers** properly integrated  
✅ **Environment Variables** configured  
✅ **Health Checks** passing  
✅ **Cost Optimization** achieved  
✅ **No Platform Conflicts**

## 🚀 **Next Steps**

1. **Custom Domain**: Configure your domain in Cloudflare
2. **SSL Certificate**: Automatic with Cloudflare
3. **Monitoring**: Set up Railway and Cloudflare alerts
4. **CI/CD**: Configure GitHub Actions
5. **Performance**: Monitor with Cloudflare Analytics
6. **Scaling**: Configure Railway auto-scaling

---

**🎯 Ready to deploy? Run: `npm run setup:mcp && npm run deploy:debug`**