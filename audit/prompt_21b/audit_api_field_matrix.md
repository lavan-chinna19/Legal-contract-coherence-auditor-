# API Field Matrix

| Endpoint | Method | Request Fields | Response Fields | Validation | Status |
|---|---|---|---|---|---|
| `/v1/privacy-policy` | GET | None | `policy_text`, `version` | None | PASS |
| `/v1/upload` | POST | `file` | `doc_id`, `message` | Mime Type, Size | PASS |
| `/v1/analyze` | POST | `doc_id` | `job_id`, `message` | UUID regex | PASS |
| `/v1/jobs/{job_id}` | GET | `job_id` | `job_id`, `status`, `error` | UUID regex | PASS |
| `/v1/jobs/{job_id}/results` | GET | `job_id` | `job_status`, `clauses` | UUID regex | FAIL (Missing Rules - BUG-006) |
| `/v1/feedback` | POST | `clause_id`, `verdict` | `feedback_id` | Schema | FAIL (Verdict Mismatch - BUG-003) |
| `/v1/maintenance/cleanup` | POST | None | `status`, `result` | Admin Key | PASS |
| `/v1/xai/attribution` | POST | `clause_id` | `tokens`, `scores` | Missing Endpoint | FAIL (BUG-005) |
| `/v1/xai/sensitivity` | POST | `clause_id` | `deltas` | Missing Endpoint | FAIL (BUG-005) |
