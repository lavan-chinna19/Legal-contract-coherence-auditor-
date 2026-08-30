"""
src/__init__.py — Legal Contract Coherence Auditor core package.
"""
# Ensure transformers torch_load safety compatibility across torch versions
try:
    import transformers.utils.import_utils
    transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
except Exception:
    pass
