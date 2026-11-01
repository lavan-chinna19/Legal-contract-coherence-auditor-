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

VERSION='experimental-obligation-binding-v1.1'
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
PASSIVE_ACTIONS={'paid':'PAY','remitted':'PAY','delivered':'DELIVER','provided':'DELIVER','notified':'NOTIFY','informed':'NOTIFY'}
PASSIVE=re.compile(r'\s*(?P<verb>paid|remitted|delivered|provided|notified|informed)\b',re.I)
OCCURRENCE=re.compile(r'\b(?:for\s+)?(?:occurrence|instance)\s+(?P<id>[A-Za-z0-9_-]+)\b',re.I)

def normalized(value):
    return re.sub(r'\s+',' ',value.strip().rstrip('.')).casefold() if value else None

def _span(source,start,end):
    return dict(text=source[start:end],char_start=start,char_end=end)

def _subject(source,start,end):
    """Only explicit conjunctive parties; alternatives never become joint responsibility."""
    raw=source[start:end];offset=len(raw)-len(raw.lstrip());raw=raw.strip();start+=offset
    prefix=re.compile(r'^(?:For\s+(?:Agreement|Phase)\s+[A-Za-z0-9_-]+|If\s+(?:approved|requested))\s*,\s*',re.I)
    while (match:=prefix.match(raw)):
        start+=match.end();raw=raw[match.end():]
    spans=[_span(source,start,start+len(raw))] if raw else []
    if re.search(r'\bor\b|and/or',raw,re.I):return None,[],'ALTERNATIVE',spans
    parties=re.split(r'\s+(?:and|&)\s+|,\s*(?:and\s+)?',raw)
    actors=[]
    for party in parties:
        name=re.sub(r'^The\s+','',party.strip(),flags=re.I)
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*(?:[ \t]+[A-Za-z][A-Za-z0-9_-]*){0,3}',name):return None,[],'UNRESOLVED',spans
        if re.search(r'\b(?:it|they|he|she|this|that|which|who|date|term|terms|invoice|accounts|defined|not|neither|either)\b',name,re.I):return None,[],'UNRESOLVED',spans
        if normalized(name) in {'inc','llc','ltd','corp','corporation'}:return None,[],'UNRESOLVED',spans
        actors.append(normalized(name))
    if not actors or len(actors)>4:return None,[],'UNRESOLVED',spans
    return ' and '.join(actors),actors,'JOINT' if len(actors)>1 else 'SINGLE',spans

def _boundaries(body):
    """Split coordinated obligations only AFTER an earlier explicit modal, never a joint subject."""
    cuts=[]
    for m in re.finditer(r'[;\r\n]+|[.!?](?:\s+|$)',body):cuts.append((m.start(),m.end()))
    last=0;sentences=[]
    for a,b in cuts:sentences.append((last,a));last=b
    sentences.append((last,len(body)));result=[]
    for left,right in sentences:
        last=left
        for m in re.finditer(r'\s+and\s+(?=[A-Za-z][A-Za-z -]{0,40}\s+(?:shall|must|is\s+required\s+to)\b)',body[left:right],re.I):
            a,b=left+m.start(),left+m.end()
            if MODAL.search(body[last:a]):result.append((last,a));last=b
        result.append((last,right))
    return result

def _actor_action_relationship(left,right):
    if not left.get('actors') or not right.get('actors') or not left['action'] or not right['action']:return 'UNCERTAIN'
    if any('NEGATION_OR_ALTERNATIVE' in r['uncertainty'] for r in [left,right]):return 'UNCERTAIN'
    if sorted(left['actors'])!=sorted(right['actors']) or left['action']!=right['action']:return 'DIFFERENT'
    if left['recipient']!=right['recipient']:return 'UNCERTAIN' if None in [left['recipient'],right['recipient']] else 'DIFFERENT'
    return 'MATCHED'

def _extract(structure):
    source=structure.source_text;records=[];issues=[]
    all_scopes={m[1] for m in SCOPE.finditer(source)};all_phases={m[1] for m in PHASE.finditer(source)}
    for unit in structure.units:
        node=next((s for s in reversed(structure.sections) if s['char_start']<=unit['char_start']<s['char_end']),None)
        body_start=node['heading_end'] if node else unit['char_start']
        body=source[body_start:unit['char_end']]
        for left,right in _boundaries(body):
            raw=body[left:right];leading=len(raw)-len(raw.lstrip());text=raw.strip()
            if not text:continue
            modals=list(MODAL.finditer(text))
            if not modals:continue
            start=body_start+left+leading;end=start+len(text)
            modal=modals[0];before=text[:modal.start()]
            fields=dict(actor=None,action=None,object=None,recipient=None,trigger=None,event_instance=None,deadline=None)
            evidence={};missing=[];uncertainty=[];unsupported=[]
            verb=modal['verb'].lower();voice='PASSIVE' if verb=='be' else 'ACTIVE'
            passive=PASSIVE.match(text[modal.end():]) if voice=='PASSIVE' else None
            actor_start,actor_end=start,start+modal.start();actors=[];actor_mode='UNRESOLVED'
            patient_start=start
            # Strip only explicit context prefixes from the passive patient, keeping joint parties intact.
            patient=before.strip();patient_start=start+len(before)-len(before.lstrip())
            context=re.compile(r'^(?:For\s+(?:Agreement|Phase)\s+[A-Za-z0-9_-]+|If\s+(?:approved|requested))\s*,\s*',re.I)
            while (prefix:=context.match(patient)):patient_start+=prefix.end();patient=patient[prefix.end():]
            if voice=='PASSIVE':
                fields['action']=PASSIVE_ACTIONS.get(passive['verb'].lower()) if passive else None
                if passive:
                    action_start=start+modal.end()+passive.start('verb');action_end=start+modal.end()+passive.end('verb')
                    evidence['action']=[_span(source,action_start,action_end)]
                    agent=re.search(r'\bby\s+',text[modal.end()+passive.end():],re.I)
                    if agent:
                        actor_start=start+modal.end()+passive.end()+agent.end()
                        rest=source[actor_start:end]
                        stop=re.search(r'\b(?:to|within|exactly|at\s+least|no\s+later\s+than|after|upon|following|on|before|unless|if|each|about|of|regarding|for)\b',rest,re.I)
                        actor_end=actor_start+(stop.start() if stop else len(rest))
                    else:actor_start=actor_end=end;uncertainty.append('MISSING_PASSIVE_BY_AGENT')
                else:actor_start=actor_end=end
            else:
                if verb=='not':
                    following=re.match(r'\s*(?P<verb>notify|inform|pay|remit|deliver|provide)\b',text[modal.end():],re.I)
                    fields['action']=ACTION_MAP.get(following['verb'].lower()) if following else None
                    if following:
                        action_start=start+modal.end()+following.start('verb');action_end=start+modal.end()+following.end('verb')
                    else:action_start,action_end=start+modal.start('verb'),start+modal.end('verb')
                else:fields['action']=ACTION_MAP.get(verb);action_start,action_end=start+modal.start('verb'),start+modal.end('verb')
                evidence['action']=[_span(source,action_start,action_end)]
            fields['actor'],actors,actor_mode,actor_spans=_subject(source,actor_start,actor_end)
            if actor_spans:evidence['actor']=actor_spans;evidence['actors']=list(actor_spans)
            if fields['actor'] is None:missing.append('actor');uncertainty.append('AMBIGUOUS_OR_NONPARTY_SUBJECT')
            if fields['action'] is None:unsupported.append('ACTION_OUTSIDE_LEXICON')
            tail_start=(action_end if voice=='ACTIVE' else patient_start)
            tail=source[tail_start:end] if voice=='ACTIVE' else patient
            stripped=tail.lstrip();object_start=tail_start+len(tail)-len(stripped)
            # Notification's grammatical patient is its recipient; a topic is a separate explicit object.
            if fields['action']=='NOTIFY':
                if voice=='PASSIVE':
                    recipient_raw=patient.strip();recipient_start=patient_start
                    topic_area=text
                    topic_base=start
                else:
                    cut=re.search(r'\b(?:about|of|regarding|within|after|upon|following|on|by|unless|each)\b',stripped,re.I)
                    recipient_raw=stripped[:cut.start() if cut else len(stripped)].strip();recipient_start=object_start
                    topic_area=stripped;topic_base=object_start
                # Legacy named Notice Alpha to Recipient grammar remains compatible.
                if not NAMED_OBJECT.match(recipient_raw):
                    recipient,recipient_parts,recipient_mode,spans=_subject(source,recipient_start,recipient_start+len(recipient_raw))
                    if recipient_mode=='SINGLE':fields['recipient']=recipient;evidence['recipient']=spans
                    else:uncertainty.append('RECIPIENT_ANTECEDENT_UNESTABLISHED')
                    topic_bound=re.search(r'\b(?:within|exactly|at\s+least|no\s+later\s+than|after|upon|following|unless|each)\b',topic_area,re.I)
                    topic=re.search(r'\b(?:about|of|regarding)\s+',topic_area[:topic_bound.start()] if topic_bound else topic_area,re.I)
                    by_cue=re.search(r'\bby\b',topic_area,re.I) if voice=='PASSIVE' else None
                    if topic and topic[0].strip().lower()=='of' and by_cue and topic.start()>by_cue.start():
                        uncertainty.append('PASSIVE_TOPIC_ATTACHMENT_UNESTABLISHED');topic=None
                    if topic:object_start=topic_base+topic.end();stripped=source[object_start:end]
                    else:object_start=end;stripped=''
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
            object_type=normalized(obj['kind']) if obj else None
            if fields['object'] is None and not ref:
                generic=re.match(r'(?:the\s+)?(?P<kind>invoice|report|shipment|notice|milestone)\b',stripped,re.I)
                if generic:
                    fields['object']=normalized(generic['kind']);object_type=fields['object']
                    evidence['object']=[_span(source,object_start,object_start+generic.end())]
                    missing=[m for m in missing if m!='object']
            event_type=(fields['action']+':'+(object_type or 'notification' if fields['action']=='NOTIFY' else object_type or 'unknown')) if fields['action'] else None
            occurrence=OCCURRENCE.search(text)
            trigger_boundary=re.search(r'\b(?:after|upon|following)\b',text,re.I)
            if occurrence and trigger_boundary and occurrence.start()>trigger_boundary.start():
                uncertainty.append('OCCURRENCE_SCOPE_UNESTABLISHED');occurrence=None
            instance_basis='NAMED_OBJECT_IDENTIFIER' if fields['event_instance'] else 'UNESTABLISHED'
            if occurrence and fields['event_instance']:
                fields['event_instance']+='|occurrence:'+normalized(occurrence['id']);instance_basis='EXPLICIT_OCCURRENCE_IDENTIFIER'
                evidence['event_instance'].append(_span(source,start+occurrence.start(),start+occurrence.end()))
            remainder=stripped[(obj.end() if obj else ref.end() if ref else 0):]
            remainder_start=object_start+(obj.end() if obj else ref.end() if ref else 0)
            if re.search(r'\band\s+(?:pay|remit|deliver|provide|notify|inform|Invoice|Report|Shipment|Notice)\b',remainder,re.I):uncertainty.append('COORDINATED_ACTION_OR_OBJECT_UNRESOLVED')
            recipient=re.match(r'\s+to\s+(?P<name>(?:The\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,2}?)(?=\s+(?:within|exactly|at|no|after|upon|following|on|by|before|unless|if|each)\b|$)',remainder,re.I)
            if recipient:
                fields['recipient']=normalized(re.sub(r'^The\s+','',recipient['name'],flags=re.I))
                evidence['recipient']=[_span(source,remainder_start+recipient.start('name'),remainder_start+recipient.end('name'))]
                if fields['recipient'] in {'it','them','him','her'}:fields['recipient']=None;uncertainty.append('RECIPIENT_ANTECEDENT_UNESTABLISHED')
            if voice=='PASSIVE' and passive and fields['action']!='NOTIFY':
                recipient_match=re.search(r'\bto\s+(?P<name>[A-Za-z][A-Za-z -]{0,40}?)(?=\s+(?:by|within|exactly|after|upon|following|on|before|unless|each)\b|$)',text[modal.end()+passive.end():],re.I)
                if recipient_match:
                    recipient_base=start+modal.end()+passive.end()
                    value,parts,mode,spans=_subject(source,recipient_base+recipient_match.start('name'),recipient_base+recipient_match.end('name'))
                    if mode=='SINGLE':fields['recipient']=value;evidence['recipient']=spans
                    else:uncertainty.append('RECIPIENT_ANTECEDENT_UNESTABLISHED')
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
            if RECURRENCE.search(text):fields['event_instance']=None;instance_basis='RECURRING_TYPE_WITHOUT_UNIQUE_OCCURRENCE';uncertainty.append('RECURRING_EVENT_INSTANCE_UNESTABLISHED');missing.append('event_instance')
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
                **fields,actors=actors,actor_mode=actor_mode,voice=voice,event_type=event_type,event_instance_basis=instance_basis,
                scope=scope,phase=phase,conditions=conditions,exceptions=exceptions,evidence=evidence,
                reference_target=ref['id'] if ref else None,missing_fields=sorted(set(missing)),uncertainty=uncertainty,unsupported=unsupported))
            if len(records)>MAX_RECORDS:return records[:MAX_RECORDS],['RECORD_LIMIT']
    return records,issues

def match_obligations(left,right,*,incomplete=False):
    """All four states explain relevant known differences and missing evidence."""
    result=dict(left_id=left['record_id'],right_id=right['record_id'],status=None,reasons=[],compared_fields={},
        actor_action_relationship=_actor_action_relationship(left,right),
        evidence=[dict(record_id=r['record_id'],char_start=r['char_start'],char_end=r['char_end'],section_uid=r['section_uid']) for r in [left,right]])
    if incomplete or left['unsupported'] or right['unsupported']:
        result.update(status='UNSUPPORTED',reasons=['INCOMPLETE_OR_UNSUPPORTED_PARSE']+left['unsupported']+right['unsupported']);return result
    for field in ['actor','action','object','event_instance','recipient','scope','phase']:
        a,b=(sorted(left['actors']),sorted(right['actors'])) if field=='actor' and left['actors'] and right['actors'] else (left[field],right[field])
        result['compared_fields'][field]=dict(left=a,right=b)
        if field=='event_instance' and left.get('event_instance_basis')!=right.get('event_instance_basis') and 'EXPLICIT_OCCURRENCE_IDENTIFIER' in [left.get('event_instance_basis'),right.get('event_instance_basis')]:
            result.update(status='UNCERTAIN',reasons=['ONE_SIDED_OCCURRENCE_IDENTITY']);return result
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
            record.update(event_type=target['event_type'],event_instance_basis=target['event_instance_basis'])
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
