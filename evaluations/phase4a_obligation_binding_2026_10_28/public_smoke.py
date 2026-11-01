"""Operational smoke on existing public-source contracts. No legal labels or accuracy."""
from pathlib import Path
import argparse,hashlib,json,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))

def main(substantive=False):
    target=BASE/('public_substantive_smoke.json' if substantive else 'public_source_smoke.json')
    if target.exists():raise FileExistsError('Preserve previous smoke evidence')
    from src.obligations import analyze_bindings
    from src.segmentation.rule_based import RuleBasedSegmenter
    from src.config import EDGAR_MANIFEST
    provenance=json.loads(EDGAR_MANIFEST.read_text(encoding='utf8')) if EDGAR_MANIFEST.exists() else None
    rows=[]
    # Deterministic bounded selection by size/path, not label or prediction quality.
    files=sorted((ROOT/'data/raw/sec_edgar').glob('*.txt'),key=lambda p:(p.stat().st_size,p.name))[:3]
    if substantive:
        # Initial smallest exhibits were reference-only with no modal duties. Use a
        # predeclared size stratum, not model prediction quality, for substantive probes.
        files=sorted((p for p in (ROOT/'data/raw/sec_edgar').glob('*.txt') if 20000<=p.stat().st_size<=200000),key=lambda p:p.name)[:3]
    for p in files:
        raw=p.read_bytes();source=raw.decode('utf8')
        for mode,text in [('raw_source',source),('existing_legacy_html_extraction',RuleBasedSegmenter()._clean_html(source))]:
            result=analyze_bindings(source_text=text,doc_id=p.stem+'_'+mode)
            spans_ok=all(text[r['char_start']:r['char_end']]==r['raw_text'] for r in result['records'])
            for r in result['records']:
                for spans in r['evidence'].values():
                    spans_ok &= all(text[s['char_start']:s['char_end']]==s['text'] for s in spans)
            rows.append(dict(path=p.relative_to(ROOT).as_posix(),raw_sha256=hashlib.sha256(raw).hexdigest(),input_mode=mode,
                input_sha256=hashlib.sha256(text.encode('utf8')).hexdigest(),input_characters=len(text),status=result['status'],
                record_count=result['record_count'],pair_counts=result['pair_counts'],issues=result['issues'],exact_spans=spans_ok,
                ground_truth=None,legal_accuracy='NOT_ASSESSED',
                coordinate_note='Offsets are in this explicitly identified input view; normalized extraction is not original HTML byte coordinates.',
                result=result))
    target.write_text(json.dumps(dict(source='Existing SEC EDGAR research corpus; original files retained',
        manifest_path=str(EDGAR_MANIFEST.relative_to(ROOT)) if EDGAR_MANIFEST.exists() else None,
        manifest_sha256=hashlib.sha256(EDGAR_MANIFEST.read_bytes()).hexdigest() if provenance else None,
        independent_labels=0,documents=len(files),observations=rows),indent=2)+'\n',encoding='utf8')
    print(json.dumps([dict(path=r['path'],mode=r['input_mode'],status=r['status'],records=r['record_count'],pairs=r['pair_counts']) for r in rows],indent=2))
    assert all(r['exact_spans'] for r in rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--substantive',action='store_true');main(parser.parse_args().substantive)
