"use client";
import { useState } from "react";
import { ThemeToggle } from "../layout/ThemeToggle";
import { normalizeEngineUrl, requestError } from "../../lib/workflow";
export function EngineSettings({ backendUrl, connected, onConnect, onDisconnect }: {
  backendUrl: string; connected: boolean; onConnect: (url: string, key: string) => void; onDisconnect: () => void;
}) {
  const [url, setUrl] = useState(backendUrl), [key, setKey] = useState("");
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  async function connect(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError("");
    try {
      const safeUrl = normalizeEngineUrl(url);
      const response = await fetch(`${safeUrl}/v1/session`, { headers: { "X-API-Key": key.trim() }, signal: AbortSignal.timeout(15000), cache: "no-store", redirect: "error" });
      if (!response.ok) throw new Error(await requestError(response));
      onConnect(safeUrl, key.trim()); setKey("");
    } catch (e) { setError(e instanceof Error ? e.message : "Could not connect to the engine."); }
    finally { setBusy(false); }
  }
  return <div className="settings-grid"><section className="card"><h2>Local engine</h2><p>Connect once for this page session. Access keys stay in memory and are cleared on sign out or reload.</p>
    <form onSubmit={connect} className="stack-form"><div><label htmlFor="api-key-input">Access key</label><input id="api-key-input" className="input-field" type="password" autoComplete="off" required value={key} onChange={e => setKey(e.target.value)} disabled={busy} placeholder={connected ? "Enter a key to switch identity" : "Enter your local access key"} /></div>
      <details><summary>Connection address</summary><label htmlFor="backend-url-input">Engine URL</label><input id="backend-url-input" className="input-field" type="url" required value={url} onChange={e => setUrl(e.target.value)} disabled={busy} /><p>Use the trusted engine configured for this application. Changing identity or engine clears the active document.</p></details>
      <div className="action-row"><button id="connect-engine-btn" className="btn" disabled={busy || !key.trim()}>{busy ? "Connectingâ€¦" : connected ? "Update connection" : "Connect engine"}</button>{connected && <button className="btn btn-secondary" type="button" onClick={onDisconnect} disabled={busy}>Sign out and clear session</button>}</div>
    </form>{connected && <p role="status">Authenticated. Local inference remains on the configured engine.</p>}{error && <p className="inline-error" role="alert">{error}</p>}
    <details><summary>Private and demonstration setup</summary><p>Private use requires your own API and stable encryption keys in the engine’s local configuration. The separate synthetic demo launcher uses public test credentials; it is not a private-use profile. This interface never chooses demo credentials automatically.</p><p>Secure persistent sign-in is not implemented. Reload requires key entry again; no key is written to browser storage or a public bundle.</p></details>
    </section><section className="card"><h2>Privacy and appearance</h2><p>Document content, filenames and saved analyses are encrypted on the engine. Retention cleanup defaults to 24 hours. No contract text or access key belongs in logs.</p><p>Reports contain sensitive excerpts. Keep exports secure. Theme preference is the only application value saved in browser storage.</p><h3>Appearance</h3><ThemeToggle /></section></div>;
}
