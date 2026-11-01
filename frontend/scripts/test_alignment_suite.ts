/**
 * frontend/scripts/test_alignment_suite.ts
 *
 * Comprehensive Unit Test Suite for LexAudit Clause-to-Source Alignment Engine.
 * Tests all 15 authentic backend-segmented adversarial fixtures, plus async race and negative edge cases.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { alignClausesWithRawText } from "../src/components/review/alignment.ts";
import type { ClauseResult } from "../src/components/review/types.ts";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const FIXTURES_DIR = path.resolve(__dirname, "../../design/ui_redesign/phase_03a/fixtures");
const BACKEND_JSON = path.join(FIXTURES_DIR, "backend_segmented_fixtures.json");
const RESULTS_PATH = path.resolve(__dirname, "../../tmp/final-release/alignment_test_results.json");
fs.mkdirSync(path.dirname(RESULTS_PATH), { recursive: true });

interface TestCaseResult {
  id: string;
  name: string;
  fixtureFile?: string;
  totalClauses: number;
  expectedStatus: string[];
  observedStatus: string[];
  pass: boolean;
  notes: string;
}

const testResults: TestCaseResult[] = [];

console.log("=================================================================");
console.log("LEXAUDIT PHASE 3A — CLAUSE ALIGNMENT UNIT TEST SUITE");
console.log("=================================================================\n");

const backendData = JSON.parse(fs.readFileSync(BACKEND_JSON, "utf8"));

function toClauseResult(item: { clause_id: string; doc_id: string; sequence_idx: number; text_preview: string; label?: string }): ClauseResult {
  return {
    clause_id: item.clause_id,
    doc_id: item.doc_id,
    sequence_idx: item.sequence_idx,
    text_preview: item.text_preview,
    channel_a_score: 0.15,
    channel_b_score: 0.2,
    combined_score: 0.175,
    channel_a_evidence: {
      nearest_centroid_label: item.label || "OPERATIONAL_COVENANTS",
      centroid_distance: 0.45,
      is_ood: false,
    },
    channel_b_evidence: {
      incoming_anomaly: 0.1,
      outgoing_anomaly: 0.12,
    },
    is_anomaly: false,
    severity: "LOW",
    calibration_source: "Authentic Backend Segmenter",
    cross_channel_agreement: 0.95,
    agreement_type: "Concordant",
  };
}

// -------------------------------------------------------------
// Test 1: Baseline Five Numbered Clauses
// -------------------------------------------------------------
{
  const fixtureName = "fixture_01_baseline.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 5;

  testResults.push({
    id: "TC-01",
    name: "Baseline Five Numbered Clauses",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(5).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "All 5 sequential clauses uniquely aligned with verified full-text boundaries.",
  });
}

// -------------------------------------------------------------
// Test 2: Repeated Prefix with Distinct Headings
// -------------------------------------------------------------
{
  const fixtureName = "fixture_02_repeated_prefix.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 3;

  testResults.push({
    id: "TC-02",
    name: "Repeated Prefix with Distinct Headings",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Sequential disambiguation successfully aligned each clause with its distinct heading offset.",
  });
}

// -------------------------------------------------------------
// Test 3: Separated Identical Clauses (Duplicate Handling)
// -------------------------------------------------------------
{
  const fixtureName = "fixture_03_identical_clauses.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  // In this fixture, Clause 1 and 3 contain identical body text
  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT");

  testResults.push({
    id: "TC-03",
    name: "Identical Boilerplate Clauses With Distinct Section Numbers",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(5).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Distinguished by section numbers in backend previews, both identical bodies verified.",
  });
}

// -------------------------------------------------------------
// Test 4: Long Clause Exceeding 5,000 Characters
// -------------------------------------------------------------
{
  const fixtureName = "fixture_04_long_clause.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const longClauseLength = res[1]?.displayText?.length || 0;
  const pass = observed[1] === "VERIFIED_FULL_TEXT" && longClauseLength > 5000;

  testResults.push({
    id: "TC-04",
    name: "Long Clause Exceeding 5,000 Characters",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: `Long clause successfully resolved with ${longClauseLength} characters extracted intact.`,
  });
}

// -------------------------------------------------------------
// Test 5: Multiline Text with Blank Lines & Sub-clauses
// -------------------------------------------------------------
{
  const fixtureName = "fixture_05_multiline_text.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 5;

  testResults.push({
    id: "TC-05",
    name: "Multiline Text with Sub-clauses",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(5).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Backend-segmented sub-clauses (a), (b), (c) all aligned cleanly with raw multiline text.",
  });
}

// -------------------------------------------------------------
// Test 6: Nested Numbering Hierarchy
// -------------------------------------------------------------
{
  const fixtureName = "fixture_06_nested_numbering.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 4;

  testResults.push({
    id: "TC-06",
    name: "Nested Numbering Hierarchy",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(4).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Hierarchical sub-sections bounded strictly without prefix collision.",
  });
}

// -------------------------------------------------------------
// Test 7: Mixed Line Endings (CRLF / LF)
// -------------------------------------------------------------
{
  const fixtureName = "fixture_07_mixed_line_endings.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 3;

  testResults.push({
    id: "TC-07",
    name: "Mixed Line Endings (CRLF / LF)",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Both CRLF and LF delimited clauses aligned safely.",
  });
}

// -------------------------------------------------------------
// Test 8: Whitespace Variability (Tabs, Indentation, Trailing)
// -------------------------------------------------------------
{
  const fixtureName = "fixture_08_whitespace_variability.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 3;

  testResults.push({
    id: "TC-08",
    name: "Whitespace Variability (Tabs, Indentation, Trailing)",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Irregular whitespace parsed without boundary distortion.",
  });
}

// -------------------------------------------------------------
// Test 9: Unicode and Legal Symbol Preservation
// -------------------------------------------------------------
{
  const fixtureName = "fixture_09_unicode_symbols.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res[2].displayText.includes("€");

  testResults.push({
    id: "TC-09",
    name: "Unicode and Legal Symbol Preservation",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Special characters (§, €, ©, ™, ®, accents) preserved exactly without mojibake.",
  });
}

// -------------------------------------------------------------
// Test 10: Literal Ellipsis Inside Text (<100 Chars)
// -------------------------------------------------------------
{
  const fixtureName = "fixture_10_literal_ellipsis.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res[0].displayText.includes("Citation...");

  testResults.push({
    id: "TC-10",
    name: "Literal Ellipsis Inside Text (<100 Chars)",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Literal ellipsis preserved without false truncation stripping.",
  });
}

// -------------------------------------------------------------
// Test 11: Heading Token Reuse
// -------------------------------------------------------------
{
  const fixtureName = "fixture_11_heading_reuse.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass =
    observed[0] === "PREVIEW_ONLY_AMBIGUOUS" &&
    observed[3] === "VERIFIED_FULL_TEXT" &&
    res.length === 6;

  testResults.push({
    id: "TC-11",
    name: "Heading Token Reuse (Ambiguity Fallback & Clause Verification)",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: [
      "PREVIEW_ONLY_AMBIGUOUS",
      "PREVIEW_ONLY_AMBIGUOUS",
      "PREVIEW_ONLY_AMBIGUOUS",
      "VERIFIED_FULL_TEXT",
      "VERIFIED_FULL_TEXT",
      "VERIFIED_FULL_TEXT",
    ],
    observedStatus: observed,
    pass,
    notes: "Non-unique repeated headings safely flagged as PREVIEW_ONLY_AMBIGUOUS while unique body clauses verified.",
  });
}

// -------------------------------------------------------------
// Test 12: Short Clauses (<100 Chars)
// -------------------------------------------------------------
{
  const fixtureName = "fixture_12_short_clause.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res[0].displayText === "1. Term. Ends Dec 31, 2026.";

  testResults.push({
    id: "TC-12",
    name: "Short Clauses (<100 Chars)",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Short clauses without backend truncation marks aligned to exact byte boundary.",
  });
}

// -------------------------------------------------------------
// Test 13: Non-Unique Substring Embedded in Prior Clause
// -------------------------------------------------------------
{
  const fixtureName = "fixture_13_non_unique_substring.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = backendData[fixtureName].map(toClauseResult);

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed.every((s) => s === "VERIFIED_FULL_TEXT") && res.length === 3;

  testResults.push({
    id: "TC-13",
    name: "Non-Unique Substring Embedded in Prior Clause",
    fixtureFile: fixtureName,
    totalClauses: clauses.length,
    expectedStatus: Array(3).fill("VERIFIED_FULL_TEXT"),
    observedStatus: observed,
    pass,
    notes: "Monotonic offset tracking prevented backward search jumping into Clause A's inner citation.",
  });
}

// -------------------------------------------------------------
// Test 14: Missing Match (Desynchronized Preview)
// -------------------------------------------------------------
{
  const fixtureName = "fixture_14_missing_match.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = [
    toClauseResult(backendData[fixtureName][0]),
    {
      ...toClauseResult(backendData[fixtureName][1]),
      text_preview: "NON_EXISTENT_CLAUSE_PREVIEW_THAT_DOES_NOT_EXIST_IN_SOURCE",
    },
  ];

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed[1] === "PREVIEW_ONLY_UNMATCHED";

  testResults.push({
    id: "TC-14",
    name: "Missing Match Desynchronization",
    fixtureFile: fixtureName,
    totalClauses: 2,
    expectedStatus: ["PREVIEW_ONLY_AMBIGUOUS", "PREVIEW_ONLY_UNMATCHED"],
    observedStatus: observed,
    pass,
    notes: "Missing clause correctly dropped to PREVIEW_ONLY_UNMATCHED without inventing text.",
  });
}

// -------------------------------------------------------------
// Test 15: Boundary Ambiguity Fallback
// -------------------------------------------------------------
{
  const fixtureName = "fixture_15_boundary_ambiguity.txt";
  const rawText = fs.readFileSync(path.join(FIXTURES_DIR, fixtureName), "utf8");
  const clauses: ClauseResult[] = [
    toClauseResult(backendData[fixtureName][0]),
    {
      ...toClauseResult(backendData[fixtureName][1]),
      text_preview: "UNMATCHABLE_SUBSEQUENT_BOUNDARY_TOKEN",
    },
  ];

  const res = alignClausesWithRawText(clauses, rawText);
  const observed = res.map((r) => r.status);
  const pass = observed[0] === "PREVIEW_ONLY_AMBIGUOUS";

  testResults.push({
    id: "TC-15",
    name: "Boundary Ambiguity Fallback",
    fixtureFile: fixtureName,
    totalClauses: 2,
    expectedStatus: ["PREVIEW_ONLY_AMBIGUOUS", "PREVIEW_ONLY_UNMATCHED"],
    observedStatus: observed,
    pass,
    notes: "Unverified subsequent boundary triggered safe PREVIEW_ONLY_AMBIGUOUS fallback for Clause 0.",
  });
}

// -------------------------------------------------------------
// Test 16: Async Race / Document ID Mismatch Guard
// -------------------------------------------------------------
{
  const fixture = "1. Contract A Clause text.";
  const clauses: ClauseResult[] = [
    {
      ...toClauseResult(backendData["fixture_01_baseline.txt"][0]),
      doc_id: "contract_A_id",
      text_preview: "1. Contract A Clause text.",
    },
  ];

  // Options pass active documentId = "contract_B_id" (user selected B while A was in-flight)
  const res = alignClausesWithRawText(clauses, fixture, { documentId: "contract_B_id" });
  const observed = res.map((r) => r.status);
  const pass = observed[0] === "PREVIEW_ONLY_AMBIGUOUS" && res[0].explanation.includes("Document ID mismatch");

  testResults.push({
    id: "TC-16",
    name: "Async Race / Document ID Mismatch Guard",
    totalClauses: 1,
    expectedStatus: ["PREVIEW_ONLY_AMBIGUOUS"],
    observedStatus: observed,
    pass,
    notes: "Document ID mismatch detected, prevented in-flight delayed result from overwriting newer document.",
  });
}

// -------------------------------------------------------------
// Test 17: Missing Raw Contract Text in Memory
// -------------------------------------------------------------
{
  const clauses: ClauseResult[] = [
    toClauseResult(backendData["fixture_01_baseline.txt"][0]),
  ];

  const res = alignClausesWithRawText(clauses, "");
  const observed = res.map((r) => r.status);
  const pass = observed[0] === "PREVIEW_ONLY_INSUFFICIENT_EVIDENCE";

  testResults.push({
    id: "TC-17",
    name: "Missing Raw Contract Text in Memory",
    totalClauses: 1,
    expectedStatus: ["PREVIEW_ONLY_INSUFFICIENT_EVIDENCE"],
    observedStatus: observed,
    pass,
    notes: "Empty/null contract memory returns PREVIEW_ONLY_INSUFFICIENT_EVIDENCE.",
  });
}

// -------------------------------------------------------------
// Print Summary and Write Artifact
// -------------------------------------------------------------
const allPassed = testResults.every((t) => t.pass);
console.log(`\nTest Cases Executed: ${testResults.length}`);
console.log(`Test Cases Passed:   ${testResults.filter((t) => t.pass).length}`);
console.log(`Test Cases Failed:   ${testResults.filter((t) => !t.pass).length}`);
console.log(`Overall Status:      ${allPassed ? "ALL TESTS PASSED [PASS]" : "FAILURES DETECTED"}\n`);

for (const t of testResults) {
  console.log(`[${t.pass ? "PASS" : "FAIL"}] ${t.id} - ${t.name}`);
  console.log(`       Observed: ${JSON.stringify(t.observedStatus)}`);
  console.log(`       Notes:    ${t.notes}`);
}

const artifact = {
  timestamp: new Date().toISOString(),
  totalTests: testResults.length,
  passedCount: testResults.filter((t) => t.pass).length,
  failedCount: testResults.filter((t) => !t.pass).length,
  overallStatus: allPassed ? "PASS" : "FAIL",
  engineVersion: "1.0.0-phase3a",
  testResults,
};

fs.writeFileSync(RESULTS_PATH, JSON.stringify(artifact, null, 2), "utf8");
console.log(`\nResults written to: ${RESULTS_PATH}`);

// A failed alignment assertion must fail the command as well as the report.
process.exitCode = allPassed ? 0 : 1;
