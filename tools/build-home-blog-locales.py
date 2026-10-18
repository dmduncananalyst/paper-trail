from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]/'assets/locales/home-blog'
chat=json.loads((root/'chat.json').read_text(encoding='utf-8'))
locales={code:json.loads((root/(code+'.json')).read_text(encoding='utf-8')) for code in chat}
assert all(set(d)==set(chat['en']) for d in chat.values())
(root/'current.js').write_text('/* Saved authored Home, Blog and guided chat translations. No provider calls. */\nwindow.PAPER_TRAIL_LOCALES='+json.dumps(locales,ensure_ascii=False)+';\nwindow.PAPER_TRAIL_CHAT_LOCALES='+json.dumps(chat,ensure_ascii=False)+';\n',encoding='utf-8')
print('Built ten page locales and ten guided chat locales, without API calls.')
