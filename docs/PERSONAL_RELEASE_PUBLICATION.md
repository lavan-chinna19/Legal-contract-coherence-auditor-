# Personal repository release

Authorized destination: **https://github.com/GoutamNandhen/NLP_**, private,
branch `main`, using the separate `personal` remote. The existing `origin`
remote remains the collaborative repository; no push to it is authorized by
this publication request.

## Source and attribution

The personal release descends directly from the validated collaborative release
`6b20b966773d84e850b1feaf7a2adafe517bc535`. All 21 existing commits and both
recorded contributors are retained, with original author identities and parent
relationships. A new personal-release commit adds documentation updates; no
squash, force push or history rewrite is used. Local `main` and the collaborative
release branch retain their existing tips. The personal commit is prepared on
the separate local branch `codex/lexaudit-personal-release` and pushed explicitly
to `personal/main`.

## Included release

All 419 files from the validated release remain included. Three documents are
added, producing **422 files in the resulting release tree**:
`CONTRIBUTORS.md`, `docs/THIRD_PARTY_NOTICES.md` and this document. README and
data-governance corrections are documentation-only changes. Application source,
tests, model assets, dependency files, Docker definitions and the 24-component
completion checklist remain unchanged from the validated release.

Included modules: backend authentication, parsing, clause preview, inference,
encrypted history, PDF/DOCX reports, explanations, sensitivity, counterfactuals,
robustness, experimental dependency checks, feedback, experimental NLP research
code, complete frontend, regression tests and deployment/configuration tools.

Private configurations, real contracts, databases, installed environments,
caches, generated user reports and raw Docker evidence are excluded. Existing
local historical research inputs/audits and the unrelated modification to
`fixtures/load_test_results.json` remain local, as documented in
[RELEASE_PUBLICATION.md](RELEASE_PUBLICATION.md).

## Preflight and verification

- GitHub connector identity and Git Credential Manager both identify
  `GoutamNandhen`. Repository metadata confirms private visibility and write access.
- Destination refs were independently checked and empty before publication.
- All 21 existing commits / 511 historical blobs were scanned. No private-key
  material, recognized service tokens, actual local deployment secret values,
  sensitive runtime paths or large file requiring LFS were found by the scoped
  checks. This is not an independent security audit.
- Largest tracked asset is the existing 3,218,819-byte coherence checkpoint;
  its original Git blob is `c1b9ab0738c58b6409913c172017d3315e65d81c`.
  Centroids retain blob `2d316e3703f8044832bc087a6896ee41e9303d4e`.
- The approximately 881 MB public model cache, optional 5.46 MB experimental
  checkpoint, temporary environments/builds and all private runtime data stay local.
- Updated documentation relative links resolve. Final staged-file, whitespace,
  history and frozen-asset checks are required before pushing. After pushing,
  compare `personal/main` with the local personal-release SHA, inspect release
  files through GitHub, confirm private visibility and compare the original
  remote refs with their pre-publication snapshot.

## Application verification and rights boundaries

The retained actual application results are 245 local backend passes / two
optional skips; 190 publication-snapshot passes / three optional skips;
frontend lint/types/build and 17 alignment assertions passed. Docker validation
passed 103 HTTP/runtime assertions, 14 image/storage checks, 10 browser assertions
and 20 Linux-image release tests. These counts overlap. No new application
regression run is claimed for this documentation-only personal publication.

The legacy GitHub Actions workflow is retained and is not represented as a
validated fresh private-repository CI installation. Its run status is distinct
from the completed local application tests.

No overall project license is declared. Legal-BERT's CC BY-SA 4.0 metadata and
dataset/derived-asset provenance boundaries are documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). No new contributor-code or
asset license is granted. Broader redistribution rights have not been
independently cleared. Application completion remains 24/24;
`DEMO_READY_WITH_LIMITATIONS`. Scientific, legal and external security
validation remain separate and outstanding.
