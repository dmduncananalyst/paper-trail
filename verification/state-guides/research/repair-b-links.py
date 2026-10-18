import json
from pathlib import Path
p=Path('verification/state-guides/research/additional-b.json');d=json.loads(p.read_text(encoding='utf8'))
repl={
'https://www.revenue.state.mn.us/sites/default/files/2026-02/m4-inst-25.pdf':('https://www.revenue.state.mn.us/sites/default/files/2026-07/m4-inst-25.pdf','Minnesota 2025 Corporation Franchise Tax Instructions Revised July 2026','Official current form search identifies the July 2026 PDF; full 16 page PDF retrieved successfully through web tool and corporate filing and minimum fee passages inspected.'),
'https://www.dor.ms.gov/sites/default/files/Forms/Business/PassThroughEntity/84100218.pdf':('https://www.dor.ms.gov/sites/default/files/tax-forms/business/2025%20CIT%20INSTRUCTIONS%2083-100%20-%20Final%20%2001.14.2026.pdf','Mississippi 2025 Corporate Income And Franchise Tax Instructions','Official current 24 page PDF retrieved successfully through web tool; page 3 verifies franchise phaseout through 2027, repeal in 2028 and capital basis.')}
for x in d['pilots']:
 for s in x['sources']:
  if s['url'] in repl:
   s['url'],s['title'],s['verification']=repl[s['url']]
   print(x['code'],s['id'],s['url'])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
