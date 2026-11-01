"""Small mechanical regression examples authored before implementation/final testing."""
from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent

def main():
    path=BASE/'focused_cases.json'
    if path.exists():raise FileExistsError('Do not overwrite focused inputs')
    cases=[]
    def add(name,left,right,state,actors_left,actors_right,action='NOTIFY',recipient='customer',relation=None,instance=None):
        cases.append(dict(case_id=name,text=f'Section 1. Duty\n{left}\nSection 2. Duty\n{right}',
            gold_state=state,gold_match=state=='MATCHED' if state in ['MATCHED','DIFFERENT'] else None,
            actors_left=actors_left,actors_right=actors_right,action=action,recipient=recipient,
            expected_actor_action_relationship=relation,expected_instance=instance,
            provenance='MECHANICAL_AUTHOR_CONSTRUCTED_EXPOSED_DEVELOPMENT',independent_annotation=False))
    add('notification_type_only','The provider shall notify the customer.','The customer shall be notified by the provider.','UNCERTAIN',['provider'],['provider'],relation='MATCHED')
    add('named_notice_passive','The provider shall notify the customer about Notice Alpha.','The customer shall be notified by the provider about Notice Alpha.','MATCHED',['provider'],['provider'],relation='MATCHED',instance='notice alpha')
    add('missing_passive_agent','The provider shall notify the customer about Notice Alpha.','The customer shall be notified about Notice Alpha.','UNCERTAIN',['provider'],[],relation='UNCERTAIN',instance='notice alpha')
    add('joint_active','The provider and subcontractor shall notify the customer about Notice Alpha.','The provider shall notify the customer about Notice Alpha.','DIFFERENT',['provider','subcontractor'],['provider'],relation='DIFFERENT',instance='notice alpha')
    add('joint_passive','The provider and subcontractor shall notify the customer about Notice Alpha.','The customer shall be notified by the provider and subcontractor about Notice Alpha.','MATCHED',['provider','subcontractor'],['provider','subcontractor'],relation='MATCHED',instance='notice alpha')
    add('joint_reordered','The provider and subcontractor shall notify the customer about Notice Alpha.','The customer shall be notified by the subcontractor and provider about Notice Alpha.','MATCHED',['provider','subcontractor'],['subcontractor','provider'],relation='MATCHED',instance='notice alpha')
    add('compound_three','The provider, subcontractor and agent shall notify the customer about Notice Alpha.','The customer shall be notified by the agent, provider and subcontractor about Notice Alpha.','MATCHED',['provider','subcontractor','agent'],['agent','provider','subcontractor'],relation='MATCHED',instance='notice alpha')
    add('alternative_subject','The provider or subcontractor shall notify the customer about Notice Alpha.','The provider shall notify the customer about Notice Alpha.','UNCERTAIN',[],['provider'],relation='UNCERTAIN',instance='notice alpha')
    add('passive_payment','Purchaser shall pay Invoice Cedar.','Invoice Cedar must be paid by Purchaser.','MATCHED',['purchaser'],['purchaser'],'PAY',None,'MATCHED','invoice cedar')
    add('passive_delivery','Provider must deliver Report Bravo to Customer.','Report Bravo shall be delivered to Customer by Provider.','MATCHED',['provider'],['provider'],'DELIVER','customer','MATCHED','report bravo')
    add('generic_event_type','Buyer shall pay the invoice.','The invoice shall be paid by Buyer.','UNCERTAIN',['buyer'],['buyer'],'PAY',None,'MATCHED')
    add('distinct_instances','Provider shall notify Customer about Notice Alpha.','Customer shall be notified by Provider about Notice Bravo.','DIFFERENT',['provider'],['provider'],relation='MATCHED')
    add('recurrence','Buyer shall pay Invoice Alpha each month.','Invoice Alpha shall be paid by Buyer each month.','UNCERTAIN',['buyer'],['buyer'],'PAY',None,'MATCHED')
    add('same_explicit_occurrence','Buyer shall pay Invoice Alpha for occurrence 1.','Invoice Alpha shall be paid by Buyer for occurrence 1.','MATCHED',['buyer'],['buyer'],'PAY',None,'MATCHED','invoice alpha|occurrence:1')
    add('different_explicit_occurrences','Buyer shall pay Invoice Alpha for occurrence 1.','Invoice Alpha shall be paid by Buyer for occurrence 2.','DIFFERENT',['buyer'],['buyer'],'PAY',None,'MATCHED')
    add('one_sided_occurrence','Buyer shall pay Invoice Alpha for occurrence 1.','Invoice Alpha shall be paid by Buyer.','UNCERTAIN',['buyer'],['buyer'],'PAY',None,'MATCHED')
    add('passive_condition','If approved, Provider shall notify Customer about Notice Alpha.','If requested, Customer shall be notified by Provider about Notice Alpha.','UNCERTAIN',['provider'],['provider'],relation='MATCHED',instance='notice alpha')
    add('passive_exception','Provider shall notify Customer about Notice Alpha unless disputed.','Customer shall be notified by Provider about Notice Alpha.','UNCERTAIN',['provider'],['provider'],relation='MATCHED',instance='notice alpha')
    add('passive_negation','Provider shall not notify Customer about Notice Alpha.','Customer shall be notified by Provider about Notice Alpha.','UNCERTAIN',['provider'],['provider'],relation='UNCERTAIN',instance='notice alpha')
    add('unknown_action','Provider shall reconcile the accounts.','The accounts shall be reconciled by Provider.','UNSUPPORTED',['provider'],[],'RECONCILE',None,'UNCERTAIN')
    path.write_text(json.dumps(dict(cases=cases,claim='Controlled authored regression cases, not unseen or expert adjudicated'),indent=2)+'\n',encoding='utf8')
    frozen={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,Path(__file__),BASE/'PROTOCOL.md']}
    (BASE/'focused_input_manifest.json').write_text(json.dumps(dict(authored_before_repairs=True,files=frozen),indent=2)+'\n',encoding='utf8')
    print('Frozen focused development cases:',len(cases))

if __name__=='__main__':main()
