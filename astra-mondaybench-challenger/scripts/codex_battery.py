"""Fresh Codex sessions; candidate text is never judged or rewritten."""
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'astra-mondaybench-challenger'
sys.path.insert(0, str(ROOT))
import yaml
from mondaybench.prompt_builder import build_prompt

def sha(b): return hashlib.sha256(b).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def prepare():
    contract = json.loads((OUT/'preflight/generation-contract.json').read_text(encoding='utf-8'))
    for row in contract['rendered_inputs']:
        sid = row['scenario_id']
        directory = ROOT/'scenarios'/sid
        meta = yaml.safe_load((directory/'scenario.yaml').read_text(encoding='utf-8'))
        sources = meta.get('sources') or meta['source_order']
        p = build_prompt(SimpleNamespace(id=sid,sources=sources,
            prompt_template=(directory/meta.get('prompt_file','prompt.md')).read_text(encoding='utf-8'),
            source_text={s:(directory/s).read_text(encoding='utf-8') for s in sources}))
        assert p.sha256 == row['rendered_input_sha256']
        target=OUT/'inputs'/f'{sid}.txt'
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f: f.write(p.text.encode('utf-8'))
    (OUT/'config').mkdir(exist_ok=True)
    (OUT/'config/system.txt').write_bytes(b'You are a helpful assistant.')
    cfg = {'display_name':'Astra','configuration_label':'Astra — reasoning effort: medium (highest available)',
           'runtime':'Codex','route':'fresh Codex CLI exec sessions using existing ChatGPT login',
           'requested_model_id':'gpt-6-astra','exact_backend_model_id':'UNOBSERVABLE',
           'reasoning_effort':'medium','reasoning_effort_note':'highest available in Codex (user-declared)',
           'system_prompt':'You are a helpful assistant.',
           'developer_instructions':'Do not use tools. Answer the supplied user input directly using only its contents. Do not invoke agents, inspect files, browse, or execute commands.',
           'temperature':'UNOBSERVABLE','top_p':'UNOBSERVABLE','caching':'UNOBSERVABLE',
           'max_output_tokens':'UNOBSERVABLE','canonical_temperature':0,'canonical_top_p':'omitted',
           'canonical_caching':False,'canonical_ceilings':{r['scenario_id']:r['output_ceiling'] for r in contract['rendered_inputs']},
           'runtime_contract_note':'Codex runtime execution authorized by user; API control equivalence is not claimed. Medium is intentional, not a qualification issue.',
           'tools':'disabled where configurable; all tool use explicitly prohibited; JSON events audited',
           'session_isolation':'new exec, no resume/fork; empty per-run cwd; project docs disabled; user config ignored',
           'suite_digest':contract['suite_digest'],'frozen_config_group_digest':contract['frozen_config_group_digest'],
           'frozen_at':now(),'expected_runs':15,'codex_version':subprocess.check_output([shutil.which('codex'),'--version'],text=True).strip()}
    write_json(OUT/'config/model-config.json',cfg)
    (OUT/'config/model-config.sha256').write_text(sha((OUT/'config/model-config.json').read_bytes())+'\n',encoding='ascii')
    print(json.dumps({'prepared':True,'config_sha256':sha((OUT/'config/model-config.json').read_bytes())}),flush=True)

def command(work, target, cfg):
    args=[shutil.which('codex'),'exec','--ignore-user-config','--ignore-rules','--ephemeral',
          '--skip-git-repo-check','--sandbox','read-only','--model',cfg['requested_model_id'],
          '--cd',str(work),'--json','--color','never','--output-last-message',str(target)]
    overrides={'model_reasoning_effort':'medium','model_instructions_file':str(OUT/'config/system.txt'),
               'developer_instructions':cfg['developer_instructions'],'project_doc_max_bytes':0,
               'web_search':'disabled','hide_agent_reasoning':True,'approval_policy':'never',
               'forced_login_method':'chatgpt',
               'features.shell_tool':False,'features.apps':False,'features.plugins':False,
               'features.browser_use':False,'features.computer_use':False,'features.multi_agent':False,
               'features.memories':False,'features.skill_search':False,'features.skip_host_skill_discovery':True}
    for key,value in overrides.items():
        args+=['-c',key+'='+json.dumps(value)]
    return args+['-']

def run_one(sid, n, cfg):
    rid=f'run-{n:03d}'
    target=OUT/'responses'/sid/f'{rid}.txt'
    metadata=OUT/'metadata'/sid/f'{rid}.json'
    if target.exists() or metadata.exists(): raise RuntimeError('Refusing existing run '+sid+'/'+rid)
    target.parent.mkdir(parents=True,exist_ok=True)
    work=OUT/'sessions'/sid/rid
    work.mkdir(parents=True,exist_ok=False)
    user=(OUT/'inputs'/f'{sid}.txt').read_bytes()
    started=now(); t0=time.perf_counter()
    attempts=[]
    for attempt in range(1,4):
        events=[]; event_types=[]; tool_events=[]; finals=[]; usage=None; thread=None; completed=False
        args=command(work,target,cfg)
        result=subprocess.run(args,input=user,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        for line in result.stdout.decode('utf-8').splitlines():
            try: e=json.loads(line)
            except ValueError: continue
            kind=e.get('type'); event_types.append(kind)
            if kind=='thread.started': thread=e.get('thread_id')
            if kind=='turn.completed': completed=True; usage=e.get('usage')
            item=e.get('item') or {}
            if kind=='item.completed' and item.get('type')=='agent_message': finals.append(item.get('text',''))
            if item.get('type') in ('command_execution','mcp_tool_call','web_search','file_change','collab_tool_call'):
                tool_events.append({'event_type':kind,'item_type':item.get('type')})
            # Do not preserve reasoning text. Keep operational events and final messages only.
            if item.get('type') != 'reasoning': events.append(e)
        write_json(OUT/'execution'/sid/f'{rid}-attempt-{attempt}.json',
                   {'returncode':result.returncode,'events':events,'stderr':result.stderr.decode('utf-8',errors='replace')})
        attempt_record={'attempt':attempt,'returncode':result.returncode,'turn_completed':completed,
                        'final_message_present':bool(finals),'event_types':event_types}
        attempts.append(attempt_record)
        if finals:
            # Extract exact JSON string. The CLI -o may append a terminal newline;
            # preserve it separately, then use the event text as canonical raw output.
            cli=target.read_bytes() if target.exists() else None
            if cli is not None:
                (OUT/'execution'/sid/f'{rid}-cli-output.txt').write_bytes(cli)
            target.write_bytes(finals[-1].encode('utf-8'))
            break
        # No answer-quality inspection: retries only for technical noncompletion.
        errors=' '.join(str(e.get('message',''))+' '+str(e.get('error','')) for e in events if e.get('type') in ('error','turn.failed'))
        transient=any(s in errors.lower() for s in ('timed out','timeout','connection','stream disconnected','429','500','502','503','504'))
        attempt_record['transient_failure']=transient
        if result.returncode == 0 or not transient or attempt==3: break
        time.sleep((2,6)[min(attempt-1,1)])
    body=target.read_bytes() if target.exists() else b''
    valid=bool(finals) and completed and not tool_events
    record={'scenario_id':sid,'run_id':rid,'model':'gpt-6-astra','model_display_name':'Astra','runtime':'Codex',
            'requested_model_id':'gpt-6-astra','model_id':'UNOBSERVABLE','reasoning_effort':'medium',
            'reasoning_effort_note':'highest available','timestamp':started,'completed_at':now(),
            'temperature':'UNOBSERVABLE','top_p':'UNOBSERVABLE','caching':'UNOBSERVABLE','max_output_tokens':'UNOBSERVABLE',
            'system_prompt_equivalence':'UNOBSERVABLE; benchmark instruction requested via model_instructions_file; Codex may add system/developer context',
            'tools_available_to_runtime':'UNOBSERVABLE; configured tool families disabled but complete backend tool inventory not exposed',
            'tools_used_by_candidate':len(tool_events),'tools_used_evidence':'Codex exec JSON item events',
            'scenario_prompt_sha256':sha(user),'response_sha256':sha(body) if finals else None,
            'config_sha256':sha((OUT/'config/model-config.json').read_bytes()),
            'qualification':{'state':'VALID_CODEX_CANDIDATE' if valid else 'EXECUTION_EXCEPTION',
                'scope':'user-authorized Codex challenger, not API-route equivalence',
                'completed':completed,'tool_events':tool_events,'independent_session':True},
            'codex_thread_id':thread,'request_id':'UNOBSERVABLE','response_id':'UNOBSERVABLE',
            'finish_reason':'UNOBSERVABLE','TTFT':'UNOBSERVABLE','TTFA':'UNOBSERVABLE',
            'reasoning_tokens':'UNOBSERVABLE','reasoning_delivery_state':'UNOBSERVABLE',
            'latency_ms':(time.perf_counter()-t0)*1000,'latency_semantics':'host wall clock including session startup and retries',
            'codex_usage':usage or 'UNOBSERVABLE','attempts':attempts,'retries':len(attempts)-1,
            'response_bytes':len(body),'provider_truncation':'UNOBSERVABLE'}
    write_json(metadata,record)
    print(json.dumps({'scenario':sid,'run':rid,'qualification':record['qualification']['state'],
                      'response_bytes':len(body),'attempts':len(attempts)}),flush=True)
    return record

def battery():
    cfg=json.loads((OUT/'config/model-config.json').read_text(encoding='utf-8'))
    assert sha((OUT/'config/model-config.json').read_bytes())==(OUT/'config/model-config.sha256').read_text().strip()
    jobs=[(f'monday-{s:03d}',r) for s in range(1,6) for r in range(1,4)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda j:run_one(*j,cfg),jobs))
    write_json(OUT/'generation-summary.json',{'runs':results,'expected':15,
        'valid':sum(r['qualification']['state']=='VALID_CODEX_CANDIDATE' for r in results),
        'evaluation_performed':False})
    files={p.relative_to(OUT).as_posix():sha(p.read_bytes()) for folder in ['responses','metadata','inputs','config'] for p in (OUT/folder).rglob('*') if p.is_file()}
    write_json(OUT/'generation-freeze-manifest.json',{'frozen_at':now(),'files':files})

if __name__=='__main__':
    prepare() if '--prepare' in sys.argv else battery()
