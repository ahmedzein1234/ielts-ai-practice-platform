# Build Checks (All Required)

## Code Quality
- ✅ **Type Safety**: `npm run typecheck` (0 exit)
- ✅ **Linting**: `npm run lint` (0 exit)
- ✅ **Formatting**: `npm run format` (0 exit)
- ✅ **Python**: `ruff check`, `black --check`, `mypy --strict` (0 exit)

## Testing
- ✅ **Unit Tests**: `npm run test` (all pass, ≥80% coverage)
- ✅ **Integration**: `npm run test:integration` (0 exit)
- ✅ **E2E**: `npm run test:e2e` (0 exit)
- ✅ **Golden Tests**: AI scoring accuracy regression tests

## Build & Deploy
- ✅ **Build**: `npm run build` (0 exit)
- ✅ **Package**: `npm run package` (0 exit)
- ✅ **Docker**: `docker build` (0 exit)
- ✅ **Terraform**: `terraform plan` (0 exit)

## Security
- ✅ **Headers Scan**: CSP, HSTS, XFO, Referrer-Policy, COOP/COEP
- ✅ **Webhook Signatures**: Stripe verification tests
- ✅ **Dependency Audit**: `npm audit`, `safety check` (no criticals)
- ✅ **Container Scan**: Trivy (no criticals)
- ✅ **SBOM**: Generated and stored per build
- ✅ **Secrets**: No secrets in repo, `.env.example` present

## Performance
- ✅ **Lighthouse**: Performance/PWA/A11y ≥ 90
- ✅ **Accessibility**: axe violations = 0
- ✅ **Load Smoke**: API p95 < 250ms @ 50 rps
- ✅ **WebSocket**: Connect success ≥ 99%
- ✅ **Bundle Size**: < 500KB gzipped

## Platform Health
- ✅ **MCP Validate**: Required servers present
- ✅ **MCP Health**: All endpoints responding
- ✅ **Database**: Migrations apply cleanly
- ✅ **Redis**: Connection and pub/sub working
- ✅ **S3**: Upload/download permissions

## Documentation
- ✅ **API Docs**: OpenAPI spec generated
- ✅ **README**: Up-to-date with current state
- ✅ **Architecture**: Diagrams and flows current
- ✅ **Runbooks**: Incident response procedures
- ✅ **Compliance**: GDPR, security policies

## Business Logic
- ✅ **IELTS Alignment**: All modules match exam format
- ✅ **Scoring Accuracy**: AI rubric within ±0.5 bands
- ✅ **OCR Quality**: ≥95% accuracy for handwritten text
- ✅ **STT Latency**: <2s for real-time feedback
- ✅ **Payment Flow**: Stripe integration working

## Observability
- ✅ **Logging**: JSON format, no PII, request_id present
- ✅ **Tracing**: OpenTelemetry initialised
- ✅ **Metrics**: RED (Rate, Errors, Duration) collected
- ✅ **Alerts**: Error budget monitoring configured

## Compliance
- ✅ **GDPR**: Data retention policies implemented
- ✅ **Privacy**: Consent management working
- ✅ **Terms**: Legal documents up-to-date
- ✅ **Cookies**: Consent banner functional

## Backup & Recovery
- ✅ **Database**: Backup restore dry-run weekly
- ✅ **S3**: Versioning and lifecycle policies
- ✅ **Secrets**: Rotation every 90 days
- ✅ **Disaster Recovery**: RTO/RPO documented

## Status Labels
- **DONE (validated)** — All checks pass
- **DONE (partially validated)** — List missing checks
- **IN PROGRESS** — Blocked by specific issue
- **BLOCKED** — Requires manual intervention

## Evidence Required
- Exact commands run
- Exit codes (must be 0)
- Artefact paths (build/, coverage/, logs/)
- Performance metrics (latency, throughput)
- Security scan results
- Test coverage reports
