"""Conservative heading/citation grammar. Every span indexes the unchanged input string.

This parser deliberately does not call the legacy HTML cleaner or neural segmenter.
Offsets describe extracted Unicode text, never PDF page coordinates. Duplicate identities
are retained, and uncertain heading candidates cannot establish a missing-target finding.
"""
from dataclasses import dataclass, field, asdict
from bisect import bisect_right
import hashlib
import re

NUMBER = r'\d+(?:\.\d+)*(?:\([a-zA-Z0-9]+\))*'
ROMAN = r'[IVXLCDMivxlcdm]+'
IDENTITY = rf'(?:{NUMBER}|{ROMAN})'
HEADING = re.compile(rf'^(?P<indent>[ \t]*)(?:(?P<kind>Section|Sec\.?|Clause|Article|Art\.?|Exhibit|Schedule|Appendix|Attachment)[ \t]+)?(?P<id>{NUMBER}|{ROMAN}|[A-Z])(?P<tail>.*)$', re.I)
RELATIVE = re.compile(r'^[ \t]*(?P<id>\([a-z]\))(?P<tail>.*)$', re.I)
CITATION = re.compile(rf'\b(?:(?P<pre>above|below)\s+)?(?P<kind>Sections?|Sec\.?|Clauses?|Articles?|Art\.?|Exhibits?|Schedules?|Appendix|Appendices|Attachments?)\s+(?P<id>{NUMBER}|{ROMAN}|[A-Z])(?!\w|\.\d)', re.I)
ORDINARY = re.compile(r'^(?:above|below|shall|must|may|will|is|are|was|were|has|have|applies|apply|provides|provide|states|supplies|requires|governs|sets|contains|describes|means|refers|and|or|through|to|units?|days?|dollars?|percent)\b', re.I)
SENTENCE_START = re.compile(r'^(?:the|this|that|these|those|if|see|pursuant|subject|under|as|for|on|in|it)\b', re.I)
MARKUP = re.compile(r'</?(?:p|div|br|table|tr|td|h[1-6])(?:\s[^<>]*|/)?\s*>', re.I)
MAX_SOURCE_CHARS = 250_000
MAX_SECTIONS = 1_000
MAX_REFERENCES = 5_000

def namespace(kind):
    kind=(kind or 'section').lower().rstrip('.')
    if kind.startswith(('art','article')):return 'ARTICLE'
    if kind.startswith(('exhibit','append','attachment')):return 'EXHIBIT'
    if kind.startswith('schedule'):return 'SCHEDULE'
    return 'SECTION'

def key(identity):
    # Case-insensitive Roman/letter matching; no decimal/parent aliasing.
    return identity.casefold()

@dataclass
class StructuralDocument:
    doc_id: str
    source_text: str
    coordinate_space: str
    sections: list = field(default_factory=list)
    references: list = field(default_factory=list)
    reviews: list = field(default_factory=list)
    units: list = field(default_factory=list)
    clause_links: list = field(default_factory=list)
    version: str = 'source-structure-v1'

    def to_dict(self):
        result=asdict(self)
        result['source_sha256']=hashlib.sha256(self.source_text.encode('utf-8')).hexdigest()
        result['offset_convention']='Unicode code points; half-open [start,end); extracted text, not PDF coordinates'
        return result

def _clause_dicts(clauses):
    result=[]
    for i,c in enumerate(clauses or []):
        c=c.to_dict() if hasattr(c,'to_dict') else c
        if not isinstance(c,dict) or not isinstance(c.get('text'),str):
            raise ValueError('Each source clause must have string text')
        result.append(dict(c,clause_id=c.get('clause_id',f'source_clause_{i}')))
    return result

def _title(tail, explicit, numeric):
    """Return evidence class and title boundaries relative to tail; never guess sentence headings."""
    if not tail.strip():return ('AMBIGUOUS',0,0)
    leading=len(tail)-len(tail.lstrip())
    rest=tail.lstrip()
    delimiter=bool(rest and rest[0] in '.):-–—')
    if delimiter:
        rest=rest[1:];leading+=1
        spaces=len(rest)-len(rest.lstrip());leading+=spaces;rest=rest.lstrip()
    elif not tail[0].isspace():return ('NOT_HEADING',0,0)
    if not rest:return ('AMBIGUOUS',leading,leading)
    if re.match(r'^\((?:above|below)\)',rest,re.I):return ('NOT_HEADING',0,0)
    if ORDINARY.match(rest) or SENTENCE_START.match(rest):return ('NOT_HEADING',0,0)
    title=re.split(r'\.\s+|[\r\n]',rest,maxsplit=1)[0].rstrip('. \t')
    # Bare integer amounts without a heading delimiter are deliberately unsupported.
    if not explicit and numeric.isdigit() and not delimiter:return ('AMBIGUOUS',leading,leading+len(title))
    if not title or not title[0].isupper() or len(title.split())>14 or re.search(r'\b(?:shall|must|will|is|are|applies|requires)\b',title,re.I):
        return ('AMBIGUOUS',leading,leading+len(title))
    return ('HEADING',leading,leading+len(title))

def parse_contract(clauses=None, doc_id=None, *, source_text=None, coordinate_space=None):
    clauses=_clause_dicts(clauses)
    doc_id=doc_id or (clauses[0].get('doc_id') if clauses else None) or 'structural_document'
    if source_text is None:
        source_text='\n\n'.join(c['text'] for c in clauses)
        coordinate_space=coordinate_space or 'assembled_clause_text'
        links=[];offset=0
        for c in clauses:
            links.append(dict(clause_id=c['clause_id'],char_start=offset,char_end=offset+len(c['text']),mapping='EXACT_CLAUSE_ASSEMBLY'))
            offset+=len(c['text'])+2
    else:
        if not isinstance(source_text,str):raise ValueError('source_text must be a string')
        coordinate_space=coordinate_space or 'original_extracted_text'
        links=[];cursor=0
        for c in clauses:
            text=c['text'];start=source_text.find(text,cursor) if text else -1
            if start>=0:
                links.append(dict(clause_id=c['clause_id'],char_start=start,char_end=start+len(text),mapping='EXACT_TEXT_MATCH'))
                cursor=start+len(text)
            elif text:
                # A legacy cleaner may have deleted content. A matching first-line anchor is
                # an association only; it never claims the remaining clause text was preserved.
                anchor=text.splitlines()[0];start=source_text.find(anchor,cursor)
                if start>=0:
                    links.append(dict(clause_id=c['clause_id'],char_start=start,char_end=start+len(anchor),mapping='PARTIAL_FIRST_LINE_ANCHOR'))
                    cursor=start+len(anchor)
    if len(source_text)>MAX_SOURCE_CHARS:raise ValueError('Structural source exceeds 250,000 characters')
    doc=StructuralDocument(str(doc_id),source_text,coordinate_space,clause_links=links)
    uncertain=[];offset=0;relative_base=None
    for line in source_text.splitlines(keepends=True):
        content=line.rstrip('\r\n');match=HEADING.match(content);relative=False
        if not match:
            match=RELATIVE.match(content);relative=bool(match)
        if match:
            identity=match['id'];kind=None if relative else match['kind'];tail=match['tail']
            # Dates/amount continuations are not structural identity evidence.
            date_like=bool(re.match(r'^[-/]\d',tail)) or (identity.isdigit() and 1900<=int(identity)<=2200 and not kind)
            status,a,b=_title(tail,bool(kind) or relative,identity)
            if relative and relative_base and tail[:1].isspace():
                # A parenthesized enumerator inside an established numbered section is
                # structural evidence even when its body starts with an ordinary sentence.
                status='HEADING';a=len(tail)-len(tail.lstrip());b=len(tail)
            if date_like:status='NOT_HEADING'
            if not kind and not relative and not re.match(r'^\d',identity):status='NOT_HEADING'
            if relative and not relative_base:status='AMBIGUOUS'
            raw_identity=identity
            if relative and relative_base:identity=relative_base+identity
            if status in ['HEADING','AMBIGUOUS']:
                if len(doc.sections)+len(uncertain)>=MAX_SECTIONS:
                    doc.reviews.append(dict(status='REVIEW_REQUIRED',reason='PARSE_LIMIT',detail='Heading inventory truncated; target resolution abstains.'))
                    break
                start=offset+len(content)-len(content.lstrip(' \t'))
                record=dict(target_type=namespace(kind),identity=identity,identity_key=key(identity),
                    raw_identifier=raw_identity,identifier_start=offset+match.start('id'),identifier_end=offset+match.end('id'),heading_start=start,heading_end=offset+len(content),
                    heading_text=source_text[start:offset+len(content)],title=tail[a:b],
                    title_start=offset+match.start('tail')+a,title_end=offset+match.start('tail')+b)
                if status=='AMBIGUOUS':
                    uncertain.append(record)
                    doc.reviews.append(dict(status='REVIEW_REQUIRED',reason='AMBIGUOUS_HEADING',**record))
                else:
                    if len(doc.sections)>=MAX_SECTIONS:
                        doc.reviews.append(dict(status='REVIEW_REQUIRED',reason='PARSE_LIMIT',detail='Section inventory truncated; target resolution abstains.'))
                        break
                    record['section_uid']=f'{doc.doc_id}:section:{len(doc.sections)}'
                    record['order']=len(doc.sections);doc.sections.append(record)
                    if record['target_type']=='SECTION' and re.match(r'^\d',identity) and not relative:
                        relative_base=re.sub(r'\([^)]*\).*','',identity)
                    elif record['target_type']!='SECTION':relative_base=None
        offset+=len(line)
    section_index={}
    for node in doc.sections:section_index.setdefault((node['target_type'],node['identity_key']),[]).append(node)
    for i,node in enumerate(doc.sections):
        identity=node['identity'];parent=re.sub(r'\([^()]*\)$','',identity) if '(' in identity else identity.rsplit('.',1)[0] if '.' in identity else None
        parents=section_index.get((node['target_type'],key(parent)),[]) if parent else []
        node.update(parent_identity=parent,parent_uid=parents[0]['section_uid'] if len(parents)==1 else None,
            parent_candidates=[p['section_uid'] for p in parents],children=[],
            char_start=node['heading_start'],char_end=doc.sections[i+1]['heading_start'] if i+1<len(doc.sections) else len(source_text))
        linked=[l['clause_id'] for l in links if l['char_start']<node['char_end'] and l['char_end']>node['char_start']]
        node['source_clause_ids']=linked;node['clause_id']=linked[0] if linked else f'{doc.doc_id}:source:{i}'
        node['text']=source_text[node['char_start']:node['char_end']]
    by_uid={n['section_uid']:n for n in doc.sections}
    for node in doc.sections:
        if node['parent_uid']:by_uid[node['parent_uid']]['children'].append(node['section_uid'])
    starts=[0]+[s['heading_start'] for s in doc.sections if s['heading_start']>0]
    for i,start in enumerate(starts):
        end=starts[i+1] if i+1<len(starts) else len(source_text)
        if end>start:doc.units.append(dict(unit_id=f'{doc.doc_id}:unit:{i}',char_start=start,char_end=end,text=source_text[start:end]))
    heading_starts=[s['heading_start'] for s in doc.sections]
    def in_heading_identifier(position):
        index=bisect_right(heading_starts,position)-1
        return index>=0 and position<doc.sections[index]['identifier_end']
    for match in CITATION.finditer(source_text):
        # A real heading is a declaration, not a self-citation. Only skip its initial marker.
        if in_heading_identifier(match.start()):continue
        start,end=match.span();identity=match['id'];typ=namespace(match['kind']);targets=[identity];unsupported=None
        tail=source_text[end:];plural=match['kind'].lower().endswith('s') or match['kind'].lower()=='appendices'
        # Inclusive ranges: same numeric prefix, integer final component, <=100 targets.
        range_match=re.match(rf'\s+(?:through|to)\s+({NUMBER})(?!\w|\.\d)',tail,re.I) if plural else None
        if range_match:
            right=range_match[1];end+=range_match.end();left_parts=identity.split('.');right_parts=right.split('.')
            if all(x.isdigit() and (len(x)==1 or not x.startswith('0')) for x in left_parts+right_parts) and left_parts[:-1]==right_parts[:-1] and 0<=int(right_parts[-1])-int(left_parts[-1])<100:
                prefix='.'.join(left_parts[:-1]);targets=[(prefix+'.' if prefix else '')+str(n) for n in range(int(left_parts[-1]),int(right_parts[-1])+1)]
            else:unsupported='UNSUPPORTED_OR_AMBIGUOUS_RANGE'
        elif plural:
            while True:
                more=re.match(rf'\s*(?:,\s*(?:and\s+)?|and\s+)({NUMBER}|{ROMAN}|[A-Z])(?!\w|\.\d)',source_text[end:],re.I)
                if not more:break
                targets.append(more[1]);end+=more.end()
        if re.match(r'(?:\.\.|\.[0-9]|\(|/)',source_text[end:]):unsupported='MALFORMED_OR_UNSUPPORTED_IDENTIFIER'
        if re.match(r'\s*(?:[-–—]\s*\d|or\s+\d|through\s+\S)',source_text[end:],re.I):unsupported='UNSUPPORTED_REFERENCE_CONTINUATION'
        if re.match(r'\s+of\s+(?:the\s+)?(?:master|other|separate)\s+agreement\b',source_text[end:],re.I):unsupported='EXTERNAL_DOCUMENT_SCOPE'
        direction=(match['pre'] or '').lower()
        post=re.match(r'[ \t,;:()]*\b(above|below)\b(?:[ \t]*\))?',source_text[end:],re.I)
        if post:
            if direction and direction!=post[1].lower():unsupported='CONFLICTING_DIRECTION_WORDS'
            direction=post[1].lower();end+=post.end()
        prefix=source_text[max(0,start-45):start]
        preceding=re.search(r'immediately\s+preceding\s*$',prefix,re.I)
        if preceding:direction='immediately_preceding';start=max(0,match.start()-45)+preceding.start()
        critical=re.search(r'(?:pursuant\s+to|subject\s+to|as\s+defined\s+in)\s*$',source_text[max(0,start-35):start],re.I)
        if critical:start=max(0,start-35)+critical.start()
        owner=next((s for s in reversed(doc.sections) if s['heading_start']<=start),None)
        exact_links=[l['clause_id'] for l in links if l['char_start']<=start<l['char_end']]
        clause_id=exact_links[0] if exact_links else owner['clause_id'] if owner else f'{doc.doc_id}:source:0'
        if typ in ['EXHIBIT','SCHEDULE']:targets=[x.upper() for x in targets]
        if len(doc.references)+len(targets)>MAX_REFERENCES:
            doc.reviews.append(dict(status='REVIEW_REQUIRED',reason='PARSE_LIMIT',detail='Reference inventory truncated; target resolution abstains.'))
            break
        # Roman section identities remain explicit unsupported evidence for the experimental graph.
        for target in targets:
            doc.references.append(dict(reference_uid=f'{doc.doc_id}:reference:{len(doc.references)}',target_type=typ,
                target_id=target,target_key=key(target),char_start=start,char_end=end,text=source_text[start:end],
                source_clause_id=clause_id,source_section_uid=owner['section_uid'] if owner else None,
                direction=direction or 'nondirectional',syntax_issue=unsupported,
                coordinate_space=coordinate_space,group_id=f'{doc.doc_id}:citation:{match.start()}'))
    # A recognized reference keyword with unsupported identifier syntax must not vanish.
    reference_spans=sorted((r['char_start'],r['char_end']) for r in doc.references)
    reference_starts=[s[0] for s in reference_spans]
    for match in re.finditer(r'\b(?P<kind>Sections?|Articles?|Exhibits?|Schedules?)\b(?:\s+(?P<token>\S+))?',source_text,re.I):
        if in_heading_identifier(match.start()):continue
        index=bisect_right(reference_starts,match.start())-1
        if index>=0 and match.start()<reference_spans[index][1]:continue
        # A keyword used as an ordinary heading-title noun is not an identifier citation
        # (e.g. "Schedule of Fees"). Explicit identifiers within titles remain detectable.
        heading_index=bisect_right(heading_starts,match.start())-1
        if heading_index>=0:
            heading=doc.sections[heading_index]
            if heading['title_start']<=match.start()<heading['title_end'] and (match['token'] or '').casefold() in ['of','for','and','or','to']:continue
        if len(doc.references)>=MAX_REFERENCES:
            if not any(r.get('reason')=='PARSE_LIMIT' for r in doc.reviews):doc.reviews.append(dict(status='REVIEW_REQUIRED',reason='PARSE_LIMIT',detail='Unsupported reference inventory truncated; target resolution abstains.'))
            break
        owner=next((s for s in reversed(doc.sections) if s['heading_start']<=match.start()),None)
        doc.references.append(dict(reference_uid='',target_type=namespace(match['kind']),target_id=match['token'] or '?',
            target_key=key(match['token'] or '?'),char_start=match.start(),char_end=match.end(),text=match[0],
            source_clause_id=owner['clause_id'] if owner else f'{doc.doc_id}:source:0',
            source_section_uid=owner['section_uid'] if owner else None,direction='nondirectional',
            syntax_issue='UNSUPPORTED_IDENTIFIER',coordinate_space=coordinate_space,group_id=f'{doc.doc_id}:citation:{match.start()}'))
    doc.references.sort(key=lambda r:(r['char_start'],r['char_end']))
    for i,ref in enumerate(doc.references):ref['reference_uid']=f'{doc.doc_id}:reference:{i}'
    doc._uncertain_headings=uncertain
    return doc
