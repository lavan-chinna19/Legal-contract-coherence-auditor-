# LexAudit Phase 4A — Explainability UI Architecture Blueprint & Scientific Grounding

## 1. Executive Summary & Algorithmic Preservation
- **Preservation Policy**: Existing XAI algorithms in [src/xai/](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/xai/) remain completely frozen. Zero model retraining or heuristic alterations are authorized.
- **Blueprint Objective**: Establish the UX architecture, subword token merging pipeline, and signed gradient visualization for the next-generation Explainability workspace (scheduled for Phase 4B/5).
- **Prohibition on Generative LLMs**: Explanations must strictly reflect deterministic mathematical gradients and perturbation score deltas. Generative natural language synthesis via commercial LLMs is strictly prohibited.

---

## 2. API Contract & Output Schema Audit

### 2.1 Integrated Gradients Attribution (`GET /v1/xai/attribution`)
- **Query Parameters**: `doc_id` (`string`), `clause_id` (`string`).
- **Response Schema** (`src/xai/schema.py:ExplanationResultModel`):
  ```typescript
  interface IntegratedGradientsPayload {
    clause_id: string;
    tokens: string[];            // Legal-BERT WordPiece token sequence
    attributions: number[];      // Signed float attribution values [-1.0, 1.0]
    baseline_type: string;       // e.g. "zero_embedding" or "all_mask"
    target_cluster: string;      // Canonical LEDGAR centroid label
    claim_scope: {
      what_this_shows: string;
      what_this_does_not_show: string;
      methodological_limits: string;
    };
  }
  ```
- **Attribution Mathematics**:
  Integrated Gradients computes path integrals over straight-line interpolations from baseline $x'$ to input embedding $x$:
  $$IG_k(x) = (x_k - x'_k) \times \int_{0}^1 \frac{\partial F(x' + \alpha(x - x'))}{\partial x_k} d\alpha$$
  - **Signed Nature**: **Yes**, attributions are strictly signed:
    - $\text{Attribution} > 0$: Token embedding features actively drive the clause representation away from the reference legal cluster (anomaly contributor).
    - $\text{Attribution} < 0$: Token features pull the clause representation toward canonical distribution (coherence anchor).
  - **Scale Comparability**: Token attributions are relative within each clause; cross-clause direct comparisons should use normalized percentage weights.

### 2.2 Perturbation Sensitivity (`GET /v1/xai/sensitivity`)
- **Query Parameters**: `doc_id` (`string`), `clause_id` (`string`).
- **Response Schema**:
  ```typescript
  interface SensitivityPayload {
    clause_id: string;
    neighbor_position: "PREDECESSOR" | "SUCCESSOR";
    masked_clause_id: string;
    original_score: number;
    perturbed_score: number;
    score_delta: number;         // Delta = Perturbed - Original in [-1.0, 1.0]
    claim_scope: Record<string, string>;
  }
  ```
- **Sensitivity Mathematics**:
  Evaluates $\Delta S_B = S_B(c_i \mid \text{mask}(c_{i-1})) - S_B(c_i \mid c_{i-1})$.
  - $\Delta S_B > 0$: Masking neighbor worsens coherence (neighbor was providing necessary context).
  - $\Delta S_B < 0$: Masking neighbor improves coherence (neighbor was causing transition conflict).

---

## 3. Subword Token Reconstruction Pipeline (WordPiece De-tokenization)
Legal-BERT tokenizer segments complex legal jargon into subword fragments:
- `["indem", "##nifi", "##cation"]` $\to$ `"indemnification"`
- `["arbit", "##ration"]` $\to$ `"arbitration"`

### Subword Aggregation Algorithm for UI Display
```typescript
interface WordGroup {
  word: string;
  subtokens: string[];
  attribution: number; // Max-magnitude or mean attribution
}

export function groupWordPieceTokens(tokens: string[], attributions: number[]): WordGroup[] {
  const groups: WordGroup[] = [];
  let currentWord = "";
  let currentSubtokens: string[] = [];
  let currentScores: number[] = [];

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    const score = attributions[i] ?? 0;

    if (token.startsWith("##")) {
      currentWord += token.slice(2);
      currentSubtokens.push(token);
      currentScores.push(score);
    } else {
      if (currentWord) {
        // Aggregate score: sign of max absolute magnitude
        const maxScore = currentScores.reduce((prev, curr) => Math.abs(curr) > Math.abs(prev) ? curr : prev, 0);
        groups.push({ word: currentWord, subtokens: currentSubtokens, attribution: maxScore });
      }
      currentWord = token;
      currentSubtokens = [token];
      currentScores = [score];
    }
  }

  if (currentWord) {
    const maxScore = currentScores.reduce((prev, curr) => Math.abs(curr) > Math.abs(prev) ? curr : prev, 0);
    groups.push({ word: currentWord, subtokens: currentSubtokens, attribution: maxScore });
  }

  return groups;
}
```

---

## 4. UI Architecture & Component Layout Blueprint

```
+------------------------------------------------------------------------------------+
| EXPLAINABILITY WORKSPACE (XAI)                                                     |
| Selected Clause: Section 3 — Indemnification (doc_066a0456_2)                      |
+------------------------------------------------------------------------------------+
| [Tab: Integrated Gradients]   [Tab: Neighbor Sensitivity]   [Tab: Claim Scope]     |
+------------------------------------------------------------------------------------+
| 1. Signed Token Highlight View                                                     |
|    "The [Company +0.12] shall [indemnify +0.68] and hold harmless the [Buyer -0.04]|
|     against any [unforeseen +0.55] [environmental +0.82] liabilities..."           |
|                                                                                    |
|    Legend: [ Red (+): Driving Anomaly ]   [ Green (-): Anchoring Coherence ]       |
+------------------------------------------------------------------------------------+
| 2. Neighbor Sensitivity Impact                                                     |
|    Predecessor Clause (§ 2: Confidentiality): Score Delta Delta = +0.210           |
|    Successor Clause (§ 4: Governing Law):     Score Delta Delta = -0.045           |
+------------------------------------------------------------------------------------+
| 3. Mandatory ClaimScope Caveat Box                                                 |
|    What this shows: Relative gradient attribution driving embedding away from      |
|    reference clusters.                                                             |
|    What this does not show: Normative legal ambiguity or contract enforceability.  |
+------------------------------------------------------------------------------------+
```

---

## 5. Async Request Lifecycle & Race Condition Guards
1. **AbortController**: Each XAI request binds to an active `AbortController`. When the user selects a new clause, the pending in-flight request is aborted immediately:
   ```typescript
   controllerRef.current?.abort();
   controllerRef.current = new AbortController();
   ```
2. **Stale Response Guard**: Responses check that `response.clause_id === currentSelectedClauseId` before committing to state.
3. **Graceful Error Handling**: If XAI is unavailable (e.g. timeout on 5,000-character clause), display clear fallback: *"Token attribution unavailable for this clause due to sequence length limit (512 tokens max)."*
