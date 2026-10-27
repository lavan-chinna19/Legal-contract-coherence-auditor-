"""Experimental positional graph over the shared source-preserving inventory.

Findings mean explicit textual position conflict, never general legal invalidity.
Legacy clause-local fields remain; absolute source spans specify their coordinate space.
"""
import re
from src.structure import parse_contract, resolve_references

def detect_dependencies(clauses: list[dict], *, source_text=None, structure=None) -> dict:
    structure=structure or parse_contract(clauses,source_text=source_text)
    resolutions=resolve_references(structure)
    edges=[];findings=[];reviews=list(structure.reviews)
    links={l['clause_id']:l for l in structure.clause_links}
    order={c['clause_id'] if isinstance(c,dict) else c.clause_id:i for i,c in enumerate(clauses)}
    def position(clause_id,start):
        return [order.get(clause_id,0),start-links.get(clause_id,{}).get('char_start',0)]
    for r in resolutions:
        if r['target_type']!='SECTION':continue
        local_start=r['char_start']-links.get(r['source_clause_id'],{}).get('char_start',0)
        edge=dict(source_clause_id=r['source_clause_id'],target_section_id=r['target_id'],reference=r['text'],
            char_start=local_start,char_end=local_start+len(r['text']),direction=r['direction'],
            source_position=position(r['source_clause_id'],r['char_start']),
            source_char_start=r['char_start'],source_char_end=r['char_end'],
            coordinate_space=structure.coordinate_space,reference_uid=r['reference_uid'],
            resolution_status=r['resolution_status'],
            clause_offset_mapping=links.get(r['source_clause_id'],{}).get('mapping','SOURCE_REGION_ONLY'))
        target=r['target'];reason=r['reason']
        if r['resolution_status']!='RESOLVED' or not re.match(r'^\d',r['target_id']):
            edge.update(status='REVIEW_REQUIRED',reason=reason if r['resolution_status']!='RESOLVED' else 'Roman section directions are outside numeric graph scope; abstained.')
            reviews.append(edge)
        else:
            edge['target']=dict(clause_id=target['clause_id'],section_id=target['identity'],
                position=position(target['clause_id'],target['heading_start']),excerpt=target['heading_text'],
                source_char_start=target['heading_start'],source_char_end=target['heading_end'],
                coordinate_space=structure.coordinate_space,section_uid=target['section_uid'])
            valid=True
            if r['direction']=='above':valid=target['heading_start']<r['char_start']
            elif r['direction']=='below':valid=target['heading_start']>r['char_start']
            elif r['direction']=='immediately_preceding':
                headings=[s for s in structure.sections if s['target_type']=='SECTION']
                current=next((s for s in headings if s['section_uid']==r['source_section_uid']),None)
                previous=headings[headings.index(current)-1] if current in headings and headings.index(current)>0 else None
                if not previous:
                    edge.update(status='REVIEW_REQUIRED',reason='Immediate predecessor cannot be established; abstained.')
                    reviews.append(edge);edges.append(edge);continue
                valid=previous['section_uid']==target['section_uid']
            edge.update(status='SATISFIED' if valid else 'VERIFIED_TEXTUAL_CONFLICT',
                reason='Explicit target location matches the reference.' if valid else "Explicit directional reference contradicts the target's location.")
            if not valid:findings.append(edge)
        edges.append(edge)
    for unit in structure.units:
        body=unit['text'];heading=next((s for s in structure.sections if s['heading_start']==unit['char_start']),None)
        if heading:body=body[heading['heading_end']-unit['char_start']:]
        vague=re.match(r'\s*(?:notwithstanding\s+)?(?:the\s+)?(?:foregoing|preceding|above-mentioned)\b',body,re.I)
        if vague:
            reviews.append(dict(source_clause_id=heading['clause_id'] if heading else unit['unit_id'],
                reference=vague[0].strip(),status='REVIEW_REQUIRED',reason='Boundary antecedent not explicit; no guessed dependency.',
                coordinate_space=structure.coordinate_space))
    return dict(experimental=True,version='source-dependency-graph-v2',edges=edges,findings=findings,reviews=reviews,
        status='FINDING' if findings else 'REVIEW_REQUIRED' if reviews else 'NO_FINDINGS',
        coordinate_space=structure.coordinate_space,parser_version=structure.version,
        scope='Deterministic textual direction only; independent scientific validation pending. Ensemble scores unchanged.')
