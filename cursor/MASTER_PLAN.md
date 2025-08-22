# Master Autonomous Build Plan

## Build Objective
Deliver a production-ready IELTS AI practice platform with real-time speaking, OCR writing analysis, and authentic exam simulation.

## Autonomous Loop
1. **Plan** → Read current state, identify next task
2. **Edit** → Implement smallest working diff
3. **Run** → Execute tests and checks
4. **Verify** → Confirm all gates pass
5. **Summarise** → Log progress, commit, repeat

## Build Order (cursor/TASKS.md)
1. Project structure and config files
2. Core packages (types, UI, prompts)
3. Database schema and migrations
4. API service with auth and basic endpoints
5. Speech service with WebSocket STT
6. OCR service for writing analysis
7. Scoring service with AI rubric judge
8. Web frontend with Next.js + Tailwind
9. Workers for async tasks
10. CI/CD pipelines and security gates
11. Infrastructure and deployment configs
12. Documentation and runbooks

## Quality Gates (cursor/CHECKS.md)
- ✅ Type safety: `npm run typecheck` (0 exit)
- ✅ Lint/format: `npm run lint` (0 exit)
- ✅ Unit tests: `npm run test` (all pass, ≥80% coverage)
- ✅ Integration: `npm run e2e` (0 exit)
- ✅ Build: `npm run build` (0 exit)
- ✅ Security: Headers, webhook signatures, dependency audit
- ✅ Performance: Lighthouse ≥90, axe violations = 0
- ✅ Load: K6 smoke test (p95 < 250ms @ 50 rps)
- ✅ MCP: Health check and validation

## MCP Servers Required (cursor/mcp.json)
- filesystem, github, openrouter, postgres, redis, s3
- browser, playwright, lighthouse, axe
- stripe, ffmpeg, stt, ocr, scoring, deploy

## Rules (cursor/RULES.md)
- British English, concise, structured
- Test-first for complex work
- No secrets in code, use env files
- Prefer small, backwards-compatible diffs
- Evidence before assertion policy

## Non-Negotiables
- All IELTS modules must mirror exam format
- Real-time speaking feedback < 2s latency
- OCR accuracy ≥ 95% for handwritten text
- AI scoring aligned to IELTS band descriptors
- GDPR compliance with data retention policies
- Security headers and webhook signature verification

## Success Criteria
- All CI gates pass (lint, type, test, security, performance)
- Speaking module: real-time STT + prosody analysis
- Writing module: OCR + AI rubric scoring
- Listening module: AI-generated audio + auto-marking
- Reading module: passages + multiple question types
- Payment integration with Stripe
- Production deployment ready

## Risk Mitigation
- GPU pool exhaustion: Deepgram MCP fallback
- STT degradation: Model switching + latency thresholds
- Payment outage: Degraded checkout mode
- Data breach: Incident response runbook
- Performance: Load testing + auto-scaling

## Timeline
- Week 1: Core infrastructure and services
- Week 2: Speaking and Writing modules
- Week 3: Listening and Reading modules
- Week 4: Social features and payments
- Week 5: CI/CD and security hardening
- Week 6: Documentation and production readiness
