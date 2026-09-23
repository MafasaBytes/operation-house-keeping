import sys,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tests.measurement_profile.test_delivery_contract_mapping import recover_case,command
from tests.measurement_profile.qualify_slice6 import wire,digest,save,read
root=Path(sys.argv[1]);root.mkdir();iv,objects,pin=recover_case(root)
def get(r):return read(objects/(r['sha256']+'.'+r['kind']))
def put(v):
 b=wire(v);r=dict(kind=v['schema'],sha256=digest(b));path=objects/(r['sha256']+'.'+r['kind'])
 if path.exists():assert path.read_bytes()==b
 else:path.write_bytes(b)
 return r
i=read(iv);q=get(i['request'])
# Independent declared request with a correctly rehashed support-context fault.
sq=get(i['request']);s=get(sq['support'][0]);s['revision']=2;s['context']['scenario_label']='other';sq['support'][0]=put(s)
# Independent request with coherently rebound P/O/S but a decoder gap.
dq=get(i['request']);old=dq['measurements'][0];p=get(old);o=get(p['decoder']);o['revision']=2
for row in o['outcomes']:
 if row['region'].get('upper') is not None:row['region']['upper']={'numerator':'49','denominator':'1'}
p['revision']=2;p['decoder']=put(o);dq['measurements'][0]=put(p)
for n,r in enumerate(dq['support']):
 s=get(r)
 if s['procedure']==old:
  s['revision']=3;s['procedure']=dq['measurements'][0];s['decoder']=p['decoder'];dq['support'][n]=put(s)
dq['id']='Q-diagnostic-decoder';dr=put(dq)
for n in range(100):
 sq['id']='Q-diagnostic-support-'+str(n);sr=put(sq)
 if sr['sha256']<dr['sha256']:break
else:raise AssertionError('could not construct ordered control')
a=get(i['selection']);d=get(a['declaration']);d['requests']=sorted([i['request'],sr,dr],key=lambda r:(r['kind'],r['sha256']));a['declaration']=put(d);i['selection']=put(a);save(iv,i)
run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',i['selection']['sha256'],'--output-dir',root/'result')
(root/'stdout').write_bytes(run.stdout);(root/'stderr').write_bytes(run.stderr)
record=dict(head=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),expected_code='DECODER_INVALID',actual_code=json.loads(run.stderr)['code'],exit=run.returncode,earlier_request=sr,later_request=dr,public_hash_consistent=True,no_output=not (root/'result').exists())
save(root/'observation.json',record);print(json.dumps(record))
