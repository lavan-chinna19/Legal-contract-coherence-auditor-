"""Separate annotation corrections and descriptive public-source failure inspection."""
from pathlib import Path
from collections import Counter
import json,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))

def dump(p,v):
    if p.exists():raise FileExistsError('Retain existing evidence')
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def main():
    from src.structure import parse_contract
    from src.obligations.binding import MODAL
    run=BASE/'results/comparison_v2'
    synthetic=[json.loads(l) for l in (run/'paired_synthetic.jsonl').open(encoding='utf8')]
    overlay=[];field_results=[];focused_fields=[]
    for stratum in ['EXPOSED_ORIGINAL_DEVELOPMENT','EXPOSED_ORIGINAL_EVALUATION']:
        rows=[r for r in synthetic if r['stratum']==stratum]
        stats={side:Counter() for side in ['old','new']}
        for r in rows:
            c=r['case']
            if c['label_provenance']=='PROVISIONAL_INTERPRETATION':continue
            for side in ['left','right']:
                for i,gold in enumerate(c['expected_'+side]):
                    corrected=gold['event_instance']
                    if c['case_id'].endswith('_same_recurring_type'):
                        corrected=None;overlay.append(dict(case_id=c['case_id'],side=side,index=i,field='event_instance',original=gold['event_instance'],corrected=None,
                            reason='Each-month language establishes a recurring event type, not a unique occurrence; no pair label changes.',provenance='Explicit mechanical annotation erratum, not qualified legal review'))
                    for version in ['old','new']:
                        observed=[x for x in r[version]['result']['records'] if x['section_identity']==c[side+'_section']]
                        rec=observed[i] if i<len(observed) else {}
                        s=stats[version];s['field_cells']+=1
                        s['raw_event_exact']+=rec.get('event_instance')==gold['event_instance']
                        s['corrected_overlay_event_exact']+=rec.get('event_instance')==corrected
                        s['actor_exact']+=rec.get('actor')==gold['actor']
        field_results.append(dict(stratum=stratum,results={k:dict(v) for k,v in stats.items()}))
    for r in synthetic:
        if r['stratum']!='FOCUSED_AUTHORED_DEVELOPMENT':continue
        c=r['case'];out=r['new']['result'];records=out['records']
        focused_fields.append(dict(case_id=c['case_id'],
            actors_correct=len(records)==2 and records[0]['actors']==c['actors_left'] and records[1]['actors']==c['actors_right'],
            actor_action_relationship_correct=r['new']['selected'].get('actor_action_relationship')==c['expected_actor_action_relationship']))
    dump(BASE/'annotation_overlay.json',dict(original_labels_changed=False,original_predictions_changed=False,pair_labels_changed=False,corrections=overlay,field_results=field_results,focused_field_checks=focused_fields))
    public=[]
    for line in (run/'paired_public.jsonl').open(encoding='utf8'):
        pair=json.loads(line);old,new=pair['old'],pair['new'];text=new['input_text'];result=new['result']
        structure=parse_contract(source_text=text);missing=[]
        for m in MODAL.finditer(text):
            if any(r['char_start']<=m.start()<r['char_end'] for r in result['records']):continue
            heading=next((s for s in structure.sections if s['heading_start']<=m.start()<s['heading_end']),None)
            start=max(0,m.start()-80);end=min(len(text),m.end()+100)
            missing.append(dict(char_start=start,char_end=end,text=text[start:end],modal_start=m.start(),
                category='PARSING_FAILURE_INLINE_BODY_SKIPPED' if heading else 'PARSING_FAILURE_OTHER',
                section_uid=heading['section_uid'] if heading else None,
                note='Lexical modal cue only; not independently labelled as an obligation or defect.'))
        indexed={r['record_id']:r for r in result['records']};candidates=[];categories=Counter()
        for p in result['pairs']:
            a,b=indexed[p['left_id']],indexed[p['right_id']]
            if 'SOURCE_MARKUP_UNSUPPORTED' in result['issues']:category='UNSUPPORTED_MARKUP'
            elif a['unsupported'] or b['unsupported']:category='UNSUPPORTED_GRAMMAR_OR_ACTION'
            elif p['status']=='UNCERTAIN':category='UNESTABLISHED_BINDING_OR_MEANING'
            else:category='SUPPORTED_TEXTUAL_BINDING_ONLY'
            categories[category]+=1
            if len(candidates)<3:
                candidates.append(dict(status=p['status'],category=category,reasons=p['reasons'],
                    evidence=[dict(record_id=r['record_id'],char_start=r['char_start'],char_end=r['char_end'],text=r['raw_text'],
                        actor=r['actor'],action=r['action'],unsupported=r['unsupported'],uncertainty=r['uncertainty']) for r in [a,b]],qualified_legal_label=None))
        public.append(dict(path=new['path'],source_url=new['source_url'],entity_name=new['entity_name'],accession=new['accession'],exhibit=new['exhibit'],filing_date=new['filing_date'],
            mode=new['mode'],raw_sha256=new['raw_sha256'],extraction_sha256=new['input_sha256'],coordinate_note=new['coordinate_note'],
            old_record_count=old['result']['record_count'],new_record_count=result['record_count'],old_pair_counts=old['result']['pair_counts'],new_pair_counts=result['pair_counts'],
            modal_cues=len(list(MODAL.finditer(text))),unrepresented_modal_cues=len(missing),
            inline_heading_cues_skipped=sum(m['category']=='PARSING_FAILURE_INLINE_BODY_SKIPPED' for m in missing),
            candidate_pair_examples=candidates,missing_modal_examples=missing[:2],decision_categories=dict(categories),
            expert_labels=0,legal_accuracy='NOT_ASSESSED'))
    dump(BASE/'public_applicability_audit.json',dict(selection='Same three substantive cached SEC exhibits as Phase 4A; no new selection based on successful predictions',
        observations=public,parser_bug_scope='Binding consumer skips complete heading lines that include inline body text. Not repaired: outside the three specified repairs; Phase 2 parser unchanged.',
        ambiguity_note='Unresolved conditions/instances are meaning or evidence uncertainty. Unsupported actions are grammar limits. Skipped source text is an implementation parsing bug; these categories are not legal defect labels.'))
    print(json.dumps(dict(annotation_corrections=len(overlay),fields=field_results,focused_actor_checks=sum(x['actors_correct'] for x in focused_fields),
        public=[dict(path=r['path'],mode=r['mode'],pairs=r['new_pair_counts'],modal_cues=r['modal_cues'],skipped_inline=r['inline_heading_cues_skipped']) for r in public]),indent=2))

if __name__=='__main__':main()
