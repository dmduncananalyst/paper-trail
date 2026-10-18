from pathlib import Path
import json,csv
out=Path('verification/localized-chat-20261016');summary=json.loads((out/'verification-summary.json').read_text(encoding='utf-8'));digits=json.loads((out/'native-phone-digit-checks.json').read_text(encoding='utf-8-sig'));assert all(r['confirmation']['confirmationTranslated'] and any(f['name']=='phone' and f['value']=='8185550123' for f in r['confirmation']['mockPayload']['fields']) for r in digits);summary['native_phone_digit_checks']=len(digits);summary['saved_chat_phrases_per_language']=89;(out/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
# Keep current audit findings accurate without changing unrelated recommendations.
p=Path('SEO-AEO-Priority-Fix-List.csv')
with p.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
for row in rows:
 if row['issue_id']=='PT-003':
  row['problem']='Multilingual release still needs speaker and production review.'
  row['evidence']='Home and Blog now have ten saved guided chat languages, including questions, choices, validation, review, editing and confirmation. Forty complete phone flows passed and twenty delivery confirmations were mocked. Other pages remain English. Translations are locally authored, not Google translations. No real CRM delivery or paid translation backend verified.'
  row['recommended_fix']='Obtain speaker review of saved translations and explicitly approved production inquiry tests. Keep existing language selector scope. Do not make paid translation calls or publish without owner approval.'
  row['status']='Review Pending'
with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
p=Path('SEO-AEO-Master-Audit.md');text=p.read_text(encoding='utf-8');heading='## Localized guided chat and service Notes correction, October 16, 2026\n\n'
if heading not in text:
 text=text.replace('\n\n','\n\n'+heading+'Home and Blog now have ten local guided chat translations with the unchanged question order and canonical answer meanings. Forty complete flows checked 560 questions at phone widths, with localized validation and review. Twenty delivery confirmations were mocked, not sent to the CRM. Four native digit formats normalize to the same valid phone number. The 48 Notes cards across twelve service pages use the About card composition on phones. Home Notes cards and the main Notes cards are preserved, with only the requested heading placement, unwanted Blog link removal and spacing changes. Speaker review and real production delivery remain pending. No Google API calls, commits, pushes or publication occurred. Latest screenshots and evidence: verification/localized-chat-20261016/review.html.\n\n',1);p.write_text(text,encoding='utf-8')
modified=['assets/site.js','assets/design.css','assets/design.js','assets/hubspot.js','index.html','blog.html','notes.html','assets/locales/home-blog/chat.json','assets/locales/home-blog/current.js','assets/locales/home-blog/manifest.json']+[p.as_posix() for p in Path('assets/locales/home-blog').glob('*.json') if p.name not in ['chat.json','manifest.json']]
(out/'modified-files.json').write_text(json.dumps({'functional_and_layout_files':modified,'resource_version_updates':'All 192 website and state HTML files reference the current local assets.','audit_findings_updated':['SEO-AEO-Master-Audit.md','SEO-AEO-Priority-Fix-List.csv'],'no_commits_pushes_or_publication':True},indent=2),encoding='utf-8')
print('Native digit checks and local handoff recorded.')
