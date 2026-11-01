"""Scoped date arithmetic and interval compatibility. No legal truth or probability inference."""
from collections import defaultdict,Counter
from datetime import date
import re
from src.structure import parse_contract
from src.rules.schema import DateEntity,RuleFlag,ClaimScope
from .extraction import extract_statements,canonical

CONFIRMED='CONFIRMED_TEMPORAL_CONFLICT'
POTENTIAL='POTENTIAL_INCONSISTENCY'
REVIEW='REVIEW_REQUIRED'
UNSUPPORTED='UNSUPPORTED'
CONSISTENT='CONSISTENT'

def analyze_temporal(clauses=None,doc_id=None,*,source_text=None,structure=None):
    structure=structure or parse_contract(clauses,doc_id,source_text=source_text)
    statements,issues=extract_statements(structure);decisions=[];flags=[];used=set();seen=set()
    def emit(category,check,items,reason,flag_type=None,extra=None,priority=None):
        if len(decisions)>=1000:
            if not any(i.get('reason')=='TEMPORAL_RELATION_LIMIT' for i in issues):issues.append(dict(category=UNSUPPORTED,reason='TEMPORAL_RELATION_LIMIT'))
            return
        signature=(check,tuple(sorted(s.statement_id for s in items)))
        if signature in seen:return
        seen.add(signature);used.update(s.statement_id for s in items)
        if category==CONFIRMED and any(s.qualifiers for s in items):
            category=POTENTIAL;reason+=' Conditions, exceptions or amendment language prevent an unconditional conflict claim.'
        # Full statements are stored once in metadata. Relation evidence preserves exact
        # source spans and IDs instead of replicating whole paragraphs for every pair.
        evidence=[dict(statement_id=s.statement_id,char_start=s.char_start,char_end=s.char_end,
            date_start=s.date_start,date_end=s.date_end,raw_date=s.raw_date,section_uid=s.section_uid,
            clause_id=s.clause_id,coordinate_space=s.coordinate_space) for s in items]
        decision=dict(category=category,check=check,reason=reason,statement_ids=[s.statement_id for s in items],
            evidence=evidence,coordinate_space=structure.coordinate_space,scope=items[0].scope if items else None,
            interpretation='Deterministic textual interpretation only; not legal correctness',details=extra or {})
        decisions.append(decision)
        if category in [CONFIRMED,POTENTIAL]:
            details=dict(extra or {},decision_category=category,temporal_check=check,statements=evidence,
                coordinate_space=structure.coordinate_space,reason=reason)
            flags.append(RuleFlag(flag_id=f'FLAG_DATE_{structure.doc_id}_{len(flags)+1:03d}',doc_id=structure.doc_id,
                flag_type=flag_type or 'TEMPORAL_'+check,category='RULE_BASED',
                severity=priority or ('HIGH' if category==CONFIRMED else 'MEDIUM'),
                title=('Effective Date ordering needs review' if check=='CONTRACT_TERM' else check.replace('_',' ').title()),
                description=reason,clause_id=items[0].clause_id if items else None,
                involved_clause_ids=sorted({s.clause_id for s in items}),evidence=details,
                claim_scope=ClaimScope(what_this_shows=f'{category}: {reason}',
                    what_this_does_not_show='Does not establish legal invalidity, precedence of amendments, enforceability or independently adjudicated accuracy.')))
    if issues:
        decisions.extend(dict(issue,evidence=[],coordinate_space=structure.coordinate_space) for issue in issues)
    absolute=[s for s in statements if s.kind=='ABSOLUTE' and s.absolute_date and s.parsing_status=='EXPLICIT_SUPPORTED' and s.scope]
    durations=[s for s in statements if s.kind=='DURATION']
    for s in statements:
        if s.parsing_status!='EXPLICIT_SUPPORTED':
            emit(UNSUPPORTED if s.parsing_status=='UNSUPPORTED' else REVIEW,'PARSE_UNCERTAINTY',[s],'; '.join(s.uncertainty))
    if not issues:
        # Explicit ranges only. Independent dates and incidental 'relates to' are not ranges.
        for a,b in zip([s for s in statements if s.kind=='ABSOLUTE'],[s for s in statements if s.kind=='ABSOLUTE'][1:]):
            if a.char_start!=b.char_start or a.char_end!=b.char_end or not a.absolute_date or not b.absolute_date:continue
            local=a.raw_text[:a.date_start-a.char_start];between=structure.source_text[a.date_end:b.date_start]
            is_range=(re.search(r'\bfrom\s*$',local,re.I) and re.fullmatch(r'\s*(?:to|through|until)\s*',between,re.I)) or (re.search(r'\bbetween\s*$',local,re.I) and re.fullmatch(r'\s*and\s*',between,re.I))
            if is_range:
                if any(x!='MISSING_OR_AMBIGUOUS_DATE_ROLE' for x in a.uncertainty+b.uncertainty):continue
                delta=(date.fromisoformat(b.absolute_date)-date.fromisoformat(a.absolute_date)).days
                emit(CONFIRMED if delta<0 else CONSISTENT,'EXPLICIT_DATE_RANGE',[a,b],
                    'Explicit interval has reversed endpoints.' if delta<0 else 'Explicit interval endpoints are ordered.',
                    'INVERTED_DATE_RANGE',dict(start_date=a.absolute_date,end_date=b.absolute_date,delta_days=delta,start_raw=a.raw_date,end_raw=b.raw_date))
        by_scope=defaultdict(list)
        for s in absolute:by_scope[(s.scope,s.phase,s.party_context)].append(s)
        for group in by_scope.values():
            eff=[s for s in group if s.role=='EFFECTIVE_DATE'];ends=[s for s in group if s.role in ['EXPIRATION_DATE','TERMINATION_DATE']]
            for a in eff:
                for b in ends:
                    if a.deadline_type!='EXACT_DATE' or b.deadline_type!='EXACT_DATE':
                        emit(REVIEW,'CONTRACT_TERM_BOUND',[a,b],'Term endpoint is an inequality, not an exact date; no singleton ordering inferred.');continue
                    delta=(date.fromisoformat(b.absolute_date)-date.fromisoformat(a.absolute_date)).days
                    emit(CONFIRMED if delta<0 else CONSISTENT,'CONTRACT_TERM',[a,b],
                        'Explicit same-scope effective date is after the stated end date.' if delta<0 else 'Same-scope effective/end endpoints are ordered.',
                        'INVERTED_CONTRACT_TERM',dict(effective_date=a.absolute_date,termination_date=b.absolute_date,
                            effective_raw=a.raw_date,termination_raw=b.raw_date,delta_days=delta),priority='HIGH' if delta<0 else None)
            for s in group:
                if s.role=='PAYMENT_DUE_DATE':
                    for a in eff:
                        if s.absolute_date<a.absolute_date:
                            allowed=bool(re.search(r'permitted|advance|deposit',s.raw_text,re.I))
                            emit(CONSISTENT if allowed else POTENTIAL,'PREPAYMENT_CANDIDATE',[s,a],
                                'Payment precedes effectiveness, but the source explicitly permits an advance/deposit.' if allowed else 'Payment precedes effectiveness arithmetically; prepayments may be permitted, so this is not a confirmed contradiction.',
                                'PAYMENT_BEFORE_EFFECTIVE_DATE',dict(payment_due_date=s.absolute_date,reference_date=a.absolute_date,
                                    reference_role=a.role,delta_days=(date.fromisoformat(a.absolute_date)-date.fromisoformat(s.absolute_date)).days))
                if s.role in ['NOTICE_DATE','EXECUTION_DATE']:
                    for end in ends:
                        if s.absolute_date>end.absolute_date:
                            emit(POTENTIAL,'NOTICE_AFTER_END' if s.role=='NOTICE_DATE' else 'EXECUTION_AFTER_END',[s,end],
                                'A notice/execution date follows the end date; survival, ratification or different event semantics require interpretation.',
                                'NOTICE_AFTER_EXPIRATION' if s.role=='NOTICE_DATE' else 'EXECUTION_AFTER_TERMINATION',
                                dict(notice_date=s.absolute_date,expiration_date=end.absolute_date,delta_days=(date.fromisoformat(end.absolute_date)-date.fromisoformat(s.absolute_date)).days))
        event_groups=defaultdict(list)
        for s in absolute:
            if s.event:event_groups[(s.scope,s.phase,s.party_context,s.event)].append(s)
        for group in event_groups.values():
            for i,a in enumerate(group):
                for b in group[i+1:]:
                    if a.absolute_date==b.absolute_date:
                        emit(CONSISTENT,'SAME_EVENT_DATE',[a,b],'Repeated same-event dates agree.');continue
                    exact=a.deadline_type==b.deadline_type=='EXACT_DATE'
                    emit(CONFIRMED if exact else POTENTIAL,'SAME_EVENT_DATE',[a,b],
                        'Same named event has disjoint exact calendar dates under the same scope/phase.' if exact else 'Different deadline bounds need interpretation; an earlier deadline may satisfy both.',
                        'TEMPORAL_EVENT_DATE_CONFLICT')
        def anchor(s):
            choices=event_groups.get((s.scope,s.phase,s.party_context,s.triggering_event),[])
            clean=[x for x in choices if not x.qualifiers and x.deadline_type=='EXACT_DATE']
            return clean[0] if clean and len({x.absolute_date for x in clean})==1 else None
        groups=defaultdict(list)
        for s in durations:
            if s.parsing_status!='EXPLICIT_SUPPORTED':continue
            if s.qualifiers:
                emit(REVIEW,'QUALIFIED_DEADLINE',[s],'Conditional/qualified deadline preserved without an unconditional comparison.');continue
            a=anchor(s)
            if not a:
                emit(REVIEW,'UNRESOLVED_TRIGGER',[s],'No unique exact date for the explicitly named trigger; no deadline date invented.');continue
            groups[(s.scope,s.phase,s.party_context,s.actor,s.action)].append(s)
            matches=event_groups.get((s.scope,s.phase,s.party_context,s.event),[])
            for due in matches:
                if due.qualifiers:emit(REVIEW,'QUALIFIED_DEADLINE',[s,due],'Qualified absolute obligation needs interpretation.');continue
                offset=(date.fromisoformat(due.absolute_date)-date.fromisoformat(a.absolute_date)).days
                lower,upper=s.lower_offset,s.upper_offset
                if due.deadline_type!='EXACT_DATE':
                    emit(POTENTIAL,'ABSOLUTE_DEADLINE_BOUND',[s,due,a],'Absolute deadline is a bound, not an exact action date; feasibility needs both constraints.');continue
                conflict=(lower is not None and offset<lower) or (upper is not None and offset>upper)
                emit(CONFIRMED if conflict else CONSISTENT,'RELATIVE_DEADLINE',[s,due,a],
                    'Exact action date violates the explicit calendar-day offset constraint.' if conflict else 'Exact action date satisfies the explicit calendar-day offset constraint.',
                    'TEMPORAL_DEADLINE_CONFLICT',dict(observed_offset_days=offset,lower_offset=lower,upper_offset=upper,trigger_date=a.absolute_date))
        for group in groups.values():
            for i,a in enumerate(group):
                for b in group[i+1:]:
                    if a.triggering_event!=b.triggering_event:
                        emit(REVIEW,'DIFFERENT_TRIGGER_BASES',[a,b],'Different named trigger events are not interchangeable; no contradiction inferred.');continue
                    lower=max(x for x in [a.lower_offset,b.lower_offset] if x is not None) if any(x is not None for x in [a.lower_offset,b.lower_offset]) else None
                    upper=min(x for x in [a.upper_offset,b.upper_offset] if x is not None) if any(x is not None for x in [a.upper_offset,b.upper_offset]) else None
                    different=(a.lower_offset,a.upper_offset)!=(b.lower_offset,b.upper_offset)
                    conflict=lower is not None and upper is not None and lower>upper
                    emit(CONFIRMED if conflict else POTENTIAL if different else CONSISTENT,'DEADLINE_COMPATIBILITY',[a,b],
                        'Same-actor/action/trigger calendar constraints have no feasible offset.' if conflict else 'Different bounds overlap; satisfying a stricter deadline can satisfy both.' if different else 'Equivalent calendar-day constraints agree.',
                        'TEMPORAL_DEADLINE_CONFLICT' if conflict else 'TEMPORAL_DIFFERING_DEADLINES',dict(feasible_lower=lower,feasible_upper=upper))
        # Explicit milestone sequence; physical section order is never an ordering constraint.
        for s in [s for s in statements if s.kind=='SEQUENCE']:
            left=event_groups.get((s.scope,s.phase,s.party_context,s.event),[]);right=event_groups.get((s.scope,s.phase,s.party_context,s.triggering_event),[])
            if not s.scope or any(x.qualifiers or x.deadline_type!='EXACT_DATE' for x in left+right):
                emit(REVIEW,'MILESTONE_SEQUENCE',[s]+left+right,'Qualified event dates or non-exact dates cannot establish an unconditional sequence.');continue
            if len({x.absolute_date for x in left})!=1 or len({x.absolute_date for x in right})!=1:
                emit(REVIEW,'MILESTONE_SEQUENCE',[s],'Sequence event dates are missing or ambiguous.');continue
            a,b=left[0],right[0]
            category=CONFIRMED if a.absolute_date>b.absolute_date else CONSISTENT if a.absolute_date<b.absolute_date else REVIEW
            emit(category,'MILESTONE_SEQUENCE',[s,a,b],'Explicit before relationship contradicts calendar-day ordering.' if category==CONFIRMED else 'Explicit sequence is ordered.' if category==CONSISTENT else 'Same-day dates cannot establish within-day ordering.', 'TEMPORAL_MILESTONE_SEQUENCE')
    for s in statements:
        if s.statement_id not in used:
            emit(REVIEW if not s.event else CONSISTENT,'UNCOMPARED_STATEMENT',[s],
                'No supported operational role/relationship can be compared.' if not s.event else 'Explicit date parsed; no second supported constraint establishes a conflict. This is not validation of event truth.')
    # Parse-limit abstention must never be masked by already collected firm decisions.
    if issues:
        flags=[]
        for d in decisions:
            if d['category'] in [CONFIRMED,POTENTIAL,CONSISTENT]:d['category']=UNSUPPORTED;d['reason']='Incomplete bounded temporal parse; no firm conclusion.'
    dates=[DateEntity(role=s.role or 'GENERAL_DATE',raw_text=s.raw_date,parsed_iso=s.absolute_date,
        clause_id=s.clause_id,char_start=s.date_start,char_end=s.date_end) for s in statements if s.kind=='ABSOLUTE' and s.absolute_date]
    counts=Counter(d['category'] for d in decisions)
    status=next((c for c in [CONFIRMED,POTENTIAL,REVIEW,UNSUPPORTED,CONSISTENT] if counts[c]),'NO_TEMPORAL_STATEMENTS')
    return dict(flags=flags,dates=dates,statements=statements,decisions=decisions,
        metadata=dict(version='context-temporal-v1',coordinate_space=structure.coordinate_space,source_sha256=structure.to_dict()['source_sha256'],
            status=status,statements=[s.to_dict() for s in statements],decisions=decisions,decision_counts=dict(counts),
            confirmed_conflict_count=counts[CONFIRMED],potential_inconsistency_count=counts[POTENTIAL],
            review_count=counts[REVIEW],unsupported_count=counts[UNSUPPORTED],
            interpretation='Textual deterministic constraints and explicit uncertainty; no legal correctness probability.'))
