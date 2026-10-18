from pathlib import Path
import re,html,json,hashlib,shutil,collections,csv
from html.parser import HTMLParser
ROOT=Path('.');OUT=ROOT/'verification/state-content-replacement-20261016';OUT.mkdir(parents=True,exist_ok=True);(OUT/'before').mkdir(exist_ok=True)
source=ROOT/'paper-trail-50-state-bookkeeping-pages-expanded.md';raw=source.read_text(encoding='utf-8-sig');parts=re.split(r'^# (.+?) Bookkeeping\s*$',raw,flags=re.M);articles={parts[i]:parts[i+1].strip().strip('-').strip() for i in range(1,len(parts),2)}
expected={p.stem.replace('-',' ').title():p for p in (ROOT/'state-records').glob('*.html')};assert len(articles)==len(expected)==50 and set(articles)==set(expected)
urls=collections.defaultdict(set);paragraphs=collections.defaultdict(list);reviews=[];mapping=[]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.value=''
 def handle_data(self,t):self.value+=t

def prose(s):
 # Preserve form identifiers, statute references, official source names, and URL punctuation.
 spans=re.split(r'(https?://\S+|\b(?:[A-Za-z]+-)?\d[\w.-]*|Source(?:s)?:.*)',s)
 return ''.join(x if re.match(r'https?://|(?:[A-Za-z]+-)?\d|Sources?:',x) else re.sub(r'(?<=\w)[-\u2010\u2011\u2013\u2014](?=\w)',' ',x).replace(' \u2014 ', ', ').replace(' \u2013 ', ', ') for x in spans)

def inline(s,state):
 s=s.replace('https://jobs.utah.gov/ui/employer/public/NewHire/New Hire Handbook.pdf','https://jobs.utah.gov/ui/employer/public/NewHire/New%20Hire%20Handbook.pdf')
 tokens=[]
 def link(label,url):
  url=url.rstrip('.,;');assert url.startswith(('http://','https://'));urls[url].add(state);tokens.append('<a href="'+html.escape(url,quote=True)+'">'+html.escape(label)+'</a>');return '\x00'+str(len(tokens)-1)+'\x00'
 s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:link(m[1],m[2]),s)
 def bare(m):
  original=m[0];clean=original.rstrip('.,;');return link(clean,clean)+original[len(clean):]
 s=re.sub(r'https?://[^\s<>\x00]+',bare,s);s=html.escape(prose(s));s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s);s=re.sub(r'\x00(\d+)\x00',lambda m:tokens[int(m[1])],s);return s

for state,article in articles.items():
 p=expected[state];before=p.read_text(encoding='utf-8');shutil.copy2(p,OUT/'before'/p.name)
 blocks=re.split(r'\n\s*\n',article);rendered=[];sections=0;insection=False;proseblocks=[];flags=[]
 for block in blocks:
  block=block.strip()
  if not block or block=='---':continue
  if block.startswith('## '):
   if insection:rendered.append('</section>')
   rendered.append('<section><h2>'+inline(block[3:].strip(),state)+'</h2>');insection=True;sections+=1
  else:
   assert not block.startswith('#'),(state,block[:50])
   block=re.sub(r'\s*\n\s*',' ',block);proseblocks.append(block)
   rendered.append('<p'+(' class="state-summary"' if len(proseblocks)==1 else '')+'>'+inline(block,state)+'</p>')
   paragraphs[re.sub(r'\s+',' ',block).casefold()].append(state)
   for category,pattern in [('Malformed statutory reference',r'\bsection\d'),('Search snippet or secondary citation',r'search results|secondary (?:summary|retention|compilation|reporting|accounting|code publisher)'),('Missing contextual cross reference',r'\b(?:part|parts) \d'),('Staging or draft source',r'preview-stage|acsitefactory|proposed regulation'),('Unverified wording',r'not (?:verified|confirmed|reproduced)|subject to confirmation')]:
    if re.search(pattern,block,re.I):flags.append({'category':category,'supplied_text':block})
 if insection:rendered.append('</section>')
 body=''.join(rendered)
 # Replace only the information container. Preserve the flag, masthead, related links, page shell, and canonical URL.
 rx=r'(<div class="state-resource-body">).*?(</div><nav class="state-related")'
 changed,n=re.subn(rx,lambda m:m[1]+body+m[2],before,count=1,flags=re.S);assert n==1,state
 title=state+' Bookkeeping | Paper Trail'; intro=proseblocks[0];first=re.split(r'(?<=[.!?])\s+',intro)[0];description=prose(first)
 if len(description)>174:description=description[:171].rsplit(' ',1)[0]+'.'
 if not description.startswith(state):description=state+' bookkeeping. '+description[0].lower()+description[1:]
 if len(description)>190:description=description[:187].rsplit(' ',1)[0]+'.'
 changed=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',changed,count=1)
 changed=re.sub(r'(<meta (?:name="(?:description|twitter:description)"|property="og:description") content=")[^"]*(")',lambda m:m[1]+html.escape(description,quote=True)+m[2],changed)
 changed=re.sub(r'(<meta (?:name="twitter:title"|property="og:title") content=")[^"]*(")',lambda m:m[1]+html.escape(title,quote=True)+m[2],changed)
 def schema(m):
  d=json.loads(m[1]);
  if d.get('@type')=='WebPage':
   d.update(name=state+' Bookkeeping',description=description,citation=sorted(u for u,names in urls.items() if state in names));d.pop('lastReviewed',None)
  return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
 changed=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,changed,flags=re.S)
 assert re.findall(r'<link rel="canonical"[^>]*>',before)==re.findall(r'<link rel="canonical"[^>]*>',changed)
 assert re.findall(r'<h1\b',changed)==['<h1']
 # Assert shell untouched outside the targeted content and metadata.
 assert before[before.index('<body'):before.index('<div class="state-resource-body">')]==changed[changed.index('<body'):changed.index('<div class="state-resource-body">')]
 assert before[before.index('<nav class="state-related"'):]==changed[changed.index('<nav class="state-related"'):]
 p.write_text(changed,encoding='utf-8')
 count=len([u for u,names in urls.items() if state in names]);
 if count==0:flags.append({'category':'No direct source URLs','supplied_text':'No direct source URLs supplied for this state.'})
 reviews.append({'state':state,'page':p.as_posix(),'status':'Local replacement complete, factual publication review pending','source_count':count,'flags':flags})
 mapping.append({'state':state,'page':p.as_posix(),'h1':state+' Bookkeeping','paragraphs':len(proseblocks),'sections':sections,'source_count':count,'source_sha256':hashlib.sha256(article.encode()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'description':description,'existing_robots':re.search(r'<meta name="robots" content="([^"]+)',before)[1]})

duplicates=[{'states':states,'text':text} for text,states in paragraphs.items() if len(set(states))>1]
(OUT/'mapping.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8');(OUT/'individual-quality-reviews.json').write_text(json.dumps(reviews,indent=2),encoding='utf-8');(OUT/'source-urls.json').write_text(json.dumps([{'url':u,'states':sorted(v)} for u,v in sorted(urls.items())],indent=2),encoding='utf-8');(OUT/'duplicated-passages.json').write_text(json.dumps(duplicates,indent=2),encoding='utf-8');(OUT/'source-file.sha256').write_text(hashlib.sha256(source.read_bytes()).hexdigest(),encoding='utf-8')
print(json.dumps({'updated':len(mapping),'sources':len(urls),'duplicate_passages':len(duplicates),'flagged_states':sum(bool(r['flags']) for r in reviews),'states_without_direct_sources':[r['state'] for r in reviews if r['source_count']==0]}))
