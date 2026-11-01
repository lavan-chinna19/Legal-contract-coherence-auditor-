# Independent Ground-Truth Oracle Specification

The Oracle (`src/redteam/oracle.py`) operates as a completely independent verification layer.
It strictly prohibits calling the evaluated models or rule checkers:
1. **Displacement / Swap**: Validated via clause sequence permutations, relative index invariant checking, and sequence length checks.
2. **Duplication**: Validated via pairwise text equivalence and unique inserted clause ID validation.
3. **Internal References**: Validated by compiling a regex-based independent section inventory and checking that the target section number is not declared as a heading.
4. **Exhibit References**: Validated by verifying absence of exhibit definitions matching the injected citation.
5. **Date Inversions**: Validated using pure standard library `datetime.strptime` comparisons between extracted date strings, bypassing `DateLogicChecker` and `dateparser`.
6. **Deletion Consequences**: Validated by scanning surviving clauses for citations pointing to the deleted section number.
7. **Negative Controls**: Validated by SHA-256 bitwise checksum equivalence.
