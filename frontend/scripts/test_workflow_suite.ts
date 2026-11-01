import test from "node:test";
import assert from "node:assert/strict";
import { auditReviewState, normalizeEngineUrl, engineIsLocal, requestError } from "../src/lib/workflow.ts";
for (const [input, output] of [["http://127.0.0.1:8010/", "http://127.0.0.1:8010"], [" http://localhost:8012 ", "http://localhost:8012"], ["http://[::1]:8000/", "http://[::1]:8000"], ["https://engine.example.test/api/", "https://engine.example.test/api"]]) {
  test(`accepted engine address: ${input.trim()}`, () => assert.equal(normalizeEngineUrl(input), output));
}
for (const value of ["javascript:alert(1)", "file:///etc/passwd", "http://engine.example.test", "https://name:password@localhost/", "http://localhost:8010?key=secret", "https://localhost/#fragment", "http://localhost.attacker.test:8010", "/api", "not a url"]) {
  test(`unsafe address rejected: ${value}`, () => assert.throws(() => normalizeEngineUrl(value)));
}
test("loopback status never labels a remote host local", () => {
  assert.equal(engineIsLocal("http://127.0.0.1:8010"), true);
  assert.equal(engineIsLocal("https://remote.example.test"), false);
  assert.equal(engineIsLocal("http://localhost.attacker.test"), false);
});
test("authentication failures have actionable setup guidance", async () => {
  assert.match(await requestError(new Response("{}", { status: 401 })), /Settings/);
  assert.match(await requestError(new Response("{}", { status: 403 })), /Authentication failed/);
});
test("malformed errors remain understandable without leaking response HTML", async () => {
  assert.equal(await requestError(new Response("<html>private internal traceback</html>", { status: 502 })), "Request failed (502).");
});
test("structured errors preserve actual supported file validation guidance", async () => {
  assert.equal(await requestError(new Response(JSON.stringify({ detail: "File exceeds the 10 MB limit." }), { status: 413 })), "File exceeds the 10 MB limit.");
});

test("A reference conflict requires review even when primary detectors have no findings", () => {
  assert.equal(auditReviewState("NO_FINDINGS", { findings: [{}], reviews: [] }), "Review required");
});
test("Unresolved references require review rather than a clean bill of health", () => {
  assert.equal(auditReviewState("NO_FINDINGS", { findings: [], reviews: [{}] }), "Review required");
});
test("No-finding and missing-state summaries retain honest scope", () => {
  assert.equal(auditReviewState("NO_FINDINGS", null), "No configured detector findings");
  assert.equal(auditReviewState("NO_FINDINGS", { findings: [], reviews: [] }), "No configured detector findings");
  assert.equal(auditReviewState(undefined, null), "Review required");
});
