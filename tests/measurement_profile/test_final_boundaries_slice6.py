"""Slice 6 resource/stream boundaries; internal seams are never CLI options."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest
from applications.bounded_decision_workflow import measurement_wire as mw
from applications.bounded_decision_workflow import measurement_runtime as rt
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError

@pytest.mark.parametrize('dimension,wire,limit',[
 ('json_nodes',b'{"a":[0,0,0]}',4),
 ('string_bytes',b'{"a":"12345"}',4),
 ('string_bytes',b'{"12345":0}',4),
 ('json_depth',b'{"a":[[]]}',2),
])
def test_resource_guard_precedes_document_allocation(monkeypatch,dimension,wire,limit):
 def forbidden(*a,**k):pytest.fail('document allocation preceded resource refusal')
 monkeypatch.setattr(mw,'parse_document',forbidden)
 with pytest.raises(MeasurementContractError) as caught:mw.decode(wire,mw.Work({dimension:limit}))
 assert caught.value.code=='RESOURCE_LIMIT_EXCEEDED'
 assert caught.value.details['dimension']==dimension


def test_closure_guard_precedes_base64_allocation(monkeypatch):
 work=mw.Work({'closure_bytes':1})
 graph=SimpleNamespace(root=mw.ref('nm.invocation.v1','0'*64),objects={('nm.basis','1'*64):b'x'*30},work=work)
 monkeypatch.setattr(rt.base64,'b64encode',lambda *a:pytest.fail('base64 allocated before closure guard'))
 with pytest.raises(MeasurementContractError) as caught:rt.closure_wire(graph,'2'*64,None)
 assert caught.value.details['dimension']=='closure_bytes'


def test_tight_diagnostic_uses_reserved_fallback(tmp_path):
 # Trusted child test seam creates an error under a caller-tightened budget.
 # This does not establish public admission or provide a production callback.
 source='''from applications.bounded_decision_workflow import measurement_cli as c
from applications.bounded_decision_workflow.measurement_wire import Work,fail
def refuse(*a):
 Work({'diagnostic_bytes':1})
 fail('SUPPORT_SUBJECT_MISMATCH','/support')
c.runtime.evaluate=refuse
raise SystemExit(c.main(['measurement-evaluate','--invocation','i','--objects-dir','o','--authority-pin','a','--output-dir','r']))
'''
 run=subprocess.run([sys.executable,'-c',source],capture_output=True)
 assert run.returncode==4 and run.stdout==b''
 d=json.loads(run.stderr);assert d['code']=='DIAGNOSTIC_LIMIT_EXCEEDED' and d['target'] is None
 assert len(run.stderr)<=2048 and run.stderr.endswith(b'\n')


def test_failed_stdout_does_not_trigger_interpreter_flush_retry(tmp_path):
 source='''from applications.bounded_decision_workflow import measurement_cli as c
c.runtime.evaluate=lambda *a:dict(schema='nm.receipt.v1',operation='measurement-evaluate',evaluation_permitted=True,disposition='preferred_within_supplied_set',result_sha256='0'*64,bundle_sha256='1'*64)
raise SystemExit(c.main(['measurement-evaluate','--invocation','i','--objects-dir','o','--authority-pin','a','--output-dir','r']))
'''
 with open('/dev/full','wb',buffering=0) as sink:
  run=subprocess.run([sys.executable,'-c',source],stdout=sink,stderr=subprocess.PIPE)
 assert run.returncode==7
 assert json.loads(run.stderr)['code']=='INTERNAL_ERROR'
 assert b'Exception ignored' not in run.stderr


def test_failed_stderr_has_bounded_exit_without_traceback(tmp_path):
 with open('/dev/full','wb',buffering=0) as sink:
  run=subprocess.run([sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate'],stdout=subprocess.PIPE,stderr=sink)
 assert run.returncode==7 and run.stdout==b''


def test_failed_read_counts_consumed_prefix(tmp_path):
 p=tmp_path/'large';p.write_bytes(b'x'*20);work=mw.Work({'invocation_bytes':8})
 with pytest.raises(MeasurementContractError) as caught:rt.read_path(p,'invocation_bytes',work)
 assert caught.value.details=={'dimension':'invocation_bytes','attempted':9,'limit':8}
 assert work.physical['bytes_read']==9 and work.physical['read_operations']==1


def test_successful_read_has_same_accounting(tmp_path):
 p=tmp_path/'exact';p.write_bytes(b'x'*8);work=mw.Work({'invocation_bytes':8})
 assert rt.read_path(p,'invocation_bytes',work)==b'x'*8
 assert work.physical['bytes_read']==8 and work.physical['read_operations']==2


def test_partial_write_failure_counts_written_prefix(tmp_path,monkeypatch):
 from applications.bounded_decision_workflow import retention
 from applications.bounded_decision_workflow.errors import WorkflowInputError
 work=mw.Work();real=os.write;calls=0
 def broken(fd,data):
  nonlocal calls
  calls+=1
  if calls==1:return real(fd,data[:3])
  raise OSError('deliberate partial-write control')
 with retention._directory(True,str(tmp_path).split('/')[1:]) as fd:
  monkeypatch.setattr(os,'write',broken)
  with pytest.raises(WorkflowInputError):retention._write_file(fd,'result.json',b'123456',None,io=work.io)
 assert work.physical['bytes_written']==3 and work.physical['write_operations']==2
 assert not (tmp_path/'result.json').exists()


def amend_request(iv,objects,mutate):
 import hashlib
 def get(r):return json.loads((objects/(r['sha256']+'.'+r['kind'])).read_bytes())
 def put(v):
  b=mw.canonical_json_bytes(v);r=mw.ref(v['schema'],hashlib.sha256(b).hexdigest());(objects/(r['sha256']+'.'+r['kind'])).write_bytes(b);return r
 i=json.loads(iv.read_bytes());q=get(i['request']);a=get(i['selection']);d=get(a['declaration'])
 mutate(q,get,put);i['request']=put(q);d['requests']=[i['request']];a['request']=i['request'];a['declaration']=put(d);i['selection']=put(a);iv.write_bytes(mw.canonical_json_bytes(i))
 return i['selection']['sha256']


def test_nomination_subcheck_precedence_across_namespaces(tmp_path):
 from tests.measurement_profile.test_delivery_contract_mapping import recover_case,command
 iv,objects,pin=recover_case(tmp_path)
 def mutation(q,get,put):
  q['hypotheses'].reverse();q['measurements']=[q['measurements'][0]]*2
 pin=amend_request(iv,objects,mutation)
 run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'refused')
 d=json.loads(run.stderr)
 assert run.returncode==3 and d['code']=='DUPLICATE_NOMINATION_REFERENCE'
 assert d['target']['field']=='/measurements' and d['target']['occurrence_count']==2
 assert d['target']['references'][0]==d['target']['references'][1]


def test_decoder_precedes_support_join_error(tmp_path):
 from tests.measurement_profile.test_delivery_contract_mapping import recover_case,command
 iv,objects,pin=recover_case(tmp_path,'J-gap')
 def mutation(q,get,put):
  # Rehash an exact new support object whose context no longer matches Q.
  s=get(q['support'][0]);s['context']['scenario_label']='other';q['support'][0]=put(s)
 pin=amend_request(iv,objects,mutation)
 run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'refused')
 assert run.returncode==3 and json.loads(run.stderr)['code']=='DECODER_INVALID'


def test_public_diagnostic_budget_and_exact_twin(tmp_path):
 from tests.measurement_profile.test_delivery_contract_mapping import recover_case,command
 iv,objects,pin=recover_case(tmp_path)
 args=['measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin','0'*64]
 baseline=command(*args,'--output-dir',tmp_path/'baseline')
 assert baseline.returncode==3 and json.loads(baseline.stderr)['code']=='AUTHORITY_PIN_REQUIRED'
 for name,cap,code,status in [('exact',len(baseline.stderr),'AUTHORITY_PIN_REQUIRED',3),('below',len(baseline.stderr)-1,'DIAGNOSTIC_LIMIT_EXCEEDED',4),('one',1,'DIAGNOSTIC_LIMIT_EXCEEDED',4)]:
  limit=tmp_path/(name+'.json');limit.write_bytes(mw.canonical_json_bytes({'diagnostic_bytes':cap}))
  run=command(*args,'--output-dir',tmp_path/name,'--limits',limit)
  assert run.returncode==status and run.stdout==b''
  assert json.loads(run.stderr)['code']==code and not (tmp_path/name).exists()
  if name=='exact':assert run.stderr==baseline.stderr
  else:assert len(run.stderr)<=2048 and json.loads(run.stderr)['target'] is None


@pytest.mark.parametrize('stage',['create','write','flush','file_fsync','rename','manifest_before_rename','directory_fsync','parent_fsync'])
def test_real_publication_fault_boundaries(tmp_path,stage):
 from tests.measurement_profile.test_delivery_contract_mapping import recover_case,command
 iv,objects,pin=recover_case(tmp_path)
 source='''import os,stat,sys
from applications.bounded_decision_workflow import retention as r
from applications.bounded_decision_workflow.cli import main
stage=sys.argv[1]
original=r._event
def fault(hook,event,name):
 if event==stage and (name=='manifest.json' if stage=='manifest_before_rename' else name=='result.json'):raise OSError('controlled fault')
 return original(hook,event,name)
r._event=fault
original_sync=os.fsync
count=0
def fsync(fd):
 global count
 if stat.S_ISDIR(os.fstat(fd).st_mode):
  count+=1
  if (stage=='directory_fsync' and count==1) or (stage=='parent_fsync' and count==2):raise OSError('controlled sync failure')
 return original_sync(fd)
os.fsync=fsync
raise SystemExit(main(sys.argv[2:]))
'''
 out=tmp_path/'faulted'
 run=subprocess.run([sys.executable,'-c',source,stage,'measurement-evaluate','--invocation',str(iv),'--objects-dir',str(objects),'--authority-pin',pin,'--output-dir',str(out)],capture_output=True)
 assert run.returncode==6 and run.stdout==b'',run.stderr
 d=json.loads(run.stderr)
 if stage.endswith('_fsync') and stage!='file_fsync':
  assert (out/'manifest.json').exists() and d['bundle_state']=='complete_visible_durability_unknown'
  assert command('measurement-verify','--bundle',out).returncode==0
 else:
  assert not (out/'manifest.json').exists() and d['bundle_state']=='incomplete'
  assert command('measurement-verify','--bundle',out).returncode==3
 assert command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out).returncode==5


def test_concurrent_publication_has_one_winner(tmp_path):
 from tests.measurement_profile.test_delivery_contract_mapping import recover_case,command
 iv,objects,pin=recover_case(tmp_path);out=tmp_path/'race'
 args=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(iv),'--objects-dir',str(objects),'--authority-pin',pin,'--output-dir',str(out)]
 children=[subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for unused in range(2)]
 streams=[p.communicate(timeout=30) for p in children]
 assert sorted(p.returncode for p in children)==[0,5]
 for p,(stdout,stderr) in zip(children,streams):
  if p.returncode==0:assert stderr==b'' and json.loads(stdout)['schema']=='nm.receipt.v1'
  else:assert stdout==b'' and json.loads(stderr)['code']=='OUTPUT_COLLISION'
 assert command('measurement-replay','--bundle',out,'--output-dir',tmp_path/'replay').returncode==0


def test_cross_context_diagnostic_selection_uses_code_then_path(tmp_path,monkeypatch):
 # Internal order seam, distinct from public hash-consistent fixture admission.
 from tests.measurement_profile.test_delivery_contract_mapping import recover_case
 iv,objects,pin=recover_case(tmp_path)
 g=mw.Graph(iv.read_bytes(),lambda k,w:(objects/(k[1]+'.'+k[0])).read_bytes(),pin,mw.Work())
 q=g.values[g.requests[0]];first=('nm.request.v1','0'*64);second=('nm.request.v1','f'*64)
 for k,name in [(first,'first'),(second,'second')]:
  g.values[k]=dict(q,id=name);g.objects[k]=mw.canonical_json_bytes(g.values[k])
 g.requests=[first,second]
 def joins(q,ref):mw.fail('SUPPORT_SUBJECT_MISMATCH' if q['id']=='first' else 'DECODER_INVALID','/measurements/0/decoder','phase_3')
 monkeypatch.setattr(g,'_joins',joins);monkeypatch.setattr(g,'_intrinsic',lambda v:None)
 with pytest.raises(MeasurementContractError) as e:g._integrity()
 assert e.value.code=='DECODER_INVALID'


def test_recovery_capture_guard_precedes_base64_allocation(monkeypatch):
 import base64
 value=dict(schema='nm.closure.v1',profile=mw.PROFILE,invocation=mw.ref('nm.invocation.v1','0'*64),authority_pin='1'*64,limits_override=None,members=[dict(reference=mw.ref('nm.basis','2'*64),encoding='base64',bytes=base64.b64encode(b'123456789').decode())])
 payload={'closure.json':mw.canonical_json_bytes(value)}
 monkeypatch.setattr(rt.base64,'b64decode',lambda *a,**k:pytest.fail('recovery allocated beyond capture budget'))
 with pytest.raises(MeasurementContractError) as e:rt.recover(payload,mw.Work({'capture_bytes':8}))
 assert e.value.details['dimension']=='capture_bytes' and e.value.details['attempted']==9


def test_surrogate_wire_is_input_refusal():
 with pytest.raises(MeasurementContractError) as e:mw.decode(b'{"x":"\\ud800"}',mw.Work())
 assert e.value.code=='JSON_INVALID'
