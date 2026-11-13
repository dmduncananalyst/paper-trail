"""Stage the explicit release inventory, leaving earlier working changes untouched."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/articles-20261113'
A=json.loads((OUT/'approved-content.json').read_text(encoding='utf8'))
LANGS=['','es','fa','hy','zh-CN','ko','tl','te','ru','ar']
paths=[(l+'/' if l else '')+a['slug'] for l in LANGS for a in A]
paths += [(l+'/' if l else '')+'blog.html' for l in LANGS]
paths += [a['image'] for a in A]
paths += ['sitemap.xml','sitemap-translations.xml','tools/production-pages.json','tools/sync-blog-translations.py','tools/build-public-site.ps1','assets/translation-workflow/current.json','assets/translation-workflow/routes.js','assets/locales/home-blog/manifest.json','assets/locales/home-blog/provider-current.json']
revision=json.loads((ROOT/'assets/translation-workflow/current.json').read_text())['revision']
paths += ['assets/translation-workflow/releases/'+revision+'/fields.json']
paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'tools').glob('*20261113*') if p.is_file()]
paths += [p.relative_to(ROOT).as_posix() for p in OUT.iterdir() if p.is_file() and p.name not in ['staged-security-review.json','live-verification.json']]
paths=sorted(set(paths))
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).strip(),'Pre-existing staged files require review'
assert all((ROOT/p).is_file() for p in paths)
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
staged=set(subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).decode().splitlines())
assert staged.issubset(set(paths))
print(json.dumps({'staged_files':len(staged),'publication_scope':'80 articles, 10 archives, 8 photos, translation state, safeguards and release evidence; prior work excluded'},indent=2))
