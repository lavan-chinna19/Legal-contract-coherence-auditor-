# Evidence Collection Script

# BUG-001
Write-Host "Reproducing BUG-001..."
$env:ENCRYPTION_KEY="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
Remove-Item Env:\STORAGE_ENCRYPTION_KEY -ErrorAction SilentlyContinue
python -c "from src.api.storage import get_fernet; f = get_fernet()" 2> "audit/prompt_21b/BUG-001_evidence.txt"

# BUG-002
Write-Host "Reproducing BUG-002..."
$env:RETENTION_TTL_SECONDS="3600"
Remove-Item Env:\DATA_RETENTION_SECONDS -ErrorAction SilentlyContinue
python -c "from src.api.retention import DEFAULT_RETENTION_SECONDS; print(DEFAULT_RETENTION_SECONDS)" > "audit/prompt_21b/BUG-002_evidence.txt"

# BUG-003
Write-Host "Reproducing BUG-003..."
python -c "
import asyncio
from src.feedback.refit import run_refit
# We can't easily mock the DB here, but we can verify the source code.
import ast
with open('src/feedback/refit.py', 'r') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Compare):
        if hasattr(node.left, 'attr') and node.left.attr == 'reviewer_verdict':
            for comp in node.comparators:
                if hasattr(comp, 's'): print(comp.s)
" > "audit/prompt_21b/BUG-003_evidence.txt"

# BUG-004
Write-Host "Reproducing BUG-004..."
Select-String -Path "frontend/src/app/page.tsx" -Pattern "useState\(.*127\.0\.0\.1" > "audit/prompt_21b/BUG-004_evidence.txt"

# BUG-005
Write-Host "Reproducing BUG-005..."
Select-String -Path "src/api/v1/router.py" -Pattern "xai|attribution" > "audit/prompt_21b/BUG-005_evidence.txt"

# BUG-006
Write-Host "Reproducing BUG-006..."
Select-String -Path "src/api/jobs.py" -Pattern "scorer\.score_document" > "audit/prompt_21b/BUG-006_evidence.txt"
Select-String -Path "src/api/jobs.py" -Pattern "UnifiedAuditor" >> "audit/prompt_21b/BUG-006_evidence.txt"

# BUG-007
Write-Host "Reproducing BUG-007..."
Select-String -Path "src/segmentation/rule_based.py" -Pattern "clause_text = text\[start_idx:end_idx\]\.strip\(\)" -Context 0,2 > "audit/prompt_21b/BUG-007_evidence.txt"

# BUG-008
Write-Host "Reproducing BUG-008..."
Select-String -Path "src/embeddings/cache.py" -Pattern "save_embeddings" -Context 0,15 > "audit/prompt_21b/BUG-008_evidence.txt"

# BUG-009
Write-Host "Reproducing BUG-009..."
Select-String -Path "src/calibration/conformal.py" -Pattern "np.quantile" -Context 0,2 > "audit/prompt_21b/BUG-009_evidence.txt"

# BUG-010
Write-Host "Reproducing BUG-010..."
Select-String -Path "src/api/jobs.py" -Pattern "JOB_STORE =" > "audit/prompt_21b/BUG-010_evidence.txt"
Select-String -Path "src/api/rate_limiter.py" -Pattern "_records:" >> "audit/prompt_21b/BUG-010_evidence.txt"

# BUG-011
Write-Host "Reproducing BUG-011..."
$hasDockerIgnore = Test-Path ".dockerignore"
$hasFrontendDockerIgnore = Test-Path "frontend/.dockerignore"
echo ".dockerignore exists: $hasDockerIgnore" > "audit/prompt_21b/BUG-011_evidence.txt"
echo "frontend/.dockerignore exists: $hasFrontendDockerIgnore" >> "audit/prompt_21b/BUG-011_evidence.txt"

# BUG-012
Write-Host "Reproducing BUG-012..."
Select-String -Path "src/api/rate_limiter.py" -Pattern "rate_limit_upload_and_analyze" -Context 0,10 > "audit/prompt_21b/BUG-012_evidence.txt"

Write-Host "Evidence collection complete."
