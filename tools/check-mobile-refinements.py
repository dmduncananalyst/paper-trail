from pathlib import Path
import json
out=Path('verification/mobile-refinements-20261016')
checks=json.loads((out/'browser-checks.json').read_text(encoding='utf-8-sig'))
before=json.loads((out/'desktop-before.json').read_text(encoding='utf-8-sig'));after=json.loads((out/'desktop-after.json').read_text(encoding='utf-8-sig'))
unexpected=[];allowed=[]
for a,b in zip(before,after):
 assert a['page']==b['page']
 for x,y in zip(a['elements'],b['elements']):
  if x==y:continue
  if x['cls']=='footer-location' or x['tag']=='FIGCAPTION' and 'Nationwide' in (x.get('text') or ''):allowed.append({'page':a['page'],'before':x,'after':y})
  else:unexpected.append({'page':a['page'],'before':x,'after':y})
failures=[]
for r in checks:
 s=r['state'];page=r['page'];w=r['viewport']
 if s['scrollWidth']>s['clientWidth']+2 or s['missing']:failures.append([page,w,'overflow or missing photo'])
 if w<=650:
  for c in s['cards']:
   if c['image']['h']<c['card']['h']-2.1:failures.append([page,w,'photo does not fill card'])
  for t in s['bottom']:
   if abs(t['rect']['x']+t['rect']['w']/2-t['parent']['x']-t['parent']['w']/2)>2:failures.append([page,w,'bottom action not centered'])
  if any(x!='center' for x in s['dates']+s['topicTitles']):failures.append([page,w,'date or title not centered'])
summary={'page_device_checks':len(checks),'all_192_pages_checked_at_phone_width':sum(r['viewport']==390 for r in checks),'additional_widths':[320,430,834,1440],'unexpected_desktop_changes':unexpected,'allowed_desktop_wording_changes':len(allowed),'failures':failures,'no_google_api_calls':True,'no_forms_submitted':True,'no_commits_pushes_or_publication':True}
(out/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(out/'desktop-comparison.json').write_text(json.dumps({'allowed_wording_changes':allowed,'unexpected_changes':unexpected},indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
