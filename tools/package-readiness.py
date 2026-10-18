"""Create local recoverable and staging archives. Never deploys or reads secrets."""
from pathlib import Path
import hashlib,json,re,zipfile
root=Path(__file__).resolve().parents[1]
out=root/'.release';out.mkdir(exist_ok=True)
locales=['es','fa','hy','zh-CN','ko','tl','te','ru','ar']
public=set(root.glob('*.html'))|set(root.glob('*.svg'))|set(root.glob('sitemap*.xml'))|{root/'robots.txt'}
for directory in ['assets','state-records',*locales]:
 public.update(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
assert not any(p.suffix.lower()=='.pdf' for p in public)
assert not any(any(x in p.parts for x in ['.git','.translation-cache','verification','tools','.release']) for p in public)
manifest={};staging=out/'paper-trail-staging.zip';recovery=out/'paper-trail-recovery.zip'
with zipfile.ZipFile(recovery,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as backup,zipfile.ZipFile(staging,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as preview:
 for p in sorted(public):
  name=p.relative_to(root).as_posix();data=p.read_bytes();manifest[name]=hashlib.sha256(data).hexdigest();backup.writestr('public/'+name,data)
  if p.suffix=='.html':
   text=data.decode('utf-8');text=re.sub(r'<meta\s+name="robots"[^>]*>','',text,flags=re.I)
   data=text.replace('</head>','<meta name="robots" content="noindex,nofollow"></head>',1).encode('utf-8')
  elif name=='robots.txt':data=b'User-agent: *\nDisallow: /\n'
  preview.writestr(name,data)
 for directory,extensions in [('tools',{'.py','.js','.ps1','.txt'}),('.translation-cache/provider-responses',{'.json'})]:
  for p in sorted((root/directory).rglob('*')):
   if p.is_file() and p.suffix in extensions and '__pycache__' not in p.parts:backup.writestr('authoring/'+p.relative_to(root).as_posix(),p.read_bytes())
 backup.writestr('public-sha256.json',json.dumps(manifest,indent=2))
 backup.writestr('RESTORE.txt','Unzip to a separate local folder. Serve public/ as the static site. All translations are saved. No Google credentials are required to display pages. authoring/ is private local workflow and provider receipt evidence, never publish it. The private shared budget ledger and existing sibling translation_pipeline modules are required only for authoring, not visitor display. No credentials or instruction PDF are in this archive. Compare public files against public-sha256.json. Do not deploy this entire recovery archive. The staging archive has noindex on every HTML page and a disallow all robots file. Production pages are preserved under public/, including noindex on unapproved state pages. Owner handles commits and publication.')
checks={}
for label,p in [('staging',staging),('recovery',recovery)]:
 with zipfile.ZipFile(p) as archive:
  bad=archive.testzip();checks[label]={'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crc_verified':bad is None,'entries':len(archive.infolist())}
  if bad:raise ValueError('Archive CRC failure '+bad)
  if label=='recovery':
   for name,expected in manifest.items():
    if hashlib.sha256(archive.read('public/'+name)).hexdigest()!=expected:raise ValueError('Recovery differs '+name)
report={'public_files':len(manifest),'public_html_pages':sum(n.endswith('.html') for n in manifest),'pdf_included':False,'credentials_included':False,'published':False,'archive_checks':checks,'recovery_hashes_verified':True}
dest=root/'verification/dns-readiness-20261016';dest.mkdir(parents=True,exist_ok=True)
(dest/'package-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
