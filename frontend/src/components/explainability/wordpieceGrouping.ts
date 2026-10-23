/**
 * frontend/src/components/explainability/wordpieceGrouping.ts
 *
 * Reconstructs WordPiece subword token sequences into human-readable words
 * while strictly preserving original token boundaries and attributions.
 */

export interface SubTokenItem {
  token: string;
  attribution: number;
  originalIndex: number;
}

export interface WordGroup {
  id: string;
  word: string;
  subtokens: SubTokenItem[];
  totalAttribution: number;      // Sum of attributions
  maxAttribution: number;        // Attribution with maximum absolute magnitude
  isSpecialToken: boolean;
  sign: "POSITIVE" | "NEGATIVE" | "NEUTRAL";
}

const SPECIAL_TOKENS = new Set(["[CLS]", "[SEP]", "[UNK]", "[PAD]", "[MASK]"]);

export function groupWordPieceTokens(tokens: string[], attributions: number[]): WordGroup[] {
  if (!tokens || tokens.length === 0) {
    return [];
  }

  const groups: WordGroup[] = [];
  let currentWord = "";
  let currentSubtokens: SubTokenItem[] = [];

  const finalizeGroup = () => {
    if (currentSubtokens.length === 0) return;

    const total = currentSubtokens.reduce((acc, curr) => acc + curr.attribution, 0);
    // Find item with largest absolute attribution
    let maxItem = currentSubtokens[0];
    for (let i = 1; i < currentSubtokens.length; i++) {
      if (Math.abs(currentSubtokens[i].attribution) > Math.abs(maxItem.attribution)) {
        maxItem = currentSubtokens[i];
      }
    }

    const isSpecial = SPECIAL_TOKENS.has(currentWord);
    let sign: "POSITIVE" | "NEGATIVE" | "NEUTRAL" = "NEUTRAL";
    if (Math.abs(total) >= 1e-5) {
      sign = total > 0 ? "POSITIVE" : "NEGATIVE";
    }

    const firstIdx = currentSubtokens[0].originalIndex;
    groups.push({
      id: `word_group_${firstIdx}_${currentWord}`,
      word: currentWord,
      subtokens: [...currentSubtokens],
      totalAttribution: Number(total.toFixed(4)),
      maxAttribution: Number(maxItem.attribution.toFixed(4)),
      isSpecialToken: isSpecial,
      sign
    });

    currentWord = "";
    currentSubtokens = [];
  };

  for (let i = 0; i < tokens.length; i++) {
    const rawToken = tokens[i];
    const score = attributions[i] ?? 0;

    if (SPECIAL_TOKENS.has(rawToken)) {
      // Special tokens always finalize previous word and exist as standalone group
      finalizeGroup();
      groups.push({
        id: `special_token_${i}_${rawToken}`,
        word: rawToken,
        subtokens: [{ token: rawToken, attribution: score, originalIndex: i }],
        totalAttribution: Number(score.toFixed(4)),
        maxAttribution: Number(score.toFixed(4)),
        isSpecialToken: true,
        sign: Math.abs(score) < 1e-5 ? "NEUTRAL" : (score > 0 ? "POSITIVE" : "NEGATIVE")
      });
      continue;
    }

    if (rawToken.startsWith("##")) {
      // Continuation fragment
      const piece = rawToken.slice(2);
      if (currentSubtokens.length > 0) {
        currentWord += piece;
        currentSubtokens.push({ token: rawToken, attribution: score, originalIndex: i });
      } else {
        // Orphan continuation fragment: treat as standalone
        currentWord = piece;
        currentSubtokens.push({ token: rawToken, attribution: score, originalIndex: i });
      }
    } else {
      // New word root
      finalizeGroup();
      currentWord = rawToken;
      currentSubtokens.push({ token: rawToken, attribution: score, originalIndex: i });
    }
  }

  finalizeGroup();
  return groups;
}
