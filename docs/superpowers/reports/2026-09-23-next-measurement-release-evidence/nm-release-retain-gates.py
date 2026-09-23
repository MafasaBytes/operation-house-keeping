from pathlib import Path
import hashlib,json,zipfile,subprocess
root=Path('/tmp/nm-release-application-gates-ready');out=Path('/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-09-23-next-measurement-release-evidence');rows=[];clones=[]
selected=[p for p in root.iterdir() if p.is_dir() and not p.is_symlink() and p.name.startswith(('test_two_clean_roots_twelve','test_accepted_s6_archive'))]
with zipfile.ZipFile(out/'fresh-s7-gates.zip','x',zipfile.ZIP_DEFLATED) as z:
 for case in selected:
  for p in sorted(case.rglob('*')):
   rel=p.relative_to(case)
   if rel.parts[0] in ['source-0','source-1','accepted-source']:
    if len(rel.parts)==1:clones.append(dict(path=str(p),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p).decode().strip(),status=subprocess.check_output(['git','status','--porcelain'],cwd=p).decode()))
    continue
   if p.is_file() and not p.is_symlink():
    b=p.read_bytes();name=p.relative_to(root).as_posix();z.writestr(name,b);rows.append(dict(path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
with zipfile.ZipFile(out/'fresh-s7-gates.zip') as z:
 for r in rows:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
(out/'fresh-s7-gates-recovery.json').write_text(json.dumps(dict(files=rows,clones=clones,excluded='Reconstruct source clones from exact committed heads; all original runtime directories preserved',archive_sha256=hashlib.sha256((out/'fresh-s7-gates.zip').read_bytes()).hexdigest(),expanded_bytes=sum(r['bytes'] for r in rows)),sort_keys=True))
print(len(rows),sum(r['bytes'] for r in rows),clones)
