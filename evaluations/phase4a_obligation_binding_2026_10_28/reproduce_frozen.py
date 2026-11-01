"""Reproduce archived exposed predictions; never call them another untouched evaluation."""
from pathlib import Path
import argparse,hashlib,json,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))

def main(run_id):
    out=BASE/'results'/run_id;out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((BASE/'implementation_frozen.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in manifest['files'].items())
    benchmark=json.loads((BASE/'benchmark_frozen_manifest.json').read_text())
    assert all(hashlib.sha256((BASE/p).read_bytes()).hexdigest()==h for p,h in benchmark['files'].items())
    from src.obligations import analyze_bindings
    checks=[]
    for name in ['development_v1','evaluation_first_pass']:
        for line in (BASE/'results'/name/'predictions.jsonl').open(encoding='utf8'):
            r=json.loads(line);actual=analyze_bindings(source_text=r['case']['text'],doc_id=r['case_id'])
            checks.append(dict(case_id=r['case_id'],identical=actual==r['result']))
    result=dict(status='EXPOSED_REPRODUCTION_ONLY',independent_new_examples=0,observations=len(checks),
        identical=sum(c['identical'] for c in checks),checks=checks)
    (out/'reproduction.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}));assert all(c['identical'] for c in checks)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True);main(parser.parse_args().run_id)
