# IELTS AI Platform - Development Debugging Guide

## 🐛 Debugging Setup Overview

This guide covers the complete debugging environment for the IELTS AI Platform, including VS Code debugging, FastAPI debug mode, and Next.js DevTools.

## 📋 Table of Contents

1. [VS Code Debugger](#vs-code-debugger)
2. [FastAPI Debug Mode](#fastapi-debug-mode)
3. [Next.js DevTools](#nextjs-devtools)
4. [Debug Scripts](#debug-scripts)
5. [Debugging Workflows](#debugging-workflows)
6. [Troubleshooting](#troubleshooting)

## 🔧 VS Code Debugger

### Launch Configurations

The project includes comprehensive VS Code debugging configurations in `.vscode/launch.json`:

#### Individual Service Debugging
- **Debug API Service** - Debug the main API gateway
- **Debug Scoring Service** - Debug the AI scoring service
- **Debug Speech Service** - Debug speech-to-text service
- **Debug OCR Service** - Debug optical character recognition
- **Debug AI Tutor Service** - Debug the AI tutoring service
- **Debug Next.js Frontend** - Debug the React frontend

#### Compound Debugging
- **Debug Full Stack** - Debug API, Scoring, and Frontend simultaneously

### How to Use

1. **Set Breakpoints**: Click in the gutter next to line numbers
2. **Start Debugging**: Press `F5` or use the Debug panel
3. **Step Through Code**: Use F10 (step over), F11 (step into), F12 (step out)
4. **Inspect Variables**: Use the Variables panel in the Debug view

### Debug Console Commands

```javascript
// Frontend debugging
console.log('Debug info:', data);
console.table(arrayData);
console.group('Grouped logs');
console.time('Performance measurement');

// Python debugging
import pdb; pdb.set_trace()  // Set breakpoint
print(f"Debug: {variable}")  // Print debugging info
```

## 🚀 FastAPI Debug Mode

### Enhanced Debugging Features

The API services include enhanced debugging middleware:

#### Debug Middleware Features
- **Request/Response Logging**: Detailed HTTP request logging
- **Performance Monitoring**: Slow request detection (>1s)
- **Error Tracking**: Comprehensive error logging
- **Request Statistics**: Real-time request metrics

#### Debug Endpoints

When `DEBUG=true`, additional endpoints are available:

```bash
# Get debugging statistics
GET http://localhost:8000/debug/stats

# API documentation
GET http://localhost:8000/docs
GET http://localhost:8000/redoc
```

#### Debug Configuration

```python
# Environment variables for debugging
DEBUG=true
LOG_LEVEL=DEBUG
PYTHONPATH=/path/to/project

# Debug middleware automatically enabled when DEBUG=true
```

### Debug Logging

The debug middleware provides structured logging:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "debug",
  "message": "HTTP Request",
  "method": "POST",
  "path": "/api/v1/scoring",
  "client_ip": "127.0.0.1",
  "request_id": "12345"
}
```

## ⚛️ Next.js DevTools

### Development Features

The Next.js frontend includes enhanced debugging:

#### Source Maps
- **Development**: `eval-source-map` for fast debugging
- **Production**: Browser source maps enabled

#### React DevTools
- **Component Inspector**: Inspect React components
- **State Debugging**: Monitor component state
- **Performance Profiling**: Analyze component performance

#### Webpack Debugging
- **Hot Reload**: Automatic code reloading
- **Error Overlay**: In-browser error display
- **Bundle Analysis**: Webpack bundle inspection

### Debug Configuration

```javascript
// next.config.js debugging features
{
  reactStrictMode: true,
  productionBrowserSourceMaps: true,
  experimental: {
    instrumentationHook: true
  },
  webpack: (config, { dev }) => {
    if (dev) {
      config.devtool = 'eval-source-map'
    }
  }
}
```

## 🛠️ Debug Scripts

### Service Manager

The `debug_all_services.py` script provides comprehensive service management:

```bash
# Start all services in debug mode
python debug_all_services.py

# Individual service debugging
python services/api/main.py
python services/scoring/main.py
python services/speech/main.py
python services/ocr/main.py
python services/ai-tutor/main.py
```

### Debug Script Features

- **Service Orchestration**: Start/stop all services
- **Process Monitoring**: Automatic service restart on failure
- **Log Aggregation**: Centralized logging
- **Health Checks**: Service status monitoring

## 🔄 Debugging Workflows

### 1. Full Stack Debugging

```bash
# 1. Start all services
python debug_all_services.py

# 2. Start frontend
cd apps/web && npm run dev

# 3. Open VS Code debugger
# Select "Debug Full Stack" configuration
# Press F5 to start debugging
```

### 2. API Service Debugging

```bash
# 1. Set breakpoints in API code
# 2. Start API service in debug mode
cd services/api
python main.py

# 3. Make API requests
curl http://localhost:8000/health

# 4. Check debug stats
curl http://localhost:8000/debug/stats
```

### 3. Frontend Debugging

```bash
# 1. Start Next.js in development mode
cd apps/web
npm run dev

# 2. Open browser DevTools (F12)
# 3. Use React DevTools extension
# 4. Monitor network requests
# 5. Check console for errors
```

### 4. AI Service Debugging

```bash
# 1. Debug scoring service
cd services/scoring
python main.py

# 2. Test scoring endpoint
curl -X POST http://localhost:8004/score \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "task_type": "writing_task_2"}'

# 3. Monitor logs for AI model interactions
```

## 🔍 Debugging Techniques

### 1. Logging Best Practices

```python
# Python logging
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)

# Structured logging with structlog
import structlog
logger = structlog.get_logger()

logger.info("Request processed", 
           user_id=user_id, 
           processing_time=processing_time)
```

```javascript
// JavaScript logging
console.log('Debug info:', data);
console.warn('Warning:', warning);
console.error('Error:', error);

// React component debugging
useEffect(() => {
  console.log('Component mounted:', props);
}, [props]);
```

### 2. Performance Debugging

```python
# Python performance debugging
import time
import cProfile
import pstats

# Simple timing
start_time = time.time()
# ... your code ...
processing_time = time.time() - start_time
logger.info(f"Processing took {processing_time:.3f}s")

# Profiling
profiler = cProfile.Profile()
profiler.enable()
# ... your code ...
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

```javascript
// JavaScript performance debugging
console.time('operation');
// ... your code ...
console.timeEnd('operation');

// React performance
import { Profiler } from 'react';

<Profiler id="Component" onRender={(id, phase, actualDuration) => {
  console.log(`${id} took ${actualDuration}ms to render`);
}}>
  <YourComponent />
</Profiler>
```

### 3. Network Debugging

```bash
# API endpoint testing
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# WebSocket testing
wscat -c ws://localhost:8002/ws

# Health checks
curl http://localhost:8000/health
curl http://localhost:8004/health
curl http://localhost:8002/health
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Conflicts

```bash
# Check what's using a port
netstat -ano | findstr :8000
lsof -i :8000

# Kill process using port
taskkill /PID <process_id> /F
kill -9 <process_id>
```

#### 2. Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/project

# Install missing dependencies
pip install -r requirements.txt
npm install
```

#### 3. Database Connection Issues

```bash
# Check database status
python -c "from services.api.database import init_db; init_db()"

# Reset database (development only)
rm -f *.db
python -c "from services.api.database import init_db; init_db()"
```

#### 4. Frontend Build Issues

```bash
# Clear Next.js cache
rm -rf apps/web/.next
npm run dev

# Clear node_modules
rm -rf node_modules
npm install
```

### Debug Checklist

- [ ] All services are running on correct ports
- [ ] Environment variables are set correctly
- [ ] Database is accessible
- [ ] Frontend can connect to backend
- [ ] Logs show no errors
- [ ] Breakpoints are set correctly
- [ ] Debug mode is enabled

## 📊 Monitoring and Metrics

### Debug Statistics

Access debug statistics at `http://localhost:8000/debug/stats`:

```json
{
  "total_requests": 150,
  "error_count": 2,
  "slow_requests": [
    {
      "path": "/api/v1/scoring",
      "method": "POST",
      "processing_time": 1.234
    }
  ]
}
```

### Performance Monitoring

- **Request Latency**: Monitor API response times
- **Error Rates**: Track error frequencies
- **Resource Usage**: Monitor CPU and memory usage
- **Database Performance**: Track query execution times

## 🎯 Best Practices

1. **Use Breakpoints Strategically**: Set breakpoints at key decision points
2. **Log Meaningful Information**: Include context in log messages
3. **Monitor Performance**: Track slow operations
4. **Test Edge Cases**: Debug error conditions
5. **Use Debug Tools**: Leverage browser DevTools and VS Code debugging
6. **Document Issues**: Keep track of debugging sessions
7. **Clean Up**: Remove debug code before production

## 📚 Additional Resources

- [VS Code Debugging Documentation](https://code.visualstudio.com/docs/editor/debugging)
- [FastAPI Debugging Guide](https://fastapi.tiangolo.com/tutorial/debugging/)
- [Next.js Debugging](https://nextjs.org/docs/advanced-features/debugging)
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Python Debugging](https://docs.python.org/3/library/pdb.html)

---

**Happy Debugging! 🐛✨**
