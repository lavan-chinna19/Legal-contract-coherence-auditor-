"""Build a fixed, detector-aware DEVELOPMENT corpus. No model imports or predictions.
Existing files are never overwritten; use --output with a new directory to reproduce.
"""
from pathlib import Path
import argparse,ast,hashlib,json
from datetime import date

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
MECH='MECHANICALLY_VERIFIABLE_SYNTHETIC'
PROV='PROVISIONAL_HUMAN_REVIEW'

def build(output):
    output.mkdir(parents=True,exist_ok=True)
    if (output/'corpus.json').exists():raise FileExistsError('Frozen corpus already exists; choose a new --output directory.')
    cases=[]
    def add(cid,family,clauses,*,kind=MECH,decls=(),refs=(),date_scopes=None,range_pairs=None,review=None,notes='',stratum='canonical',labels=None,origin=None):
        # Labels come from author-supplied literal anchors and primitive arithmetic,
        # not production detector regexes, predictions or neural scores.
        declarations=[]
        for identity,index,anchor in decls:
            offset=clauses[index].index(anchor)
            declarations.append({'identity':identity,'clause_index':index,'anchor':anchor,'position':[index,offset]})
        references=[];presence=[];direction=[]
        for target,index,anchor,relation in refs:
            pos=[index,clauses[index].index(anchor)]
            matches=[d for d in declarations if d['identity']==target]
            presence.append(not matches)
            ref={'target':target,'clause_index':index,'anchor':anchor,'relation':relation,'source_position':pos,'target_count':len(matches)}
            if len(matches)==1:
                if relation=='above':bad=not(matches[0]['position']<pos)
                elif relation=='below':bad=not(matches[0]['position']>pos)
                elif relation=='immediately_preceding':
                    heads=sorted(declarations,key=lambda d:d['position']);current=[d for d in heads if d['position']<=pos]
                    previous=heads[heads.index(current[-1])-1] if current and heads.index(current[-1])>0 else None
                    bad=previous is not matches[0]
                else:bad=False
                ref['directional_conflict']=bad;direction.append(bad)
            references.append(ref)
        task_labels={}
        if refs:task_labels['reference_presence']=any(presence)
        if refs and all(r['target_count']==1 for r in references) and stratum!='unsupported_identity':task_labels['directional_position']=any(direction)
        if date_scopes is not None:
            task_labels['date_chronology']=any(date.fromisoformat(a)>date.fromisoformat(b) for scope,a,b in date_scopes)
        if range_pairs is not None:task_labels['date_chronology']=any(date.fromisoformat(a)>date.fromisoformat(b) for a,b in range_pairs)
        if labels:task_labels.update(labels)
        item={'case_id':cid,'family':family,'split':'EXPOSED_DEVELOPMENT','label_provenance':kind,'independently_adjudicated':False,
              'source_document':f'cases/{cid}.txt','clauses':clauses,'expected_authored_units':len(clauses),'task_labels':task_labels,
              'facts':{'declarations':declarations,'references':references,'date_scopes':date_scopes,'range_pairs':range_pairs},
              'expected_graph_review':review,'stratum':stratum,'interpretation':notes,'origin':origin or 'Agent-authored controlled synthetic text; no expert legal review.'}
        cases.append(item)
    # Explicit-reference facts: scope is textual location/existence, never legal validity.
    a='Section 1. Definitions\nServices means the example work.'
    b='Section 2. Payment\nPayment follows Section 1 above.'
    add('R01','valid_directional',[a,b],decls=[('1',0,'Section 1.'),('2',1,'Section 2.')],refs=[('1',1,'Section 1 above','above')])
    add('R02','incorrect_directional',[b,a],decls=[('2',0,'Section 2.'),('1',1,'Section 1.')],refs=[('1',0,'Section 1 above','above')])
    c='Section 1. Payment\nPayment follows Section 2 below.';d='Section 2. Services\nThe services are defined here.'
    add('R03','valid_directional',[c,d],decls=[('1',0,'Section 1.'),('2',1,'Section 2.')],refs=[('2',0,'Section 2 below','below')])
    add('R04','incorrect_directional',[d,c],decls=[('2',0,'Section 2.'),('1',1,'Section 1.')],refs=[('2',1,'Section 2 below','below')])
    for cid,clauses,index,target in [('R05',[a,'Section 2. Payment\nSee Section 1.'],1,'1'),('R06',['Section 2. Payment\nSee Section 1.',a],0,'1')]:
        idx=0 if index==1 else 1
        add(cid,'valid_nondirectional',clauses,decls=[('1',idx,'Section 1.'),('2',index,'Section 2.')],refs=[(target,index,'Section 1.','nondirectional')],notes='Moving an intact non-directional reference does not create a location defect.')
    add('R07','valid_nondirectional',['Section 3. Notices\nNotices must be written.',a,'Section 2. Payment\nSee Section 1.'],decls=[('3',0,'Section 3.'),('1',1,'Section 1.'),('2',2,'Section 2.')],refs=[('1',2,'Section 1.','nondirectional')])
    dec='Section 1.2. Services\nThe services are stated here.'
    add('R08','valid_directional',[dec,'Section 2. Payment\nSee Section 1.2 above.'],decls=[('1.2',0,'Section 1.2.'),('2',1,'Section 2.')],refs=[('1.2',1,'Section 1.2 above','above')])
    add('R09','incorrect_directional',['Section 2. Payment\nSee Section 1.2 above.',dec],decls=[('2',0,'Section 2.'),('1.2',1,'Section 1.2.')],refs=[('1.2',0,'Section 1.2 above','above')])
    add('R10','missing_targets',['Section 1. Payment\nPayment is governed by Section 9.'],decls=[('1',0,'Section 1.')],refs=[('9',0,'Section 9.','nondirectional')],review=True)
    add('R11','missing_targets',['Section 1. Payment\nSection 9 above applies to payment.'],decls=[('1',0,'Section 1.')],refs=[('9',0,'Section 9 above','above')],review=True,stratum='challenge',notes='A sentence-start citation is not a declaration; no actual Section 9 heading exists.')
    add('R12','missing_targets',['Section 1. Payment\nSection 9 shall apply to the invoice.'],decls=[('1',0,'Section 1.')],refs=[('9',0,'Section 9 shall','nondirectional')],review=True,stratum='challenge')
    add('R13','duplicate_targets',[a,'Section 1. Different definition\nGoods means example goods.','Section 2. Payment\nSee Section 1 above.'],decls=[('1',0,'Section 1.'),('1',1,'Section 1.'),('2',2,'Section 2.')],refs=[('1',2,'Section 1 above','above')],review=True,notes='Target exists but intended identity is ambiguous. No directional binary label is assigned.')
    add('R14','duplicate_targets',['Section 1. First meaning\nFirst text.\nSection 1. Second meaning\nSecond text.','Section 2. Payment\nSee Section 1 above.'],decls=[('1',0,'Section 1. First'),('1',0,'Section 1. Second'),('2',1,'Section 2.')],refs=[('1',1,'Section 1 above','above')],review=True)
    add('R15','missing_targets',['Section 1.1. Meaning\nThe numbered identity is exactly 1.1.','Section 2. Payment\nPayment is governed by Section 1.01.'],decls=[('1.1',0,'Section 1.1.'),('2',1,'Section 2.')],refs=[('1.01',1,'Section 1.01.','nondirectional')],review=True,stratum='challenge',notes='Controlled namespace uses exact identity strings; equivalence of 1.01 and 1.1 is not assumed. Policy-sensitive challenge, not universal legal numbering guidance.')
    add('R16','missing_targets',['Section 1.1(a). Services\nOnly subclause (a) is declared.','Section 2. Payment\nSee Section 1.1(b).'],decls=[('1.1(a)',0,'Section 1.1(a).'),('2',1,'Section 2.')],refs=[('1.1(b)',1,'Section 1.1(b).','nondirectional')],review=True,stratum='challenge')
    add('R17','valid_directional',['Section 1.1(a). Services\nSubclause text.','Section 2. Payment\nSee Section 1.1(a) above.'],decls=[('1.1(a)',0,'Section 1.1(a).'),('2',1,'Section 2.')],refs=[('1.1(a)',1,'Section 1.1(a) above','above')])
    for cid,clauses,idx in [('R18',['Section III. Meaning\nDefined text.','Section 2. Payment\nSee Section III above.'],1),('R19',['Section 2. Payment\nSee Section III above.','Section III. Meaning\nDefined text.'],0)]:
        add(cid,'unsupported_roman',clauses,decls=[('III',1-idx,'Section III.'),('2',idx,'Section 2.')],refs=[('III',idx,'Section III above','above')],review=True,stratum='unsupported_identity',notes='Roman graph identities are outside declared graph scope; expected conservative abstention, not a directional accuracy denominator.')
    add('R20','vague_antecedent',[a,'Section 2. Qualification\nThe foregoing obligation applies here.'],kind=PROV,review=True,notes='Antecedent resolution requires review. This is not an independently established legal defect.')
    add('R21','valid_directional',[a,'Section 2. Payment\nPayment follows the immediately preceding Section 1.'],decls=[('1',0,'Section 1.'),('2',1,'Section 2.')],refs=[('1',1,'Section 1.','immediately_preceding')])
    add('R22','incorrect_directional',[a,'Section 2. Goods\nGoods are specified here.','Section 3. Payment\nPayment follows the immediately preceding Section 1.'],decls=[('1',0,'Section 1.'),('2',1,'Section 2.'),('3',2,'Section 3.')],refs=[('1',2,'Section 1.','immediately_preceding')])
    add('R23','incorrect_directional',['Section 2. Payment\nSee Section 1, above.',a],decls=[('2',0,'Section 2.'),('1',1,'Section 1.')],refs=[('1',0,'Section 1, above','above')],stratum='challenge',notes='Punctuation variation retains the explicit above relationship.')
    add('R24','incorrect_directional',['Section 2. Payment\nSee above Section 1 for the definition.',a],decls=[('2',0,'Section 2.'),('1',1,'Section 1.')],refs=[('1',0,'above Section 1','above')],stratum='challenge')
    add('R25','missing_targets',['Section 1. Payment\nPayment follows Sections 8 and 9.'],decls=[('1',0,'Section 1.')],refs=[('8',0,'Sections 8 and 9','nondirectional'),('9',0,'Sections 8 and 9','nondirectional')],review=True,stratum='challenge')
    add('R26','valid_directional',['Section 1. Definition\nThe definition stated in Section 1 above applies throughout.'],decls=[('1',0,'Section 1. Definition')],refs=[('1',0,'Section 1 above','above')],notes='Same-clause earlier declaration is valid; do not use clause indices alone as position.')
    add('R27','missing_exhibit',['Section 1. Scope\nSpecifications follow Exhibit Z.'],decls=[('1',0,'Section 1.')],refs=[('EXHIBIT:Z',0,'Exhibit Z.','nondirectional')],review=None,notes='Exhibit resolution belongs to the reference checker; graph does not claim exhibit support.')
    add('R28','missing_exhibit',['Section 1. Scope\nExhibit Z supplies the specifications.'],decls=[('1',0,'Section 1.')],refs=[('EXHIBIT:Z',0,'Exhibit Z supplies','nondirectional')],stratum='challenge',notes='Sentence-start exhibit citation is not an attached exhibit heading.')
    # Date labels express author-specified within-scope arithmetic, not legal defect validity.
    for cid,start,end,fmt in [('T01','2026-01-01','2026-12-31','iso'),('T02','2026-12-31','2026-01-01','iso'),('T03','2026-01-01','2026-12-31','words'),('T04','2026-12-31','2026-01-01','words')]:
        def display(v):return date.fromisoformat(v).strftime('%B %d, %Y') if fmt=='words' else v
        add(cid,'date_term',[f'Section 1. Term\nThe Effective Date is {display(start)}.',f'Section 2. End\nThe Termination Date is {display(end)}.'],date_scopes=[('one_agreement',start,end)])
    for cid,start,end in [('T05','2026-01-01','2026-12-31'),('T06','2026-12-31','2026-01-01')]:
        add(cid,'date_range',[f'Section 1. Service period\nService runs from {start} to {end}.'],range_pairs=[(start,end)])
    add('T07','date_independent_events',['Section 1. Archive\nThe archive records December 31, 2026 and October 1, 2026 as independent review dates, without an ordered service interval.'],range_pairs=[])
    add('T08','date_independent_events',['Section 1. Archive\nThe record dated December 31, 2026 relates to a separate historical entry dated January 1, 2026.'],range_pairs=[],stratum='challenge',notes='The substring "to" is not evidence of an ordered date range.')
    add('T09','date_payment',['Section 1. Effective date\nThe Effective Date is 2026-06-01.','Section 2. Payment\nPayment due on 2026-05-01.'],date_scopes=[('payment_before_effective_predicate','2026-06-01','2026-05-01')],notes='Task is the stated arithmetic predicate only, not legal invalidity of prepayments.')
    add('T10','date_notice',['Section 1. End\nThe Expiration Date is 2026-06-01.','Section 2. Notice\nNotice required by 2026-07-01.'],date_scopes=[('notice_before_end_predicate','2026-07-01','2026-06-01')])
    add('T11','ambiguous_date_format',['Section 1. Term\nThe Effective Date is 03/04/2026.','Section 2. End\nThe Termination Date is 04/03/2026.'],kind=PROV,notes='No locale specified: month/day interpretation is ambiguous. No binary chronology label.')
    add('T12','date_separate_scopes',['Section 1. Agreement A\nFor Agreement A, the Effective Date is 2026-06-01.','Section 2. Agreement A\nFor Agreement A, the Termination Date is 2026-12-31.','Section 3. Agreement B\nFor Agreement B, the Effective Date is 2026-01-01.','Section 4. Agreement B\nFor Agreement B, the Termination Date is 2026-03-01.'],date_scopes=[('A','2026-06-01','2026-12-31'),('B','2026-01-01','2026-03-01')],stratum='challenge')
    add('T13','date_linewrap',['Section 1. Term\nThe Effective Date is\n2026-06-01.\nThe Termination Date is\n2026-05-01.'],date_scopes=[('one_agreement','2026-06-01','2026-05-01')],stratum='challenge')
    add('T14','invalid_calendar_date',['Section 1. Term\nThe Effective Date is February 30, 2026.'],labels={'calendar_invalid':True},notes='Calendar-invalid date is mechanically known; calendar validity is a separate unsupported detector task, not chronology F1.')
    add('T15','intentional_prepayment',['Section 1. Effective\nThe Effective Date is 2026-06-01.','Section 2. Deposit\nPayment due on 2026-05-01 is an expressly permitted refundable advance deposit before effectiveness.'],kind=PROV,notes='Potential legal false alarm if an arithmetic warning is treated as a defect. No expert legal label assigned.')
    add('T16','date_far_role',['Section 1. Term\nThe Effective Date is '+('specified for the sole synthetic agreement with no other date roles in this passage. '*2)+'2026-06-01.','Section 2. End\nThe Termination Date is 2026-05-01.'],date_scopes=[('one_agreement','2026-06-01','2026-05-01')],stratum='challenge')
    add('T17','date_trailing_role',['Section 1. Term\n2026-12-31 is the Effective Date.','Section 2. End\n2026-01-01 is the Termination Date.'],date_scopes=[('one_agreement','2026-12-31','2026-01-01')],stratum='challenge')
    # Segmentation/extraction challenge predicates and noncontradiction controls.
    add('S01','segmentation_plain_paragraphs',['The buyer shall pay within thirty days.','The supplier shall deliver conforming goods.'],notes='Author-defined paragraph units; this is not an expert legal segmentation standard.')
    add('S02','segmentation_linewrapped_numbers',['Section 1. Prices\nThe amount is\n100 dollars payable after delivery.'],notes='A line-wrapped amount is body text, not a new numbered provision.',stratum='challenge')
    add('S03','segmentation_uppercase_body',['Section 1. Notices\nNOTICE ONLY\nThis uppercase line belongs to this authored clause.'],notes='Controlled authored unit includes an internal uppercase line; legal segmentation may admit other conventions.',stratum='challenge')
    add('S04','literal_angle_text',['Section 1. Payment\nIf price < 100, payment follows Section 9; if volume > 20, delivery is expedited.'],decls=[('1',0,'Section 1.')],refs=[('9',0,'Section 9;','nondirectional')],review=True,stratum='challenge',notes='Plain-text comparison signs are not HTML tags; the missing citation must not disappear.')
    add('S05','normalized_html',['<p>Section 1. Definitions</p><p>Services means example work.</p>','<p>Section 2. Payment</p><p>Payment follows Section 1 above.</p>'],notes='HTML normalization is an existing behavior; raw offsets are not normalized offsets. No legal/task binary score.')
    for i,wording in enumerate(['The buyer shall remit payment within thirty days after receipt of an invoice.','Whensoever an invoice is received, the obligor shall discharge the pecuniary sum within thirty days.','On receipt of the billing instrument, remittance shall occur within a thirty-day period.','The invoice-receiving party undertakes timely satisfaction of the stated monetary obligation.'],1):
        add(f'W{i:02d}','unusual_wording',['Section 1. Payment\n'+wording,'Section 2. Notices\nAll notices must be in writing.'],kind=PROV,notes='Intended benign paraphrase, not independently adjudicated legal validity. Neural flag frequency only; no legal FP/TN assigned.')
    original=ROOT/'src/redteam/fixtures.py';tree=ast.parse(original.read_text(encoding='utf-8'))
    families=[]
    for function in ['get_synthetic_msa_clauses','get_synthetic_sla_clauses']:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function)
        assignment=next(n for n in node.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='raw_clauses' for t in n.targets))
        families.append((function,[pair[0] for pair in ast.literal_eval(assignment.value)]))
    families.append(('new_generic_template',['Section 1. Definitions\nGoods means the example products.','Section 2. Supply\nThe supplier shall deliver the goods.','Section 3. Payment\nThe buyer shall pay after delivery.','Section 4. Confidentiality\nEach party shall protect confidential information.','Section 5. Term\nThe parties may terminate by written notice.','Section 6. Notices\nNotices must be in writing.']))
    for family,texts in families:
        n=len(texts);orders=[('original',list(range(n))),('swap_middle',list(range(n))),('reverse',list(reversed(range(n)))),('move_block',list(range(2,n))+[0,1])]
        swap=orders[1][1];swap[2],swap[3]=swap[3],swap[2]
        for operation,order in orders:
            cid=f'O{sum(c["case_id"].startswith("O") for c in cases)+1:02d}'
            add(cid,'clause_order_proxy',[texts[i] for i in order],labels={'order_changed_proxy':order!=list(range(n))},notes='Mechanical order-change proxy ONLY. Reordering is not labelled a legal defect. Original and perturbed texts are exposed development evidence.',origin={'fixture':family,'source_file':'src/redteam/fixtures.py' if family!='new_generic_template' else None,'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest() if family!='new_generic_template' else None,'operation':operation,'permutation':order,'family_id':family})
    for cid,first,last,note in [
      ('C01','The buyer must pay each invoice exactly thirty days after receipt.','The buyer must pay each same invoice exactly sixty days after receipt.','Potential incompatible same-invoice deadlines; scope and precedence need independent review.'),
      ('C02','Standard invoices are payable within thirty days.','Disputed invoices are payable within sixty days.','Different invoice classes can explain different deadlines; no legal correctness label.'),
      ('C03','The recipient must never disclose the confidential information to any third party.','The recipient must disclose that confidential information to the named third-party auditor.','Potential disclosure exception/contradiction requires scope and precedence interpretation.'),
      ('C04','The monthly service fee is one hundred dollars.','The annual service fee is twelve hundred dollars.','Potentially compatible statements; no adjudicated legal label.')]:
        add(cid,'distant_contradiction_candidates',['Section 1. Obligation\n'+first,'Section 2. Delivery\nDelivery occurs on request.','Section 3. Notices\nNotices must be in writing.','Section 4. Definitions\nInvoice means the written billing document.','Section 5. Obligation\n'+last],kind=PROV,notes=note)
    case_dir=output/'cases';case_dir.mkdir(exist_ok=True)
    for c in cases:
        (output/c['source_document']).write_text('\n\n'.join(c['clauses']),encoding='utf-8')
    payload={'schema_version':'1.0','dataset_role':'DETECTOR_AWARE_EXPOSED_DEVELOPMENT_DIAGNOSTIC','created_client_date':'2026-10-26','author':'AI-assisted case construction; no independent annotation','cases':cases}
    (output/'corpus.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Frozen-input cases:',len(cases));print('Mechanical:',sum(c['label_provenance']==MECH for c in cases),'Provisional:',sum(c['label_provenance']==PROV for c in cases),'Independent: 0')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=BASE);args=p.parse_args();build(args.output)
