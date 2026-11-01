"""Extract limited, explicit temporal syntax without altering the source or guessing dates."""
from dataclasses import dataclass,field,asdict
from datetime import date,datetime
import re

MONTHS=r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Sept\.?|Oct\.?|Nov\.?|Dec\.?)'
DATE_RE=re.compile(rf'\b(?:\d{{4}}[-/]\d{{1,2}}[-/]\d{{1,2}}|\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{4}}|{MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}|\d{{1,2}}(?:st|nd|rd|th)?(?:\s+day\s+of)?\s+{MONTHS},?\s+\d{{4}})\b',re.I)
ROLES=[('EFFECTIVE_DATE',r'effective\s+(?:date|as\s+of|on|from)|commenc(?:es?|ing|ement)(?:\s+(?:on|date|as\s+of))?|start\s+date'),
    ('EXPIRATION_DATE',r'expiration\s+date|expiry\s+date|expires?\s+(?:on|as\s+of)'),
    ('TERMINATION_DATE',r'termination\s+date|terminat(?:es?|ed)\s+(?:on|as\s+of)|end\s+date|ends\s+on'),
    ('EXECUTION_DATE',r'executed\s+on|execution\s+date|signed\s+on|entered\s+into\s+on'),
    ('PAYMENT_DUE_DATE',r'payment\s+(?:due|is\s+due|payable)|invoice\s+due|(?:shall|must|will)\s+pay\b'),
    ('NOTICE_DATE',r'notice\s+(?:required\s+by|given\s+by|date)|(?:shall|must|will)\s+(?:give\s+notice|notify)\b')]
ROLE_RE=[(name,re.compile(pattern,re.I)) for name,pattern in ROLES]
NUMBERS=dict(zip('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split(),range(20)))
NUMBERS.update(dict(zip('twenty thirty forty fifty sixty seventy eighty ninety'.split(),range(20,100,10))))
QUANTITY=r'(?:\d+|(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[ -](?:one|two|three|four|five|six|seven|eight|nine))?|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)'
DURATION_RE=re.compile(rf'\b(?:(?P<op>within|no\s+later\s+than|at\s+least|exactly)\s+)?(?P<n>{QUANTITY})(?:\s*\((?P<digits>\d+)\))?\s+(?:(?P<basis>calendar|business)\s+)?(?P<unit>days?|weeks?|months?|years?)\b(?:\s+(?P<relation>after|before|from)\s+(?P<trigger>[^.;\n]+))?',re.I)
QUALIFIER=re.compile(r'\b(?:if|unless|except|provided\s+that|subject\s+to|notwithstanding|amendment|amended|supersedes|approximately|approximate|about|on\s+or\s+about|permitted|refundable\s+advance|retrospective|retroactive)\b',re.I)
EVENT_RE=re.compile(r'\b(?P<event>(?:Event|Milestone|Delivery)\s+[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Z][a-zA-Z0-9_-]*){0,3})\s+(?:occurs?|is\s+scheduled|is\s+set|is)\s+(?:on\s+)?',re.I)
ACTOR_RE=re.compile(r'\b(?P<actor>(?:The\s+)?[A-Za-z][A-Za-z -]{0,40}?)\s+(?:shall|must|will)\s+(?P<action>.+)',re.I|re.S)
SCOPE_RE=re.compile(r'(?i:\bAgreement)\s+(?P<name>[A-Z][A-Za-z0-9_-]*)(?!\w)')
TIME_CUE=re.compile(r'\b(?:date|deadline|days?|weeks?|months?|years?|notice|renewal|expires?|termination|effective|effectiveness|promptly|milestone|delivery|invoice|amendment|term)\b',re.I)
PHASE_RE=re.compile(r'\bPhase\s+([A-Za-z0-9_-]+)\b',re.I)
PARTY_CONTEXT_RE=re.compile(r'\bFor\s+(Buyer|Seller|Supplier|Customer|Licensee|Licensor)\s*,',re.I)

def canonical(value):return re.sub(r'\s+',' ',(value or '').strip().rstrip('.').lower())

def trigger_key(text):
    value=canonical(text);value=re.sub(r'^(?:the|event)\s+','',value)
    value=re.sub(r'^(?:receipt\s+of)\s+(invoice\s+[a-z0-9_-]+)$',r'\1 receipt',value)
    if value in ['effective date','expiration date','termination date']:return value
    if re.fullmatch(r'(?:invoice\s+[a-z0-9_-]+\s+receipt|delivery\s+[a-z0-9_-]+|[a-z0-9_-]+(?:\s+[a-z0-9_-]+){0,3})',value):return value
    return None

def parse_date(raw):
    parts=re.fullmatch(r'(\d{1,4})[-/](\d{1,2})[-/](\d{1,4})',raw)
    if parts:
        a,b,c=map(int,parts.groups())
        if len(parts[1])==4:year,month,day=a,b,c
        elif a<=12 and b<=12 and a!=b:return None,'AMBIGUOUS_NUMERIC_DATE'
        elif a>12:year,month,day=c,b,a
        else:year,month,day=c,a,b
        try:return date(year,month,day).isoformat(),None
        except ValueError:return None,'INVALID_CALENDAR_DATE'
    normalized=re.sub(r'(\d)(?:st|nd|rd|th)\b',r'\1',raw,flags=re.I)
    normalized=re.sub(r'\bday\s+of\s+','',normalized,flags=re.I).replace(',','').replace('.','')
    normalized=re.sub(r'\bSept\b','Sep',normalized,flags=re.I)
    for fmt in ['%B %d %Y','%b %d %Y','%d %B %Y','%d %b %Y']:
        try:return datetime.strptime(normalized,fmt).date().isoformat(),None
        except ValueError:pass
    return None,'INVALID_OR_UNSUPPORTED_DATE'

@dataclass
class TemporalStatement:
    statement_id:str
    raw_text:str
    char_start:int
    char_end:int
    coordinate_space:str
    clause_id:str
    section_uid:str|None
    section_identity:str|None
    scope:str|None
    phase:str
    party_context:str|None=None
    kind:str='ABSOLUTE'
    role:str|None=None
    event:str|None=None
    actor:str|None=None
    action:str|None=None
    triggering_event:str|None=None
    absolute_date:str|None=None
    raw_date:str|None=None
    date_start:int|None=None
    date_end:int|None=None
    duration_value:int|None=None
    duration_unit:str|None=None
    timing_basis:str|None=None
    deadline_type:str|None=None
    relation:str|None=None
    lower_offset:int|None=None
    upper_offset:int|None=None
    qualifiers:list=field(default_factory=list)
    uncertainty:list=field(default_factory=list)
    parsing_status:str='EXPLICIT_SUPPORTED'
    def to_dict(self):return asdict(self)

def extract_statements(structure):
    source=structure.source_text;statements=[];issues=[]
    names={m['name'] for m in SCOPE_RE.finditer(source) if m['name'] not in ['The','This']}
    current_scope='document' if len(names)<=1 else None
    for unit in structure.units:
        unit_text=unit['text'];node=next((s for s in reversed(structure.sections) if s['heading_start']<=unit['char_start']<s['char_end']),None)
        heading_scope=SCOPE_RE.search(node['heading_text']) if node else None
        if heading_scope:current_scope='agreement:'+heading_scope['name'].lower()
        boundaries=[0]+[m.end() for m in re.finditer(r'(?<=[.!?])\s+(?=[A-Z0-9])',unit_text)]+[len(unit_text)]
        unit_dates=list(DATE_RE.finditer(unit_text));unit_roles={name for name,regex in ROLE_RE if regex.search(unit_text)}
        for left,right in zip(boundaries,boundaries[1:]):
            raw=unit_text[left:right];trim=len(raw)-len(raw.lstrip());text=raw.strip()
            if not text:continue
            start=unit['char_start']+left+trim;end=start+len(text)
            explicit_scopes={m['name'].lower() for m in SCOPE_RE.finditer(text)}
            scope='agreement:'+next(iter(explicit_scopes)) if len(explicit_scopes)==1 else None if len(explicit_scopes)>1 else current_scope
            if len(explicit_scopes)==1:current_scope=scope
            phase='RENEWAL' if re.search(r'\brenewal\s+term\b',text,re.I) else 'INITIAL' if re.search(r'\binitial\s+term\b',text,re.I) else 'CURRENT'
            # A phase named in the heading is also explicit source evidence.
            if node and phase=='CURRENT':
                if re.search(r'\brenewal\b',node['title'],re.I):phase='RENEWAL'
                elif re.search(r'\binitial\b',node['title'],re.I):phase='INITIAL'
            named_phases={canonical(m[1]) for m in PHASE_RE.finditer(text)}
            if not named_phases and node:named_phases={canonical(m[1]) for m in PHASE_RE.finditer(node['title'])}
            if len(named_phases)==1:phase='PHASE:'+next(iter(named_phases))
            contexts={canonical(m[1]) for m in PARTY_CONTEXT_RE.finditer(text)}
            party_context=next(iter(contexts)) if len(contexts)==1 else None
            multiple_actions=len(re.findall(r'\b(?:shall|must|will)\b',text,re.I))>1
            actor_match=ACTOR_RE.search(text);actor=canonical(actor_match['actor']) if actor_match else None
            action=actor_match['action'] if actor_match else None
            if action:action=re.split(r'\b(?:within|exactly|at least|no later than|on|by|before|after)\b',action,maxsplit=1,flags=re.I)[0].strip()
            if actor in ['it','they','this','that']:actor=None
            if actor and re.search(r'\b(?:date|dates|invoice|invoices|term|event|milestone|deadline)\b',actor,re.I):actor=None;action=None
            if multiple_actions:actor=None;action=None
            qualifiers=[m[0] for m in QUALIFIER.finditer(text)]
            if node:qualifiers+= [m[0] for m in QUALIFIER.finditer(node['title'])]
            links=[l['clause_id'] for l in structure.clause_links if l['char_start']<=start<l['char_end']]
            common=dict(raw_text=text,char_start=start,char_end=end,coordinate_space=structure.coordinate_space,
                clause_id=links[0] if links else node['clause_id'] if node else unit['unit_id'],
                section_uid=node['section_uid'] if node else None,section_identity=node['identity'] if node else None,
                scope=scope,phase=phase,party_context=party_context,actor=actor,action=canonical(action) or None,qualifiers=qualifiers)
            if len(text)>8192:
                statements.append(TemporalStatement(statement_id=f'{structure.doc_id}:time:{len(statements)}',**common,kind='UNPARSED',
                    parsing_status='UNSUPPORTED',uncertainty=['TEMPORAL_STATEMENT_LENGTH_LIMIT']))
                continue
            date_matches=list(DATE_RE.finditer(text));created=False
            for match in date_matches:
                parsed,error=parse_date(match[0]);preceding=text[:match.start()];following=text[match.end():]
                roles=[(name,m.end()) for name,regex in ROLE_RE for m in regex.finditer(preceding)]
                role=max(roles,key=lambda x:x[1])[0] if roles else None
                ambiguity=False
                if len(date_matches)==1 and len({x[0] for x in roles})>1 and re.search(r'\band\b',preceding,re.I):ambiguity=True;role=None
                if not role and not ambiguity:
                    after=[name for name,regex in ROLE_RE if regex.search(following)]
                    if len(after)==1:role=after[0]
                    elif len(unit_dates)==1 and len(unit_roles)==1:role=next(iter(unit_roles))
                events=list(EVENT_RE.finditer(preceding));event_match=events[-1] if events else None
                event=canonical(event_match['event']) if event_match else None
                receipt=re.search(r'\b(invoice\s+[a-z0-9_-]+)\s+is\s+received\s+on\s*$',preceding,re.I)
                if receipt:event=canonical(receipt[1])+' receipt'
                if event:event=re.sub(r'^event\s+','',event);role=role or 'EVENT_DATE'
                if role in ['EFFECTIVE_DATE','EXPIRATION_DATE','TERMINATION_DATE']:event=role.lower().replace('_',' ')
                if actor and action and actor_match.start()<match.start() and role not in ['EFFECTIVE_DATE','EXPIRATION_DATE','TERMINATION_DATE']:
                    event='obligation:'+actor+':'+canonical(action);role=role or 'DEADLINE'
                uncertainty=[error] if error else []
                if re.search(r'\b(?:not|never|neither)\b',text,re.I):uncertainty.append('NEGATED_DATE_FACT')
                if re.search(r'\b(?:either|alternatively)\b|\bor\b',text,re.I):uncertainty.append('ALTERNATIVE_DATE_FACTS')
                if multiple_actions:uncertainty.append('MULTIPLE_ACTIONS_REQUIRE_BINDING')
                if len(named_phases)>1 or len(contexts)>1:uncertainty.append('AMBIGUOUS_PHASE_OR_PARTY_CONTEXT')
                if not role:uncertainty.append('MISSING_OR_AMBIGUOUS_DATE_ROLE')
                if scope is None:uncertainty.append('AMBIGUOUS_AGREEMENT_SCOPE')
                if re.search(r'\b(?:about|approximately|approximate)\b',text,re.I):uncertainty.append('APPROXIMATE_DATE')
                time_of_day=bool(re.search(r'\b\d{1,2}:\d{2}\b',text))
                if time_of_day:uncertainty.append('TIME_OF_DAY_UNSUPPORTED')
                date_operator='NO_LATER_THAN_DATE' if re.search(r'\b(?:by|no later than|due on)\s*$',preceding,re.I) else 'BEFORE_DATE' if re.search(r'\bbefore\s*$',preceding,re.I) else 'AFTER_DATE' if re.search(r'\bafter\s*$',preceding,re.I) else 'EXACT_DATE'
                statement=TemporalStatement(statement_id=f'{structure.doc_id}:time:{len(statements)}',**common,
                    role=role,event=event,absolute_date=parsed,raw_date=match[0],date_start=start+match.start(),date_end=start+match.end(),
                    deadline_type=date_operator,uncertainty=uncertainty,
                    parsing_status='UNSUPPORTED' if time_of_day else 'REVIEW_REQUIRED' if uncertainty else 'EXPLICIT_SUPPORTED')
                statements.append(statement);created=True
            for match in DURATION_RE.finditer(text):
                quantity=match['n'].lower();value=int(quantity) if quantity.isdigit() else sum(NUMBERS[x] for x in re.split('[ -]',quantity))
                unit_name=match['unit'].lower().rstrip('s');basis=(match['basis'] or '').lower()
                uncertainty=[]
                # Never parse the trailing 'one' in unsupported 'one hundred and one'.
                if re.search(r'\b(?:hundred|thousand|and)\s*$',text[:match.start()],re.I):uncertainty.append('UNSUPPORTED_COMPOUND_QUANTITY')
                if multiple_actions:uncertainty.append('MULTIPLE_ACTIONS_REQUIRE_BINDING')
                if len(named_phases)>1 or len(contexts)>1:uncertainty.append('AMBIGUOUS_PHASE_OR_PARTY_CONTEXT')
                if match['digits'] and int(match['digits'])!=value:uncertainty.append('WRITTEN_NUMERIC_DURATION_DISAGREEMENT')
                timing='BUSINESS_DAY' if basis=='business' else 'CALENDAR_DAY' if basis=='calendar' or unit_name=='week' else 'UNSPECIFIED_DAY' if unit_name=='day' else unit_name.upper()
                trigger=trigger_key(match['trigger']) if match['trigger'] else None;op=canonical(match['op']) or None;relation=canonical(match['relation']) or None
                if not actor:uncertainty.append('MISSING_ACTOR')
                if not trigger:uncertainty.append('MISSING_OR_UNSUPPORTED_TRIGGER')
                if not scope:uncertainty.append('AMBIGUOUS_AGREEMENT_SCOPE')
                if not op:uncertainty.append('MISSING_DEADLINE_OPERATOR')
                if timing=='UNSPECIFIED_DAY':uncertainty.append('UNSPECIFIED_DAY_BASIS')
                if timing=='BUSINESS_DAY':uncertainty.append('BUSINESS_CALENDAR_UNPROVIDED')
                if unit_name in ['month','year']:uncertainty.append('CALENDAR_DURATION_POLICY_UNSUPPORTED')
                days=value*7 if unit_name=='week' else value;lower=None;upper=None
                if timing=='CALENDAR_DAY' and relation in ['after','before','from']:
                    if relation=='before':
                        lower=-days if op in ['within','exactly'] else None
                        upper=-days if op in ['no later than','at least','exactly'] else 0 if op=='within' else None
                    else:
                        lower=days if op in ['at least','exactly'] else 0 if op=='within' else None
                        upper=days if op in ['within','no later than','exactly'] else None
                statement=TemporalStatement(statement_id=f'{structure.doc_id}:time:{len(statements)}',**common,kind='DURATION',
                    role='NOTICE_DATE' if action and re.search(r'notice|notify',action,re.I) else 'PAYMENT_DUE_DATE' if action and re.match(r'pay\b',action,re.I) else 'DEADLINE',
                    event=('obligation:'+actor+':'+canonical(action)) if actor and action else None,
                    triggering_event=trigger,duration_value=value,duration_unit=unit_name,timing_basis=timing,deadline_type=op,
                    relation=relation,lower_offset=lower,upper_offset=upper,uncertainty=uncertainty,
                    parsing_status='UNSUPPORTED' if unit_name in ['month','year'] or timing=='BUSINESS_DAY' else 'REVIEW_REQUIRED' if uncertainty else 'EXPLICIT_SUPPORTED')
                statements.append(statement);created=True
            sequence=re.search(r'\b(?P<left>Milestone\s+[A-Za-z0-9_-]+)\s+must\s+occur\s+before\s+(?P<right>Milestone\s+[A-Za-z0-9_-]+)',text,re.I)
            if sequence:
                statements.append(TemporalStatement(statement_id=f'{structure.doc_id}:time:{len(statements)}',**common,kind='SEQUENCE',
                    event=canonical(sequence['left']),triggering_event=canonical(sequence['right']),deadline_type='before'));created=True
            if not created and TIME_CUE.search(text) and not (node and start>=node['heading_start'] and end<=node['heading_end']):
                statements.append(TemporalStatement(statement_id=f'{structure.doc_id}:time:{len(statements)}',**common,kind='UNPARSED',
                    parsing_status='UNSUPPORTED',uncertainty=['TEMPORAL_LANGUAGE_OUTSIDE_SUPPORTED_GRAMMAR']))
            if len(statements)>500:
                return statements[:500],[dict(category='UNSUPPORTED',reason='TEMPORAL_PARSE_LIMIT',source_start=0,source_end=len(source))]
    return statements,issues
