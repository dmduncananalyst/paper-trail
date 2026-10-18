"""Static checks of local pages and the explicit correction requirements."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.links=[];self.base='';self.meta={};self.canonical='';self.selectors=0;self.h1=0;self.title='';self._title=False
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='base':self.base=a.get('href','')
        if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href','')
        if tag=='h1':self.h1+=1
        if tag=='title':self._title=True
        if a.get('id')=='language':self.selectors+=1
        for key in ['href','src','poster']:
            if key in a and tag!='base':self.links.append(a[key])
    def handle_endtag(self,tag):
        if tag=='title':self._title=False
    def handle_data(self,text):
        if self._title:self.title+=text

pages=list(root.glob('*.html'))+list((root/'state-records').glob('*.html'))
broken=[];metadata=[];selectors=[];schema_errors=[];state_checks=[]
for path in pages:
    text=path.read_text(encoding='utf-8');p=Page(text);relative=path.relative_to(root).as_posix()
    base=(path.parent/p.base).resolve() if p.base else path.parent
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc or not u.path:continue
        local=(root/u.path.lstrip('/')) if u.path.startswith('/') else (base/unquote(u.path))
        if not local.exists():broken.append({'page':relative,'link':link})
    if not p.title or not p.meta.get('description') or p.h1!=1:metadata.append(relative)
    if p.selectors:selectors.append(relative)
    for value in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
        try:json.loads(value)
        except Exception as error:schema_errors.append({'page':relative,'error':str(error)})
    if path.parent.name=='state-records':
        expected='https://www.papertrailusa.com/'+relative
        state_checks.append({'page':relative,'title':p.title,'description':p.meta.get('description'),'canonical_correct':p.canonical==expected,'draft_noindex':'noindex' in p.meta.get('robots',''),'review_date_hidden':'state-review-date' not in text,'flag_header_present':'reading-masthead state-masthead' in text})

sitemap=ET.parse(root/'sitemap.xml').getroot()
urls=[e.text for e in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
missing_sitemap=[u for u in urls if not (root/urlsplit(u).path.lstrip('/')).exists() and urlsplit(u).path!='/']
state_in_sitemap=[u for u in urls if '/state-records/' in u or '/verification/' in u]
nationwide=(root/'nationwide-bookkeeping.html').read_text(encoding='utf-8')
flags=re.search(r'<ul class="state-mosaic".*?</ul>',nationwide,re.S)[0]
root_selector_scope=sorted(selectors)==['blog.html','index.html']
report={'checked_on':'2026-10-16','html_pages':len(pages),'state_pages':len(state_checks),'root_selector_pages':selectors,'selector_scope_correct':root_selector_scope,'broken_local_resources':broken,'metadata_errors':metadata,'schema_errors':schema_errors,'state_checks':state_checks,'unique_state_titles':len({x['title'] for x in state_checks}),'unique_state_descriptions':len({x['description'] for x in state_checks}),'flag_count':flags.count('<li>'),'flag_links':flags.count('<a '),'state_action_labels':flags.count('class="state-action"'),'old_state_placeholder_present':'State resources are being reviewed.' in nationwide,'sitemap_entries':len(urls),'missing_sitemap_destinations':missing_sitemap,'draft_or_verification_sitemap_entries':state_in_sitemap,'google_translation_calls_made_by_check':0}
(root/'verification/visual-corrections/static-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
failures=len(broken)+len(metadata)+len(schema_errors)+len(missing_sitemap)+len(state_in_sitemap)+int(not root_selector_scope)
failures+=sum(not(x['canonical_correct'] and x['draft_noindex'] and x['review_date_hidden'] and x['flag_header_present']) for x in state_checks)
print(json.dumps({'pages':len(pages),'state_pages':len(state_checks),'sitemap_entries':len(urls),'state_flag_links':report['flag_links'],'failures':failures}))
raise SystemExit(bool(failures))
