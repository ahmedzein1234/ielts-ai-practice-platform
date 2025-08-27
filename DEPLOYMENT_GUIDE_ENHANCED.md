# Enhanced AI Tutor - Deployment Guide

## 🚀 **Quick Start Deployment**

### **Prerequisites**
- Node.js 18+ and Python 3.9+
- Docker and Docker Compose (for production)
- Supabase project with database setup
- OpenAI API key configured

### **1. Backend Deployment**

#### **Install Dependencies**
```bash
cd services/ai-tutor
pip install -r requirements.txt
```

#### **Environment Configuration**
```bash
# Copy and configure environment variables
cp .env.example .env

# Required environment variables
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
DATABASE_URL=your_database_url
```

#### **Database Setup**
```bash
# Run database migrations
alembic upgrade head

# Initialize speech processing tables
python -c "from services.speech_processor import SpeechProcessor; SpeechProcessor().initialize_tables()"
```

#### **Start Enhanced AI Tutor Service**
```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### **2. Frontend Deployment**

#### **Install Dependencies**
```bash
cd apps/web
npm install
```

#### **Environment Configuration**
```bash
# Copy and configure environment variables
cp .env.example .env.local

# Required environment variables
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_AI_TUTOR_WS_URL=ws://localhost:8001/ws
NEXT_PUBLIC_AI_TUTOR_API_URL=http://localhost:8001
```

#### **Build and Start**
```bash
# Development
npm run dev

# Production build
npm run build
npm start
```

### **3. Docker Deployment (Recommended)**

#### **Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  ai-tutor:
    build: ./services/ai-tutor
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./services/ai-tutor:/app
    restart: unless-stopped

  web:
    build: ./apps/web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_AI_TUTOR_WS_URL=ws://ai-tutor:8001/ws
      - NEXT_PUBLIC_AI_TUTOR_API_URL=http://ai-tutor:8001
    depends_on:
      - ai-tutor
    restart: unless-stopped
```

#### **Deploy with Docker**
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## 🔧 **Configuration Options**

### **AI Tutor Service Configuration**

#### **Speech Processing Settings**
```python
# services/ai-tutor/config/speech_config.py
SPEECH_CONFIG = {
    "sample_rate": 16000,
    "chunk_size": 1024,
    "supported_formats": ["wav", "mp3", "ogg", "flac"],
    "analysis_interval": 0.5,  # seconds
    "min_audio_duration": 1.0,  # seconds
    "max_audio_duration": 60.0,  # seconds
}
```

#### **WebSocket Configuration**
```python
# services/ai-tutor/config/websocket_config.py
WEBSOCKET_CONFIG = {
    "max_connections": 1000,
    "heartbeat_interval": 30,  # seconds
    "connection_timeout": 300,  # seconds
    "max_message_size": 1024 * 1024,  # 1MB
    "enable_compression": True,
}
```

### **Frontend Configuration**

#### **Audio Recording Settings**
```typescript
// apps/web/config/audio-config.ts
export const AUDIO_CONFIG = {
  sampleRate: 16000,
  channels: 1,
  bitDepth: 16,
  format: 'wav',
  maxDuration: 60, // seconds
  minDuration: 1,  // seconds
  chunkSize: 1024,
}
```

#### **WebSocket Connection Settings**
```typescript
// apps/web/config/websocket-config.ts
export const WEBSOCKET_CONFIG = {
  reconnectAttempts: 5,
  reconnectInterval: 1000, // ms
  heartbeatInterval: 30000, // ms
  connectionTimeout: 10000, // ms
}
```

## 🧪 **Testing Deployment**

### **Health Checks**

#### **Backend Health Check**
```bash
# Test AI Tutor service
curl http://localhost:8001/health

# Test WebSocket connection
wscat -c ws://localhost:8001/ws
```

#### **Frontend Health Check**
```bash
# Test web application
curl http://localhost:3000

# Test API endpoints
curl http://localhost:3000/api/health
```

### **Feature Testing**

#### **1. Basic AI Tutor**
- Navigate to `/ai-tutor`
- Send a text message
- Verify AI response

#### **2. Enhanced AI Tutor**
- Navigate to `/ai-tutor/enhanced`
- Test text chat functionality
- Test voice recording (requires microphone)
- Verify speech analysis dashboard
- Test personality settings

#### **3. WebSocket Communication**
- Open browser developer tools
- Monitor WebSocket connection
- Test real-time features
- Verify connection recovery

### **Performance Testing**

#### **Load Testing**
```bash
# Install artillery for load testing
npm install -g artillery

# Test WebSocket connections
artillery run websocket-load-test.yml

# Test API endpoints
artillery run api-load-test.yml
```

#### **Audio Processing Test**
```bash
# Test speech processing service
python -m pytest services/ai-tutor/tests/test_speech_processor.py -v

# Test with sample audio files
python services/ai-tutor/test_audio_processing.py
```

## 🔍 **Monitoring & Logging**

### **Application Logs**

#### **Backend Logging**
```python
# services/ai-tutor/config/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai-tutor.log'),
        logging.StreamHandler()
    ]
)
```

#### **Frontend Logging**
```typescript
// apps/web/utils/logger.ts
export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data)
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error)
  },
  debug: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, data)
    }
  }
}
```

### **Performance Monitoring**

#### **Key Metrics to Monitor**
- WebSocket connection count
- Audio processing latency
- API response times
- Memory usage
- CPU utilization
- Error rates

#### **Monitoring Setup**
```bash
# Install monitoring tools
pip install prometheus-client
npm install @sentry/nextjs

# Configure Prometheus metrics
python services/ai-tutor/monitoring/metrics.py

# Configure Sentry error tracking
# Add to next.config.js
const { withSentryConfig } = require('@sentry/nextjs')
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. WebSocket Connection Failed**
```bash
# Check if service is running
curl http://localhost:8001/health

# Check firewall settings
sudo ufw status

# Check port availability
netstat -tulpn | grep 8001
```

#### **2. Audio Recording Not Working**
```bash
# Check browser permissions
# Ensure HTTPS in production
# Check microphone access

# Test audio devices
navigator.mediaDevices.enumerateDevices()
  .then(devices => console.log(devices))
```

#### **3. Speech Processing Errors**
```bash
# Check Python dependencies
pip list | grep -E "(numpy|scipy|librosa)"

# Check audio file permissions
ls -la /tmp/audio_files/

# Check memory usage
free -h
```

### **Debug Mode**

#### **Enable Debug Logging**
```bash
# Backend debug mode
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug

# Frontend debug mode
export NEXT_PUBLIC_DEBUG=true
npm run dev
```

#### **WebSocket Debug**
```typescript
// Enable WebSocket debugging
const ws = new WebSocket('ws://localhost:8001/ws')
ws.onopen = () => console.log('WebSocket connected')
ws.onmessage = (event) => console.log('Message received:', event.data)
ws.onerror = (error) => console.error('WebSocket error:', error)
ws.onclose = () => console.log('WebSocket disconnected')
```

## 📚 **Additional Resources**

### **Documentation**
- [Enhanced AI Tutor API Documentation](http://localhost:8001/docs)
- [Frontend Component Library](http://localhost:3000/storybook)
- [WebSocket Protocol Specification](./WEBSOCKET_PROTOCOL.md)

### **Support**
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-community)
- [Email Support](mailto:support@your-domain.com)

### **Updates**
- [Changelog](./CHANGELOG.md)
- [Migration Guide](./MIGRATION_GUIDE.md)
- [Roadmap](./ROADMAP.md)
