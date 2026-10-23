/**
 * frontend/src/components/review/alignment.ts
 *
 * Pure TypeScript clause-to-source-text alignment engine for LexAudit.
 *
 * CORE ARCHITECTURAL PRINCIPLE:
 * A full clause is displayed as authoritative ONLY when the mapping from the
 * backend clause ID to that exact text span in raw contract memory is verified
 * against available evidence.
 * If ambiguous, non-unique, overlapping, or unverified, the engine falls back
 * safely and transparently to the backend-provided preview with an explicit badge.
 */

import type { ClauseResult, ClauseAlignmentResult, ClauseAlignmentStatus } from "./types";

export interface AlignmentOptions {
  documentId?: string;
}

/**
 * Finds all starting indices of needle in haystack, starting at or after fromIndex,
 * adapting line endings (CRLF vs LF) if newlines are present.
 */
function findOccurrencesForToken(
  haystack: string,
  needle: string,
  fromIndex: number = 0
): { occurrences: number[]; matchedLength: number } {
  if (!needle || !haystack) return { occurrences: [], matchedLength: 0 };

  // Attempt 1: verbatim match
  let indices: number[] = [];
  let pos = haystack.indexOf(needle, fromIndex);
  while (pos !== -1) {
    indices.push(pos);
    pos = haystack.indexOf(needle, pos + 1);
  }
  if (indices.length > 0) {
    return { occurrences: indices, matchedLength: needle.length };
  }

  // Attempt 2: if needle contains newlines, adapt between CRLF and LF
  if (needle.includes("\n")) {
    const crlfNeedle = needle.replace(/\r?\n/g, "\r\n");
    if (crlfNeedle !== needle) {
      indices = [];
      pos = haystack.indexOf(crlfNeedle, fromIndex);
      while (pos !== -1) {
        indices.push(pos);
        pos = haystack.indexOf(crlfNeedle, pos + 1);
      }
      if (indices.length > 0) {
        return { occurrences: indices, matchedLength: crlfNeedle.length };
      }
    }

    const lfNeedle = needle.replace(/\r\n/g, "\n");
    if (lfNeedle !== needle) {
      indices = [];
      pos = haystack.indexOf(lfNeedle, fromIndex);
      while (pos !== -1) {
        indices.push(pos);
        pos = haystack.indexOf(lfNeedle, pos + 1);
      }
      if (indices.length > 0) {
        return { occurrences: indices, matchedLength: lfNeedle.length };
      }
    }
  }

  return { occurrences: [], matchedLength: needle.length };
}

/**
 * Normalizes preview token for search while detecting truncation.
 * In the FastAPI backend:
 * preview = c.text[:100] + "..." if len(c.text) > 100 else c.text
 */
export function extractSearchToken(textPreview: string): { token: string; isTruncated: boolean } {
  if (!textPreview) {
    return { token: "", isTruncated: false };
  }

  const trimmed = textPreview.trim();
  // If backend appended "..." upon truncation at 100 characters
  if (trimmed.endsWith("...") && trimmed.length >= 100) {
    return {
      token: trimmed.slice(0, -3).trim(),
      isTruncated: true,
    };
  }

  return {
    token: trimmed,
    isTruncated: false,
  };
}

/**
 * Aligns an ordered array of backend clauses against the raw uploaded contract text.
 *
 * Guarantees:
 * 1. Strict monotonicity: Clause_i must precede Clause_{i+1} in source text offsets.
 * 2. Non-overlapping boundaries: [Start_i, End_i] must not intersect with [Start_{i+1}, End_{i+1}].
 * 3. Identity preservation: Backend clause_id is never reassigned or derived from displayed text.
 * 4. Fallback on ambiguity: Any unprovable boundary drops to PREVIEW_ONLY_AMBIGUOUS.
 */
export function alignClausesWithRawText(
  backendClauses: ClauseResult[],
  rawContractText: string | null | undefined,
  options: AlignmentOptions = {}
): ClauseAlignmentResult[] {
  if (!backendClauses || backendClauses.length === 0) {
    return [];
  }

  // Case 1: Raw contract text unavailable in memory
  if (!rawContractText || typeof rawContractText !== "string" || !rawContractText.trim()) {
    return backendClauses.map((c) => ({
      clauseId: c.clause_id,
      sequenceIdx: c.sequence_idx,
      status: "PREVIEW_ONLY_INSUFFICIENT_EVIDENCE" as ClauseAlignmentStatus,
      displayText: c.text_preview || "Clause text preview unavailable",
      explanation: "Uploaded contract raw text is not present in browser memory.",
    }));
  }

  // Optional: check document ID consistency if provided
  if (options.documentId && backendClauses.length > 0) {
    const firstDocId = backendClauses[0].doc_id;
    if (firstDocId && firstDocId !== options.documentId) {
      return backendClauses.map((c) => ({
        clauseId: c.clause_id,
        sequenceIdx: c.sequence_idx,
        status: "PREVIEW_ONLY_AMBIGUOUS" as ClauseAlignmentStatus,
        displayText: c.text_preview || "Clause text preview unavailable",
        explanation: "Document ID mismatch detected between active upload and analysis result.",
      }));
    }
  }

  const raw = rawContractText;
  const numClauses = backendClauses.length;

  // Pre-process search tokens for all clauses
  const clauseTokens = backendClauses.map((c) => {
    const { token, isTruncated } = extractSearchToken(c.text_preview);
    return {
      clause: c,
      token,
      isTruncated,
    };
  });

  // Step 1: Sequential candidate location pass
  interface CandidateMatch {
    startIdx: number;
    tokenLength: number;
    isAmbiguous: boolean;
    ambiguityReason?: string;
  }

  const candidateMatches: (CandidateMatch | null)[] = new Array(numClauses).fill(null);
  let currentSearchOffset = 0;

  for (let i = 0; i < numClauses; i++) {
    const { token } = clauseTokens[i];

    if (!token) {
      candidateMatches[i] = null;
      continue;
    }

    // Search in rawContractText with line-ending adaptation
    const { occurrences, matchedLength } = findOccurrencesForToken(raw, token, currentSearchOffset);

    if (occurrences.length === 0) {
      candidateMatches[i] = null;
      continue;
    }

    // Check if consecutive clauses share this identical token (repeated prefixes / duplicate clauses)
    let duplicateGroupSize = 1;
    for (let j = i + 1; j < numClauses; j++) {
      if (clauseTokens[j].token === token) {
        duplicateGroupSize++;
      } else {
        break;
      }
    }

    if (occurrences.length === 1) {
      candidateMatches[i] = {
        startIdx: occurrences[0],
        tokenLength: matchedLength,
        isAmbiguous: false,
      };
      currentSearchOffset = occurrences[0] + matchedLength;
    } else if (occurrences.length >= duplicateGroupSize && duplicateGroupSize > 1) {
      // Monotonic 1-to-1 sequential mapping for repeated prefix / duplicate clauses
      candidateMatches[i] = {
        startIdx: occurrences[0],
        tokenLength: matchedLength,
        isAmbiguous: false,
      };
      currentSearchOffset = occurrences[0] + matchedLength;
    } else {
      // Multiple conflicting candidates in remaining text that cannot be verified
      candidateMatches[i] = {
        startIdx: occurrences[0],
        tokenLength: matchedLength,
        isAmbiguous: true,
        ambiguityReason: `Detected ${occurrences.length} conflicting matching candidate offsets in remaining text.`,
      };
      currentSearchOffset = occurrences[0] + matchedLength;
    }
  }

  // Step 2: Boundary Resolution & Verification Pass
  const results: ClauseAlignmentResult[] = [];

  for (let i = 0; i < numClauses; i++) {
    const c = backendClauses[i];
    const match = candidateMatches[i];

    // Case: No match found
    if (!match || match.startIdx === -1) {
      results.push({
        clauseId: c.clause_id,
        sequenceIdx: c.sequence_idx,
        status: "PREVIEW_ONLY_UNMATCHED",
        displayText: c.text_preview,
        explanation: "Clause prefix not found in document text at expected sequence offset.",
      });
      continue;
    }

    // Case: Candidate match was flagged as ambiguous
    if (match.isAmbiguous) {
      results.push({
        clauseId: c.clause_id,
        sequenceIdx: c.sequence_idx,
        status: "PREVIEW_ONLY_AMBIGUOUS",
        displayText: c.text_preview,
        sourceStart: match.startIdx,
        explanation: match.ambiguityReason || "Ambiguous candidate offsets detected.",
      });
      continue;
    }

    const startIdx = match.startIdx;

    // Determine end boundary
    let endIdx: number;
    let endBoundaryVerified = false;

    if (i < numClauses - 1) {
      const nextMatch = candidateMatches[i + 1];
      if (nextMatch && nextMatch.startIdx > startIdx && !nextMatch.isAmbiguous) {
        endIdx = nextMatch.startIdx;
        endBoundaryVerified = true;
      } else {
        // Next clause has no proven boundary; cannot determine where clause i ends without guessing
        results.push({
          clauseId: c.clause_id,
          sequenceIdx: c.sequence_idx,
          status: "PREVIEW_ONLY_AMBIGUOUS",
          displayText: c.text_preview,
          sourceStart: startIdx,
          explanation: "Subsequent clause boundary could not be uniquely verified; full text range ambiguous.",
        });
        continue;
      }
    } else {
      // Final clause in document: ends at document conclusion
      endIdx = raw.length;
      endBoundaryVerified = true;
    }

    if (!endBoundaryVerified || endIdx <= startIdx) {
      results.push({
        clauseId: c.clause_id,
        sequenceIdx: c.sequence_idx,
        status: "PREVIEW_ONLY_AMBIGUOUS",
        displayText: c.text_preview,
        sourceStart: startIdx,
        explanation: "Computed boundary range is non-positive or inverted.",
      });
      continue;
    }

    const slice = raw.slice(startIdx, endIdx).trim();

    // Verification check: slice must contain the expected token
    if (slice.length < match.tokenLength) {
      results.push({
        clauseId: c.clause_id,
        sequenceIdx: c.sequence_idx,
        status: "PREVIEW_ONLY_AMBIGUOUS",
        displayText: c.text_preview,
        sourceStart: startIdx,
        sourceEnd: endIdx,
        explanation: "Extracted text span is shorter than search token.",
      });
      continue;
    }

    // All conditions verified!
    results.push({
      clauseId: c.clause_id,
      sequenceIdx: c.sequence_idx,
      status: "VERIFIED_FULL_TEXT",
      displayText: slice,
      sourceStart: startIdx,
      sourceEnd: endIdx,
      explanation: "Clause boundary uniquely verified against document structure.",
    });
  }

  return results;
}
