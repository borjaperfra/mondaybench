"""Read-only benchmark/provider checks; never generates a completion."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import httpx
import yaml
from mondaybench.config import _load_dotenv
from mondaybench.prompt_builder import build_prompt, SYSTEM_PROMPT
from mondaybench.providers.openai_compatible import OpenAICompatibleProvider
from mondaybench.suite import verify_suite, load_suite_index

OUT = ROOT / 'astra-mondaybench-challenger'
def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    manifest = yaml.safe_load((ROOT / 'releases/v1.0/SUITE-FROZEN.yaml').read_text(encoding='utf-8'))
    index = load_suite_index('1.0', ROOT)
    drift = verify_suite('1.0', ROOT)
    rows = []
    for entry in manifest['scenarios']:
        directory = ROOT / 'scenarios' / entry['id']
        meta = yaml.safe_load((directory / 'scenario.yaml').read_text(encoding='utf-8'))
        sources = meta.get('sources') or meta['source_order']
        # Deliberately avoid load_scenario: it also opens rubrics and ground truth.
        scenario = SimpleNamespace(id=entry['id'], sources=sources,
            prompt_template=(directory / meta.get('prompt_file', 'prompt.md')).read_text(encoding='utf-8'),
            source_text={s:(directory / s).read_text(encoding='utf-8') for s in sources})
        prompt = build_prompt(scenario)
        ceiling = meta.get('generation', {}).get('safety_ceiling_tokens', 32000)
        payload, unsupported = OpenAICompatibleProvider(base_url='https://example.invalid/v1', api_key='NOT_A_CREDENTIAL')._payload(
            model_id='ASTRA_ID_UNRESOLVED', system_prompt=prompt.system_prompt, user_prompt=prompt.text,
            generation_config={'temperature':0,'max_output_tokens':ceiling,
                               'extra_body':{'caching':False,'reasoning_effort':'medium'}}, stream=True)
        assert prompt.sha256 == entry['prompt_sha256']
        assert payload['messages'] == [{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':prompt.text}]
        assert 'tools' not in payload and 'top_p' not in payload and not unsupported
        rows.append({'scenario_id':entry['id'],'rendered_input_bytes':len(prompt.text.encode('utf-8')),
                     'rendered_input_sha256':prompt.sha256,'canonical_match':True,'sources':sources,
                     'source_count':len(sources),'output_ceiling':ceiling,
                     'request_keys':list(payload)})
    core = ['runner.py','prompt_builder.py','scenarios.py','providers/openai_compatible.py',
            'providers/anthropic_native.py','providers/base.py','providers/__init__.py','reasoning.py','official.py']
    core_checks = {f:sha((ROOT/'mondaybench'/f).read_bytes()) == index['harness']['mondaybench/'+f] for f in core}
    baseline_checks = {}
    for f, expected in index['harness'].items():
        if f in {p for p,_,_ in drift['harness'].changed}:
            old = subprocess.check_output(['git','show','bea927f:'+f],cwd=ROOT)
            baseline_checks[f] = sha(old) == expected
    report = {'suite_version':'1.0','suite_digest':manifest['suite_digest'],
              'frozen_config_group_digest':manifest['groups']['config']['content_digest'],
              'frozen_artifacts_pass':all(v.ok for v in drift.values()),
              'scenario_artifacts_identical':drift['scenarios'].identical,
              'system_prompt':SYSTEM_PROMPT,'system_prompt_sha256':sha(SYSTEM_PROMPT.encode()),
              'temperature':0,'top_p':'OMITTED / provider default','caching':False,
              'reasoning_effort':'medium','display_name':'Astra — reasoning effort: medium (highest available)',
              'configuration_status':'PARTIAL; provider and exact model ID unresolved; not execution-frozen',
              'core_generation_files_match_v1_0':core_checks,'drift_comparison_baseline_verified':baseline_checks,
              'rendered_inputs':rows,'runs_expected':15,'runs_attempted':0,
              'preprocessing':'Path.read_text UTF-8 universal newlines; frozen build_prompt strips source boundaries and substitutes placeholders or appends fixed headings.',
              'conversation':'Fresh system and user messages only; no prior messages or tools.',
              'raw_response_hash_convention':'SHA-256 of exact provider final response string encoded as UTF-8',
              'evaluation_performed':False}
    (OUT/'preflight').mkdir(parents=True,exist_ok=True)
    (OUT/'preflight'/'generation-contract.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,ensure_ascii=True))

def discover():
    _load_dotenv(ROOT)
    def probe(prefix):
        base = os.environ.get(prefix+'_BASE_URL','').rstrip('/')
        key = os.environ.get(prefix+'_API_KEY','')
        record = {'provider':prefix.lower(),'base_url_env':prefix+'_BASE_URL','api_key_env':prefix+'_API_KEY',
                  'endpoint_configured':bool(base),'credential_present':bool(key)}
        if not base or not key:
            return record
        url = base+'/models' if base.endswith('/v1') else base+'/v1/models'
        try:
            response = httpx.get(url,headers={'Authorization':'Bearer '+key},timeout=20)
            record['http_status'] = response.status_code
            if response.is_success:
                ids = [i.get('id') for i in response.json().get('data',[]) if isinstance(i,dict)]
                record['model_ids'] = ids
                record['astra_matches'] = [i for i in ids if isinstance(i,str) and 'astra' in i.lower()]
        except Exception as exc:
            # Exception messages and response bodies may contain credentials.
            record['error_type'] = type(exc).__name__
        return record
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(probe,['HELMCODE','NAN']))
    (OUT/'preflight').mkdir(parents=True,exist_ok=True)
    (OUT/'preflight'/'provider-discovery.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(records))

if __name__ == '__main__':
    discover() if '--discover' in sys.argv else main()
