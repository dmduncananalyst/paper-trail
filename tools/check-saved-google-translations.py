"""Offline verification of all saved pages, references, and Google provenance."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,urljoin,unquote
import importlib.util,json,re,hashlib,xml.etree.ElementTree as ET
from functools import lru_cache
@lru_cache(maxsize=None)
def reference_exists(path):return Path(path).exists()
spec=importlib.util.spec_from_file_location('pt',Path(__file__).with_name('paper-trail-translations.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Page(HTMLParser):
 def __init__(self,s):super().__init__();self.links=[];self.media=[];self.ids=[];self.tags=[];self.selectors=0;self.credit=0;self.h1=0;self.body=False;self.feed(s)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='body':self.body=True
  if self.body:self.tags.append(t)
  if 'id' in a:self.ids.append(a['id'])
  if t=='a' and a.get('href'):self.links.append(a['href'])
  if t in ['img','video','source'] and a.get('src'):self.media.append(a['src'])
  if t=='select' and a.get('id')=='language':self.selectors+=1
  if t=='aside' and a.get('class')=='translation-credit':self.credit+=1
  if t=='h1':self.h1+=1
root=m.ROOT;out=m.OUT;current=json.loads((root/m.BASE/'current.json').read_text());issues=[];total=0;local_links=0;media=0
fields=json.loads((root/m.BASE/'releases'/current['revision']/'fields.json').read_text())['fields']
for key,row in fields.items():
 if row.get('provider')!='google' or key!=m.key(row['source'],row['locale']):issues.append({'cache':key,'error':'Invalid provenance or source fingerprint'})
pages,refs,_,missing,inventory=m.inventory()
if inventory['candidate_fields']:issues.append({'error':'Missing saved translations','fields':inventory['candidate_fields']})
before=out/'before'
for name,inv in pages.items():
 original=(before/name).read_text(encoding='utf-8')
 def without_requested_footer_row(markup):return re.sub(r'(<footer class="pt-footer">).*?(<nav class="footer-cities")',r'\1\2',markup,count=1,flags=re.S)
 orig=m.Inventory(without_requested_footer_row(original));current_source=m.Inventory(without_requested_footer_row(inv.markup))
 permitted_header_sources={'Language','Only the Home and Blog pages are available in this language.'}
 if [s['source'] for s in orig.slots if s['source'] not in permitted_header_sources]!=[s['source'] for s in current_source.slots if s['source'] not in permitted_header_sources]:issues.append({'page':name,'error':'English source changed beyond requested header and footer rows'})
 if re.search(r'<link rel="canonical"[^>]*>',original)[0]!=re.search(r'<link rel="canonical"[^>]*>',inv.markup)[0]:issues.append({'page':name,'error':'English canonical changed'})
 expected=Page(original);draft=bool(re.search(r'<meta name="robots" content="[^"]*noindex',original))
 for locale in m.LOCALES:
  file=root/locale/name;total+=1
  if not file.exists():issues.append({'page':str(file),'error':'Missing file'});continue
  s=file.read_text(encoding='utf-8');parsed=Page(s)
  if parsed.h1!=expected.h1 or parsed.h1!=1:issues.append({'page':str(file),'error':'H1 mismatch'})
  if [x for x in parsed.media if x!='assets/google-translate-attribution.png']!=expected.media:issues.append({'page':str(file),'error':'Media changed'})
  if parsed.credit!=1:issues.append({'page':str(file),'error':'Missing or duplicate Google credit'})
  if parsed.selectors!=1:issues.append({'page':str(file),'error':'Language selector scope'})
  if draft!=bool(re.search(r'<meta name="robots" content="[^"]*noindex',s)):issues.append({'page':str(file),'error':'Draft indexing changed'})
  if re.search(r'<link rel="canonical" href="([^"]+)',s)[1]!='https://www.papertrailusa.com/'+locale+'/'+name:issues.append({'page':str(file),'error':'Localized canonical'})
  base=re.search(r'<base href="([^"]+)',s)[1];base=urljoin(file.as_uri(),base)
  for value in parsed.links+parsed.media:
   u=urlsplit(value)
   if u.scheme or u.netloc:continue
   dest=Path(unquote(urlsplit(urljoin(base,value)).path).lstrip('/') if re.match(r'^/[A-Za-z]:/',urlsplit(base).path) else unquote(urlsplit(urljoin(base,value)).path))
   if not reference_exists(str(dest)):issues.append({'page':str(file),'error':'Missing local reference','url':value})
   if value in parsed.links:local_links+=1
   else:media+=1
sitemap=ET.parse(root/'sitemap-translations.xml');urls=[e.text for e in sitemap.getroot().iter() if e.tag.endswith('}loc')]
if len(urls)!=len(set(urls)):issues.append({'error':'Duplicate sitemap URLs'})
for url in urls:
 file=root/urlsplit(url).path.lstrip('/')
 if not file.is_file() or re.search(r'<meta name="robots" content="[^"]*noindex',file.read_text(encoding='utf-8')):issues.append({'error':'Invalid sitemap entry','url':url})
manifest=json.loads((root/'assets/locales/home-blog/manifest.json').read_text());report={'translated_pages':total,'source_pages':len(pages),'local_links_checked':local_links,'media_references_checked':media,'sitemap_entries':len(urls),'cache_fields':len(fields),'pending_fields':inventory['candidate_fields'],'provider':manifest['provider'],'actual_google_calls':manifest['google_calls'],'actual_google_characters_sent':manifest['google_characters_sent'],'issues':issues}
(out/'static-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='issues'}));print('Issues:',len(issues));print(json.dumps(issues[:10]))
raise SystemExit(bool(issues))
