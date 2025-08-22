# IELTS AI Practice Platform

A comprehensive AI-powered IELTS preparation platform with real-time speech recognition, OCR-powered writing analysis, and personalized feedback.

## 🚀 Features

### Core Modules
- **Speaking Practice**: Real-time speech recognition with WebSocket STT
- **Writing Practice**: OCR-powered handwriting recognition and AI feedback
- **Listening Practice**: Audio playback with multiple accents (coming soon)
- **Reading Practice**: Authentic passages with various question types (coming soon)

### AI-Powered Features
- **Real-time Transcription**: Live speech-to-text using faster-whisper
- **OCR Text Extraction**: Handwriting recognition with PaddleOCR/TrOCR
- **AI Scoring**: IELTS band scoring with detailed feedback
- **Personalized Learning**: Adaptive practice based on performance

### Technical Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy, Alembic
- **AI/ML**: faster-whisper (STT), PaddleOCR/TrOCR (OCR), OpenRouter LLMs
- **Database**: PostgreSQL (production), SQLite (development)
- **Real-time**: WebSocket for live transcription
- **Background Tasks**: Celery with Redis
- **Authentication**: JWT with refresh tokens

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ielts-ai-platform.git
   cd ielts-ai-platform
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python -m alembic upgrade head
   ```

5. **Start the development servers**
   ```bash
   # Start API Gateway
   python -m uvicorn services.api.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Start Speech Service
   python -m uvicorn services.speech.main:app --host 0.0.0.0 --port 8002
   
   # Start OCR Service
   python -m uvicorn services.ocr.main:app --host 0.0.0.0 --port 8003
   
   # Start Scoring Service
   python -m uvicorn services.scoring.main:app --host 0.0.0.0 --port 8005
   
   # Start Frontend
   npm run dev
   ```

## 🏗️ Project Structure

```
ielts-ai-platform/
├── apps/web/                 # Next.js frontend application
├── packages/                 # Shared packages
│   ├── types/               # TypeScript type definitions
│   └── ui/                  # Shared UI components
├── services/                # Backend microservices
│   ├── api/                 # API Gateway (FastAPI)
│   ├── speech/              # Speech-to-Text service
│   ├── ocr/                 # OCR service
│   ├── scoring/             # AI scoring service
│   ├── workers/             # Background task processing
│   └── common/              # Shared utilities
├── db/                      # Database migrations
├── scripts/                 # CI/CD and utility scripts
└── cursor/                  # Cursor IDE configuration
```

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev                  # Start frontend development server
npm run build               # Build for production
npm run start               # Start production server

# Code Quality
npm run lint                # Run ESLint
npm run format              # Run Prettier
npm run type-check          # Run TypeScript type checking

# Testing
npm run test                # Run tests
npm run test:watch          # Run tests in watch mode

# MCP Validation
npm run mcp:validate        # Validate MCP server configuration
npm run mcp:health          # Check service health

# Security
npm run security:audit      # Run security audit
npm run security:headers    # Check security headers
```

### API Endpoints

- **API Gateway**: http://localhost:8000
- **Speech Service**: http://localhost:8002
- **OCR Service**: http://localhost:8003
- **Scoring Service**: http://localhost:8005
- **Frontend**: http://localhost:3000

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export DATABASE_URL="postgresql://..."
   export REDIS_URL="redis://..."
   export OPENROUTER_API_KEY="your-api-key"
   ```

2. **Database Migration**
   ```bash
   python -m alembic upgrade head
   ```

3. **Build and Deploy**
   ```bash
   npm run build
   # Deploy to your preferred platform (Vercel, AWS, etc.)
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) for speech recognition
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for OCR capabilities
- [shadcn/ui](https://ui.shadcn.com/) for UI components
- [Next.js](https://nextjs.org/) for the React framework
- [FastAPI](https://fastapi.tiangolo.com/) for the Python web framework

## 📞 Support

For support, email support@ielts-ai.com or create an issue in this repository.

---

**Built with ❤️ for IELTS students worldwide**
