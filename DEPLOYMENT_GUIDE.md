# 🚀 IELTS AI Platform - Deployment Guide

## 📋 Overview

This guide covers deploying the IELTS AI Platform to production using Railway (backend) and Vercel (frontend).

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Railway       │    │   Supabase      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│   Next.js       │    │   FastAPI       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis Cloud   │
                       │   (Caching)     │
                       └─────────────────┘
```

## 🛠️ Prerequisites

1. **GitHub Account** - For source code and CI/CD
2. **Railway Account** - For backend services
3. **Vercel Account** - For frontend deployment
4. **Supabase Account** - For database and auth
5. **Redis Cloud Account** - For caching

## 📦 Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note down your project URL and API keys

### 1.2 Environment Variables

Add these to your Railway environment:

```bash
# Database
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_ANON_KEY=[your-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]

# Redis
REDIS_URL=redis://[username]:[password]@[host]:[port]

# AI Services
OPENAI_API_KEY=[your-openai-key]
ANTHROPIC_API_KEY=[your-anthropic-key]

# JWT
JWT_SECRET=[your-jwt-secret]
```

## 🚂 Step 2: Railway Backend Deployment

### 2.1 Install Railway CLI

```bash
npm install -g @railway/cli
```

### 2.2 Login to Railway

```bash
railway login
```

### 2.3 Deploy Services

#### API Gateway
```bash
cd services/api
railway init
railway up
```

#### Scoring Service
```bash
cd services/scoring
railway init
railway up
```

#### AI Tutor Service
```bash
cd services/ai-tutor
railway init
railway up
```

### 2.4 Configure Environment Variables

For each service in Railway dashboard:

1. Go to your service
2. Click "Variables" tab
3. Add all environment variables from Step 1.2

## ⚡ Step 3: Vercel Frontend Deployment

### 3.1 Connect GitHub Repository

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3.2 Environment Variables

Add these to Vercel:

```bash
# API URLs
NEXT_PUBLIC_API_URL=https://[railway-api-url]
NEXT_PUBLIC_SCORING_URL=https://[railway-scoring-url]
NEXT_PUBLIC_AI_TUTOR_URL=https://[railway-ai-tutor-url]

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[project-id].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[your-anon-key]

# Auth
NEXTAUTH_SECRET=[your-nextauth-secret]
NEXTAUTH_URL=https://[your-vercel-domain]
```

## 🔄 Step 4: CI/CD Setup

### 4.1 GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:

```bash
RAILWAY_TOKEN=[your-railway-token]
VERCEL_TOKEN=[your-vercel-token]
VERCEL_ORG_ID=[your-vercel-org-id]
VERCEL_PROJECT_ID=[your-vercel-project-id]
```

### 4.2 Railway Token

```bash
railway login
railway whoami
# Copy the token from Railway dashboard
```

### 4.3 Vercel Token

1. Go to Vercel dashboard → Settings → Tokens
2. Create new token
3. Copy the token

## 🧪 Step 5: Testing Deployment

### 5.1 Health Checks

Test your deployed services:

```bash
# API Gateway
curl https://[railway-api-url]/health

# Scoring Service
curl https://[railway-scoring-url]/health

# AI Tutor Service
curl https://[railway-ai-tutor-url]/health

# Frontend
curl https://[vercel-domain]
```

### 5.2 API Documentation

Access your API docs:

- API Gateway: `https://[railway-api-url]/docs`
- Scoring Service: `https://[railway-scoring-url]/docs`
- AI Tutor Service: `https://[railway-ai-tutor-url]/docs`

## 📊 Step 6: Monitoring & Analytics

### 6.1 Railway Monitoring

- **Logs**: View real-time logs in Railway dashboard
- **Metrics**: Monitor CPU, memory, and network usage
- **Deployments**: Track deployment history

### 6.2 Vercel Analytics

- **Performance**: Monitor Core Web Vitals
- **Analytics**: Track user behavior
- **Functions**: Monitor serverless function performance

### 6.3 Supabase Monitoring

- **Database**: Monitor query performance
- **Auth**: Track user authentication
- **Storage**: Monitor file uploads

## 🔧 Step 7: Custom Domain Setup

### 7.1 Railway Custom Domain

1. Go to Railway service settings
2. Click "Custom Domains"
3. Add your domain
4. Configure DNS records

### 7.2 Vercel Custom Domain

1. Go to Vercel project settings
2. Click "Domains"
3. Add your domain
4. Configure DNS records

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Binding Issues
```bash
# Ensure services use PORT environment variable
import os
port = int(os.environ.get("PORT", 8000))
```

#### 2. Database Connection Issues
```bash
# Check DATABASE_URL format
# Ensure SSL is enabled for Supabase
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

#### 3. CORS Issues
```bash
# Update CORS origins in FastAPI
ALLOWED_ORIGINS=["https://your-vercel-domain.vercel.app"]
```

#### 4. Environment Variables
```bash
# Check all required variables are set
# Use Railway CLI to verify
railway variables
```

### Debug Commands

```bash
# Check Railway logs
railway logs

# Check service status
railway status

# Redeploy service
railway up

# Check environment variables
railway variables
```

## 💰 Cost Optimization

### Railway Cost Optimization

1. **Use Pro plan** for better performance
2. **Monitor usage** in Railway dashboard
3. **Scale down** during low traffic periods
4. **Use sleep mode** for development environments

### Vercel Cost Optimization

1. **Use Pro plan** for custom domains
2. **Monitor bandwidth** usage
3. **Optimize images** and assets
4. **Use edge functions** for better performance

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: All services use HTTPS by default
3. **CORS**: Configure allowed origins properly
4. **Rate Limiting**: Implement API rate limiting
5. **Input Validation**: Validate all user inputs
6. **SQL Injection**: Use parameterized queries
7. **XSS Protection**: Sanitize user inputs

## 📈 Scaling Considerations

### Auto-scaling

- **Railway**: Automatically scales based on traffic
- **Vercel**: Automatically scales serverless functions
- **Supabase**: Handles database scaling automatically

### Performance Optimization

1. **Caching**: Use Redis for session and data caching
2. **CDN**: Vercel provides global CDN
3. **Database Indexing**: Optimize database queries
4. **Image Optimization**: Use Next.js image optimization

## 🎯 Next Steps

1. **Set up monitoring** with Sentry or similar
2. **Configure backups** for database
3. **Set up staging environment**
4. **Implement feature flags**
5. **Add analytics** tracking
6. **Set up alerts** for downtime

---

## 📞 Support

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)
- **Redis Cloud**: [redis.com/docs](https://redis.com/docs)

---

**Happy Deploying! 🚀✨**
