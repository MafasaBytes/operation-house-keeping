from pathlib import Path
import json,xml.etree.ElementTree as ET,hashlib,shutil
out=Path('/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-09-23-next-measurement-release-evidence');records={}
for name in ['nm-final-full-suite','nm-release-application-gates','nm-release-application-gates-ready','nm-release-loopback-rerun']:
 root=ET.parse('/tmp/'+name+'.xml').getroot();suites=list(root.iter('testsuite'));cases=list(root.iter('testcase'));issues=[]
 for c in cases:
  for kind in ['skipped','failure','error']:
   node=c.find(kind)
   if node is not None:issues.append(dict(node=c.attrib.get('classname','')+'::'+c.attrib['name'],kind=kind,message=node.attrib.get('message'),text=node.text))
 records[name]=dict(tests=sum(int(s.attrib['tests']) for s in suites),errors=sum(int(s.attrib['errors']) for s in suites),failures=sum(int(s.attrib['failures']) for s in suites),skipped=sum(int(s.attrib['skipped']) for s in suites),seconds=sum(float(s.attrib['time']) for s in suites),issues=issues)
 for suffix in ['xml','log']:shutil.copyfile('/tmp/'+name+'.'+suffix,out/(name+'.'+suffix))
(out/'test-accounting.json').write_text(json.dumps(records,sort_keys=True))
print(json.dumps({k:{n:v for n,v in r.items() if n!='issues'} for k,r in records.items()},indent=2))
