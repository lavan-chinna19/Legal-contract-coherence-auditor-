"""Final source-consumption verification on the same three public contracts. No new labels."""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def main():
    target=BASE/'public_source_verification.json'
    if target.exists():raise FileExistsError('Keep the original verification')
    from src.obligations import analyze_bindings
    from src.obligations.binding import MODAL
    from src.structure import parse_contract,resolve_references
    from src.segmentation.rule_based import RuleBasedSegmenter
    path=BASE/'baseline_binding.py'
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))
    assert digest(path)==before['files']['src/obligations/binding.py']
    spec=importlib.util.spec_from_file_location('pre_source_fix_binding',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    prior=ROOT/'evaluations/phase4a1_reliability_2026_10_28/results/comparison_v2/paired_public.jsonl'
    rows=[];segmenter=RuleBasedSegmenter()
    for line in prior.open(encoding='utf8'):
        saved=json.loads(line)['new'];source=saved['input_text'];doc_id=saved['result']['doc_id']
        inventory_before=[c.to_dict() for c in segmenter.segment(source,doc_id)]
        structure=parse_contract(source_text=source,doc_id=doc_id)
        baseline=old.analyze_bindings(source_text=source,doc_id=doc_id)
        assert baseline==saved['result'],'Pre-fix public result does not reproduce'
        current=analyze_bindings(source_text=source,doc_id=doc_id)
        inventory_after=[c.to_dict() for c in segmenter.segment(source,doc_id)]
        summaries={}
        for name,result in [('before',baseline),('after',current)]:
            missing=[]
            for m in MODAL.finditer(source):
                if not any(r['char_start']<=m.start()<r['char_end'] for r in result['records']):
                    missing.append(dict(char_start=m.start(),char_end=m.end(),text=m[0]))
            summaries[name]=dict(records=result['record_count'],emitted_pairs=result['evaluated_pair_count'],candidate_pairs=result['candidate_pair_count'],
                pair_counts=result['pair_counts'],decided_pairs=sum(v for k,v in result['pair_counts'].items() if k in ['MATCHED','DIFFERENT']),
                abstained_pairs=sum(v for k,v in result['pair_counts'].items() if k in ['UNCERTAIN','UNSUPPORTED']),
                lexical_modal_cues=len(list(MODAL.finditer(source))),unrepresented_modal_cues=missing,issues=result['issues'],complete=result['complete'])
            for r in result['records']:
                assert source[r['char_start']:r['char_end']]==r['raw_text']
                for spans in r['evidence'].values():
                    for s in spans:assert source[s['char_start']:s['char_end']]==s['text']
        structure_after=parse_contract(source_text=source,doc_id=doc_id)
        row=dict(path=saved['path'],source_url=saved['source_url'],entity_name=saved['entity_name'],accession=saved['accession'],exhibit=saved['exhibit'],filing_date=saved['filing_date'],
            mode=saved['mode'],source_text=source,raw_sha256=saved['raw_sha256'],input_sha256=saved['input_sha256'],coordinate_note=saved['coordinate_note'],
            summaries=summaries,source_preserved=structure.source_text==source and ''.join(u['text'] for u in structure.units)==source,
            structure_identical=structure.to_dict()==structure_after.to_dict(),references_identical=resolve_references(structure)==resolve_references(structure_after),
            clause_inventory_identical=inventory_before==inventory_after,clause_inventory_before=inventory_before,clause_inventory_after=inventory_after,
            structural_document=structure.to_dict(),before_binding=baseline,after_binding=current,qualified_legal_labels=0)
        rows.append(row)
    with (BASE/'public_source_evidence.jsonl').open('w',encoding='utf8') as stream:
        for r in rows:stream.write(json.dumps(r,ensure_ascii=False)+'\n')
    normalized=[r for r in rows if r['mode']=='existing_legacy_html_extraction']
    summary=dict(verification_scope='Source-consumption regression only; no new benchmark, labels or accuracy claim',documents=len(normalized),observations=len(rows),
        contracts=[dict(path=r['path'],url=r['source_url'],clauses=len(r['clause_inventory_before']),
            before=r['summaries']['before'],after=r['summaries']['after']) for r in normalized],
        all_source_preserved=all(r['source_preserved'] for r in rows),all_structures_identical=all(r['structure_identical'] for r in rows),
        all_references_identical=all(r['references_identical'] for r in rows),all_clause_inventories_identical=all(r['clause_inventory_identical'] for r in rows),
        normalized_modal_cues=sum(r['summaries']['after']['lexical_modal_cues'] for r in normalized),
        skipped_normalized_modal_cues_before=sum(len(r['summaries']['before']['unrepresented_modal_cues']) for r in normalized),
        skipped_normalized_modal_cues_after=sum(len(r['summaries']['after']['unrepresented_modal_cues']) for r in normalized),
        qualified_legal_labels=0,legal_accuracy='NOT_ASSESSED')
    dump(target,summary);print(json.dumps(summary,indent=2))
    assert summary['all_source_preserved'] and summary['all_structures_identical'] and summary['all_references_identical'] and summary['all_clause_inventories_identical']
    assert summary['skipped_normalized_modal_cues_after']==0,'An in-scope inline source omission remains'

if __name__=='__main__':main()
