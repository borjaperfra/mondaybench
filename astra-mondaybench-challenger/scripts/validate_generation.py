"""Structural/provenance checks only: never grade candidate content."""
import hashlib
import json
from pathlib import Path
import sys

OUT=Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))

def validate():
    freeze=read(OUT/'generation-freeze-manifest.json')
    for rel,digest in freeze['files'].items():
        assert sha((OUT/rel).read_bytes())==digest, rel
    contract=read(OUT/'preflight/generation-contract.json')
    cfg=read(OUT/'config/model-config.json')
    config_hash=sha((OUT/'config/model-config.json').read_bytes())
    assert cfg['model']=='gpt-6-astra' and cfg['reasoning_effort']=='medium'
    assert all(cfg[k]=='UNOBSERVABLE' for k in ['temperature','top_p','caching','max_output_tokens'])
    expected={(f'monday-{s:03d}',f'run-{r:03d}') for s in range(1,6) for r in range(1,4)}
    actual={(p.parent.name,p.stem) for p in (OUT/'responses').glob('*/*.txt')}
    assert actual==expected
    assert {(p.parent.name,p.stem) for p in (OUT/'metadata').glob('*/*.json')}==expected
    threads=[]; hashes=[]; records=[]; warnings=[]; all_item_types=set()
    for sid,rid in sorted(expected):
        meta=read(OUT/'metadata'/sid/f'{rid}.json')
        body=(OUT/'responses'/sid/f'{rid}.txt').read_bytes()
        row=next(r for r in contract['rendered_inputs'] if r['scenario_id']==sid)
        assert sha((OUT/'inputs'/f'{sid}.txt').read_bytes())==row['rendered_input_sha256']==meta['scenario_prompt_sha256']
        assert sha(body)==meta['response_sha256']
        assert meta['config_sha256']==config_hash and meta['reasoning_effort']=='medium'
        assert meta['qualification']['state']=='VALID_CODEX_CANDIDATE'
        assert meta['tools_used_by_candidate']==0
        threads.append(meta['codex_thread_id']); hashes.append(meta['response_sha256'])
        last=read(OUT/'execution'/sid/f'{rid}-attempt-{len(meta["attempts"])}.json')
        final=[e['item']['text'] for e in last['events'] if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message'][-1]
        assert final.encode('utf-8')==body
        assert last['returncode']==0 and any(e.get('type')=='turn.completed' for e in last['events'])
        for e in last['events']:
            item=e.get('item',{})
            if item: all_item_types.add(item['type'])
            if item.get('type')=='error': warnings.append({'scenario':sid,'run':rid,'message':item['message']})
        records.append(meta)
    assert len(set(threads))==15 and None not in threads
    assert all_item_types<= {'agent_message','error'}
    # Duplicates are reported, never used to select a better sample.
    report={'frozen_suite':'PASS','canonical_rendered_inputs':'PASS','runtime':'Codex','model':'gpt-6-astra',
      'reasoning_effort_medium_all_runs':'PASS','independent_sessions':len(set(threads)),
      'valid_runs':len(records),'valid_per_scenario':{f'monday-{s:03d}':3 for s in range(1,6)},
      'final_event_exact_bytes':'PASS','response_hashes':'PASS','single_configuration':'PASS',
      'tools_used_by_candidate':0,'tools_available_to_runtime':'UNOBSERVABLE',
      'no_best_of_n':'PASS','no_evaluation_performed':'PASS','generation_blindness':'PASS',
      'system_prompt_equivalence':'UNOBSERVABLE','api_equivalence_claimed':False,
      'retries':sum(r['retries'] for r in records),'duplicate_response_hashes':15-len(set(hashes)),
      'execution_failures':sum(sum(a['returncode']!=0 for a in r['attempts']) for r in records),
      'provider_truncations':'UNOBSERVABLE','normal_codex_completions':15,
      'runtime_warnings':warnings,'observed_item_types':sorted(all_item_types),
      'config_sha256':config_hash,'generation_freeze_sha256':sha((OUT/'generation-freeze-manifest.json').read_bytes())}
    return report

if __name__=='__main__':
    result=validate()
    (OUT/'generation-integrity.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='runtime_warnings'}))
