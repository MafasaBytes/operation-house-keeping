import json,base64,hashlib,pathlib,subprocess
root=pathlib.Path('/mnt/d/operation-house-keeping')
p=root/'docs/superpowers/reports/2026-09-19-next-measurement-preparation'
out=root/'docs/superpowers/reports/2026-09-23-next-measurement-slice6-oracle-closure-evidence'
def sha(b):return hashlib.sha256(b).hexdigest()
def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
c=json.loads((p/'inputs/CL-historical-invalid/capture.json').read_bytes())
objects={m['reference']['sha256']:base64.b64decode(m['bytes'],validate=True) for m in c['members']}
assert all(sha(b)==s for s,b in objects.items())
def get(r):return json.loads(objects[r['sha256']])
i=get(c['invocation']);q=get(i['request']);rows=[];path=''
while True:
 for idx,pr in enumerate(q['measurements']):
  procedure=get(pr);decoder=get(procedure['decoder'])
  if decoder['id']=='OLD-O':
   high,low=decoder['outcomes'];assert high['region']['lower']==low['region']['upper']=={'numerator':'50','denominator':'1'}
   assert high['region']['lower_closed']==low['region']['upper_closed']==False
   rows.append(dict(revision=q['revision'],decoder=procedure['decoder'],code='DECODER_INVALID',stage='phase_3',field=path+'/measurements/'+str(idx)+'/decoder',reason='50 belongs to neither declared interval'))
 if q['predecessor'] is None:break
 path+='/predecessor';q=get(q['predecessor'])
assert len(rows)==2
rows.sort(key=lambda r:(r['code'].encode('ascii'),r['field'].encode('ascii')))
assert [r['revision'] for r in rows]==[2,1]
old=(p/'expected/CL-historical-invalid/stderr.jsonl').read_bytes()
v=json.loads(old);oldvalue=v['target']['field'];v['target']['field']=rows[0]['field'];new=wire(v)+b'\n'
assert sha(new)=='ed2b2e22dee2ba86342ffe708c1a50faf477887f29905d797483f2280bb4c072'
record=dict(authority='semantic-candidate section 4 normative phase/code ASCII/canonical path order; phase 3 decoder totality; neither phase 2 traversal nor nomination exceptions apply',oracle_authorship='same author independent static derivation, not independent reviewer evidence and no runtime output used',candidates=rows,comparison=dict(common_prefix='/predecessor/',first_distinct_bytes=[109,112],letters=['m','p']),pointer='/target/field',old=oldvalue,new=rows[0]['field'],old_sha256=sha(old),new_sha256=sha(new),amendment_sha256='013363cad50982537b1643a764354e062b29a23e54ff25b2bc1de2a18a459128',status='owner authorized subject to normative verification; verified; overlay only',base_package_sha256=sha((p/'package.zip').read_bytes()))
(out/'normative-derivation.json').write_bytes(wire(record))
(out/'corrected-stderr.jsonl').write_bytes(new)
print(json.dumps(record,indent=2))
