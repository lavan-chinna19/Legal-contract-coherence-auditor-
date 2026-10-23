# License and asset provenance review

Reviewed 2026-10-24 for the existing private personal repository. This is a
source/provenance review, not independent legal clearance.

## Contributor code

No root project `LICENSE` file was found. This copy adds no license, replaces no
attribution, and makes no sole-ownership claim. Original commits remain
ancestors of the personal release. See [contributors](../CONTRIBUTORS.md).
The repository stays private. Broader redistribution requires separate review
of contributor permissions and all applicable asset terms.

## Models and data

| Item | Primary source / declared terms | Release treatment |
| --- | --- | --- |
| `nlpaueb/legal-bert-base-uncased` | [Official model card](https://huggingface.co/nlpaueb/legal-bert-base-uncased): CC BY-SA 4.0; [license](https://creativecommons.org/licenses/by-sa/4.0/legalcode) | Upstream weights downloaded separately, excluded from Git. Preserve notices and applicable attribution/share-alike terms for redistribution. The previous MIT entry was incorrect. |
| LEGAL-BERT authors | I. Chalkidis, M. Fergadiotis, P. Malakasiotis, N. Aletras and I. Androutsopoulos, [LEGAL-BERT: The Muppets straight out of Law School](https://aclanthology.org/2020.findings-emnlp.261/), 2020 | Attribution retained here; no upstream authorship claim. |
| Existing coherence head, centroids and compatibility map | Project-produced assets from the documented model/data pipeline; original Git history and hashes retained | Small existing assets preserved unchanged. No separate asset-license grant found. This review does not establish unrestricted redistribution or determine all applicable upstream conditions; review before broader publication. |
| LEDGAR via LexGLUE | [Dataset card](https://huggingface.co/datasets/coastalcph/lex_glue) shows CC BY 4.0 metadata; its detailed licensing section requests more information. LEDGAR: Tuggener et al., 2020 | Raw clauses, local corpus and datasets excluded. Metadata is not blanket clearance for every underlying issuer document or derived asset. |
| SEC EDGAR issuer filings | Publicly accessible issuer documents; [17 USC 105](https://www.copyright.gov/title17/92chap1.html#105) concerns US government works | Filing access does not establish government authorship of privately authored agreements. Raw filings excluded; per-document redistribution review remains necessary. |
| CUAD | [The Atticus Project](https://www.atticusprojectai.org/cuad/): CC BY 4.0; The Atticus Project and collaborators, described by Hendrycks et al., 2021 | No raw dataset bundled. Retain attribution and applicable upstream terms for separately obtained material. |
| `facebook/bart-large-mnli` | [Official model card](https://huggingface.co/facebook/bart-large-mnli): MIT | Historical optional model reference. No BART cache bundled or required for verified default inference. |

Original frozen assets are unchanged; no retraining, relabeling or rewriting of
historical results occurs. Independent rights clearance for broader distribution
remains outstanding; private visibility is not a substitute for applicable rights.

## Dependencies and images

Requirements and npm lockfiles reference third-party distributions, each with
its own license and notices. Installed environments, `node_modules`, upstream
caches and image archives are excluded. This review is not a complete transitive
license certification. Key projects include
[PyTorch](https://github.com/pytorch/pytorch/blob/main/LICENSE),
[Transformers](https://github.com/huggingface/transformers/blob/main/LICENSE),
[FastAPI](https://github.com/fastapi/fastapi/blob/master/LICENSE) and
[Next.js](https://github.com/vercel/next.js/blob/canary/license.md).

Python/Debian, Node/Alpine, Nginx and PostgreSQL images are built/pulled separately
and retain their distribution notices. Source publication does not certify every
image layer or dependency as independently legally audited.
