"""Assemble frozen judging materials only AFTER generation freeze; no judging."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from validate_generation import validate
from mondaybench.config import load_evaluator
from mondaybench.scenarios import load_scenario
from mondaybench.suite import load_suite_index, load_suite_manifest
from mondaybench.evaluator import resolve_ground_truth
from mondaybench.judge import criterion_prompt, noise_prompt, penalty_prompt

def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,text):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f: f.write(text)
def dump(p,obj): write(p,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def main():
    integrity=validate()
    assert integrity['valid_runs']==15
    pack=OUT/'blind-judge-pack'
    pack.mkdir(exist_ok=False)
    index=load_suite_index('1.0',ROOT)
    release=load_suite_manifest('1.0',ROOT)
    provenance=[]; candidates=[]; selected_sources={}
    def frozen_bytes(path,group):
        rel=path.relative_to(ROOT).as_posix()
        data=path.read_bytes()
        assert sha(data)==index[group][rel],rel
        selected_sources[rel]=sha(data)
        return data
    for entry in release['scenarios']:
        sid=entry['id']; num=int(sid[-3:])
        scenario=load_scenario(sid,rubric_file=entry['rubric_file'])
        evaluator_path=ROOT/'evaluators'/f'evaluator-opus5-v0.{num}.yaml'
        frozen_bytes(evaluator_path,'evaluators')
        evaluator=load_evaluator(evaluator_path.stem)
        assert evaluator.rubric_file==entry['rubric_file']
        rubric=frozen_bytes(scenario.directory/entry['rubric_file'],'scenarios')
        ground=frozen_bytes(scenario.directory/scenario.ground_truth_file,'scenarios')
        criterion_instructions=None; penalty_instructions=None
        if evaluator.prompt_file:
            criterion_instructions=frozen_bytes(ROOT/'evaluators'/sid/evaluator.prompt_file,'evaluators').decode('utf-8')
        if evaluator.penalty_prompt_file:
            penalty_instructions=frozen_bytes(ROOT/'evaluators'/sid/evaluator.penalty_prompt_file,'evaluators').decode('utf-8')
        prompt=(OUT/'inputs'/f'{sid}.txt').read_bytes()
        assert sha(prompt)==entry['prompt_sha256']
        criteria=[]
        for criterion in scenario.rubric.criteria:
            paths=evaluator.ground_truth_map.get(criterion.id,[])
            excerpt=(resolve_ground_truth(scenario.ground_truth,paths) if paths else
                     scenario.ground_truth or {'answer_key':scenario.ground_truth_text})
            criteria.append({**asdict(criterion),'reference_paths':paths,'reference_material':excerpt})
        assert len(criteria)==entry['criteria']
        semantics={'rubric_version':scenario.rubric.version,'total_base_points':scenario.rubric.total_base_points,
           'dimension_max':scenario.rubric.dimension_max,'penalties':{k:asdict(v) for k,v in scenario.rubric.penalties.items()},
           'maximum_global_penalty':scenario.rubric.maximum_global_penalty,
           'noise':asdict(scenario.rubric.noise) if scenario.rubric.noise else None,
           'penalty_rule':'Only materially_misleading=true violations incur their defined points. Sum penalties, cap total magnitude at maximum_global_penalty; dismissed candidates incur zero.',
           'noise_rule':'If present, start at starting_points; subtract deduction_per_false_action for each triggered category, floor at minimum_points.',
           'aggregation_rule':'Use the frozen criterion label point mappings. Sum dimensions, then apply capped penalties with a final floor of zero. No points have been assigned in this package.',
           'tie_rule':'Choose the lower label when between two labels.'}
        for run in range(1,4):
            cid=f'CANDIDATE-{num:03d}-R{run}'; rid=f'run-{run:03d}'
            directory=pack/cid; directory.mkdir()
            response=(OUT/'responses'/sid/f'{rid}.txt').read_bytes()
            meta=json.loads((OUT/'metadata'/sid/f'{rid}.json').read_text(encoding='utf-8'))
            assert sha(response)==meta['response_sha256']
            (directory/'input.txt').write_bytes(prompt)
            (directory/'response.txt').write_bytes(response)
            (directory/'rubric.yaml').write_bytes(rubric)
            reference_name='reference'+Path(scenario.ground_truth_file).suffix
            (directory/reference_name).write_bytes(ground)
            dump(directory/'atomic-criteria.json',criteria)
            dump(directory/'penalty-and-weight-semantics.json',semantics)
            # Original criterion instructions are preserved; full per-criterion packets
            # use the standard renderer with official reference slicing. No model call.
            for c,details in zip(scenario.rubric.criteria,criteria):
                text=criterion_prompt(c,details['reference_material'],response.decode('utf-8'),instructions=criterion_instructions)
                write(directory/'criterion-packets'/f'{c.id}.txt',text)
            if criterion_instructions:
                write(directory/'criterion-instructions.md',criterion_instructions)
            if penalty_instructions:
                write(directory/'penalty-instructions.md',penalty_instructions)
            else:
                write(directory/'penalty-instructions.md',penalty_prompt(scenario.ground_truth,prompt.decode('utf-8'),response.decode('utf-8')))
            if scenario.rubric.noise:
                write(directory/'noise-instructions.md',noise_prompt(scenario.rubric.noise.false_actions,response.decode('utf-8')))
            template={'candidate_id':cid,'criteria':[{'criterion_id':c.id,'result':None,'evidence':None,'reason':None} for c in scenario.rubric.criteria],
                'noise':([{'id':a.id,'triggered':None,'evidence':None} for a in scenario.rubric.noise.false_actions] if scenario.rubric.noise else None),
                'penalties':None,'penalty_entry_fields':['type','evidence','reason','materially_misleading']}
            dump(directory/'blank-verdict-template.json',template)
            case={'candidate_id':cid,'scenario_id':sid,'scenario_name':entry['name'],'input':'input.txt',
                 'response':'response.txt','rubric':'rubric.yaml','reference':reference_name,
                 'criterion_ids':[c.id for c in scenario.rubric.criteria],
                 'input_sha256':sha(prompt),'response_sha256':sha(response),'rubric_sha256':sha(rubric),'reference_sha256':sha(ground)}
            dump(directory/'case.json',case); candidates.append({'candidate_id':cid,'case':cid+'/case.json'})
            provenance.append({'candidate_id':cid,'scenario_id':sid,'run_id':rid,'model':'gpt-6-astra','runtime':'Codex',
                'response_path':f'responses/{sid}/{rid}.txt','response_sha256':sha(response),
                'codex_thread_id':meta['codex_thread_id'],'request_id':meta['request_id'],'response_id':meta['response_id']})
    write(pack/'README.md','''# MondayBench v1.0 blind judge package

This package contains fifteen ungraded candidates. Each candidate directory is self-contained: exact input, exact response, frozen rubric, reference material, criterion packets, penalty instructions, weights and an unfilled verdict template.

Evaluate one candidate at a time. For each atomic criterion use its packet, which contains the applicable frozen definition and reference material. Judge meaning rather than exact wording; do not reward unstated facts or penalize style. When between labels choose the lower. Record PASS, PARTIAL or FAIL, response evidence and a criterion-specific reason for every criterion. Blank values are unfilled fields, not verdicts.

For penalties, read the candidate's penalty-instructions.md, frozen rubric, complete input and reference. The input is the authority on whether a statement is supported; the reference is not an exhaustive list of permissible facts. Use only penalty types defined for that scenario. Be conservative; omissions and weak answers are handled by atomic criteria. Record considered penalties with evidence, reason and materially_misleading=true/false; an explicit empty list is valid when none apply. Only materially misleading violations incur penalties. The semantics JSON contains the frozen type mappings, weights, cap and noise deduction rules.

For candidates with noise-instructions.md, classify every listed category explicitly. Do not default blank noise fields to false. Produce labels and evidence; deterministic point conversion is separate. Do not infer candidate identity, compare candidates, or use outside results. No judgments or scores are supplied here.

Criterion and penalty instruction files follow the frozen recorded-evaluator materials. Versioned scenario instructions are preserved for scenarios 002–005; scenario 001 uses the built-in instructions whose default rendering is unchanged from v1.0. Candidate references, weights and rubric definitions are frozen v1.0 artifacts. Criterion packets intentionally omit weights from the atomic judging prompt, while the accompanying rubric and semantics retain them for later deterministic conversion.
''')
    dump(pack/'cases.json',{'suite_version':'1.0','candidates':candidates})
    forbidden=re.compile(r'\b(astra|codex)\b|gpt-6-astra|reasoning_effort|reasoning effort',re.I)
    leaks=[]
    for p in pack.rglob('*'):
        if p.is_file() and (forbidden.search(p.relative_to(pack).as_posix()) or forbidden.search(p.read_text(encoding='utf-8'))):
            leaks.append(p.relative_to(pack).as_posix())
    assert not leaks, 'Identity scan failed: '+str(leaks)
    files={p.relative_to(pack).as_posix():sha(p.read_bytes()) for p in pack.rglob('*') if p.is_file()}
    dump(pack/'integrity-manifest.json',{'files':files})
    dump(OUT/'private-provenance-map.json',{'generation_freeze_sha256':integrity['generation_freeze_sha256'],'candidates':provenance,'frozen_judging_sources':selected_sources})
    with zipfile.ZipFile(OUT/'blind-judge-pack.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(pack.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(pack).as_posix())
    validate()  # Pack construction must not change any frozen candidate artifact.
    dump(OUT/'judge-pack-integrity.json',{'candidates':15,'identity_scan':'PASS','mapping_excluded':'PASS',
         'frozen_source_hash_checks':'PASS','generation_freeze_unchanged':'PASS','evaluation_performed':False,
         'zip_sha256':sha((OUT/'blind-judge-pack.zip').read_bytes()),'files':len(files)+1})
    print(json.dumps({'blind_candidates':15,'identity_scan':'PASS','evaluation_performed':False,'files':len(files)+1}))

if __name__=='__main__': main()
