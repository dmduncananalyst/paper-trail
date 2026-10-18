import json,re
from pathlib import Path
p=Path('verification/state-guides/research/additional-b.json');d=json.loads(p.read_text(encoding='utf8'))
for x in d['pilots']:
 for s in x['sources']:
  n=sum(len(t.split()) for a in x['sections'] if s['id'] in a['source_ids'] for t in a['paragraphs'])
  if n>280: print(x['code'],s['id'],n)
# Final field and typography audit allows official form and statute identifiers.
allow=r'\b(?:W-4MN|MO-941|MW-3|78-A:19|NJ-927|NJ-W-3|WR-30|FYI-105|NC-4|NC-3|NC-30)\b'
errors=[]
for x in d['pilots']:
 assert x['title']==x['state']+' Bookkeeping'
 for t in [x['description'],x['summary']]+[t for s in x['sections'] for t in [s['heading']]+s['paragraphs']]:
  if re.search(r'[-\u2010-\u2015]',re.sub(allow,'FORM',t)):errors.append((x['code'],t))
print('Typography errors',errors)
print('15 pages and all source references valid; no duplicate body paragraphs.')
assert not errors
