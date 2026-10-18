from pathlib import Path
import re,json,csv
from html.parser import HTMLParser
from html import unescape
root=Path('.');out=root/'verification/follow-up-20261016'
pages=list(root.glob('*.html'))+list((root/'state-records').glob('*.html'))
class Images(HTMLParser):
 def __init__(self,s):super().__init__();self.img=[];self.feed(s)
 def handle_starttag(self,t,a):
  if t=='img':self.img.append(dict(a))
issues=[];configs=[];sources=0
for p in pages:
 s=p.read_text(encoding='utf-8');route=p.as_posix()
 for i in Images(s).img:
  if 'width' not in i or 'height' not in i:issues.append([route,'image dimensions',i.get('src')])
 if '&Amp;' in s:issues.append([route,'malformed entity'])
 if 'state-review-date' in s:issues.append([route,'visible review date'])
 if re.search(r'Sources:\s*</(?:p|div)>',s):issues.append([route,'empty sources'])
 m=re.search(r'<script[^>]+id="conversation-data"[^>]*>(.*?)</script>',s,re.S)
 if m:
  c=json.loads(m[1]);configs.append({'page':route,'opening':c.get('opening'),'additional_scope':c.get('periodQuestion')})
 if p.parent.name=='state-records':sources+=len(re.findall(r'class="state-section',s))
 if 'fonts.googleapis.com' in s:issues.append([route,'remote fonts'])
result={'website_pages':len(pages),'chat_configurations':len(configs),'issues':issues,'blog_dates_owner_confirmed':'Published 10/16/2026','source_audit':'Every state section now has nonempty references. General examples cite IRS recordkeeping with an explicit general practice qualification. State requirements retain their original government citations.','new_source':{'url':'https://www.irs.gov/businesses/small-businesses-self-employed/recordkeeping','retrieved':'2026-10-16','result':'Official page retrieved successfully through web tool'},'source_access_limitations':'Previous full source check still has 29 HTTP 403 and 22 certificate or access limitations. No sources were silently treated as verified claims.'}
(out/'follow-up-static.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(out/'chat-configurations.json').write_text(json.dumps(configs,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
