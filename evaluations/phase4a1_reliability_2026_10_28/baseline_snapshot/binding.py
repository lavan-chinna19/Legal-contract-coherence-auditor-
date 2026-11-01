"""Small deterministic binding grammar with explicit evidence and conservative abstention.

No temporal/neural inference is modified. MATCHED means potentially comparable explicit
records under this bounded grammar, not identical legal duties or conflicting deadlines.
"""
from collections import Counter
from itertools import combinations
import hashlib
import re
from src.structure import parse_contract,resolve_references
from src.structure.parser import MARKUP

VERSION='experimental-obligation-binding-v1'
ACTION_MAP={'pay':'PAY','remit':'PAY','deliver':'DELIVER','provide':'DELIVER','notify':'NOTIFY','inform':'NOTIFY'}
MODAL=re.compile(r'\b(?:shall|must|is\s+required\s+to)\s+(?P<verb>[a-z]+)\b',re.I)
NAMED_OBJECT=re.compile(r'(?:the\s+)?(?P<kind>Invoice|Report|Shipment|Notice|Milestone)\s+(?P<id>[A-Za-z0-9_-]+)\b',re.I)
REFERENCE_OBJECT=re.compile(r'(?:the\s+)?(?:obligation|payment|delivery)\s+in\s+Section\s+(?P<id>\d+(?:\.\d+)*(?:\([a-z0-9]+\))*)',re.I)
TRIGGER=re.compile(r'\b(?:after|upon|following)\s+(?:the\s+)?(?P<event>(?:receipt|acceptance|delivery|execution)\s+of\s+(?:the\s+)?(?:Invoice|Report|Shipment|Notice|Milestone)\s+[A-Za-z0-9_-]+)\b',re.I)
TIMING=re.compile(r'\b(?:within|exactly|at\s+least|no\s+later\s+than)\s+(?:\d+|[A-Za-z]+(?:-[A-Za-z]+)?)(?:\s*\(\d+\))?\s+(?:(?:calendar|business)\s+)?(?:days?|weeks?|months?|years?)\b|\b(?:on|by|before)\s+\d{4}-\d{2}-\d{2}\b',re.I)
EXCEPTIONS=re.compile(r'\b(?:unless|except|notwithstanding|subject\s+to|provided\s+that|amendment|supersedes)\b',re.I)
SCOPE=re.compile(r'\bAgreement\s+([A-Z][A-Za-z0-9_-]*)\b')
PHASE=re.compile(r'\bPhase\s+([A-Za-z0-9_-]+)\b',re.I)
RECURRENCE=re.compile(r'\b(?:each|every|monthly|annually|weekly|recurring|successive)\b',re.I)
MAX_RECORDS=100
MAX_PAIRS=1000
MAX_STATEMENT_CHARS=8192

def normalized(value):
    return re.sub(r'\s+',' ',value.strip().rstrip('.')).casefold() if value else None

def _span(source,start,end):
    return dict(text=source[start:end],char_start=start,char_end=end)

def _extract(structure):
    source=structure.source_text;records=[];issues=[]
    all_scopes={m[1] for m in SCOPE.finditer(source)};all_phases={m[1] for m in PHASE.finditer(source)}
    for unit in structure.units:
        node=next((s for s in reversed(structure.sections) if s['char_start']<=unit['char_start']<s['char_end']),None)
        body_start=node['heading_end'] if node else unit['char_start']
        body=source[body_start:unit['char_end']]
        # Split explicit sentence/semicolon boundaries and coordinated explicit modal subjects.
        separators=re.compile(r'[;\r\n]+|[.!?](?:\s+|$)|\s+and\s+(?=[A-Za-z][A-Za-z -]{0,40}\s+(?:shall|must|is\s+required\s+to)\b)',re.I)
        boundaries=[];last=0
        for cut in separators.finditer(body):
            boundaries.append((last,cut.start()));last=cut.end()
        boundaries.append((last,len(body)))
        for left,right in boundaries:
            raw=body[left:right];leading=len(raw)-len(raw.lstrip());text=raw.strip()
            if not text:continue
            modals=list(MODAL.finditer(text))
            if not modals:continue
            start=body_start+left+leading;end=start+len(text)
            modal=modals[0];before=text[:modal.start()]
            # Only the explicit local subject after context/condition prefixes binds.
            actor_raw=before.rsplit(',',1)[-1].strip();actor_start=start+before.rfind(actor_raw) if actor_raw else start+modal.start()
            fields=dict(actor=None,action=None,object=None,recipient=None,trigger=None,event_instance=None,deadline=None)
            evidence={};missing=[];uncertainty=[];unsupported=[]
            if re.fullmatch(r'(?:The\s+)?[A-Za-z][A-Za-z0-9_-]*(?:[ \t]+[A-Za-z][A-Za-z0-9_-]*){0,3}',actor_raw or ''):
                if re.search(r'\b(?:it|they|he|she|this|that|which|who|and|or|date|term|invoice)\b',actor_raw,re.I):
                    uncertainty.append('AMBIGUOUS_OR_NONPARTY_SUBJECT')
                else:
                    fields['actor']=normalized(re.sub(r'^The\s+','',actor_raw,flags=re.I))
                    evidence['actor']=[_span(source,actor_start,actor_start+len(actor_raw))]
            if fields['actor'] is None:missing.append('actor')
            verb=modal['verb'].lower();fields['action']=ACTION_MAP.get(verb)
            evidence['action']=[_span(source,start+modal.start('verb'),start+modal.end('verb'))]
            if fields['action'] is None:unsupported.append('ACTION_OUTSIDE_LEXICON')
            tail=text[modal.end():];tail_start=start+modal.end();stripped=tail.lstrip();object_start=tail_start+len(tail)-len(stripped)
            obj=NAMED_OBJECT.match(stripped);ref=REFERENCE_OBJECT.match(stripped)
            if obj and obj['id'].lower() not in {'to','by','on','before','after','within','of','for','is','the','a'}:
                fields['object']=normalized(obj[0]);fields['object']=re.sub(r'^the\s+','',fields['object'])
                fields['event_instance']=fields['object']
                evidence['object']=[_span(source,object_start,object_start+obj.end())]
                evidence['event_instance']=list(evidence['object'])
            elif ref:
                evidence['reference']=[_span(source,object_start,object_start+ref.end())]
            else:
                missing.extend(['object','event_instance']);uncertainty.append('NO_EXPLICIT_NAMED_OBJECT_INSTANCE')
            remainder=stripped[(obj.end() if obj else ref.end() if ref else 0):]
            remainder_start=object_start+(obj.end() if obj else ref.end() if ref else 0)
            if re.search(r'\band\s+(?:pay|remit|deliver|provide|notify|inform|Invoice|Report|Shipment|Notice)\b',remainder,re.I):uncertainty.append('COORDINATED_ACTION_OR_OBJECT_UNRESOLVED')
            recipient=re.match(r'\s+to\s+(?P<name>(?:The\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,2}?)(?=\s+(?:within|exactly|at|no|after|upon|following|on|by|before|unless|if|each)\b|$)',remainder,re.I)
            if recipient:
                fields['recipient']=normalized(re.sub(r'^The\s+','',recipient['name'],flags=re.I))
                evidence['recipient']=[_span(source,remainder_start+recipient.start('name'),remainder_start+recipient.end('name'))]
                if fields['recipient'] in {'it','them','him','her'}:fields['recipient']=None;uncertainty.append('RECIPIENT_ANTECEDENT_UNESTABLISHED')
            trigger=TRIGGER.search(text)
            if trigger:
                fields['trigger']=normalized(trigger['event'])
                evidence['trigger']=[_span(source,start+trigger.start('event'),start+trigger.end('event'))]
                if len(list(TRIGGER.finditer(text)))>1:uncertainty.append('MULTIPLE_TRIGGER_BINDING_UNRESOLVED')
            elif re.search(r'\b(?:after|upon|following)\b',text,re.I):uncertainty.append('UNRESOLVED_TRIGGER')
            timing=TIMING.search(text)
            if timing:
                fields['deadline']=normalized(timing[0]);evidence['deadline']=[_span(source,start+timing.start(),start+timing.end())]
            if not fields['deadline']:missing.append('deadline')
            conditions=[];condition=re.match(r'\s*If\s+(approved|requested)\s*,',text,re.I)
            if condition:
                conditions=[normalized('if '+condition[1])]
                evidence['conditions']=[_span(source,start+condition.start(),start+condition.end())]
            elif re.search(r'\bif\b',text,re.I):uncertainty.append('CONDITION_OUTSIDE_SIMPLE_GRAMMAR')
            exceptions=[m[0] for m in EXCEPTIONS.finditer(text)]
            if node:exceptions.extend(m[0] for m in EXCEPTIONS.finditer(node['title']))
            if exceptions:uncertainty.append('EXCEPTION_OR_PRECEDENCE_UNRESOLVED')
            if RECURRENCE.search(text):fields['event_instance']=None;uncertainty.append('RECURRING_EVENT_INSTANCE_UNESTABLISHED');missing.append('event_instance')
            if re.search(r'\b(?:not|never|neither|either|alternatively)\b',text,re.I):uncertainty.append('NEGATION_OR_ALTERNATIVE')
            if len(modals)>1:uncertainty.append('MULTIPLE_MODAL_BINDING_UNRESOLVED')
            if len(text)>MAX_STATEMENT_CHARS:unsupported.append('STATEMENT_LENGTH_LIMIT')
            scopes={normalized(m[1]) for m in SCOPE.finditer(text)}
            phases={normalized(m[1]) for m in PHASE.finditer(text)}
            if not scopes and node:scopes={normalized(m[1]) for m in SCOPE.finditer(node['title'])}
            if not phases and node:phases={normalized(m[1]) for m in PHASE.finditer(node['title'])}
            scope=next(iter(scopes)) if len(scopes)==1 else 'document' if not all_scopes else None
            phase=next(iter(phases)) if len(phases)==1 else 'current' if not all_phases else None
            if scope is None:uncertainty.append('SCOPE_UNESTABLISHED')
            if phase is None:uncertainty.append('PHASE_UNESTABLISHED')
            if any(r.get('reason')=='AMBIGUOUS_HEADING' for r in structure.reviews):uncertainty.append('AMBIGUOUS_SOURCE_STRUCTURE')
            links=[x['clause_id'] for x in structure.clause_links if x['char_start']<=start<x['char_end']]
            records.append(dict(record_id=f'{structure.doc_id}:obligation:{len(records)}',raw_text=text,char_start=start,char_end=end,
                coordinate_space=structure.coordinate_space,section_uid=node['section_uid'] if node else None,
                section_identity=node['identity'] if node else None,clause_id=links[0] if links else node['clause_id'] if node else unit['unit_id'],
                **fields,scope=scope,phase=phase,conditions=conditions,exceptions=exceptions,evidence=evidence,
                reference_target=ref['id'] if ref else None,missing_fields=sorted(set(missing)),uncertainty=uncertainty,unsupported=unsupported))
            if len(records)>MAX_RECORDS:return records[:MAX_RECORDS],['RECORD_LIMIT']
    return records,issues

def match_obligations(left,right,*,incomplete=False):
    """All four states explain relevant known differences and missing evidence."""
    result=dict(left_id=left['record_id'],right_id=right['record_id'],status=None,reasons=[],compared_fields={},
        evidence=[dict(record_id=r['record_id'],char_start=r['char_start'],char_end=r['char_end'],section_uid=r['section_uid']) for r in [left,right]])
    if incomplete or left['unsupported'] or right['unsupported']:
        result.update(status='UNSUPPORTED',reasons=['INCOMPLETE_OR_UNSUPPORTED_PARSE']+left['unsupported']+right['unsupported']);return result
    for field in ['actor','action','object','event_instance','recipient','scope','phase']:
        a,b=left[field],right[field];result['compared_fields'][field]=dict(left=a,right=b)
        if a is not None and b is not None and a!=b:
            result.update(status='DIFFERENT',reasons=['EXPLICIT_DIFFERENT_'+field.upper()]);return result
    reasons=left['uncertainty']+right['uncertainty']
    for field in ['actor','action','object','event_instance','scope','phase']:
        if left[field] is None or right[field] is None:reasons.append('MISSING_'+field.upper())
    if (left['recipient'] is None)!=(right['recipient'] is None):reasons.append('ONE_SIDED_RECIPIENT')
    result['compared_fields']['trigger']=dict(left=left['trigger'],right=right['trigger'])
    if left['trigger']!=right['trigger']:reasons.append('TRIGGER_RELATION_UNESTABLISHED')
    result['compared_fields']['conditions']=dict(left=left['conditions'],right=right['conditions'])
    if left['conditions']!=right['conditions']:reasons.append('CONDITION_RELATION_UNESTABLISHED')
    result.update(status='UNCERTAIN' if reasons else 'MATCHED',reasons=sorted(set(reasons)) if reasons else ['EXPLICIT_FIELDS_MATCH_POTENTIALLY_COMPARABLE'])
    return result

def analyze_bindings(clauses=None,doc_id=None,*,source_text=None):
    structure=parse_contract(clauses,doc_id,source_text=source_text)
    records,issues=_extract(structure)
    if MARKUP.search(structure.source_text):issues.append('SOURCE_MARKUP_UNSUPPORTED')
    resolutions=resolve_references(structure)
    for record in records:
        if not record['reference_target']:continue
        references=[r for r in resolutions if r['target_id']==record['reference_target'] and record['char_start']<=r['char_start']<record['char_end']]
        resolved=[r for r in references if r['resolution_status']=='RESOLVED']
        targets=[r for r in records if resolved and r['section_uid']==resolved[0]['target']['section_uid'] and not r['reference_target']]
        if len(resolved)==1 and len(targets)==1 and targets[0]['object'] and targets[0]['action']==record['action']:
            target=targets[0]
            record.update(object=target['object'],event_instance=target['event_instance'],resolved_object_from=target['record_id'])
            for name in ['object','event_instance']:record['evidence'][name]=list(target['evidence'].get(name,[]))+record['evidence']['reference']
            if target['conditions'] or target['exceptions'] or target['uncertainty']:record['uncertainty'].append('REFERENCED_OBLIGATION_CONTEXT_REQUIRES_REVIEW')
        else:record['uncertainty'].append('REFERENCE_OBJECT_UNRESOLVED_OR_AMBIGUOUS')
        for name in ['object','event_instance']:
            if not record[name] and name not in record['missing_fields']:record['missing_fields'].append(name)
    if any(r.get('reason')=='PARSE_LIMIT' for r in structure.reviews):issues.append('STRUCTURE_PARSE_LIMIT')
    total=len(records)*(len(records)-1)//2
    if total>MAX_PAIRS:issues.append('PAIR_LIMIT')
    pairs=[]
    for a,b in combinations(records,2):
        if len(pairs)>=MAX_PAIRS:break
        pairs.append(match_obligations(a,b,incomplete=bool(issues)))
    counts=Counter(p['status'] for p in pairs)
    return dict(version=VERSION,experimental=True,doc_id=structure.doc_id,coordinate_space=structure.coordinate_space,
        source_sha256=hashlib.sha256(structure.source_text.encode('utf8')).hexdigest(),records=records,pairs=pairs,
        pair_counts=dict(counts),candidate_pair_count=total,evaluated_pair_count=len(pairs),complete=not issues,issues=issues,
        record_count=len(records),status='UNSUPPORTED' if issues else 'ANALYZED' if records else 'NO_SUPPORTED_OBLIGATIONS',
        limits=dict(max_records=MAX_RECORDS,max_pairs=MAX_PAIRS,max_statement_chars=MAX_STATEMENT_CHARS),
        interpretation='Experimental explicit-field binding only. MATCHED means potentially comparable, never legal equivalence or contradiction. No neural/date scores are changed.')
