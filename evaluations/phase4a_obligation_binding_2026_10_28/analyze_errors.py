"""Post-exposure error audit, never a retuned or relabelled initial evaluation."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parent

def main():
    target=BASE/'post_evaluation_error_audit.json'
    if target.exists():raise FileExistsError('Preserve error audit')
    results=[]
    for name in ['development_v1','evaluation_first_pass']:
        rows=[json.loads(l) for l in (BASE/'results'/name/'predictions.jsonl').open(encoding='utf8')]
        invalid_cells=[];valid_cells=[]
        for r in rows:
            if r['case']['label_provenance']=='PROVISIONAL_INTERPRETATION':continue
            for side in ['left','right']:
                observed=[x for x in r['result']['records'] if x['section_identity']==r['case'][side+'_section']]
                for i,gold in enumerate(r['case']['expected_'+side]):
                    pred=observed[i].get('event_instance') if i<len(observed) else None
                    cell=dict(case_id=r['case_id'],side=side,index=i,gold=gold['event_instance'],prediction=pred)
                    if r['case_id'].endswith('_same_recurring_type'):
                        invalid_cells.append(dict(cell,reason='Gold copied the named invoice type even though each-month language does not identify a unique event occurrence. Pair gold UNCERTAIN remains valid.'))
                    else:valid_cells.append(cell)
        corrected=[];introduced=[]
        for r in rows:
            if r['gold_state'] is None:continue
            old_ok=r['ablation']==r['gold_state'];new_ok=r['prediction']==r['gold_state']
            if not old_ok and new_ok:corrected.append(r['case_id'])
            if old_ok and not new_ok:introduced.append(r['case_id'])
        results.append(dict(run=name,raw_metrics_unchanged=True,event_instance_label_cells_requiring_review=invalid_cells,
            posthoc_event_exact_sensitivity=dict(correct=sum(c['gold']==c['prediction'] for c in valid_cells),denominator=len(valid_cells),
                note='Excludes only the two invalid type-vs-occurrence gold cells. This is explicitly posthoc sensitivity, not a replacement untouched score.'),
            guard_ablation_corrected_state_errors=corrected,guard_ablation_introduced_state_errors=introduced,
            remaining_pair_errors=[dict(case_id=r['case_id'],gold=r['gold_state'],prediction=r['prediction'],source=r['case']['text'],evidence=r['selected_pair']) for r in rows if r['outcome_correct'] is False],
            field_errors=[dict(case_id=r['case_id'],errors=r['field_errors']) for r in rows if r['field_errors']]))
    target.write_text(json.dumps(dict(audit_type='POST_EXPOSURE_LABEL_AND_ERROR_REVIEW',production_changed=False,
        frozen_labels_or_results_changed=False,results=results),indent=2)+'\n',encoding='utf8');print(json.dumps(results,indent=2))

if __name__=='__main__':main()
