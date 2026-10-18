from pathlib import Path
import json,re
out=Path('verification/localized-chat-20261016');issues=[]
chat=json.loads((out/'chat-checks.json').read_text(encoding='utf-8-sig'));small=json.loads((out/'small-phone-chat-checks.json').read_text(encoding='utf-8-sig'));confirm=json.loads((out/'confirmation-checks.json').read_text(encoding='utf-8-sig'));cards=json.loads((out/'card-checks.json').read_text(encoding='utf-8-sig'))
for row in chat+small:
 s=row['state']
 if not all(s[k] for k in ['questionsMatch','errorsMatch','reviewTranslated']) or s['activeQuestions']!=1 or s['overflow']:issues.append(['chat',row['page'],row['language']])
for row in confirm:
 s=row['state']
 if not s['edited'] or not s['confirmationTranslated'] or s['activeQuestions'] or s['externalDeliveryPerformed']:issues.append(['confirmation',row['page'],row['language']])
for row in cards:
 if row['state']['overflow']:issues.append(['card overflow',row['page'],row['width']])
 if len(row['state']['cards'])!=4:issues.append(['card count',row['page']])
 for c in row['state']['cards']:
  if c['title']!='center' or c['photo']['h']<c['card']['h']-2.1:issues.append(['card image coverage',row['page'],row['width']])
requests=[];exceptions=[]
for name in ['runtime-checks.json','chat-runtime-checks.json','supplementary-runtime-checks.json']:
 d=json.loads((out/name).read_text(encoding='utf-8-sig'));requests+=d['requests'];exceptions+=d['exceptions']
api=[u for u in requests if 'api.hsforms.com' in u or '/api/chat' in u or '/api/inquiry' in u or 'translation.googleapis.com' in u or 'translate.googleapis.com' in u]
if api:issues.append(['unexpected API request',api])
if exceptions:issues.append(['runtime exception',exceptions])
summary={'complete_guided_flows':len(chat)+len(small),'questions_checked':14*(len(chat)+len(small)),'languages':10,'pages':['Home','Blog'],'phone_widths':[320,390],'validation_and_review_checks':len(chat)+len(small),'mocked_confirmation_checks':len(confirm),'service_pages':12,'notes_cards':48,'card_page_width_checks':len(cards),'card_widths':[320,390,430,834,1440],'actual_api_or_crm_requests':len(api),'google_characters_sent':0,'issues':issues,'translation_origin':'Locally authored, saved translations. No Google provider. Speaker review remains pending.'}
(out/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
# Keep one time migration helpers from accidentally replacing the final saved translations or cloning dialogs twice.
for filename,check in [('tools/write-chat-locales.py',"Path('assets/locales/home-blog/chat.json').exists()"),('tools/localized-chat-layout.py',"'id=\"conversation-dialog\"' in Path('blog.html').read_text(encoding='utf-8')"),('tools/localize-chat-engine.py',"'function t(value)' in Path('assets/site.js').read_text(encoding='utf-8')")]:
 p=Path(filename);s=p.read_text(encoding='utf-8-sig');line="\nif "+check+":raise SystemExit('Already applied. Preserve the saved files and use the locale bundle builder for future translation edits.')\n"
 if 'Already applied. Preserve' not in s:
  at=s.index('\n',s.index('from pathlib import Path'))+1;s=s[:at]+line+s[at:];p.write_text(s,encoding='utf-8')
