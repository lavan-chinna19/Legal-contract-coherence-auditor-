# API Field Matrix

| Endpoint | Method | Request Fields | Response Fields | Validation | Status |
|---|---|---|---|---|---|
| `/v1/upload` | POST | `file` | `doc_id` | Mime Type, Size | PASS |
| `/v1/jobs` | POST | `doc_id` | `job_id` | UUID regex | PASS |
| `/v1/jobs/{id}/results` | GET | `id` | `job_status`, `clauses` | UUID regex | FAIL (Missing Rules - BUG-006) |
| `/v1/feedback` | POST | `clause_id`, `verdict` | `feedback_id` | Schema | FAIL (Verdict Mismatch - BUG-003) |
| `/v1/xai/attribution` | POST | `clause_id` | `tokens`, `scores` | Missing Endpoint | FAIL (BUG-005) |
