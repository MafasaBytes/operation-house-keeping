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
