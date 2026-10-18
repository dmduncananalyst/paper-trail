from pathlib import Path
import json
p=Path('verification/localized-chat-20261016/native-phone-digit-checks.json');d=json.loads(p.read_text(encoding='utf-8-sig'));print(json.dumps([{'language':r['language'],'review':r['review']['reviewTranslated'],'confirmation':r['confirmation'].get('confirmationTranslated'),'phone':[f['value'] for f in r['confirmation'].get('mockPayload',{}).get('fields',[]) if f['name']=='phone']} for r in d]))
