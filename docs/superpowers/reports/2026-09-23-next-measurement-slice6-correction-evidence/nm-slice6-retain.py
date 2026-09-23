from pathlib import Path
import hashlib,json,os,stat,zipfile
out=Path('/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-09-23-next-measurement-slice6-correction-evidence')
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,v):p.write_text(json.dumps(v,sort_keys=True,separators=(',',':')))
def archive(label,root):
 root=Path(root);rows=[];recovered=0;total=0
 with zipfile.ZipFile(out/(label+'.zip'),'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(root.rglob('*')):
   rel=p.relative_to(root).as_posix();st=p.lstat()
   if stat.S_ISREG(st.st_mode):
    b=p.read_bytes();z.writestr(rel,b);rows.append(dict(path=rel,kind='file',bytes=len(b),sha256=sha(b)));total+=len(b)
   elif stat.S_ISDIR(st.st_mode):z.writestr(rel+'/',b'');rows.append(dict(path=rel,kind='directory'))
   elif stat.S_ISLNK(st.st_mode):rows.append(dict(path=rel,kind='symlink',target=os.readlink(p)))
   else:rows.append(dict(path=rel,kind='special',mode=st.st_mode))
 save(out/(label+'-inventory.json'),rows)
 with zipfile.ZipFile(out/(label+'.zip')) as z:
  for r in rows:
   if r['kind']=='file':
    b=z.read(r['path']);assert len(b)==r['bytes'] and sha(b)==r['sha256'];recovered+=1
 record=dict(archive=label+'.zip',source=str(root),files_verified=recovered,expanded_regular_bytes=total,archive_bytes=(out/(label+'.zip')).stat().st_size,archive_sha256=sha((out/(label+'.zip')).read_bytes()),specials='Recorded as metadata only; never followed or automatically recreated')
 save(out/(label+'-recovery.json'),record);print(json.dumps(record),flush=True)
if __name__=='__main__':
 import sys
 for label,root in zip(sys.argv[1::2],sys.argv[2::2]):archive(label,root)
