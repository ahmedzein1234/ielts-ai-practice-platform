# Build Tasks (Ordered)

## Phase 1: Foundation (Week 1)
1. **Project Structure** ✅
   - Create all directories and config files
   - Setup .gitignore, .editorconfig, .prettierrc
   - Configure ESLint, TypeScript, Python tooling

2. **Core Packages**
   - `packages/types/` - DTOs (TypeScript + Pydantic)
   - `packages/ui/` - Shared UI primitives
   - `packages/prompts/` - AI scoring prompts
   - `packages/evals/` - Golden tests and fixtures

3. **Database Schema**
   - `db/migrations/` - PostgreSQL schema versions
   - Users, sessions, submissions, scores tables
   - Indexes for performance and analytics

4. **API Service Foundation**
   - `services/api/main.py` - FastAPI gateway
   - `services/api/routers/` - Auth, items, scoring, payments
   - `services/common/logging.py` - JSON logger

## Phase 2: Core Services (Week 2)
5. **Speech Service**
   - `services/speech/app.py` - WebSocket STT
   - Real-time transcription with faster-whisper
   - Prosody analysis (WPM, pauses, fillers)

6. **OCR Service**
   - `services/ocr/app.py` - Document analysis
   - PaddleOCR for printed text
   - TrOCR for handwritten text
   - Text cleaning and validation

7. **Scoring Service**
   - `services/scoring/app.py` - AI rubric judge
   - IELTS band descriptor alignment
   - Feedback generation with specific improvements

8. **Workers**
   - `workers/jobs/queue.py` - Redis/RQ wiring
   - `workers/jobs/tasks.py` - Async scoring, renders, reports

## Phase 3: Frontend (Week 3)
9. **Web Application**
   - `apps/web/` - Next.js 14 with TypeScript
   - Tailwind CSS + shadcn/ui components
   - Authentication and user management

10. **Speaking Module**
    - `apps/web/app/(app)/speaking/page.tsx`
    - WebRTC audio capture
    - Real-time transcription display
    - Band score and feedback UI

11. **Writing Module**
    - `apps/web/app/(app)/writing/page.tsx`
    - File upload with drag-and-drop
    - OCR preview and editing
    - Score breakdown and feedback

## Phase 4: Additional Modules (Week 4)
12. **Listening Module**
    - `apps/web/app/(app)/listening/page.tsx`
    - AI-generated audio with TTS
    - Question types (MCQ, completion, matching)
    - Auto-marking with explanations

13. **Reading Module**
    - `apps/web/app/(app)/reading/page.tsx`
    - Passage display with highlighting
    - Question types (TF/NG, headings, completion)
    - Timer and progress tracking

14. **Social Features**
    - `apps/web/app/(app)/clubs/page.tsx`
    - Practice rooms and leaderboards
    - Streak tracking and achievements

## Phase 5: Business Logic (Week 5)
15. **Payments Integration**
    - Stripe subscription management
    - Pro tier features and limits
    - Add-on purchases (human reviews)

16. **Analytics and Reporting**
    - Progress tracking and band improvement
    - Session analytics and retention metrics
    - Export functionality for users

17. **Admin Dashboard**
    - User management and moderation
    - Content management for passages/audio
    - System health monitoring

## Phase 6: Quality and Deployment (Week 6)
18. **Testing Suite**
    - Unit tests for all services (≥80% coverage)
    - Integration tests for API endpoints
    - E2E tests with Playwright
    - Golden tests for AI scoring accuracy

19. **CI/CD Pipeline**
    - GitHub Actions workflows
    - Security scanning and dependency audit
    - Performance testing with Lighthouse
    - Load testing with K6

20. **Infrastructure**
    - Docker compose for development
    - Terraform for production AWS resources
    - Monitoring and alerting setup
    - Backup and disaster recovery

21. **Documentation**
    - API documentation with OpenAPI
    - User guides and tutorials
    - Developer documentation
    - Runbooks for operations

## Phase 7: Production Readiness
22. **Security Hardening**
    - Security headers and CSP
    - Webhook signature verification
    - Rate limiting and abuse prevention
    - GDPR compliance implementation

23. **Performance Optimization**
    - Database query optimization
    - Caching strategies (Redis)
    - CDN setup for static assets
    - Auto-scaling configuration

24. **Monitoring and Observability**
    - Log aggregation and analysis
    - Metrics collection and dashboards
    - Error tracking and alerting
    - User analytics and feedback

## Success Criteria
- All modules functional and tested
- CI/CD pipeline green
- Security and performance gates passed
- Documentation complete
- Production deployment ready
