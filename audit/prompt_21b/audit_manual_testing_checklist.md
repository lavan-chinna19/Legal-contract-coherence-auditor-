# Manual Testing Checklist

**Note**: Items marked as "NOT TESTED" have only been verified via automated or static checks, and lack real browser testing evidence.

### Automated / Static Checks
- [x] Verify API health endpoint (Automated test)
- [x] Test invalid authentication rejection (Automated test)
- [x] Check frontend build compilation (Static check `npm run build`)

### Manual Browser Verification
- [ ] Validate PDF file upload via browser UI (NOT TESTED)
- [ ] Trigger analysis job and wait for completion in UI (NOT TESTED)
- [ ] Verify Docker Compose boots correctly and serves UI (NOT TESTED)
- [ ] Submit reviewer feedback in UI (NOT TESTED - BUG-003 prevents success)
- [ ] Request XAI attribution in UI (NOT TESTED - BUG-005 prevents success)
