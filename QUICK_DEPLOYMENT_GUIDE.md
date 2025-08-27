# 🚀 Quick Deployment Guide - Enhanced AI Tutor

## Prerequisites

- Docker Desktop installed and running
- Node.js 18+ and npm
- API keys for OpenAI, Anthropic, and OpenRouter

## 🎯 Quick Start (Windows)

### 1. Setup Environment
```powershell
# Copy environment template
Copy-Item env.example .env

# Edit .env file and add your API keys:
# OPENAI_API_KEY=your-actual-openai-key
# ANTHROPIC_API_KEY=your-actual-anthropic-key  
# OPENROUTER_API_KEY=your-actual-openrouter-key
```

### 2. Deploy Enhanced Features
```powershell
# Option 1: Using npm script
npm run dev:enhanced

# Option 2: Direct PowerShell execution
powershell -ExecutionPolicy Bypass -File deploy-enhanced.ps1
```

## 🎯 Quick Start (Linux/Mac)

### 1. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your API keys
nano .env
```

### 2. Deploy Enhanced Features
```bash
# Make script executable
chmod +x deploy-enhanced.sh

# Run deployment
./deploy-enhanced.sh
```

## 🔧 Manual Deployment

If you prefer manual deployment:

### 1. Build Services
```bash
docker-compose build ai-tutor web
```

### 2. Start Core Services
```bash
docker-compose up -d postgres redis api scoring ai-tutor
```

### 3. Start Frontend
```bash
docker-compose up -d web
```

### 4. Verify Deployment
```bash
# Check service health
curl http://localhost:8001/health  # AI Tutor
curl http://localhost:8000/health  # API
curl http://localhost:3000         # Web Frontend
```

## 🌐 Access Enhanced Features

Once deployed, access the enhanced features at:

- **Enhanced AI Tutor**: http://localhost:3000/ai-tutor/enhanced
- **API Documentation**: http://localhost:8001/docs
- **WebSocket Endpoint**: ws://localhost:8001/ws

## 🔍 Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker Desktop
   # Then retry deployment
   ```

2. **Port conflicts**
   ```bash
   # Check what's using the ports
   netstat -ano | findstr :8001
   netstat -ano | findstr :3000
   
   # Stop conflicting services
   ```

3. **API key errors**
   ```bash
   # Verify .env file has correct API keys
   # Check logs for specific errors
   docker-compose logs ai-tutor
   ```

4. **Build failures**
   ```bash
   # Clean and rebuild
   docker-compose down
   docker system prune -f
   docker-compose build --no-cache ai-tutor web
   ```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-tutor
docker-compose logs -f web
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart ai-tutor
```

## 📊 Service Status

Check service status:
```bash
docker-compose ps
```

Expected output:
```
Name                Command               State           Ports
--------------------------------------------------------------------------------
ielts-cursor-ai-tutor-1     python main.py                Up      0.0.0.0:8001->8001/tcp
ielts-cursor-api-1          uvicorn main:app --host ...   Up      0.0.0.0:8000->8000/tcp
ielts-cursor-postgres-1     docker-entrypoint.sh postgres Up      0.0.0.0:5432->5432/tcp
ielts-cursor-redis-1        docker-entrypoint.sh redis... Up      0.0.0.0:6379->6379/tcp
ielts-cursor-scoring-1      python main.py                Up      0.0.0.0:8001->8001/tcp
ielts-cursor-web-1          node server.js                Up      0.0.0.0:3000->3000/tcp
```

## 🎉 Success Indicators

✅ **Deployment Successful When:**
- All containers show "Up" status
- Health checks pass (200 OK responses)
- Enhanced AI Tutor loads at http://localhost:3000/ai-tutor/enhanced
- WebSocket connection established
- Voice recording works (microphone permission granted)

## 📚 Next Steps

1. **Test Enhanced Features**:
   - Try text chat with AI tutor
   - Test voice recording and speech analysis
   - Explore personality settings
   - Check real-time feedback

2. **Customize Configuration**:
   - Modify teaching styles in the interface
   - Adjust speech processing parameters
   - Configure WebSocket settings

3. **Production Deployment**:
   - Review `DEPLOYMENT_GUIDE_ENHANCED.md` for production setup
   - Configure SSL certificates
   - Set up monitoring and logging
   - Implement backup strategies

## 🆘 Support

- **Documentation**: `DEPLOYMENT_GUIDE_ENHANCED.md`
- **Integration Summary**: `FRONTEND_INTEGRATION_SUMMARY.md`
- **Debug Guide**: `DEBUG_GUIDE.md`

For issues, check the logs first:
```bash
docker-compose logs -f [service-name]
```
