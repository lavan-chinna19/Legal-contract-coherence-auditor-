"""Author-controlled slot labels, frozen before implementation; no model label generation."""
from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent

def canonical(s):return ' '.join(s.lower().split()) if s else None

def build(split):
    # Families differ in grammar and IDs across splits, not merely shuffled documents.
    dev=split=='development';actor='Buyer' if dev else 'Purchaser';other='Seller' if dev else 'Vendor'
    obj='Invoice Alpha' if dev else 'Invoice Cedar';target='Report Beta' if dev else 'Report Juniper'
    trigger='receipt of Invoice Alpha' if dev else 'receipt of Invoice Cedar'
    defaults=dict(actor=actor,action='PAY',object=obj,recipient=None,trigger=trigger,event_instance=obj,
        timing='within 10 calendar days',condition=None)
    cases=[]
    def clause(s,side,style=None):
        if s.get('literal'):return s['literal']
        verb={'PAY':'pay' if side==0 else 'remit','DELIVER':'deliver' if side==0 else 'provide','NOTIFY':'notify' if side==0 else 'inform'}[s['action']]
        modal='shall' if dev else ('is required to' if side==0 else 'must')
        actor_text=s.get('surface_actor',s['actor']) or ''
        if style=='passive':body=f"{s['object']} must be paid by {s['actor']}"
        else:body=f"{actor_text} {modal} {verb} {s['object']}".strip()
        if s.get('recipient'):body+=' to '+s['recipient']
        if s.get('timing'):body+=' '+s['timing']
        if s.get('trigger'):body+=' after '+s['trigger']
        if s.get('condition'):body='If '+s['condition']+', '+body
        if s.get('suffix'):body+=' '+s['suffix']
        return body+'.'
    def expected(s):
        return {k:canonical(s.get(k)) if k!='action' else s.get(k) for k in ['actor','action','object','recipient','trigger','event_instance']}
    def add(name,label,binary,change=None,leftchange=None,style=None,note='',provisional=False):
        left=dict(defaults,**(leftchange or {}));right=dict(defaults,**(change or {}))
        lt=clause(left,0,style);rt=clause(right,1,style)
        ids=('1','2') if dev else ('7','9')
        text=f'Section {ids[0]}. Duty\n{lt}\n\nSection {ids[1]}. Duty\n{rt}'
        cases.append(dict(case_id=f'{split}_{name}',family_id=f'{split}_{name}',split=split,text=text,
            gold_state=label,gold_match=binary,mechanical_rule=note or name,
            label_provenance='PROVISIONAL_INTERPRETATION' if provisional else 'AUTHOR_CONSTRUCTED_MECHANICAL',
            independently_adjudicated=False,left_section=ids[0],right_section=ids[1],left_index=0,right_index=0,
            expected_left=[expected(left)],expected_right=[expected(right)]))
    add('synonym_identity','MATCHED',True,note='Explicit same party, payment action, named invoice occurrence and receipt trigger; controlled remit/pay paraphrase')
    add('different_actor','DIFFERENT',False,dict(actor=other))
    add('different_action','DIFFERENT',False,dict(action='DELIVER'))
    add('different_instance','DIFFERENT',False,dict(object=target,event_instance=target))
    add('different_trigger','UNCERTAIN',None,dict(trigger='acceptance of '+obj),note='Trigger equivalence not established, not labelled legal conflict')
    add('one_missing_trigger','UNCERTAIN',None,dict(trigger=None))
    add('same_condition','MATCHED',True,dict(condition='approved'),dict(condition='approved'))
    add('different_condition','UNCERTAIN',None,dict(condition='approved'),dict(condition='requested'))
    add('one_condition','UNCERTAIN',None,dict(condition='approved'))
    add('exception','UNCERTAIN',None,dict(suffix='unless disputed'))
    add('pronoun','UNCERTAIN',None,dict(actor=None,surface_actor='It'))
    add('missing_actor','UNCERTAIN',None,dict(actor=None))
    add('same_recipient','MATCHED',True,dict(recipient=other),dict(recipient=other))
    add('different_recipient','DIFFERENT',False,dict(recipient='Agent'),dict(recipient=other))
    add('one_missing_recipient','UNCERTAIN',None,dict(recipient=other))
    add('no_timing','MATCHED',True,dict(timing=None),dict(timing=None))
    add('different_deadlines','MATCHED',True,dict(timing='within 20 calendar days'),note='Different deadlines do not change identity; binding never classifies temporal conflict')
    add('same_recurring_type','UNCERTAIN',None,dict(suffix='each month'),dict(suffix='each month'),note='Same type, no uniquely established occurrence')
    add('different_object_same_party','DIFFERENT',False,dict(object='Invoice Bravo' if dev else 'Invoice Spruce',event_instance='Invoice Bravo' if dev else 'Invoice Spruce'))
    add('generic_object','UNCERTAIN',None,dict(object='the invoice',event_instance=None),dict(object='the invoice',event_instance=None))
    add('unsupported_action','UNSUPPORTED',None,dict(action=None,literal=f'{actor} shall reconcile the accounts.'))
    add('complex_semantics',None,None,dict(literal=f'{actor} will perform reasonably necessary acts notwithstanding prior practice.'),provisional=True)
    # Multiple independently explicit modal subjects in a clause; select the second obligation.
    add('multiple_modals','MATCHED',True)
    c=cases[-1];extra=dict(defaults,actor=other,action='DELIVER',object=target,event_instance=target,trigger=None,timing=None)
    first=clause(extra,0);c['text']=c['text'].replace(clause(defaults,0),first+' '+clause(defaults,0),1)
    c['left_index']=1;c['expected_left']=[expected(extra),expected(defaults)]
    # Exact reference resolves an object only, never imports the target's actor or conditions.
    add('reference_object','MATCHED',True,dict(trigger=None),dict(trigger=None))
    c=cases[-1];ref=c['left_section'];c['text']=c['text'].replace(obj,'the obligation in Section '+ref,1 if False else 0) if False else c['text']
    # Rewrite only right object to the unique left section, retaining its explicit party/action.
    start=c['text'].index('Section '+c['right_section']+'.')
    c['text']=c['text'][:start]+c['text'][start:].replace(obj,'the obligation in Section '+ref,1)
    c['expected_right'][0]['object']=canonical(obj);c['expected_right'][0]['event_instance']=canonical(obj)
    add('missing_reference','UNCERTAIN',None,dict(object='the obligation in Section 99',event_instance=None,trigger=None),dict(trigger=None))
    add('ambiguous_reference','UNCERTAIN',None,dict(object='the obligation in Section 5',event_instance=None,trigger=None),dict(trigger=None))
    c=cases[-1];c['text']+='\nSection 5. Extra\n'+clause(defaults,0)+'\nSection 5. Duplicate\n'+clause(defaults,0)
    add('different_scope','DIFFERENT',False)
    c=cases[-1];c['text']=c['text'].replace('\n'+clause(defaults,0),'\nFor Agreement A, '+clause(defaults,0)).replace('\n'+clause(defaults,1),'\nFor Agreement B, '+clause(defaults,1))
    add('different_phase','DIFFERENT',False)
    c=cases[-1];c['text']=c['text'].replace('\n'+clause(defaults,0),'\nFor Phase 1, '+clause(defaults,0)).replace('\n'+clause(defaults,1),'\nFor Phase 2, '+clause(defaults,1))
    if not dev:
        # Known mechanically labelled grammar expansion withheld from implementation tuning.
        add('passive_identity','MATCHED',True,style='passive',note='Explicit by-agent passive grammar, same named invoice and trigger; no inference needed by annotator')
        add('coordinated_subject','DIFFERENT',False,dict(actor='Purchaser and Vendor'),note='Explicit joint subject differs from sole subject; unsupported grammar may abstain')
    return cases

def main():
    files=[]
    for split in ['development','evaluation']:
        p=BASE/(split+'.json')
        if p.exists():raise FileExistsError('Frozen benchmark must not be overwritten')
        p.write_text(json.dumps(dict(split=split,independent_annotation_count=0,cases=build(split)),indent=2)+'\n',encoding='utf8');files.append(p)
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files+[BASE/'PROTOCOL.md',Path(__file__)]}
    (BASE/'benchmark_frozen_manifest.json').write_text(json.dumps(dict(before_implementation=True,files=manifest,policy='Evaluation split not executed until source freeze. Distinct document/template families; author-controlled synthetic labels, not independent legal holdout.'),indent=2)+'\n',encoding='utf8')
    dev=build('development');ev=build('evaluation')
    assert not {x['family_id'] for x in dev}&{x['family_id'] for x in ev}
    assert not {x['text'] for x in dev}&{x['text'] for x in ev}
    print('Frozen development/evaluation counts:',len(dev),len(ev));print('Do not inspect or execute evaluation predictions before source freeze.')

if __name__=='__main__':main()
