export function normalizeEngineUrl(value: string): string {
  const url = new URL(value.trim());
  const loopback = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if (url.username || url.password || url.search || url.hash ||
      (url.protocol !== "https:" && !(url.protocol === "http:" && loopback))) {
    throw new Error("Use an HTTPS engine address or loopback HTTP, without credentials, query or fragment.");
  }
  return url.toString().replace(/\/+$/, "");
}

export function engineIsLocal(value: string): boolean {
  try { return ["localhost", "127.0.0.1", "[::1]"].includes(new URL(value).hostname); }
  catch { return false; }
}

export async function requestError(response: Response): Promise<string> {
  const data = await response.json().catch(() => ({}));
  if (response.status === 401 || response.status === 403) return "Authentication failed. Check the access key in Settings.";
  return typeof data.detail === "string" ? data.detail : `Request failed (${response.status}).`;
}

export function auditReviewState(analysisState: string | undefined, graph: { findings: unknown[]; reviews: unknown[] } | null): string {
  return analysisState === "NO_FINDINGS" && !graph?.findings.length && !graph?.reviews.length
    ? "No configured detector findings" : "Review required";
}
