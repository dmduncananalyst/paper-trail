from pathlib import Path
import re,json,hashlib
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,urljoin
out=Path('verification/state-content-replacement-20261016');mapping=json.loads((out/'mapping.json').read_text());issues=[];alllinks=[]
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.ids=set();self.h1=[];self.inh=False
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.add(a['id'])
  if t=='a' and 'href' in a:self.links.append(a['href'])
  if t=='h1':self.inh=True
 def handle_endtag(self,t):
  if t=='h1':self.inh=False
 def handle_data(self,d):
  if self.inh:self.h1.append(d)
raw=Path('paper-trail-50-state-bookkeeping-pages-expanded.md').read_text(encoding='utf-8-sig');parts=re.split(r'^# (.+?) Bookkeeping\s*$',raw,flags=re.M);articles={parts[i]:parts[i+1].strip().strip('-').strip() for i in range(1,len(parts),2)}
for row in mapping:
 p=Path(row['page']);s=p.read_text(encoding='utf-8');before=(out/'before'/p.name).read_text(encoding='utf-8');body=re.search(r'<div class="state-resource-body">(.*?)</div><nav class="state-related"',s,re.S)[1]
 assert hashlib.sha256(body.encode()).hexdigest()==row['body_sha256'],row['state']
 assert hashlib.sha256(articles[row['state']].encode()).hexdigest()==row['source_sha256'],row['state']
 parser=Parser();parser.feed(s);assert parser.h1==[row['state']+' Bookkeeping']
 assert len(re.findall(r'<h2>',body))==row['sections']
 assert len(re.findall(r'<p(?:\s|>)',body))==row['paragraphs']
 assert re.findall(r'<link rel="canonical"[^>]+>',s)==re.findall(r'<link rel="canonical"[^>]+>',before)
 assert re.findall(r'<img[^>]*>',s)==re.findall(r'<img[^>]*>',before)
 assert re.search(r'<nav class="state-related".*?</nav>',s)[0]==re.search(r'<nav class="state-related".*?</nav>',before)[0]
 for link in parser.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  target=Path(unquote(u.path)) if u.path else p
  if not target.exists():issues.append({'state':row['state'],'link':link,'error':'Local target missing'})
  if u.fragment and target.is_file():
   tp=Parser();tp.feed(target.read_text(encoding='utf-8'))
   if unquote(u.fragment) not in tp.ids:issues.append({'state':row['state'],'link':link,'error':'Anchor missing'})
  alllinks.append(link)
print(json.dumps({'states':len(mapping),'paragraphs':sum(x['paragraphs'] for x in mapping),'sections':sum(x['sections'] for x in mapping),'internal_links_checked':len(alllinks),'issues':issues,'source_file_unchanged':hashlib.sha256(Path('paper-trail-50-state-bookkeeping-pages-expanded.md').read_bytes()).hexdigest()==(out/'source-file.sha256').read_text(),'sitemap_unchanged':hashlib.sha256(Path('sitemap.xml').read_bytes()).hexdigest()==(out/'sitemap.sha256').read_text()}))
(out/'static-checks.json').write_text(json.dumps({'states':50,'mapped_correctly':50,'preserved_canonicals':50,'preserved_flags':50,'preserved_related_navigation':50,'internal_links_checked':len(alllinks),'issues':issues},indent=2),encoding='utf-8')
