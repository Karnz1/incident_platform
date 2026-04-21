Developer pushes code
    ↓
GitHub Actions CI runs
    ↓
lint + unit tests + integration tests
    ↓
security/dependency scan
    ↓
build Docker image
    ↓
push image to registry
    ↓
deploy to staging
    ↓
run smoke test
    ↓
manual approval or tag-based release
    ↓
deploy to production
    ↓
post-deploy health check