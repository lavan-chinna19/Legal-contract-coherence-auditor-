export function ModelEvaluation() { return <section className="card research-evaluation">
            <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", color: "var(--color-text-primary)" }}>
              Model Evaluation (Research)
            </h2>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginBottom: "1.5rem" }}>
              Historical development results. These are not current-document metrics or independent evidence of legal correctness.
            </p>
            <div className="caveat-box"><strong>Exploratory evidence only.</strong> A development audit found compromised preregistration and invalid order transformations. Later review retained 9 directional candidates and 15 eligible negatives for development. Independent human annotation and unseen-family evaluation remain pending.</div>

            <div className="grid-kpis">
              <div className="kpi-card">
                <div className="kpi-label">Kendall&apos;s Tau (LEDGAR)</div>
                <div className="kpi-value">-0.0285</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>95% CI: [-0.125, +0.073]</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Clean SEC FPR (High)</div>
                <div className="kpi-value">1.18%</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>95% CI: [0.57%, 2.41%]</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Clean SEC FPR (Med+High)</div>
                <div className="kpi-value">44.54%</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>95% CI: [40.59%, 48.55%]</div>
              </div>
            </div>

            <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
                  <th style={{ padding: "0.5rem" }}>Model Architecture</th>
                  <th style={{ padding: "0.5rem" }}>Accuracy</th>
                  <th style={{ padding: "0.5rem" }}>F1 Score</th>
                  <th style={{ padding: "0.5rem" }}>Kendall&apos;s Tau</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>Dual-Channel Auditor (Our Model)</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>50.0%</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.00</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>-0.2100</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>Logistic Regression Baseline</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>55.0%</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.6087</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>+0.0816</td>
                </tr>
                <tr>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>Majority-Vote Baseline</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>50.0%</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.00</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.0000</td>
                </tr>
              </tbody>
            </table>
          </section>; }
