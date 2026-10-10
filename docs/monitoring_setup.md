# Production Monitoring & Alerting Strategy (Prompt 20)

This document specifies the uptime monitoring, telemetry, and alerting architecture for the Legal Contract Coherence Auditor.

---

## 1. Monitoring Layers

1. **Liveness Probe (`/health`):**
   - Lightweight unauthenticated endpoint returning HTTP 200 `{"status": "ok"}`.
   - Polled every 30 seconds by PaaS platform orchestrators (Render, Railway) and external uptime monitors.
2. **Readiness Probe (`/ready`):**
   - Validates that NLP and ML dependencies (spaCy tokenizer, BERT weights, discourse transition matrix) are initialized in memory.
3. **Audit Log Stream:**
   - Structured JSON logs tagged with `[AUDIT]` capturing request counts, response codes, client identity hashes, and latency without leaking contract text or secrets.

---

## 2. External Alerting Integration (UptimeRobot / BetterStack)

For zero-cost live monitoring with automated incident alerts:

1. Create a free HTTP monitor in [UptimeRobot](https://uptimerobot.com) or [BetterStack](https://betterstack.com).
2. Configure **Monitor Target**: `https://<YOUR_DEPLOYED_URL>/health`.
3. Set **Monitoring Interval**: 1 minute.
4. Set **Notification Channels**: Email, Discord Webhook, or PagerDuty.
5. Set **Degradation Threshold**: Alert if down for > 2 consecutive checks (2 minutes).

---

## 3. Simulated Failure Alert Verification

The monitoring script `scripts/monitor_health.py` validates failure alerting:
- On simulated server stop or unroutable port (e.g. `http://127.0.0.1:9999`), it catches the connection error and triggers the `[ALERT]` notification block, exiting with code 1.
