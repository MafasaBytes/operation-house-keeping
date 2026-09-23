import sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from applications.bounded_decision_workflow import measurement_wire as m
from tests.measurement_profile.qualify_slice6 import read
p=Path('/tmp/nm-slice6-corrected-matrix/p');iv=(p/'invocation.json').read_bytes();pin=json.loads(iv)['selection']['sha256']
g=m.Graph(iv,lambda k,w:(p/'objects'/(k[1]+'.'+k[0])).read_bytes(),pin,m.Work())
q=g.values[g.requests[0]]
first=('nm.request.v1','0'*64);second=('nm.request.v1','f'*64)
g.values[first]=dict(q,id='first');g.values[second]=dict(q,id='second');g.requests=[first,second]
g.objects[first]=m.canonical_json_bytes(g.values[first]);g.objects[second]=m.canonical_json_bytes(g.values[second])
def joins(q,ref):
 m.fail('SUPPORT_SUBJECT_MISMATCH' if q['id']=='first' else 'DECODER_INVALID','/measurements/0/decoder','phase_3')
g._joins=joins;g._intrinsic=lambda v:None
try:g._integrity()
except m.MeasurementContractError as e:
 print(json.dumps(dict(code=e.code,expected='DECODER_INVALID',layer='internal validation-order seam; not public SHA admission')))
 assert e.code=='DECODER_INVALID'
else:raise AssertionError('accepted invalid graph')
