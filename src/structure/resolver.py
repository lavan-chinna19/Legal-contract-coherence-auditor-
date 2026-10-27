"""Exact target resolution and abstention; positional checking is a separate consumer."""
import re
from .parser import MARKUP, key

def resolve_references(document):
    index={}
    for node in document.sections:index.setdefault((node['target_type'],node['identity_key']),[]).append(node)
    uncertain={}
    for node in getattr(document,'_uncertain_headings',[]):uncertain.setdefault((node['target_type'],node['identity_key']),[]).append(node)
    incomplete=any(r.get('reason')=='PARSE_LIMIT' for r in document.reviews)
    results=[]
    for ref in document.references:
        matches=index.get((ref['target_type'],ref['target_key']),[])
        candidates=uncertain.get((ref['target_type'],ref['target_key']),[])
        reason=None
        if incomplete:status='UNSUPPORTED';reason='Incomplete bounded parse; target identity/absence cannot be established.'
        elif ref['syntax_issue']:status='UNSUPPORTED';reason=ref['syntax_issue']
        elif candidates:status='AMBIGUOUS_STRUCTURE';reason='An uncertain heading could declare this identity.'
        elif len(matches)>1:status='AMBIGUOUS_TARGET';reason='Multiple actual declarations; intended target is not unique.'
        elif len(matches)==1:status='RESOLVED';reason='Exactly one source-backed declaration has this exact identity.'
        elif MARKUP.search(document.source_text):status='UNSUPPORTED';reason='Markup structure is not parsed; absence cannot be established.'
        elif ref['target_type']=='SECTION' and not re.match(r'^\d',ref['target_id']):status='UNSUPPORTED';reason='Roman section identity resolution is outside supported numeric grammar.'
        else:status='MISSING';reason='No matching declaration in supported extracted structure.'
        results.append(dict(ref,resolution_status=status,status='REVIEW_REQUIRED' if status in ['UNSUPPORTED','AMBIGUOUS_STRUCTURE','AMBIGUOUS_TARGET'] else status,
            reason=reason,candidates=[m['section_uid'] for m in matches],target=matches[0] if status=='RESOLVED' else None))
    return results
