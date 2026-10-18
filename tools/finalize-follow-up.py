from pathlib import Path
import json,csv,re
from html import unescape
out=Path('verification/follow-up-20261016');b=json.loads((out/'browser-checks.json').read_text(encoding='utf-8-sig'));c=json.loads((out/'cold-load-checks.json').read_text(encoding='utf-8-sig'))
summary={'pages':192,'page_device_checks':len(b['pageChecks']),'language_checks':len(b['languageChecks']),'cold_load_checks':len(c),'cold_load_protocols':['http','file'],'maximum_observed_layout_shift':max(sum(s['value'] for s in r['result']['shifts']) for r in c),'missing_images':sum(bool(r['state']['missingImages']) for r in b['pageChecks']),'overflow_failures':sum(bool(r['state']['overflow']) for r in b['pageChecks']),'runtime_exceptions':len(b['uncaughtExceptions']),'google_translation_requests':len(b['translationRequests']),'forms_submitted':0,'publication_performed':False}
(out/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
msg='Checked all 192 website pages on desktop, iPad, and mobile, 576 page and device combinations. All 60 language checks kept the header, menu, and language selector anchored. There were no observed overflow defects, missing images, or uncaught JavaScript exceptions. The 42 cold load checks, 21 HTTP and 21 direct file previews, recorded zero layout shift. These are local browser checks, not real user Core Web Vitals.'
p=Path('SEO-AEO-Master-Audit.md');s=p.read_text(encoding='utf-8');intro='## Follow up correction verification, October 16, 2026\n\n'+msg+'\n\nThe latest evidence and actual screenshots are in verification/follow-up-20261016/review.html. All 136 shared chat configurations now use a single question at each step, remove answered prompts, preserve answers, and support review and editing. Desktop phone links show call and copy options, mobile links preserve tel navigation. No real calls or inquiries were sent. PT-005 and PT-018 are corrected locally. The state source set has 327 URLs, with 51 earlier automated access limitations still recorded for factual review. State drafts remain noindex and excluded from the 142 URL published sitemap. Earlier counts below are historical snapshots.\n\n';s=s.replace('\n\n## Current visual','\n\n'+intro+'## Current visual',1);p.write_text(s,encoding='utf-8')
# Update source inventory statements that this follow up directly supersedes.
p=Path('SEO-AEO-Page-Inventory.csv')
with p.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
for r in rows:
 source=r.get('source_file','');file=Path(source)
 if source.startswith('state-records/'):
  r['content_findings']+=' Follow up: flag header present, public review date hidden at owner request, all sections have references. Internal review records retained.'
 if source in ['catch-up-bookkeeping-overdue-books.html','profit-vs-cash-flow-business-money.html','tax-ready-bookkeeping-records.html']:
  r['content_findings']+=' Owner confirmed Published 10/16/2026, shown visibly and in schema.'
 if file.is_file() and source.endswith('.html') and not source.startswith('verification/'):
  m=re.search(r'<main\b.*?</main>',file.read_text(encoding='utf-8'),re.S)
  if m:
   txt=unescape(re.sub(r'<[^>]+>',' ',m[0]));count=len(txt.split());r['content_findings']=re.sub(r'Main words \d+',f'Main words {count}',r['content_findings'])
with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
# Human readable local handoff, including actual evidence and remaining limits.
(out/'handoff.md').write_text('# Paper Trail follow up verification\n\n'+msg+'\n\nChanged shared CSS, JavaScript and local font assets, all 192 HTML documents for stable dimensions and resource versions, ten Home and Blog locale JSON files plus bundle, 50 state flag headers and their provenance manifest, state source research, Blog date manifest, relevant service card copy, and three audit reports. Detailed file groups and earlier snapshots are recorded in applied.json, card-copy-changes.json and before-assets.json.\n\nChat was tested through review, edit and reset without sending. Existing CRM fields are preserved; state and meeting details are included in the message field. Sources added to general examples are explicitly distinguished from state legal requirements. The earlier 51 source access limitations still need review, as does each state financial resource before owner publication. No Google API calls, commits, pushes, or publishing.\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
