# Repeat-Until-Green Loop

## Loop Process
1. **Read State** → Analyse current project state
2. **Identify Task** → Find next uncompleted task from TASKS.md
3. **Plan Change** → Design smallest working diff
4. **Implement** → Write code with tests
5. **Run Checks** → Execute all quality gates
6. **Verify** → Confirm all checks pass
7. **Commit** → Log progress and continue

## Loop Rules
- **Maximum 3 fix cycles** per task before stopping
- **Evidence before assertion** - never claim "working" without proof
- **Smallest diffs** - prefer incremental changes
- **Test-first** for complex logic
- **No breaking changes** without migration plan

## Check Execution Order
1. **Type Safety**: `npm run typecheck`
2. **Linting**: `npm run lint`
3. **Formatting**: `npm run format`
4. **Unit Tests**: `npm run test`
5. **Build**: `npm run build`
6. **Integration**: `npm run test:integration`
7. **E2E**: `npm run test:e2e`
8. **Security**: Headers, audit, container scan
9. **Performance**: Lighthouse, axe, load test
10. **MCP**: Health and validation

## Failure Handling
- **Type Errors**: Fix type definitions, add proper interfaces
- **Lint Errors**: Apply auto-fix, manual corrections
- **Test Failures**: Fix implementation, update tests
- **Build Errors**: Resolve dependencies, fix imports
- **Security Issues**: Update dependencies, fix vulnerabilities
- **Performance Issues**: Optimise code, reduce bundle size

## Success Criteria
- All checks return exit code 0
- No critical security vulnerabilities
- Performance targets met
- Documentation updated
- Tests passing with ≥80% coverage

## Loop Termination
- **Success**: All tasks complete, all checks pass
- **Blocked**: 3 fix cycles exhausted, manual intervention needed
- **Error**: Critical failure requiring investigation

## Progress Tracking
- Update TASKS.md with completion status
- Log evidence (commands, exit codes, paths)
- Commit with descriptive messages
- Update PROGRESS.md with build ledger
